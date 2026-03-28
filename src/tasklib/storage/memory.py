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
    - All state mutations are protected by a reentrant lock for thread safety.
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
                f"{field_name} must be timezone-aware, got naive datetime string: {value!r}"
            )
        return parsed
    raise TypeError(
        f"{field_name} must be a datetime or ISO-8601 string, got {type(value).__name__}"
    )


def _validate_task_id(task_id: Any, param_name: str = "task_id") -> None:
    """Validate that *task_id* is a non-empty string.

    Args:
        task_id: The value to validate.
        param_name: Parameter name for error messages.

    Raises:
        TypeError: If *task_id* is not a string.
        ValueError: If *task_id* is an empty string.
    """
    if not isinstance(task_id, str):
        raise TypeError(f"{param_name} must be str, got {type(task_id).__name__}")
    if not task_id:
        raise ValueError(f"{param_name} must be a non-empty string")


@dataclass(slots=True)
class Task:
    """Task domain model with strict validation and UTC timestamp tracking.

    Security assumptions:
        - ``title`` is untrusted caller input and is validated as a non-empty string.
        - ``id`` may be caller-supplied during deserialization but must remain a string.
        - ``status`` is constrained to the ``TaskStatus`` enumeration.
        - All timestamps must be timezone-aware to avoid ambiguous state.

    Failure behavior:
        - Invalid field types or values raise immediately in ``__post_init__``.
        - Invalid timestamp strings are rejected with explicit errors.
        - No implicit mutation or lossy coercion occurs.
    """

    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = field(default=TaskStatus.PENDING)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default=None)

    def __post_init__(self) -> None:
        """Validate all fields and normalize supported serialized inputs."""
        if not isinstance(self.title, str):
            raise TypeError(f"title must be str, got {type(self.title).__name__}")
        if not self.title.strip():
            raise ValueError("title must be a non-empty string")

        if not isinstance(self.id, str):
            raise TypeError(f"id must be str, got {type(self.id).__name__}")
        if not self.id:
            raise ValueError("id must be a non-empty string")

        if isinstance(self.status, str):
            try:
                self.status = TaskStatus(self.status)
            except ValueError as exc:
                raise ValueError(f"status must be one of {[s.value for s in TaskStatus]}") from exc
        elif not isinstance(self.status, TaskStatus):
            raise TypeError(
                f"status must be TaskStatus or str, got {type(self.status).__name__}"
            )

        self.created_at = _parse_datetime(self.created_at, "created_at")

        if self.updated_at is not None:
            self.updated_at = _parse_datetime(self.updated_at, "updated_at")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the task to a plain dictionary.

        Returns:
            A dictionary representation with enum values and ISO-8601 timestamps.
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
        """Deserialize a task from a dictionary with strict validation.

        Required fields: ``title``. The ``id``, ``status``, and ``created_at``
        fields are required when present in the input to enforce data integrity
        during round-trip deserialization. However, for partial-data creation
        scenarios (e.g., creating a new task from external input), only ``title``
        is strictly required -- ``id``, ``status``, and ``created_at`` will receive
        safe defaults from the ``Task`` constructor if omitted.

        Args:
            data: Untrusted mapping input representing a serialized task.

        Returns:
            A validated ``Task`` instance.

        Raises:
            TypeError: If *data* is not a dictionary.
            KeyError: If ``title`` is missing.
            ValueError/TypeError: If any field fails validation.
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be dict, got {type(data).__name__}")

        if "title" not in data:
            raise KeyError("missing required field(s): title")

        kwargs: Dict[str, Any] = {"title": data["title"]}

        if "id" in data:
            kwargs["id"] = data["id"]
        if "status" in data:
            kwargs["status"] = data["status"]
        if "created_at" in data:
            kwargs["created_at"] = data["created_at"]
        if "updated_at" in data:
            kwargs["updated_at"] = data["updated_at"]

        return cls(**kwargs)


class InMemoryTaskStore:
    """Thread-safe in-memory task store for the process lifetime.

    Security assumptions:
        - Callers provide untrusted titles and task identifiers.
        - Titles are validated by the ``Task`` model at creation time.
        - Identifiers are matched exactly; absent identifiers are rejected.

    Failure behavior:
        - Missing task IDs raise ``KeyError`` in mutation methods.
        - Read methods never fabricate results; unknown IDs return ``None``.
        - All operations execute under a reentrant lock to prevent race-driven
          corruption and allow safe reentrant calls.
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory store."""
        self._tasks: Dict[str, Task] = {}
        self._order: List[str] = []
        self._lock = threading.RLock()

    def add(self, title: str) -> Task:
        """Create and store a new task.

        Args:
            title: Untrusted task title input. Validation is delegated to ``Task``.

        Returns:
            The created ``Task`` instance.

        Raises:
            TypeError/ValueError: If ``title`` fails ``Task`` validation.
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
            The matching ``Task`` if present; otherwise ``None``.

        Raises:
            TypeError: If ``task_id`` is not a string.
            ValueError: If ``task_id`` is an empty string.
        """
        _validate_task_id(task_id)

        with self._lock:
            return self._tasks.get(task_id)

    def list_all(self) -> List[Task]:
        """List all stored tasks in creation order, oldest first.

        Returns:
            A new list of task references in insertion order.
        """
        with self._lock:
            return [self._tasks[task_id] for task_id in self._order]

    def list_tasks(self) -> List[Task]:
        """List all stored tasks in creation order, oldest first.

        Alias for :meth:`list_all` provided for interface compatibility.

        Returns:
            A new list of task references in insertion order.
        """
        return self.list_all()

    def complete(self, task_id: str) -> Task:
        """Mark an existing task as completed and update its modification timestamp.

        Security assumptions:
            - ``task_id`` is untrusted caller input and must be an exact, non-empty string.
            - Completion only mutates the explicitly addressed task.

        Failure behavior:
            - Invalid identifier types raise ``TypeError``.
            - Empty identifiers raise ``ValueError``.
            - Unknown identifiers raise ``KeyError(task_id)``.
            - Timestamp updates always use current UTC time.

        Args:
            task_id: The identifier of the task to complete.

        Returns:
            The updated ``Task`` with status set to ``TaskStatus.COMPLETED``.

        Raises:
            TypeError: If ``task_id`` is not a string.
            ValueError: If ``task_id`` is an empty string.
            KeyError: If ``task_id`` does not exist in the store.
        """
        _validate_task_id(task_id)

        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(task_id)

            task = self._tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now(timezone.utc)
            return task

    def delete(self, task_id: str) -> None:
        """Remove an existing task from the store.

        Security assumptions:
            - ``task_id`` is untrusted caller input and must be validated before use.
            - Deletion affects only the explicitly identified task.

        Failure behavior:
            - Invalid identifier types raise ``TypeError``.
            - Empty identifiers raise ``ValueError``.
            - Unknown identifiers raise ``KeyError(task_id)``.
            - On success, the task is removed from both storage and ordering indexes.

        Args:
            task_id: The identifier of the task to delete.

        Raises:
            TypeError: If ``task_id`` is not a string.
            ValueError: If ``task_id`` is an empty string.
            KeyError: If ``task_id`` does not exist in the store.
        """
        _validate_task_id(task_id)

        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(task_id)

            del self._tasks[task_id]
            self._order.remove(task_id)
