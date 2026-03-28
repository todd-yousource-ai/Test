"""In-memory task store backed by a plain dict.

Provides add, get, and list_all operations for Task instances.
This module has zero external dependencies -- it only imports from
tasklib.models.task.

Security assumptions:
    - This store is ephemeral and single-process; no persistence or
      concurrent-access guarantees are provided.
    - All input (titles, task IDs) is validated strictly; invalid input
      raises immediately rather than silently succeeding.

Failure behavior:
    - add() raises ValueError on empty or whitespace-only titles.
    - get() raises KeyError with a descriptive message when the requested
      task ID is not present. This is a deliberate, documented design
      choice (see PR #4 design decisions). Callers may catch and convert
      to None if desired.
    - No silent failure paths exist; every error surfaces with context.
"""

from __future__ import annotations

from tasklib.models.task import Task


class InMemoryTaskStore:
    """Dict-backed in-memory store for Task objects.

    Tasks are keyed by their string identifier. Insertion order is
    preserved (Python 3.7+ dict ordering guarantee), which means
    list_all() returns tasks in creation order, oldest first.

    This class owns Task construction to guarantee ID uniqueness --
    callers pass a title string, not a pre-built Task.
    """

    def __init__(self) -> None:
        """Initialise an empty task store.

        The internal dict is private; external code must use the public
        add/get/list_all interface.
        """
        self._tasks: dict[str, Task] = {}

    def add(self, title: str) -> Task:
        """Create a new Task from *title*, store it, and return it.

        Args:
            title: A non-empty, non-whitespace-only string used as the
                task's human-readable title.

        Returns:
            The newly created Task instance with a unique id, PENDING
            status, and a created_at timestamp.

        Raises:
            TypeError: If *title* is not a string.
            ValueError: If *title* is empty or contains only whitespace.
        """
        if not isinstance(title, str):
            raise TypeError(
                f"title must be a str, got {type(title).__name__}"
            )

        if not title.strip():
            raise ValueError(
                "title must be a non-empty string (whitespace-only titles "
                "are not allowed)"
            )

        task = Task(title=title)
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Task:
        """Retrieve a task by its identifier.

        Args:
            task_id: The string identifier of the task to retrieve.

        Returns:
            The Task instance associated with *task_id*.

        Raises:
            KeyError: If no task with the given *task_id* exists in the
                store. The error message includes the missing ID for
                diagnostic context.
        """
        try:
            return self._tasks[task_id]
        except KeyError:
            raise KeyError(f"Task not found: {task_id}") from None

    def list_all(self) -> list[Task]:
        """Return a list of all stored tasks in insertion order.

        Returns:
            A **new** list object on every call (not a live view of the
            internal data structure). If the store is empty, returns an
            empty list.
        """
        return list(self._tasks.values())