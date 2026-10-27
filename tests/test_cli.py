"""Tests for Forge's command-line interface."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from forge.cli import main


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "nested" / "forge.db"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def invoke(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = main(["--db", str(self.database_path), *args])
        return status, stdout.getvalue(), stderr.getvalue()

    def test_init_creates_database_and_can_be_repeated(self) -> None:
        status, output, error = self.invoke("init")
        self.assertEqual(status, 0)
        self.assertIn("Initialized database", output)
        self.assertEqual(error, "")
        self.assertTrue(self.database_path.exists())

        status, _, _ = self.invoke("init")
        self.assertEqual(status, 0)

    def test_add_list_and_show_project(self) -> None:
        status, added, _ = self.invoke(
            "add", "Forge", "--path", "/work/forge", "--description", "Project tracker"
        )
        self.assertEqual(status, 0)
        self.assertIn("Added project 1: Forge", added)

        status, listing, _ = self.invoke("list")
        self.assertEqual(status, 0)
        self.assertIn("1\tForge\t/work/forge", listing)

        status, details, _ = self.invoke("show", "1")
        self.assertEqual(status, 0)
        self.assertIn("Description: Project tracker", details)
        self.assertIn("Path: /work/forge", details)

    def test_list_empty_database(self) -> None:
        status, output, _ = self.invoke("list")

        self.assertEqual(status, 0)
        self.assertEqual(output.strip(), "No projects found.")

    def test_show_missing_project_returns_error(self) -> None:
        status, output, error = self.invoke("show", "99")

        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn("Project 99 not found", error)

    def test_edit_archive_list_all_and_restore(self) -> None:
        self.invoke("add", "Forge", "--path", "/old")

        status, output, _ = self.invoke("edit", "1", "--name", "Forge Updated")
        self.assertEqual(status, 0)
        self.assertIn("Updated project 1: Forge Updated", output)

        status, output, _ = self.invoke("archive", "1")
        self.assertEqual(status, 0)
        self.assertIn("Archived project 1", output)
        self.assertEqual(self.invoke("list")[1].strip(), "No projects found.")
        self.assertIn("1\tForge Updated\t/old\tarchived", self.invoke("list", "--all")[1])

        status, details, _ = self.invoke("show", "1")
        self.assertEqual(status, 0)
        self.assertIn("Archived: yes", details)

        status, output, _ = self.invoke("restore", "1")
        self.assertEqual(status, 0)
        self.assertIn("Restored project 1", output)
        self.assertIn("1\tForge Updated\t/old", self.invoke("list")[1])

    def test_edit_requires_a_field(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.invoke("edit", "1")

        self.assertEqual(raised.exception.code, 2)

    def test_edit_missing_project_returns_error(self) -> None:
        status, output, error = self.invoke("edit", "99", "--name", "Missing")

        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn("Project 99 not found", error)

    def test_add_and_edit_reject_blank_names(self) -> None:
        status, output, error = self.invoke("add", "   ")
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("Project name cannot be empty", error)

        self.invoke("add", "Forge")
        status, output, error = self.invoke("edit", "1", "--name", "  ")
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("Project name cannot be empty", error)

        self.assertIn("Name: Forge", self.invoke("show", "1")[1])


if __name__ == "__main__":
    unittest.main()
