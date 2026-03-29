"""tasklib core task model types.

Defines the TaskStatus enumeration and Task frozen dataclass that form
the core public data model for tasklib.

Security assumptions:
- All external input to from_dict() is treated as untrusted and validated strictly.
- Invalid status strings raise ValueError (fail closed).
- Title must be a string.
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
from typing import Any
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

    Security assumptions:
    - Serialized input is untrusted and must contain only expected string fields.
    - Invalid or missing fields are rejected explicitly.
    - This model performs no I/O and has no import-time side effects.

    Failure behavior:
    - Invalid title, id, status, or created_at values raise ValueError.
    - Invalid mapping input to from_dict() raises ValueError.
    - No validation failures are ignored or coerced silently.
    """

    title: str
    id: str = field(default="")
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default="")

    def __post_init__(self) -> None:
        """Validate fields and auto-populate generated values when absent.

        Because the dataclass is frozen, ``object.__setattr__`` is used to
        set auto-generated defaults for ``id`` and ``created_at`` when the
        caller does not supply them (i.e., they are empty strings).

        Raises:
            ValueError: If title is not a non-empty string, if id is not a
                string, if created_at is not a string, or if status is not
                a valid TaskStatus member.
        """
        if not isinstance(self.title, str):
            raise ValueError(
                f"Task title must be a string, got {type(self.title).__name__}"
            )

        if not self.title.strip():
            raise ValueError("Task title must be a non-empty string")

        if not isinstance(self.id, str):
            raise ValueError(f"Task id must be a string, got {type(self.id).__name__}")

        if not isinstance(self.created_at, str):
            raise ValueError(
                "Task created_at must be a string, "
                f"got {type(self.created_at).__name__}"
            )

        if not isinstance(self.status, TaskStatus):
            raise ValueError(
                f"Task status must be a TaskStatus member, got {self.status!r}"
            )

        if self.id == "":
            object.__setattr__(self, "id", _generate_id())

        if self.created_at == "":
            object.__setattr__(self, "created_at", _generate_created_at())

    def to_dict(self) -> dict[str, str]:
        """Serialize the task to a plain dictionary with string values.

        Returns:
            A dict with keys ``id``, ``title``, ``status``, ``created_at``,
            all with string values suitable for JSON serialization.
        """
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Reconstruct a Task from a dictionary.

        All input is treated as untrusted and validated strictly. Missing
        or invalid fields cause a ``ValueError`` to be raised -- no silent
        coercion or defaults are applied for required fields.

        Args:
            data: A mapping containing ``id``, ``title``, ``status``, and
                ``created_at`` keys with string values.

        Returns:
            A new Task instance populated from the provided data.

        Raises:
            ValueError: If any required key is missing, if any value has
                an unexpected type, or if the status string is not a valid
                TaskStatus member.
        """
        if not isinstance(data, dict):
            raise ValueError(
                f"Task.from_dict expects a dict, got {type(data).__name__}"
            )

        required_keys = {"id", "title", "status", "created_at"}
        missing = required_keys - set(data.keys())
        if missing:
            raise ValueError(
                f"Task.from_dict missing required key(s): {', '.join(sorted(missing))}"
            )

        for key in required_keys:
            if not isinstance(data[key], str):
                raise ValueError(
                    f"Task.from_dict expected string for '{key}', "
                    f"got {type(data[key]).__name__}"
                )

        try:
            status = TaskStatus(data["status"])
        except ValueError:
            raise ValueError(
                f"Invalid task status: {data['status']!r}. "
                f"Valid values: {[s.value for s in TaskStatus]}"
            )

        return cls(
            id=data["id"],
            title=data["title"],
            status=status,
            created_at=data["created_at"],
        )


__all__ = ["Task", "TaskStatus"]
