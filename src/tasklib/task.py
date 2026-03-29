"""tasklib core task model types.

Security assumptions:
- Callers provide untrusted input to ``Task`` and ``Task.from_dict``.
- This module validates required fields and enum coercion explicitly.
- Invalid input raises ``ValueError`` and no partial object mutation occurs.

Failure behavior:
- Task construction fails closed for empty or non-string titles.
- Deserialization fails closed for missing keys, non-string values, or invalid
  status values.
- This module has no import-time side effects beyond stdlib imports and symbol
  definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict
from uuid import uuid4


class TaskStatus(str, Enum):
    """Allowed lifecycle states for a task.

    Security assumptions:
    - Status values may originate from untrusted serialized input.
    - Enum construction is relied upon to reject invalid values.

    Failure behavior:
    - Constructing from an unsupported string raises ``ValueError``.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


def _generate_id() -> str:
    """Generate a UUID4 hex identifier.

    Security assumptions:
    - Identifier generation uses stdlib UUID4 randomness.

    Failure behavior:
    - Any unexpected stdlib failure propagates; no fallback identifiers are used.
    """

    return uuid4().hex


def _generate_created_at() -> str:
    """Generate a UTC ISO-8601 timestamp string.

    Security assumptions:
    - Timestamps are generated in UTC to avoid local timezone ambiguity.

    Failure behavior:
    - Any unexpected datetime failure propagates; no fallback timestamps are used.
    """

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Task:
    """Immutable task record with deterministic serialization.

    Security assumptions:
    - ``title`` is required user input and is validated as a non-empty string.
    - ``id`` and ``created_at`` may be omitted and will be generated safely.
    - ``status`` may be provided as ``TaskStatus`` or a valid status string.

    Failure behavior:
    - Empty or non-string titles raise ``ValueError``.
    - Invalid status values raise ``ValueError``.
    - Frozen dataclass semantics prevent mutation after construction.
    """

    title: str
    id: str = field(default="")
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default="")

    def __post_init__(self) -> None:
        """Validate fields and populate generated values.

        Security assumptions:
        - All constructor input is treated as untrusted and validated explicitly.

        Failure behavior:
        - Invalid field types or values raise ``ValueError`` immediately.
        - Missing ``id`` or ``created_at`` are populated atomically via
          ``object.__setattr__`` for frozen dataclass compatibility.
        """

        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not self.title.strip():
            raise ValueError("title must be a non-empty string")

        if isinstance(self.status, str) and not isinstance(self.status, TaskStatus):
            object.__setattr__(self, "status", TaskStatus(self.status))
        elif not isinstance(self.status, TaskStatus):
            raise ValueError("status must be a TaskStatus or valid status string")

        if not isinstance(self.id, str):
            raise ValueError("id must be a string")
        if not self.id:
            object.__setattr__(self, "id", _generate_id())

        if not isinstance(self.created_at, str):
            raise ValueError("created_at must be a string")
        if not self.created_at:
            object.__setattr__(self, "created_at", _generate_created_at())

    def to_dict(self) -> Dict[str, str]:
        """Serialize the task to a plain string dictionary.

        Security assumptions:
        - Output contains only plain strings to support safe JSON/dict round trips.

        Failure behavior:
        - Returns a complete dictionary representation without mutating the object.
        """

        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Task:
        """Deserialize a task from a plain string dictionary.

        Security assumptions:
        - ``data`` is untrusted input and is validated strictly.
        - Only the required keys are accepted for reconstruction.

        Failure behavior:
        - Non-dict input raises ``ValueError``.
        - Missing required keys, non-string values, or invalid status values
          raise ``ValueError``.
        """

        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        required_keys = ("id", "title", "status", "created_at")
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"missing required keys: {', '.join(missing_keys)}")

        validated: Dict[str, str] = {}
        for key in required_keys:
            value: Any = data[key]
            if not isinstance(value, str):
                raise ValueError(f"{key} must be a string")
            validated[key] = value

        return cls(
            id=validated["id"],
            title=validated["title"],
            status=TaskStatus(validated["status"]),
            created_at=validated["created_at"],
        )


__all__ = ["Task", "TaskStatus"]
