"""Behavioral tests for project persistence."""

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from forge.models import Project
from forge.repository import ProjectRepository


class ProjectRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "forge.db"
        self.repository = ProjectRepository(self.database_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_initialize_creates_projects_table_and_is_repeatable(self) -> None:
        self.repository.initialize()
        self.repository.initialize()

        with closing(sqlite3.connect(self.database_path)) as connection:
            table = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'projects'"
            ).fetchone()

        self.assertEqual(table, ("projects",))

    def test_initialize_migrates_existing_table_without_losing_projects(self) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    "CREATE TABLE projects (id INTEGER PRIMARY KEY, name TEXT NOT NULL, "
                    "path TEXT, description TEXT NOT NULL DEFAULT '')"
                )
                connection.execute(
                    "INSERT INTO projects (id, name, path, description) "
                    "VALUES (1, 'Existing', NULL, '')"
                )

        self.repository.initialize()

        self.assertEqual(self.repository.get(1), Project(id=1, name="Existing"))

    def test_saved_project_retains_its_data_when_read_from_database(self) -> None:
        self.repository.initialize()
        project = Project(
            name="Forge",
            path="/home/user/forge",
            description="Local project manager",
        )

        saved = self.repository.save(project)
        loaded = self.repository.get(saved.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(
            loaded,
            Project(
                id=saved.id,
                name="Forge",
                path="/home/user/forge",
                description="Local project manager",
            ),
        )
        self.assertIsNone(project.id)

    def test_get_returns_none_for_missing_id(self) -> None:
        self.repository.initialize()

        self.assertIsNone(self.repository.get(999))

    def test_list_returns_projects_in_id_order(self) -> None:
        self.repository.initialize()
        first = self.repository.save(Project(name="First"))
        second = self.repository.save(Project(name="Second"))

        self.assertEqual(self.repository.list(), [first, second])

    def test_archive_and_restore_control_default_listing(self) -> None:
        self.repository.initialize()
        project = self.repository.save(Project(name="Keep me"))

        self.assertTrue(self.repository.archive(project.id))
        archived = self.repository.get(project.id)
        self.assertIsNotNone(archived)
        self.assertIsNotNone(archived.archived_at)
        self.assertEqual(self.repository.list(), [])
        self.assertEqual(self.repository.list(include_archived=True), [archived])
        self.assertTrue(self.repository.archive(project.id))  # idempotent

        self.assertTrue(self.repository.restore(project.id))
        self.assertIsNone(self.repository.get(project.id).archived_at)
        self.assertEqual(self.repository.list(), [project])
        self.assertTrue(self.repository.restore(project.id))  # idempotent
        self.assertFalse(self.repository.archive(999))
        self.assertFalse(self.repository.restore(999))

    def test_update_changes_only_supplied_fields(self) -> None:
        self.repository.initialize()
        project = self.repository.save(Project(name="Before", path="/old"))

        updated = self.repository.update(project.id, {"name": "After"})

        self.assertEqual(updated, Project(id=project.id, name="After", path="/old"))


if __name__ == "__main__":
    unittest.main()
