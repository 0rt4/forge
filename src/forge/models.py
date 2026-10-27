"""Data models used by Forge."""

from dataclasses import dataclass


@dataclass
class Project:
    name: str
    path: str | None = None
    description: str = ""
    id: int | None = None
    archived_at: str | None = None
