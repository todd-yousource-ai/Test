"""tasklib core task model types.

Defines the TaskStatus enumeration and Task frozen dataclass that form
the core public data model for tasklib.

Security assumptions:
- All external input to from_dict() is treated as untrusted and validated strictly.
- Invalid status strings raise ValueError and are never coerced.
- Required fields must be present and typed correctly.
- Unknown/extra keys in from_dict() are rejected explicitly.
- No secrets or credentials are handled by this module.

Failure behavior:
- Construction with invalid types or values raises ValueError with context.
- Attribute assignment on frozen Task raises FrozenInstanceError.
- No silent failure paths; every validation check surfaces an explicit error.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class TaskStatus(str, Enum):
    """Allowed lifecycle states for a task.

    Extends both str and Enum so enum members serialize as plain strings.
    TaskStatus.PENDING == 'pending' evaluates to True.

    Invalid values raise ValueError when constructing the enum.
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

    A task may be constructed with only a title. The id and created_at fields
    are auto-generated when omitted, and status defaults to TaskStatus.PENDING.

    The status field accepts either a TaskStatus enum instance or a plain string
    matching one of the valid status values (e.g. ``'pending'``). String values
    are coerced to the corresponding TaskStatus member during construction.

    Security assumptions:
    - Serialized input is untrusted and validated strictly.
    - Only the expected keys are accepted by from_dict().
    - Invalid field values fail closed with explicit ValueError exceptions.

    Failure behavior:
    - Invalid title, id, status, or created_at values raise ValueError.
    - Invalid input to from_dict() raises ValueError with context.
    - No validation errors are ignored or coerced silently.
    """

    title: str
    id: str = field(default_factory=_generate_id)
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=_generate_created_at)

    def __post_init__(self) -> None:
        """Validate fields after construction.

        All validation failures raise ValueError with descriptive context.
        Uses object.__setattr__ on frozen dataclass to coerce status strings
        to TaskStatus enum members when a plain string is provided.

        Validation order: title, id, status (with coercion), created_at.
        """
        # Validate title: must be a non-empty string
        if not isinstance(self.title, str):
            raise ValueError(
                f"Task title must be a string, got {type(self.title).__name__}"
            )
        if not self.title.strip():
            raise ValueError("Task title must be non-empty")

        # Validate id: must be a non-empty string
        if not isinstance(self.id, str):
            raise ValueError(
                f"Task id must be a string, got {type(self.id).__name__}"
            )
        if not self.id.strip():
            raise ValueError("Task id must be non-empty")

        # Validate and coerce status: accept TaskStatus or valid string
        if isinstance(self.status, str) and not isinstance(self.status, TaskStatus):
            try:
                coerced = TaskStatus(self.status)
            except ValueError:
                raise ValueError(
                    f"Invalid task status: {self.status!r}. "
                    f"Must be one of: {[s.value for s in TaskStatus]}"
                )
            object.__setattr__(self, "status", coerced)
        elif not isinstance(self.status, TaskStatus):
            raise ValueError(
                f"Task status must be a TaskStatus enum or valid string, "
                f"got {type(self.status).__name__}"
            )

        # Validate created_at: must be a non-empty string
        if not isinstance(self.created_at, str):
            raise ValueError(
                f"Task created_at must be a string, got {type(self.created_at).__name__}"
            )
        if not self.created_at.strip():
            raise ValueError("Task created_at must be non-empty")

    def to_dict(self) -> dict[str, str]:
        """Serialize task to a plain dictionary with string values.

        Returns:
            dict[str, str]: Dictionary with keys 'id', 'title', 'status',
                'created_at'. The status value is the plain string value of the
                enum member.
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

        All input is treated as untrusted and validated strictly. Unknown keys
        are rejected. Required keys must be present. Values are validated by
        the dataclass __post_init__ method.

        Args:
            data: Dictionary with keys 'id', 'title', 'status', 'created_at'.

        Returns:
            Task: A new immutable Task instance.

        Raises:
            ValueError: If data is not a dict, contains unknown keys, or is
                missing required keys.
            ValueError: If any field value is invalid (propagated from __post_init__).
        """
        if not isinstance(data, dict):
            raise ValueError(
                f"Task.from_dict() requires a dict, got {type(data).__name__}"
            )

        expected_keys = {"id", "title", "status", "created_at"}
        actual_keys = set(data.keys())

        unknown_keys = actual_keys - expected_keys
        if unknown_keys:
            raise ValueError(
                f"Task.from_dict() received unknown keys: {sorted(unknown_keys)}"
            )

        missing_keys = expected_keys - actual_keys
        if missing_keys:
            raise ValueError(
                f"Task.from_dict() missing required keys: {sorted(missing_keys)}"
            )

        return cls(
            title=data["title"],
            id=data["id"],
            status=data["status"],
            created_at=data["created_at"],
        )
