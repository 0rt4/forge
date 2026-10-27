"""Application rules for managing projects."""

from .models import Project
from .repository import ProjectRepository


class ValidationError(ValueError):
    """Raised when project data violates a business rule."""


class ProjectService:
    """Apply project rules and coordinate persistence operations."""

    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def initialize(self) -> None:
        self.repository.initialize()

    def add(self, project: Project) -> Project:
        return self.repository.save(
            Project(
                name=self._validated_name(project.name),
                path=project.path,
                description=project.description,
            )
        )

    def get(self, project_id: int) -> Project | None:
        return self.repository.get(project_id)

    def list(self, include_archived: bool = False) -> list[Project]:
        return self.repository.list(include_archived=include_archived)

    def edit(self, project_id: int, changes: dict[str, str | None]) -> Project | None:
        validated_changes = dict(changes)
        if "name" in validated_changes:
            validated_changes["name"] = self._validated_name(validated_changes["name"] or "")
        return self.repository.update(project_id, validated_changes)

    def archive(self, project_id: int) -> bool:
        return self.repository.archive(project_id)

    def restore(self, project_id: int) -> bool:
        return self.repository.restore(project_id)

    @staticmethod
    def _validated_name(name: str) -> str:
        normalized = name.strip()
        if not normalized:
            raise ValidationError("Project name cannot be empty or whitespace only.")
        return normalized
