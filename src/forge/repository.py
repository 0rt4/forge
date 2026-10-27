"""SQLite persistence for Forge projects."""

import sqlite3
from contextlib import closing
from pathlib import Path

from .models import Project


class ProjectRepository:
    """Store and retrieve projects in a SQLite database."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)

    def initialize(self) -> None:
        """Create the projects table if it does not already exist."""
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        path TEXT,
                        description TEXT NOT NULL DEFAULT ''
                    )
                    """
                )

    def save(self, project: Project) -> Project:
        """Insert a project and return it with its database ID."""
        if project.id is not None:
            raise ValueError("Cannot save a project that already has an ID")

        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
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
        """Return a project by ID, or None when no such project exists."""
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT id, name, path, description FROM projects WHERE id = ?",
                (project_id,),
            ).fetchone()

        if row is None:
            return None

        return Project(
            id=row["id"],
            name=row["name"],
            path=row["path"],
            description=row["description"],
        )
