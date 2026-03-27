# === src/tasklib/models/task.py ===
"""Task model and TaskStatus enumeration."""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict


class TaskStatus(Enum):
    """Enumeration of valid task statuses."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


def _generate_id() -> str:
    return str(uuid.uuid4())


def _now() -> float:
    return time.time()


def _coerce_status(value: Any) -> TaskStatus:
    """Coerce a string or TaskStatus into a TaskStatus, raising ValueError on failure."""
    if isinstance(value, TaskStatus):
        return value
    if isinstance(value, str):
        try:
            return TaskStatus(value)
        except ValueError:
            raise ValueError(
                f"Invalid status {value!r}. "
                f"Must be one of {[s.value for s in TaskStatus]}."
            )
    raise ValueError(
        f"Invalid status type {type(value).__name__}. "
        f"Expected TaskStatus or str."
    )


@dataclass
class Task:
    """Represents a single task."""

    title: str
    status: TaskStatus = TaskStatus.PENDING
    description: str = ""
    id: str = field(default_factory=_generate_id)
    created_at: float = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Task title must be a non-empty string.")

        self.status = _coerce_status(self.status)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the task to a plain dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """Deserialize a task from a plain dictionary."""
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", TaskStatus.PENDING),
            id=data.get("id", _generate_id()),
            created_at=data.get("created_at", _now()),
        )


# === src/tasklib/models/__init__.py ===
"""Public model surface for tasklib.models."""

from tasklib.models.task import Task, TaskStatus

__all__ = ["Task", "TaskStatus"]
