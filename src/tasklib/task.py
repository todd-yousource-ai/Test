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
        - Type validation occurs *before* any mutation (default generation),
          ensuring non-string falsy values (e.g., ``0``) are rejected rather
          than silently overwritten.

        Failure behavior:
        - Invalid field types or values raise ``ValueError`` immediately.
        - Missing ``id`` or ``created_at`` are populated atomically via
          ``object.__setattr__`` for frozen dataclass compatibility.
        """

        if not isinstance(self.title, str):
            raise ValueError("title must be a string")
        if not self.title.strip():
            raise ValueError("title must be non-empty")

        if not isinstance(self.id, str):
            raise ValueError("id must be a string")
        if not isinstance(self.created_at, str):
            raise ValueError("created_at must be a string")

        try:
            normalized_status = (
                self.status
                if isinstance(self.status, TaskStatus)
                else TaskStatus(self.status)
            )
        except ValueError as exc:
            raise ValueError(f"invalid status: {self.status!r}") from exc

        object.__setattr__(self, "status", normalized_status)

        if not self.id:
            object.__setattr__(self, "id", _generate_id())

        if not self.created_at:
            object.__setattr__(self, "created_at", _generate_created_at())

    def to_dict(self) -> dict[str, str]:
        """Serialize the task to a plain string dictionary.

        Security assumptions:
        - Output is intended for trusted or untrusted transport as plain data.

        Failure behavior:
        - This method does not mask invalid internal state; unexpected failures
          propagate rather than returning partial or lossy output.
        """

        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Task:
        """Deserialize a task from a plain string dictionary.

        Security assumptions:
        - ``data`` is treated as untrusted input and validated strictly.
        - Only the recognized serialized keys are accepted; unknown keys are
          silently ignored to support forward compatibility (e.g., newer
          serialization formats adding optional fields).
        - All recognized values are explicitly validated as strings before use.

        Failure behavior:
        - Non-dict input or missing required keys raise ``ValueError``.
        - Non-string values for required keys raise ``ValueError``.
        - Invalid status strings raise ``ValueError`` via enum coercion.
        """

        if not isinstance(data, dict):
            raise ValueError("data must be a dict[str, str]")

        required_keys = {"id", "title", "status", "created_at"}
        missing = required_keys - set(data.keys())
        if missing:
            raise ValueError(
                f"data is missing required keys: {', '.join(sorted(missing))}"
            )

        for key in required_keys:
            value: Any = data[key]
            if not isinstance(value, str):
                raise ValueError(f"{key} must be a string")

        return cls(
            id=data["id"],
            title=data["title"],
            status=TaskStatus(data["status"]),
            created_at=data["created_at"],
        )


__all__ = ["Task", "TaskStatus"]
