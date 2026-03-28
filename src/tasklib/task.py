"""Core task model types for tasklib.

Defines the TaskStatus enumeration and Task dataclass that form the
foundational data model for the task management library.

Security / design assumptions:
    - Task IDs are generated via uuid4().hex -- not cryptographically
      guaranteed unique across adversarial contexts, but sufficient for
      a local in-memory task store with no trust implications.
    - No external input is accepted without validation (from_dict validates
      status values strictly via the TaskStatus enum constructor).
    - Frozen dataclass ensures immutability after construction.
    - No import-time side effects. No logging. No configuration.

Failure behavior:
    - Constructing TaskStatus with an invalid string raises ValueError.
    - from_dict raises KeyError if required keys are missing.
    - from_dict raises ValueError if the status string is not a valid member.
    - Attribute assignment on a Task instance raises FrozenInstanceError.
"""

import dataclasses
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict


class TaskStatus(str, Enum):
    """Lifecycle status of a task.

    Extends both str and Enum so that enum members compare equal to their
    plain-string values and serialize naturally in dicts / JSON.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclasses.dataclass(frozen=True)
class Task:
    """Immutable representation of a single unit of work.

    Can be constructed with only a ``title``; ``id``, ``status``, and
    ``created_at`` are auto-populated when not supplied.

    Attributes:
        id: Unique hex string identifier (auto-generated from uuid4).
        title: Human-readable task description (required).
        status: Current lifecycle state (defaults to PENDING).
        created_at: ISO-8601 UTC timestamp string (auto-generated).
    """

    title: str
    id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""

    def __post_init__(self) -> None:
        """Auto-populate id and created_at when not provided.

        Uses ``object.__setattr__`` because the dataclass is frozen and
        normal attribute assignment is disallowed after ``__init__``.
        """
        if not self.id:
            object.__setattr__(self, "id", uuid.uuid4().hex)

        if not self.created_at:
            object.__setattr__(
                self,
                "created_at",
                datetime.now(timezone.utc).isoformat(),
            )

    def to_dict(self) -> Dict[str, str]:
        """Serialize the task to a plain dictionary with string values.

        Returns:
            dict with keys ``id``, ``title``, ``status``, ``created_at``,
            all as plain strings.
        """
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Task":
        """Reconstruct a Task from a dictionary produced by ``to_dict()``.

        Args:
            data: Dictionary with keys ``id``, ``title``, ``status``,
                  ``created_at``. All values must be strings.

        Returns:
            A new Task instance with the exact field values from the dict.

        Raises:
            KeyError: If any required key is missing from *data*.
            ValueError: If the ``status`` value is not a valid TaskStatus member.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            status=TaskStatus(data["status"]),
            created_at=data["created_at"],
        )
