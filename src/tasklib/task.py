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
    return uuid4().hex


def _generate_created_at() -> str:
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
    id: str = field(default_factory=_generate_id)
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=_generate_created_at)

    def __post_init__(self) -> None:
        # --- title: must be a non-empty string ---
        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not self.title.strip():
            raise ValueError("title must be a non-empty string")

        # --- status: coerce valid strings; reject everything else ---
        if isinstance(self.status, str) and not isinstance(self.status, TaskStatus):
            object.__setattr__(self, "status", TaskStatus(self.status))
        elif not isinstance(self.status, TaskStatus):
            raise ValueError("status must be a TaskStatus or valid status string")

        # --- id: validate type eagerly ---
        if not isinstance(self.id, str):
            raise ValueError("id must be a string")
        if not self.id:
            object.__setattr__(self, "id", _generate_id())

        # --- created_at: validate type eagerly ---
        if not isinstance(self.created_at, str):
            raise ValueError("created_at must be a string")
        if not self.created_at:
            object.__setattr__(self, "created_at", _generate_created_at())

    def to_dict(self) -> dict[str, str]:
        """Serialize the task to plain string fields.

        Failure behavior:
        - Returns a complete dictionary representation with no omitted fields.
        """

        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Task:
        """Deserialize a task from a plain dictionary.

        Security assumptions:
        - ``data`` is untrusted external input and is validated strictly.

        Failure behavior:
        - Missing required keys, non-dict inputs, non-string values, or invalid
          status values raise ``ValueError``.
        """

        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        required_keys = ("id", "title", "status", "created_at")
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"missing required keys: {', '.join(missing_keys)}")

        values: dict[str, str] = {}
        for key in required_keys:
            value = data[key]
            if not isinstance(value, str):
                raise ValueError(f"{key} must be a string")
            values[key] = value

        try:
            status = TaskStatus(values["status"])
        except ValueError:
            raise ValueError(
                f"invalid status: {values['status']!r}"
            ) from None

        return cls(
            id=values["id"],
            title=values["title"],
            status=status,
            created_at=values["created_at"],
        )


__all__ = ["Task", "TaskStatus"]
