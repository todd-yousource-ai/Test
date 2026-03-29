"""Foundational data model for tasklib: status enumeration and task record.

Provides ``TaskStatus``, a tri-state lifecycle enum, and ``Task``, a frozen
dataclass that enforces non-empty titles and valid status values at
construction time.  Both types are designed for use as pure value objects
with no I/O, no logging, and no import-time side effects.

Security / design assumptions
─────────────────────────────
- Task IDs default to ``str(uuid4())`` -- canonical UUID string form,
  sufficient for a local in-memory store with no adversarial trust
  requirements.
- The frozen dataclass prevents mutation after construction; any attempt
  to reassign an attribute raises ``FrozenInstanceError``.
- ``from_dict`` treats its input as untrusted: missing keys surface as
  ``KeyError``; invalid status strings surface as ``ValueError``.

Failure behavior
────────────────
- ``Task(title="")`` or ``Task(title="   ")`` → ``ValueError``.
- ``Task(title=42)`` → ``ValueError`` (must be a real ``str``).
- ``Task(status="bogus")`` → ``ValueError`` (must be a ``TaskStatus``).
- ``TaskStatus("nope")`` → ``ValueError``.
- ``Task.from_dict({})`` → ``KeyError`` for the first missing key.
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timezone
from enum import Enum


class TaskStatus(str, Enum):
    """Lifecycle status of a task.

    Extends both ``str`` and ``Enum`` so that members compare equal to their
    plain-string values and serialize naturally in dicts / JSON.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclasses.dataclass(frozen=True)
class Task:
    """Immutable representation of a single unit of work.

    Only ``title`` is required at construction time; ``id``, ``status``,
    and ``created_at`` carry sensible defaults.

    Validation (enforced in ``__post_init__``):
        - ``title`` must be a ``str`` that contains at least one
          non-whitespace character.
        - ``status`` must be a ``TaskStatus`` instance or a string that
          can be converted to one.

    Failure behavior:
        - ``ValueError`` when either constraint is violated.
    """

    title: str
    id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""

    # -----------------------------------------------------------------
    # Construction helpers
    # -----------------------------------------------------------------

    def __post_init__(self) -> None:
        """Validate inputs and auto-populate generated fields.

        Uses ``object.__setattr__`` because the dataclass is frozen and
        normal attribute assignment is disallowed after ``__init__``.
        """
        # --- title validation ---
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError(
                "title must be a non-empty string (got {!r})".format(self.title)
            )

        # --- status coercion & validation ---
        if not isinstance(self.status, TaskStatus):
            # Attempt to coerce a string (or other value) into a TaskStatus.
            # Invalid values will raise ValueError from TaskStatus().
            try:
                object.__setattr__(self, "status", TaskStatus(self.status))
            except (ValueError, KeyError):
                raise ValueError(
                    "status must be a TaskStatus member (got {!r})".format(self.status)
                )

        # --- auto-populated defaults ---
        if not self.id:
            object.__setattr__(self, "id", str(uuid.uuid4()))

        if not self.created_at:
            object.__setattr__(
                self,
                "created_at",
                datetime.now(timezone.utc).isoformat(),
            )

    # -----------------------------------------------------------------
    # Serialization
    # -----------------------------------------------------------------

    def to_dict(self) -> dict[str, str]:
        """Serialize the task to a plain dictionary of string values.

        Returns:
            Dictionary with keys ``id``, ``title``, ``status``, and
            ``created_at``.
        """
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Task:
        """Reconstruct a ``Task`` from a dictionary (e.g. one produced by
        ``to_dict``).

        The input is treated as untrusted:

        - Missing required keys raise ``KeyError``.
        - An unrecognised ``status`` string raises ``ValueError`` during
          ``TaskStatus`` construction.

        Args:
            data: Flat string-valued dictionary with at least the keys
                ``id``, ``title``, ``status``, and ``created_at``.

        Returns:
            A fully validated ``Task`` instance.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            status=TaskStatus(data["status"]),
            created_at=data["created_at"],
        )
