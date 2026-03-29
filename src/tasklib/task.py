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
from typing import Any
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
        - Type validation occurs before default generation to prevent silent
          coercion or overwrite of invalid values.

        Failure behavior:
        - Invalid field types or values raise ``ValueError`` immediately.
        - UUID and timestamp generation errors propagate without fallback.
        """

        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not self.title.strip():
            raise ValueError("title must be non-empty")

        # Type checks must precede emptiness checks so that non-string falsy
        # values (e.g. 0, None) are rejected rather than silently replaced with
        # a generated default.
        if not isinstance(self.id, str):
            raise ValueError("id must be a string")
        if not isinstance(self.created_at, str):
            raise ValueError("created_at must be a string")

        try:
            status = self.status if isinstance(self.status, TaskStatus) else TaskStatus(self.status)
        except (TypeError, ValueError) as exc:
            raise ValueError("status must be a valid TaskStatus") from exc

        object.__setattr__(self, "status", status)

        if self.id == "":
            object.__setattr__(self, "id", _generate_id())
        elif not self.id.strip():
            raise ValueError("id must be non-empty when provided")

        if self.created_at == "":
            object.__setattr__(self, "created_at", _generate_created_at())
        elif not self.created_at.strip():
            raise ValueError("created_at must be non-empty when provided")

    def to_dict(self) -> dict[str, str]:
        """Serialize the task to a plain string dictionary.

        Security assumptions:
        - Serialization emits only primitive string values for safe downstream use.

        Failure behavior:
        - This method performs no silent coercion beyond enum-to-string conversion.
        """

        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Task:
        """Deserialize a task from a dictionary produced by ``to_dict``.

        Security assumptions:
        - ``data`` is untrusted and validated for required keys and string values.
        - Status is reconstructed through ``TaskStatus`` to reject invalid states.

        Failure behavior:
        - Missing keys, non-dict input, non-string values, or invalid status values
          raise ``ValueError``.
        """

        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")

        required_keys = ("id", "title", "status", "created_at")
        for key in required_keys:
            if key not in data:
                raise ValueError(f"missing required key: {key}")

        validated: dict[str, str] = {}
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
