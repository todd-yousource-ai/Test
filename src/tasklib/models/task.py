"""Task dataclass and TaskStatus enumeration for tasklib.

This module defines the foundational data structures for the tasklib library:

- ``TaskStatus``: An enumeration of valid lifecycle states for a task.
- ``Task``: A dataclass representing a single unit of work.

Security / validation assumptions:
    - ``title`` is validated in ``__post_init__`` to be non-empty after stripping
      whitespace. Construction with empty or whitespace-only titles raises
      ``ValueError`` (fail closed -- no silent creation of invalid tasks).
    - ``status`` is validated in ``__post_init__`` to be a ``TaskStatus`` instance.
      Passing a raw string (e.g. ``"TODO"``) raises ``TypeError`` (fail closed --
      prevents type confusion and invalid enum bypass).
    - ``id`` is auto-generated as a UUID4 string. Callers may override it, but
      uniqueness is not enforced at the model layer (that is the store's
      responsibility).
    - ``created_at`` and ``updated_at`` default to ``datetime.datetime.now()``
      (UTC-naive). Timezone policy is deferred to higher layers.

Failure behavior:
    - All validation errors raise immediately during ``__init__`` (via
      ``__post_init__``). There are no deferred or silent failure paths.

Dependencies: stdlib only (``uuid``, ``datetime``, ``dataclasses``, ``enum``).
"""

from __future__ import annotations

import dataclasses
import datetime
import enum
import uuid


class TaskStatus(enum.Enum):
    """Lifecycle status of a task.

    Members have string values matching their names for clean serialization
    to and from plain dictionaries / JSON.
    """

    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


@dataclasses.dataclass
class Task:
    """A single unit of work in the tasklib system.

    Only ``title`` is required at construction time. All other fields carry
    sensible defaults and are populated automatically.

    Raises:
        ValueError: If ``title`` is empty or contains only whitespace.
        TypeError: If ``status`` is not a ``TaskStatus`` instance.
    """

    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.now,
    )
    updated_at: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.now,
    )

    def __post_init__(self) -> None:
        """Validate invariants immediately after construction.

        Fail closed:
            - Empty / whitespace-only titles are rejected with ``ValueError``.
            - Non-``TaskStatus`` status values are rejected with ``TypeError``.
        """
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError(
                "Task title must be a non-empty string (got "
                f"{self.title!r})."
            )

        if not isinstance(self.status, TaskStatus):
            raise TypeError(
                "Task status must be a TaskStatus instance, got "
                f"{type(self.status).__name__}: {self.status!r}."
            )
