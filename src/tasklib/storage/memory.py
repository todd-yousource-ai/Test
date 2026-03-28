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
    """Coerce *value* to a timezone-aware datetime.

    Accepts ``datetime`` instances directly and ISO-8601 strings (as produced
    by ``datetime.isoformat()``).  Returns a timezone-aware ``datetime`` or
    raises ``TypeError`` / ``ValueError`` with a clear message.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"{field_name} string is not valid ISO-8601: {value!r}"
            ) from exc
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
        """Validate all fields eagerly and fail closed on invalid data."""
        if not isinstance(self.title, str):
            raise TypeError(f"title must be a str, got {type(self.title).__name__}")
        if not self.title.strip():
            raise ValueError("title must be a non-empty string")

        if not isinstance(self.id, str):
            raise TypeError(f"id must be a str, got {type(self.id).__name__}")
        if not self.id:
            raise ValueError("id must be a non-empty string")

        if not isinstance(self.status, TaskStatus):
            raise TypeError(
                f"status must be a TaskStatus, got {type(self.status).__name__}"
            )

        if not isinstance(self.created_at, datetime):
            raise TypeError(
                "created_at must be a datetime, "
                f"got {type(self.created_at).__name__}"
            )
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

        if self.updated_at is not None:
            if not isinstance(self.updated_at, datetime):
                raise TypeError(
                    "updated_at must be a datetime or None, "
                    f"got {type(self.updated_at).__name__}"
                )
            if self.updated_at.tzinfo is None:
                raise ValueError("updated_at must be timezone-aware when provided")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the task to a dictionary with enum values normalized."""
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """Deserialize a Task from a validated dictionary payload.

        Accepts both ``datetime`` objects and ISO-8601 strings for the
        *created_at* and *updated_at* fields so that round-tripping through
        ``to_dict`` (and any intermediate JSON serialization) works reliably.
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data).__name__}")

        required_keys = {"title", "id", "status", "created_at"}
        missing = required_keys - data.keys()
        if missing:
            raise ValueError(f"missing required task fields: {sorted(missing)}")

        status_value = data["status"]
        try:
            status = TaskStatus(status_value)
        except ValueError as exc:
            raise ValueError(f"invalid task status: {status_value!r}") from exc

        created_at = _parse_datetime(data["created_at"], "created_at")

        raw_updated = data.get("updated_at")
        if raw_updated is not None:
            updated_at: Optional[datetime] = _parse_datetime(
                raw_updated, "updated_at"
            )
        else:
            updated_at = None

        return cls(
            title=data["title"],
            id=data["id"],
            status=status,
            created_at=created_at,
            updated_at=updated_at,
        )


class InMemoryTaskStore:
    """Thread-safe in-memory task store.

    Security assumptions:
        - This store is process-local and does not persist data.
        - Callers provide untrusted task titles and task IDs; titles are
          validated by Task and IDs are matched exactly against stored values.

    Failure behavior:
        - Missing task IDs raise KeyError for complete/delete and return None for get.
        - Invalid task construction fails immediately.
        - No mutation path silently ignores errors.
    """

    def __init__(self) -> None:
        """Initialize an empty task store protected by a re-entrant lock."""
        self._tasks: Dict[str, Task] = {}
        self._order: List[str] = []
        self._lock = threading.RLock()

    def add(self, title: str) -> Task:
        """Create, store, and return a new task."""
        task = Task(title=title)
        with self._lock:
            self._tasks[task.id] = task
            self._order.append(task.id)
        return task

    def get(self, task_id: str) -> Optional[Task]:
        """Return the task for *task_id*, or None if it does not exist."""
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be a str, got {type(task_id).__name__}")
        with self._lock:
            return self._tasks.get(task_id)

    def list_all(self) -> List[Task]:
        """Return all tasks in creation order, oldest first."""
        with self._lock:
            return [self._tasks[task_id] for task_id in self._order]

    def complete(self, task_id: str) -> Task:
        """Mark an existing task as completed and update its mutation timestamp.

        Security assumptions:
            - task_id is untrusted input and must be an exact string key match.

        Failure behavior:
            - Raises TypeError if task_id is not a string.
            - Raises KeyError if the task does not exist.
            - Never creates implicit tasks or ignores missing identifiers.
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be a str, got {type(task_id).__name__}")

        with self._lock:
            task = self._tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now(timezone.utc)
            return task

    def delete(self, task_id: str) -> None:
        """Remove an existing task from the store.

        Security assumptions:
            - task_id is untrusted input and must be an exact string key match.

        Failure behavior:
            - Raises TypeError if task_id is not a string.
            - Raises KeyError if the task does not exist.
            - Deletes only the addressed task and preserves all others.
        """
        if not isinstance(task_id, str):
            raise TypeError(f"task_id must be a str, got {type(task_id).__name__}")

        with self._lock:
            del self._tasks[task_id]
            self._order.remove(task_id)
