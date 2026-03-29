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
    from uuid import uuid4

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
        """Validate fields and auto-populate generated values when absent."""
        if not isinstance(self.title, str):
            raise ValueError(
                f"Task title must be a string, got {type(self.title).__name__}"
            )

        if not isinstance(self.id, str):
            raise ValueError(f"Task id must be a string, got {type(self.id).__name__}")

        if not isinstance(self.created_at, str):
            raise ValueError(
                "Task created_at must be a string, "
                f"got {type(self.created_at).__name__}"
            )

        if isinstance(self.status, str) and not isinstance(self.status, TaskStatus):
            try:
                object.__setattr__(self, "status", TaskStatus(self.status))
            except ValueError as exc:
                raise ValueError(f"Invalid task status: {self.status!r}") from exc
        elif not isinstance(self.status, TaskStatus):
            raise ValueError(
                "Task status must be a TaskStatus or string, "
                f"got {type(self.status).__name__}"
            )

        if self.id == "":
            object.__setattr__(self, "id", _generate_id())

        if self.created_at == "":
            object.__setattr__(self, "created_at", _generate_created_at())

    def to_dict(self) -> dict[str, str]:
        """Serialize the task to a plain string-only dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Deserialize a task from a plain dictionary.

        Security assumptions:
        - ``data`` is untrusted external input.
        - Only the exact required keys are accepted.
        - All values must be strings and status must map to a valid enum member.

        Failure behavior:
        - Raises ValueError on non-dict input, missing keys, unexpected keys,
          non-string values, or invalid status values.
        """
        if not isinstance(data, dict):
            raise ValueError(
                f"Task data must be a dict, got {type(data).__name__}"
            )

        expected_keys = {"id", "title", "status", "created_at"}
        actual_keys = set(data.keys())

        missing_keys = expected_keys - actual_keys
        if missing_keys:
            raise ValueError(
                f"Task data missing required keys: {sorted(missing_keys)}"
            )

        unexpected_keys = actual_keys - expected_keys
        if unexpected_keys:
            raise ValueError(
                f"Task data contains unexpected keys: {sorted(unexpected_keys)}"
            )

        id_value = data["id"]
        title_value = data["title"]
        status_value = data["status"]
        created_at_value = data["created_at"]

        for field_name, field_value in (
            ("id", id_value),
            ("title", title_value),
            ("status", status_value),
            ("created_at", created_at_value),
        ):
            if not isinstance(field_value, str):
                raise ValueError(
                    f"Task field {field_name!r} must be a string, "
                    f"got {type(field_value).__name__}"
                )

        try:
            status = TaskStatus(status_value)
        except ValueError as exc:
            raise ValueError(f"Invalid task status: {status_value!r}") from exc

        return cls(
            id=id_value,
            title=title_value,
            status=status,
            created_at=created_at_value,
        )
