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

    The status field accepts both TaskStatus enum instances and raw status
    strings (e.g. ``"pending"``), which are converted to the corresponding
    enum member during validation.

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
        """Validate fields and populate generated defaults when absent.

        Raw status strings are accepted and converted to TaskStatus members.
        Auto-generated id and created_at values are verified non-empty after
        generation.
        """
        if not isinstance(self.title, str):
            raise ValueError("Task title must be a string")
        if not self.title.strip():
            raise ValueError("Task title must be non-empty")

        if not isinstance(self.id, str):
            raise ValueError("Task id must be a string")
        if not isinstance(self.created_at, str):
            raise ValueError("Task created_at must be a string")

        # Accept raw status strings so callers need not import TaskStatus.
        if not isinstance(self.status, TaskStatus):
            if isinstance(self.status, str):
                try:
                    object.__setattr__(self, "status", TaskStatus(self.status))
                except ValueError as exc:
                    raise ValueError(f"Invalid task status: {self.status!r}") from exc
            else:
                raise ValueError("Task status must be a TaskStatus or valid status string")

        # Final guard: ensure both fields are populated.
        if not self.id:
            raise ValueError("Task id must be non-empty")
        if not self.created_at:
            raise ValueError("Task created_at must be non-empty")

    def to_dict(self) -> dict[str, str]:
        """Serialize the task to a plain dictionary of strings."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Task:
        """Deserialize a task from a plain dictionary of strings.

        The input is treated as untrusted. Required keys must be present, all
        values must be strings, and unknown/extra keys are rejected to prevent
        unexpected data from passing silently.
        """
        if not isinstance(data, dict):
            raise ValueError("Task data must be a dictionary")

        expected_keys = {"id", "title", "status", "created_at"}
        actual_keys = set(data.keys())

        unknown_keys = actual_keys - expected_keys
        if unknown_keys:
            raise ValueError(
                f"Task data contains unknown keys: {sorted(unknown_keys)}"
            )

        missing_keys = expected_keys - actual_keys
        if missing_keys:
            raise ValueError(
                f"Task data missing required keys: {sorted(missing_keys)}"
            )

        for key in expected_keys:
            value: Any = data[key]
            if not isinstance(value, str):
                raise ValueError(f"Task field {key!r} must be a string")

        try:
            status = TaskStatus(data["status"])
        except ValueError as exc:
            raise ValueError(f"Invalid task status: {data['status']!r}") from exc

        return cls(
            id=data["id"],
            title=data["title"],
            status=status,
            created_at=data["created_at"],
        )
