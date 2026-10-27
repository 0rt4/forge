"""Tests for project business rules."""

import tempfile
import unittest
from pathlib import Path

from forge.models import Project
from forge.repository import ProjectRepository
from forge.services import ProjectService, ValidationError


class ProjectServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.service = ProjectService(ProjectRepository(Path(self.temp_dir.name) / "forge.db"))
        self.service.initialize()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_trims_name_and_preserves_other_fields(self) -> None:
        project = self.service.add(
            Project(name="  Forge  ", path="/work/forge", description="Manager")
        )

        self.assertEqual(project.name, "Forge")
        self.assertEqual(project.path, "/work/forge")
        self.assertEqual(project.description, "Manager")

    def test_add_rejects_empty_or_whitespace_name(self) -> None:
        for name in ("", "   ", "\t\n"):
            with self.subTest(name=repr(name)):
                with self.assertRaises(ValidationError):
                    self.service.add(Project(name=name))

        self.assertEqual(self.service.list(), [])

    def test_edit_rejects_empty_name_without_changing_project(self) -> None:
        project = self.service.add(Project(name="Forge"))

        with self.assertRaises(ValidationError):
            self.service.edit(project.id, {"name": "   "})

        self.assertEqual(self.service.get(project.id).name, "Forge")


if __name__ == "__main__":
    unittest.main()
