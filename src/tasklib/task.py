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

    Invalid values raise ValueError when constructing the enum.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


def _generate_id() -> str:
    """Generate a unique task identifier using uuid4 hex."""
    result = uuid4().hex
    assert result, "uuid4().hex produced empty string"
    return result


def _generate_created_at() -> str:
    """Generate an ISO-8601 UTC timestamp for task creation time."""
    result = datetime.now(timezone.utc).isoformat()
    assert result, "datetime isoformat() produced empty string"
    return result


@dataclass(frozen=True)
class Task:
    """Immutable task record with deterministic serialization.

    A task may be constructed with only a title. The id and created_at fields
    are auto-generated when omitted, and status defaults to TaskStatus.PENDING.

    The status field must be a TaskStatus enum instance.

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

        All validation failures raise ValueError with context.
        """
        # Validate title
        if not isinstance(self.title, str):
            raise ValueError(
                f"Task title must be a string, got {type(self.title).__name__}"
            )
        if not self.title.strip():
            raise ValueError("Task title must be non-empty")

        # Validate id
        if not isinstance(self.id, str):
            raise ValueError(
                f"Task id must be a string, got {type(self.id).__name__}"
            )
        if not self.id.strip():
            raise ValueError("Task id must be non-empty")

        # Validate status -- must be a TaskStatus enum member, no coercion
        if not isinstance(self.status, TaskStatus):
            raise ValueError(
                f"Task status must be a TaskStatus enum member, "
                f"got {type(self.status).__name__}: {self.status!r}. "
                f"Must be one of: {[s for s in TaskStatus]}"
            )

        # Validate created_at
        if not isinstance(self.created_at, str):
            raise ValueError(
                f"Task created_at must be a string, got {type(self.created_at).__name__}"
            )
        if not self.created_at.strip():
            raise ValueError("Task created_at must be non-empty")

    def to_dict(self) -> dict[str, str]:
        """Serialize the task to a plain dictionary with string values.

        Returns:
            A dict with keys 'id', 'title', 'status', 'created_at',
            all mapped to string values. The status field is serialized
            as its lowercase string value (e.g. 'pending').
        """
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Deserialize a Task from a plain dictionary.

        All input is treated as untrusted and validated strictly.
        Only the expected keys ('id', 'title', 'status', 'created_at') are
        accepted. Extra or missing keys raise ValueError.

        Args:
            data: A dictionary with string keys and values representing
                  a serialized Task.

        Returns:
            A new Task instance reconstructed from the dictionary.

        Raises:
            ValueError: If data is not a dict, has missing/extra keys,
                        or contains invalid values.
        """
        if not isinstance(data, dict):
            raise ValueError(
                f"Task.from_dict() requires a dict, got {type(data).__name__}"
            )

        expected_keys = {"id", "title", "status", "created_at"}
        actual_keys = set(data.keys())

        missing = expected_keys - actual_keys
        if missing:
            raise ValueError(
                f"Task.from_dict() missing required keys: {sorted(missing)}"
            )

        extra = actual_keys - expected_keys
        if extra:
            raise ValueError(
                f"Task.from_dict() received unexpected keys: {sorted(extra)}"
            )

        # Validate all values are strings before proceeding
        for key in expected_keys:
            if not isinstance(data[key], str):
                raise ValueError(
                    f"Task.from_dict() value for '{key}' must be a string, "
                    f"got {type(data[key]).__name__}"
                )

        # Convert status string to TaskStatus enum -- fails closed on invalid value
        try:
            status = TaskStatus(data["status"])
        except ValueError:
            raise ValueError(
                f"Task.from_dict() invalid status: {data['status']!r}. "
                f"Must be one of: {[s.value for s in TaskStatus]}"
            )

        return cls(
            id=data["id"],
            title=data["title"],
            status=status,
            created_at=data["created_at"],
        )

    def __eq__(self, other: object) -> bool:
        """Check equality based on all fields."""
        if not isinstance(other, Task):
            return NotImplemented
        return (
            self.id == other.id
            and self.title == other.title
            and self.status == other.status
            and self.created_at == other.created_at
        )

    def __hash__(self) -> int:
        """Hash based on all fields for use in sets and dicts."""
        return hash((self.id, self.title, self.status, self.created_at))
