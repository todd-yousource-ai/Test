"""Task dataclass, TaskStatus enumeration, and in-memory storage for tasklib.

Defines the core domain model and a thread-safe in-memory storage backend.
A Task is an immutable-id, mutable-status value object with automatic UUID
generation and UTC timestamp tracking. InMemoryTaskStore provides CRUD-style
operations over a collection of tasks.

Security assumptions:
    - Task IDs are generated via uuid4 and are not caller-controllable.
    - All fields are type-checked at construction where feasible.
    - No external input is trusted without validation.
    - Mutation methods only operate on explicit task identifiers.

Failure behavior:
    - Construction with invalid types raises immediately.
    - No silent coercion or default-swallowing occurs.
    - Storage lookups, completion, and deletion for missing IDs raise KeyError.
    - All state mutations are protected by a lock for thread safety.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Enumeration of valid task lifecycle states.

    PENDING -- task has been created but not yet completed.
    COMPLETED -- task has been marked as done.
    """

    PENDING = "pending"
    COMPLETED = "completed"


def _parse_datetime(value: Any, field_name: str) -> datetime:
    """Coerce *value* to a timezone-aware ``datetime``.

    Accepts ``datetime`` instances and ISO-8601 strings (as produced by
    ``datetime.isoformat()``).  The returned value is **always**
    timezone-aware; naive datetimes and strings that parse to naive
    datetimes are rejected outright so that all timestamps in the domain
    model carry an unambiguous instant in time.

    Args:
        value: A ``datetime`` object or an ISO-8601 formatted string.
        field_name: Human-readable field name used in error messages.

    Returns:
        A timezone-aware ``datetime``.

    Raises:
        TypeError: If *value* is neither a ``datetime`` nor a ``str``.
        ValueError: If a string cannot be parsed as ISO-8601 or if the
            resulting ``datetime`` is naive (has no ``tzinfo``).
    """
    if isinstance(value, datetime):
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError(
                f"{field_name} must be timezone-aware, got naive datetime: {value!r}"
            )
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"{field_name} string is not valid ISO-8601: {value!r}"
            ) from exc
        if parsed.tzinfo is None or parsed.tzinfo.utcoffset(parsed) is None:
            raise ValueError(
                f"{field_name} must be timezone-aware, got naive datetime "
                f"from string: {value!r}"
            )
        return parsed
    raise TypeError(
        f"{field_name} must be a datetime or ISO-8601 string, "
        f"got {type(value).__name__}"
    )


@dataclass
class Task:
    """A single task with an auto-generated ID and creation timestamp.

    Only *title* is required at construction time. The *id*, *status*,
    *created_at*, and *updated_at* fields are populated automatically.

    Security assumptions:
        - Title is caller-provided and validated strictly.
        - Identifier and timestamps must be explicit, valid Python objects.

    Failure behavior:
        - Invalid field types raise TypeError immediately.
        - Invalid field values raise ValueError immediately.
        - Invalid status values are rejected rather than coerced.
    """

    title: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default=None)

    def __post_init__(self) -> None:
        """Validate and normalise all fields immediately after construction.

        Every field is checked for correct type and, where applicable,
        correct value.  This method runs automatically after
        ``__init__`` and ensures no ``Task`` instance can exist with
        invalid or inconsistent state.

        Raises:
            TypeError: If *title* is not a ``str``, *id* is not a ``str``,
                *status* is not a ``TaskStatus``, or timestamp fields are
                not ``datetime``/ISO-8601 strings.
            ValueError: If *title* is empty or blank, *id* is empty or
                blank, timestamp strings are malformed, or timestamps
                are naive (missing timezone information).
        """
        # -- title --
        if not isinstance(self.title, str):
            raise TypeError(
                f"title must be a str, got {type(self.title).__name__}"
            )
        if not self.title.strip():
            raise ValueError("title must not be empty or blank")

        # -- id --
        if not isinstance(self.id, str):
            raise TypeError(f"id must be a str, got {type(self.id).__name__}")
        if not self.id.strip():
            raise ValueError("id must not be empty or blank")

        # -- status --
        if isinstance(self.status, str):
            try:
                self.status = TaskStatus(self.status)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid status string: {self.status!r}"
                ) from exc
        if not isinstance(self.status, TaskStatus):
            raise TypeError(
                f"status must be a TaskStatus, got {type(self.status).__name__}"
            )

        # -- created_at --
        self.created_at = _parse_datetime(self.created_at, "created_at")

        # -- updated_at --
        if self.updated_at is not None:
            self.updated_at = _parse_datetime(self.updated_at, "updated_at")

    # ---- serialisation helpers ----

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain-dict representation suitable for JSON encoding.

        ``status`` is stored as its string value; ``created_at`` and
        ``updated_at`` are ISO-8601 strings (always timezone-aware).

        Returns:
            A ``dict`` with string keys and JSON-serialisable values.
        """
        data = asdict(self)
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        if self.updated_at is not None:
            data["updated_at"] = self.updated_at.isoformat()
        else:
            data["updated_at"] = None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Reconstruct a ``Task`` from a dict previously produced by :meth:`to_dict`.

        All validation in ``__post_init__`` applies, so round-tripping
        through ``to_dict`` / ``from_dict`` is safe and will surface any
        corruption immediately.

        Args:
            data: A dictionary containing at least ``title`` and ``id``
                keys, plus optional ``status``, ``created_at``, and
                ``updated_at``.

        Returns:
            A fully validated :class:`Task` instance.

        Raises:
            TypeError: If *data* is not a dict.
            KeyError: If required keys are missing.
        """
        if not isinstance(data, dict):
            raise TypeError(
                f"from_dict expects a dict, got {type(data).__name__}"
            )
        return cls(
            title=data["title"],
            id=data["id"],
            status=data["status"],
            created_at=data["created_at"],
            updated_at=data.get("updated_at"),
        )


class InMemoryTaskStore:
    """Thread-safe in-memory store for :class:`Task` objects.

    Maintains insertion order so that :meth:`list_all` returns tasks sorted
    oldest-first (by insertion time).

    Security assumptions:
        - All task IDs are treated as opaque strings; never interpreted as
          paths, SQL, or shell input.
        - Callers cannot inject tasks with duplicate IDs because IDs are
          auto-generated via uuid4.

    Failure behavior:
        - ``get`` returns ``None`` for missing IDs (no exception).
        - ``complete`` raises ``KeyError`` for missing IDs (fail closed).
        - ``delete`` raises ``KeyError`` for missing IDs (fail closed).
        - All mutations are serialised through a threading lock.
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()

    def add(self, title: str) -> Task:
        """Create a new task with the given *title* and store it.

        Args:
            title: Non-empty string for the task title.

        Returns:
            The newly created :class:`Task`.

        Raises:
            TypeError: If *title* is not a string.
            ValueError: If *title* is empty or blank.
        """
        task = Task(title=title)
        with self._lock:
            self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by its identifier.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The matching :class:`Task`, or ``None`` if not found.
        """
        with self._lock:
            return self._tasks.get(task_id)

    def list_all(self) -> List[Task]:
        """Return all tasks in insertion order (oldest first).

        Returns:
            A new list of all stored :class:`Task` objects.
        """
        with self._lock:
            return list(self._tasks.values())

    def complete(self, task_id: str) -> Task:
        """Mark a task as completed by its identifier.

        Sets the task's status to ``TaskStatus.COMPLETED`` and updates
        ``updated_at`` to the current UTC timestamp.

        Args:
            task_id: The unique identifier of the task to complete.

        Returns:
            The updated :class:`Task` with ``COMPLETED`` status.

        Raises:
            KeyError: If *task_id* does not exist in the store.
                Fails closed -- no partial state change occurs for
                non-existent tasks.

        Security assumptions:
            - Only the targeted task is mutated; all other tasks are
              unchanged.
            - The lock ensures no concurrent mutation can interleave.
        """
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(task_id)
            task = self._tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now(timezone.utc)
            return task

    def delete(self, task_id: str) -> None:
        """Remove a task from the store by its identifier.

        The task is looked up explicitly before removal so that a missing
        *task_id* always raises ``KeyError`` with a clear, predictable
        control flow rather than relying on the internal dict's own
        exception propagation.

        Args:
            task_id: The unique identifier of the task to delete.

        Raises:
            KeyError: If *task_id* does not exist in the store.
                Fails closed -- no state change occurs for non-existent
                task IDs.

        Security assumptions:
            - Only the targeted task is removed; all other tasks are
              unchanged.
            - The lock ensures no concurrent mutation can interleave.
        """
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(task_id)
            del self._tasks[task_id]
