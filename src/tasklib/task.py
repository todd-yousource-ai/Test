"""tasklib core task model types.

Defines the TaskStatus enumeration and Task frozen dataclass that form
the core public data model for tasklib.

Security assumptions:
- All external input to from_dict() is treated as untrusted and validated strictly.
- Invalid status strings raise ValueError (fail closed).
- Title must be a string; non-string titles are rejected.
- No secrets or credentials are handled by this module.

Failure behavior:
- Construction with invalid types or values raises ValueError with context.
- Attribute assignment on frozen Task raises FrozenInstanceError.
- No silent failure paths -- every validation check surfaces an explicit error.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict
from uuid import uuid4


class TaskStatus(str, Enum):
    """Allowed lifecycle states for a task.

    Extends both str and Enum so that enum members compare equal to their
    string values and serialize naturally in dicts/JSON.

    Constructing with an invalid string raises ValueError.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


def _generate_id() -> str:
    """Generate a unique task identifier using uuid4 hex."""
    return uuid4().hex


def _generate_created_at() -> str:
    """Generate an ISO-8601 UTC timestamp for task creation time."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Task:
    """Immutable task record with deterministic serialization.

    Can be constructed with only a ``title``; ``id``, ``status``, and
    ``created_at`` are auto-populated when not explicitly provided.

    Uses ``object.__setattr__`` in ``__post_init__`` to set auto-generated
    fields on the frozen instance.

    Raises:
        ValueError: If title is non-string, status is invalid,
            or field types are incorrect.
    """

    title: str
    id: str = field(default="")
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default="")

    def __post_init__(self) -> None:
        """Validate all fields and auto-populate id/created_at if missing.

        Validation order:
        1. title -- must be a string
        2. id -- must be a string (may be empty for auto-generation)
        3. created_at -- must be a string (may be empty for auto-generation)
        4. status -- coerce from string if needed, reject invalid values
        5. Auto-populate id if empty
        6. Auto-populate created_at if empty
        """
        # Validate title is a string
        if not isinstance(self.title, str):
            raise ValueError(
                f"Task title must be a string, got {type(self.title).__name__}"
            )

        # Validate id type
        if not isinstance(self.id, str):
            raise ValueError(
                f"Task id must be a string, got {type(self.id).__name__}"
            )

        # Validate created_at type
        if not isinstance(self.created_at, str):
            raise ValueError(
                f"Task created_at must be a string, got {type(self.created_at).__name__}"
            )

        # Coerce status from string if necessary, reject invalid values
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
        """Serialize task to a plain dictionary with string values.

        Returns:
            Dict with keys: id, title, status, created_at -- all string values.
        """
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """Deserialize a Task from a plain dictionary.

        All input is treated as untrusted and validated through the
        normal __post_init__ validation path.

        Args:
            data: Dictionary with keys id, title, status, created_at.

        Returns:
            A new Task instance.

        Raises:
            KeyError: If required key 'title' is missing.
            ValueError: If any field value is invalid.
        """
        if not isinstance(data, dict):
            raise ValueError(
                f"Task.from_dict expects a dict, got {type(data).__name__}"
            )
        if "title" not in data:
            raise KeyError("Task.from_dict requires 'title' key in data")

        return cls(
            title=data["title"],
            id=data.get("id", ""),
            status=data.get("status", TaskStatus.PENDING),
            created_at=data.get("created_at", ""),
        )
