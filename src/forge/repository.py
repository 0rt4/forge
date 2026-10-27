"""SQLite persistence for Forge projects."""

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from .models import Project


class ProjectPathConflictError(ValueError):
    """Raised when another project already uses the requested path."""


class ProjectRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)

    def initialize(self) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        path TEXT,
                        description TEXT NOT NULL DEFAULT '',
                        archived_at TEXT
                    )
                    """
                )
                columns = {
                    row[1]
                    for row in connection.execute("PRAGMA table_info(projects)")
                }
                if "archived_at" not in columns:
                    connection.execute("ALTER TABLE projects ADD COLUMN archived_at TEXT")

    def save(self, project: Project) -> Project:
        if project.id is not None:
            raise ValueError("Cannot save a project that already has an ID")

        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                if project.path:
                    owner = connection.execute(
                        "SELECT id FROM projects WHERE path = ?", (project.path,)
                    ).fetchone()
                    if owner is not None:
                        raise ProjectPathConflictError(
                            f"Path is already used by project {owner[0]}: {project.path}"
                        )
                cursor = connection.execute(
                    "INSERT INTO projects (name, path, description) VALUES (?, ?, ?)",
                    (project.name, project.path, project.description),
                )
                project_id = cursor.lastrowid

        return Project(
            id=project_id,
            name=project.name,
            path=project.path,
            description=project.description,
        )

    def get(self, project_id: int) -> Project | None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT id, name, path, description, archived_at FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()

        if row is None:
            return None

        return Project(
            id=row["id"],
            name=row["name"],
            path=row["path"],
            description=row["description"],
            archived_at=row["archived_at"],
        )

    def list(self, include_archived: bool = False) -> list[Project]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            where_clause = "" if include_archived else "WHERE archived_at IS NULL"
            rows = connection.execute(
                f"SELECT id, name, path, description, archived_at FROM projects "
                f"{where_clause} ORDER BY id"
            ).fetchall()

        return [
            Project(
                id=row["id"],
                name=row["name"],
                path=row["path"],
                description=row["description"],
                archived_at=row["archived_at"],
            )
            for row in rows
        ]

    def update(self, project_id: int, changes: dict[str, str | None]) -> Project | None:
        allowed_fields = {"name", "path", "description"}
        if not changes or not changes.keys() <= allowed_fields:
            raise ValueError("Changes must include one or more editable project fields")

        changes = dict(changes)
        assignments = ", ".join(f"{field} = ?" for field in changes)
        values = [*changes.values(), project_id]
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                exists = connection.execute(
                    "SELECT 1 FROM projects WHERE id = ?", (project_id,)
                ).fetchone()
                if exists is None:
                    return None

                path = changes.get("path")
                if "path" in changes and path:
                    owner = connection.execute(
                        "SELECT id FROM projects WHERE path = ? AND id != ?",
                        (path, project_id),
                    ).fetchone()
                    if owner is not None:
                        raise ProjectPathConflictError(
                            f"Path is already used by project {owner[0]}: {path}"
                        )
                cursor = connection.execute(
                    f"UPDATE projects SET {assignments} WHERE id = ?", values
                )
                if cursor.rowcount == 0:
                    return None

        return self.get(project_id)

    def archive(self, project_id: int) -> bool:
        archived_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    "UPDATE projects SET archived_at = COALESCE(archived_at, ?) WHERE id = ?",
                    (archived_at, project_id),
                )
                return connection.execute(
                    "SELECT 1 FROM projects WHERE id = ?", (project_id,)
                ).fetchone() is not None

    def restore(self, project_id: int) -> bool:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    "UPDATE projects SET archived_at = NULL WHERE id = ?", (project_id,)
                )
                return connection.execute(
                    "SELECT 1 FROM projects WHERE id = ?", (project_id,)
                ).fetchone() is not None
