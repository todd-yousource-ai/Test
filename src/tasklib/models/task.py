"""Task model and status enumeration for tasklib.

Defines the core Task dataclass and TaskStatus enum used throughout the
tasklib library. All imports are stdlib-only. No third-party dependencies.

Security / validation assumptions:
- All external input to Task fields is treated as untrusted and validated
  strictly in __post_init__.
- Invalid inputs fail closed with explicit TypeError or ValueError -- no
  silent coercion or fallback defaults.
- Auto-generated fields (id, created_at, updated_at) use isolated private
  helpers so they can be deterministically mocked in tests without
  monkey-patching stdlib globals.

Failure behavior:
- TypeError raised when title is not a str, description is not None/str,
  or status is not a TaskStatus instance.
- ValueError raised when title is empty or whitespace-only after stripping.
- No exceptions are swallowed; every validation error surfaces immediately
  at construction time.
"""

import dataclasses
import enum
import uuid
from datetime import datetime, timezone
from typing import Optional


class TaskStatus(enum.Enum):
    """Lifecycle status of a task.

    Exactly two members as specified by TRD-TASKLIB §3.1 FR-4/FR-7.
    """

    PENDING = "pending"
    COMPLETED = "completed"


def _generate_task_id() -> str:
    """Return a new UUID4 string for use as a task identifier.

    Isolated as a private module-level helper so tests can mock it for
    deterministic id generation without patching uuid directly.

    Returns:
        A lowercase hyphenated UUID4 string, e.g.
        ``'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d'``.
    """
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    """Return the current UTC-aware datetime.

    Isolated as a private module-level helper so tests can mock it for
    deterministic timestamp generation.

    Returns:
        A timezone-aware ``datetime`` with ``tzinfo=timezone.utc``.
    """
    return datetime.now(timezone.utc)


@dataclasses.dataclass
class Task:
    """A single unit of work in the task management library.

    Satisfies TRD-TASKLIB §3.1 functional requirements FR-1 through FR-7.

    Attributes:
        id: Auto-generated UUID4 string uniquely identifying this task.
        title: Required non-empty human-readable name for the task.
        description: Optional longer description; defaults to ``None``.
        status: Lifecycle status; defaults to ``TaskStatus.PENDING``.
        created_at: UTC-aware timestamp of when the task was created.
        updated_at: UTC-aware timestamp of last modification; initially
            equal to ``created_at`` semantics (both set at construction).

    Raises:
        TypeError: If ``title`` is not a ``str``, ``description`` is
            neither ``None`` nor a ``str``, or ``status`` is not a
            ``TaskStatus`` instance.
        ValueError: If ``title`` is empty or contains only whitespace.
    """

    title: str
    id: str = dataclasses.field(default_factory=_generate_task_id)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = dataclasses.field(default_factory=_utc_now)
    updated_at: datetime = dataclasses.field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        """Validate all fields immediately after construction.

        Fail-closed validation: every invalid input raises an explicit
        exception with a descriptive message. No silent coercion.

        Raises:
            TypeError: If ``title`` is not a ``str``.
            ValueError: If ``title`` is empty or whitespace-only.
            TypeError: If ``description`` is not ``None`` and not a ``str``.
            TypeError: If ``status`` is not a ``TaskStatus`` instance.
        """
        #