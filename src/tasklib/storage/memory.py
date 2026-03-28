"""Task dataclass, TaskStatus enumeration, and in-memory storage for tasklib.

Defines the core domain model and a thread-safe in-memory storage backend.
A Task is an immutable-id, mutable-status value object with automatic UUID
generation and UTC timestamp tracking.  MemoryStorage provides CRUD
operations over a collection of tasks.

Security assumptions:
    - Task IDs are generated via uuid4 and are not caller-controllable.
    - All fields are type-checked at construction where feasible.
    - No external input is trusted without validation.

Failure behavior:
    - Construction with invalid types raises TypeError immediately.
    - No silent coercion or default-swallowing occurs.
    - Storage lookups for missing IDs raise KeyError.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------

class TaskStatus(Enum):
    """Enumeration of valid task lifecycle states.

    PENDING  -- task has been created but not yet completed.
    COMPLETED -- task has been marked as done.
    """

    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    """A single task with an auto-generated ID and creation timestamp.

    Only *title* is required at construction time. The *id*, *status*,
    *created_at*, and *updated_at* fields are populated automatically.

    Attributes:
        title: Human-readable task description. Must be a non-empty string.
        id: Unique identifier (UUID4 hex string), auto-generated.
        status: Current lifecycle state, defaults to PENDING.
        created_at: UTC datetime when the task was created.
        updated_at: UTC datetime when the task was last modified, or None
            if the task has never been mutated after creation.
    """

    title: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default=None)

    # -- Validation ----------------------------------------------------------

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

    # -- Serialization -------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the task to a plain dictionary.

        Returns:
            A dictionary with string keys suitable for JSON-like
            serialization.
        """
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at is not None
                else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """Deserialize a task from a plain dictionary.

        Args:
            data: Dictionary with keys matching Task field names.

        Returns:
            A Task instance reconstructed from the dictionary values.

        Raises:
            TypeError: If *data* is not a dictionary.
            KeyError: If required keys are missing.
            ValueError: If enum or datetime values cannot be parsed.
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data).__name__}")

        updated_at_raw = data.get("updated_at")
        updated_at = (
            datetime.fromisoformat(updated_at_raw)
            if updated_at_raw is not None
            else None
        )
        return cls(
            title=data["title"],
            id=data["id"],
            status=TaskStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=updated_at,
        )


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

class MemoryStorage:
    """Thread-safe, in-memory task store keyed by task ID.

    All public methods acquire an internal lock so the store can be shared
    safely across threads.

    Attributes:
        _tasks: Internal mapping from task ID to Task instance.
        _lock: Reentrant lock guarding all mutations and reads.
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}
        self._lock: threading.RLock = threading.RLock()

    # -- CRUD ----------------------------------------------------------------

    def add(self, task: Task) -> Task:
        """Insert a new task into the store.

        Args:
            task: The Task instance to store.

        Returns:
            The same Task instance that was stored.

        Raises:
            TypeError: If *task* is not a Task instance.
            ValueError: If a task with the same ID already exists.
        """
        if not isinstance(task, Task):
            raise TypeError(f"task must be a Task, got {type(task).__name__}")
        with self._lock:
            if task.id in self._tasks:
                raise ValueError(f"task with id {task.id!r} already exists")
            self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Task:
        """Retrieve a task by its unique ID.

        Args:
            task_id: The UUID hex string identifying the task.

        Returns:
            The matching Task instance.

        Raises:
            KeyError: If no task with *task_id* exists.
        """
        with self._lock:
            try:
                return self._tasks[task_id]
            except KeyError:
                raise KeyError(f"no task with id {task_id!r}")

    def list_all(self) -> List[Task]:
        """Return a list of every task in insertion order.

        Returns:
            A new list containing all stored Task instances. Modifying the
            returned list does not affect the internal store.
        """
        with self._lock:
            return list(self._tasks.values())

    def update(self, task_id: str, **changes: Any) -> Task:
        """Apply field-level updates to an existing task.

        Only *title* and *status* may be changed. The *updated_at*
        timestamp is set automatically.

        Args:
            task_id: ID of the task to modify.
            **changes: Keyword arguments whose keys must be ``"title"``
                and/or ``"status"``.

        Returns:
            The modified Task instance.

        Raises:
            KeyError: If no task with *task_id* exists.
            ValueError: If an unsupported field name is given.
        """
        allowed = {"title", "status"}
        bad = set(changes) - allowed
        if bad:
            raise ValueError(f"cannot update fields: {bad!r}")

        with self._lock:
            task = self.get(task_id)

            if "title" in changes:
                title = changes["title"]
                if not isinstance(title, str) or not title.strip():
                    raise ValueError("title must be a non-empty string")
                task.title = title

            if "status" in changes:
                status = changes["status"]
                if not isinstance(status, TaskStatus):
                    raise TypeError(
                        f"status must be a TaskStatus, got {type(status).__name__}"
                    )
                task.status = status

            task.updated_at = datetime.now(timezone.utc)
        return task

    def delete(self, task_id: str) -> Task:
        """Remove a task from the store and return it.

        Args:
            task_id: ID of the task to remove.

        Returns:
            The Task instance that was removed.

        Raises:
            KeyError: If no task with *task_id* exists.
        """
        with self._lock:
            try:
                return self._tasks.pop(task_id)
            except KeyError:
                raise KeyError(f"no task with id {task_id!r}")

    def clear(self) -> None:
        """Remove all tasks from the store."""
        with self._lock:
            self._tasks.clear()

    def __len__(self) -> int:
        """Return the number of tasks currently stored."""
        with self._lock:
            return len(self._tasks)

    def __contains__(self, task_id: str) -> bool:
        """Check whether a task with the given ID exists."""
        with self._lock:
            return task_id in self._tasks