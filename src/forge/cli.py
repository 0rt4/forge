"""Command-line interface for Forge."""

import argparse
import os
import sqlite3
import sys
from pathlib import Path
from typing import Sequence

from .models import Project
from .repository import ProjectRepository
from .services import ProjectService, ValidationError


def _default_database_path() -> Path:
    data_home = os.environ.get("XDG_DATA_HOME")
    base = Path(data_home).expanduser() if data_home else Path.home() / ".local" / "share"
    return base / "forge" / "forge.db"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forge", description="Manage local developer projects")
    parser.add_argument(
        "--db",
        type=Path,
        default=_default_database_path(),
        help="SQLite database path (default: %(default)s)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("init", help="initialize the project database")

    add_parser = commands.add_parser("add", help="add a project")
    add_parser.add_argument("name", help="project name")
    add_parser.add_argument("--path", help="project directory")
    add_parser.add_argument("--description", default="", help="project description")

    list_parser = commands.add_parser("list", help="list projects")
    list_parser.add_argument("--all", action="store_true", help="include archived projects")

    show_parser = commands.add_parser("show", help="show a project")
    show_parser.add_argument("id", type=int, help="project ID")

    edit_parser = commands.add_parser("edit", help="edit a project")
    edit_parser.add_argument("id", type=int, help="project ID")
    edit_parser.add_argument("--name", help="new project name", default=argparse.SUPPRESS)
    edit_parser.add_argument("--path", help="new project directory", default=argparse.SUPPRESS)
    edit_parser.add_argument(
        "--description", help="new project description", default=argparse.SUPPRESS
    )

    archive_parser = commands.add_parser("archive", help="archive a project")
    archive_parser.add_argument("id", type=int, help="project ID")

    restore_parser = commands.add_parser("restore", help="restore an archived project")
    restore_parser.add_argument("id", type=int, help="project ID")
    return parser


def _format_project(project: Project) -> str:
    return (
        f"ID: {project.id}\n"
        f"Name: {project.name}\n"
        f"Path: {project.path or '-'}\n"
        f"Description: {project.description or '-'}\n"
        f"Archived: {'yes' if project.archived_at else 'no'}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    database_path: Path = args.db.expanduser()

    try:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        service = ProjectService(ProjectRepository(database_path))
        service.initialize()

        if args.command == "init":
            print(f"Initialized database at {database_path}")
        elif args.command == "add":
            project = service.add(
                Project(name=args.name, path=args.path, description=args.description)
            )
            print(f"Added project {project.id}: {project.name}")
        elif args.command == "list":
            projects = service.list(include_archived=args.all)
            if not projects:
                print("No projects found.")
            else:
                for project in projects:
                    status = "\tarchived" if project.archived_at else ""
                    print(f"{project.id}\t{project.name}\t{project.path or '-'}{status}")
        elif args.command == "show":
            project = service.get(args.id)
            if project is None:
                print(f"Project {args.id} not found.", file=sys.stderr)
                return 1
            print(_format_project(project))
        elif args.command == "edit":
            changes = {
                field: getattr(args, field)
                for field in ("name", "path", "description")
                if hasattr(args, field)
            }
            if not changes:
                parser.error("edit requires at least one of --name, --path, or --description")
            project = service.edit(args.id, changes)
            if project is None:
                print(f"Project {args.id} not found.", file=sys.stderr)
                return 1
            print(f"Updated project {project.id}: {project.name}")
        elif args.command == "archive":
            if not service.archive(args.id):
                print(f"Project {args.id} not found.", file=sys.stderr)
                return 1
            print(f"Archived project {args.id}.")
        elif args.command == "restore":
            if not service.restore(args.id):
                print(f"Project {args.id} not found.", file=sys.stderr)
                return 1
            print(f"Restored project {args.id}.")
        return 0
    except ValidationError as error:
        print(f"forge: {error}", file=sys.stderr)
        return 2
    except (OSError, sqlite3.Error) as error:
        print(f"forge: {error}", file=sys.stderr)
        return 1
