"""Data models used by Forge."""

from dataclasses import dataclass


@dataclass
class Project:
    """A developer project tracked by Forge."""

    name: str
    path: str | None = None
    description: str = ""
    id: int | None = None
