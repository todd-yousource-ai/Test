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

__all__: list[str] = ["Task", "TaskStatus", "InMemoryTaskStore"]


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
    ``datetime.isoformat()``). The returned value is always timezone-aware;
    naive datetimes and strings that parse to naive datetimes are rejected
    outright so that all timestamps in the domain model carry an
    unambiguous instant in time.

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
        f"{field_name} must be a datetime or ISO-8601 string, got "
        f"{type(value).__name__}"
    )


@dataclass
class Task:
    """Domain model for a single task.

    Security assumptions:
        - Callers may provide untrusted values for any constructor field.
        - Validation is enforced during post-initialization before the
          instance is considered valid.

    Failure behavior:
        - Invalid field types or values raise immediately in ``__post_init__``.
        - Naive datetimes are rejected to avoid ambiguous timestamp handling.
        - Enum coercion is strict; unknown status strings raise ``ValueError``.
    """

    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default=None)

    def __post_init__(self) -> None:
        """Validate and normalize constructor inputs.

        Raises:
            TypeError: If fields are of invalid types.
            ValueError: If fields contain invalid values.
        """
        if not isinstance(self.title, str):
            raise TypeError(
                f"title must be of type str, got {type(self.title).__name__}"
            )
        if not self.title.strip():
            raise ValueError("title must not be empty or whitespace-only")

        if not isinstance(self.id, str):
            raise TypeError(f"id must be of type str, got {type(self.id).__name__}")
        if self.id == "":
            raise ValueError("id must not be empty")

        if isinstance(self.status, TaskStatus):
            normalized_status = self.status
        elif isinstance(self.status, str):
            try:
                normalized_status = TaskStatus(self.status)
            except ValueError as exc:
                raise ValueError(f"invalid task status: {self.status!r}") from exc
        else:
            raise TypeError(
                "status must be a TaskStatus or str, got "
                f"{type(self.status).__name__}"
            )
        self.status = normalized_status

        self.created_at = _parse_datetime(self.created_at, "created_at")

        if self.updated_at is not None:
            self.updated_at = _parse_datetime(self.updated_at, "updated_at")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the task to a JSON-friendly dictionary.

        Returns:
            Dictionary containing primitive values only; enum values are
            emitted as strings and datetimes as ISO-8601 strings.
        """
        data = asdict(self)
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = (
            self.updated_at.isoformat() if self.updated_at is not None else None
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """Deserialize a task previously produced by ``to_dict``.

        All fields that are part of the serialized representation (``title``,
        ``id``, ``status``, ``created_at``) are required. Omitting any of
        them raises ``KeyError`` so that data loss during deserialization is
        never silently masked by falling back to defaults.

        Security assumptions:
            - *data* is treated as untrusted input and validated strictly.
            - Unknown types, invalid enum values, and malformed timestamps
              are rejected.

        Failure behavior:
            - Missing required fields (``title``, ``id``, ``status``,
              ``created_at``) surface as ``KeyError``.
            - Invalid field types or values raise ``TypeError``/``ValueError``.
            - Only ``updated_at`` may be omitted (defaults to ``None``).
        """
        if not isinstance(data, dict):
            raise TypeError(
                f"data must be of type dict, got {type(data).__name__}"
            )

        # Require all serialized fields explicitly to avoid masking data loss.
        # Accessing via [] ensures KeyError on omission.
        title = data["title"]
        task_id = data["id"]
        status = data["status"]
        created_at = data["created_at"]
        updated_at = data.get("updated_at", None)

        return cls(
            title=title,
            id=task_id,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
        )


class InMemoryTaskStore:
    """Thread-safe in-memory store for ``Task`` instances.

    Security assumptions:
        - The store is process-local and non-persistent.
        - Callers are responsible for holding references returned from the
          store; objects are stored and returned by identity.
        - All external task identifiers are treated as untrusted and matched
          explicitly against in-memory keys.

    Failure behavior:
        - Missing task IDs in mutation methods raise ``KeyError``.
        - Invalid titles or malformed task construction failures surface from
          the ``Task`` constructor without suppression.
        - No method silently ignores an error condition.
    """

    def __init__(self) -> None:
        """Initialize an empty task store."""
        self._tasks: Dict[str, Task] = {}
        self._order: List[str] = []
        self._lock = threading.RLock()

    def add(self, title: str) -> Task:
        """Create and store a new task.

        Args:
            title: Human-readable task title. Validation is delegated to
                ``Task``.

        Returns:
            The newly created and stored ``Task``.

        Raises:
            TypeError: If ``title`` has an invalid type.
            ValueError: If ``title`` is invalid for task creation.
        """
        task = Task(title=title)
        with self._lock:
            self._tasks[task.id] = task
            self._order.append(task.id)
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by identifier.

        Args:
            task_id: Task identifier to look up.

        Returns:
            The matching ``Task`` if present, otherwise ``None``.
        """
        with self._lock:
            return self._tasks.get(task_id)

    def list_all(self) -> List[Task]:
        """List all stored tasks in creation order, oldest first.

        Returns:
            A list of tasks in insertion order. If the internal ordering
            index references a task ID that no longer exists in the primary
            store (indicating an internal consistency error), that ID is
            silently skipped rather than raising an exception, so callers
            always receive a usable list.
        """
        with self._lock:
            return [
                self._tasks[tid]
                for tid in self._order
                if tid in self._tasks
            ]

    def complete(self, task_id: str) -> Task:
        """Mark an existing task as completed.

        Security assumptions:
            - ``task_id`` is treated as untrusted input and must match an
              existing stored task exactly.
            - Completion mutates only the explicitly addressed task.

        Failure behavior:
            - Raises ``KeyError`` immediately if ``task_id`` does not exist.
            - No partial mutation occurs for missing task identifiers.

        Args:
            task_id: Identifier of the task to complete.

        Returns:
            The updated ``Task`` instance with completed status and a UTC
            ``updated_at`` timestamp.

        Raises:
            KeyError: If no task exists for ``task_id``.
        """
        with self._lock:
            task = self._tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now(timezone.utc)
            return task

    def delete(self, task_id: str) -> None:
        """Delete an existing task from the store.

        Security assumptions:
            - ``task_id`` is treated as untrusted input and deletion is
              scoped strictly to the matching key.

        Failure behavior:
            - Raises ``KeyError`` immediately if ``task_id`` does not exist.
            - No other tasks are modified or removed on failure.

        Args:
            task_id: Identifier of the task to remove.

        Raises:
            KeyError: If no task exists for ``task_id``.
        """
        with self._lock:
            del self._tasks[task_id]
            self._order.remove(task_id)
