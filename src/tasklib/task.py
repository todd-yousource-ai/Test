"""tasklib core task model types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict
from uuid import uuid4


class TaskStatus(str, Enum):
    """Allowed lifecycle states for a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


def _generate_id() -> str:
    return uuid4().hex


def _generate_created_at() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Task:
    """Immutable task record with deterministic serialization."""

    title: str
    id: str = field(default="")
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default="")

    def __post_init__(self) -> None:
        # Validate title
        if not isinstance(self.title, str):
            raise ValueError(
                f"Task title must be a string, got {type(self.title).__name__}"
            )

        # Validate id type before checking emptiness
        if self.id and not isinstance(self.id, str):
            raise ValueError(
                f"Task id must be a string, got {type(self.id).__name__}"
            )
        if not isinstance(self.id, str):
            raise ValueError(
                f"Task id must be a string, got {type(self.id).__name__}"
            )

        # Validate created_at type before checking emptiness
        if self.created_at and not isinstance(self.created_at, str):
            raise ValueError(
                f"Task created_at must be a string, got {type(self.created_at).__name__}"
            )
        if not isinstance(self.created_at, str):
            raise ValueError(
                f"Task created_at must be a string, got {type(self.created_at).__name__}"
            )

        # Coerce status from string if necessary
        if isinstance(self.status, str) and not isinstance(self.status, TaskStatus):
            try:
                object.__setattr__(self, "status", TaskStatus(self.status))
            except ValueError:
                raise ValueError(
                    f"Invalid task status: {self.status!r}; "
                    f"expected one of {[s.value for s in TaskStatus]}"
                )
        elif not isinstance(self.status, TaskStatus):
            raise ValueError(
                f"Task status must be a TaskStatus or valid status string, "
                f"got {type(self.status).__name__}"
            )

        # Auto-populate id if not provided
        if not self.id:
            object.__setattr__(self, "id", _generate_id())

        # Auto-populate created_at if not provided
        if not self.created_at:
            object.__setattr__(self, "created_at", _generate_created_at())

    def to_dict(self) -> Dict[str, str]:
        """Serialize task to a plain dictionary with string values."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """Reconstruct a Task from a dictionary.

        Args:
            data: Dictionary with keys ``id``, ``title``, ``status``, ``created_at``.

        Returns:
            A new ``Task`` instance.
        """
        if not isinstance(data, dict):
            raise ValueError(
                f"Task.from_dict expects a dict, got {type(data).__name__}"
            )

        required_keys = {"id", "title", "status", "created_at"}
        missing = required_keys - set(data.keys())
        if missing:
            raise ValueError(
                f"Task.from_dict missing required keys: {sorted(missing)}"
            )

        for key in required_keys:
            if not isinstance(data[key], str):
                raise ValueError(
                    f"Task.from_dict expects string for '{key}', "
                    f"got {type(data[key]).__name__}"
                )

        try:
            status = TaskStatus(data["status"])
        except ValueError:
            raise ValueError(
                f"Invalid task status: {data['status']!r}; "
                f"expected one of {[s.value for s in TaskStatus]}"
            )

        return cls(
            id=data["id"],
            title=data["title"],
            status=status,
            created_at=data["created_at"],
        )


__all__ = ["Task", "TaskStatus"]
