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


if __name__ == "__main__":
    unittest.main()
