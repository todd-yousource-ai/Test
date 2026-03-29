"""In-memory task store providing CRUD operations for Task objects.

This module implements ``InMemoryTaskStore``, the single source of truth for
task state within a session (TRD §3.2).  All public methods return **deep
copies** of stored ``Task`` instances so that callers cannot mutate internal
store state.

Security / failure assumptions
------------------------------
* ``add()`` fails closed with ``ValueError`` on duplicate IDs -- never silently
  overwrites.
* ``get()``, ``update()``, ``delete()`` fail closed with ``KeyError`` when the
  requested ID is absent -- never return ``None`` silently.
* ``update()`` validates every field name against the Task dataclass and raises
  ``AttributeError`` immediately on the first invalid name -- no partial
  application occurs before the error.
* No external dependencies -- only Python stdlib (``copy``, ``datetime``,
  ``dataclasses``).
"""

from __future__ import annotations

import copy
import dataclasses
from datetime import datetime, timezone
from typing import Any

from tasklib.models.task import Task


class InMemoryTaskStore:
    """Dict-backed in-memory store for ``Task`` objects.

    Internal storage is a plain ``dict[str, Task]`` keyed by ``task.id``.
    Insertion order is preserved (Python 3.7+ dict guarantee) so that
    ``list_all()`` returns tasks in creation order.

    All returned ``Task`` objects are deep copies.  Mutating a returned task
    has no effect on the data held inside the store.
    """

    def __init__(self) -> None:
        """Initialise an empty task store."""
        self._tasks: dict[str, Task] = {}

    # -- Field-name whitelist (computed once) --------------------------------

    _TASK_FIELD_NAMES: frozenset[str] = frozenset(
        f.name for f in dataclasses.fields(Task)
    )

    # -- Public CRUD ---------------------------------------------------------

    def add(self, task: Task) -> Task:
        """Store *task* and return a deep copy of the stored instance.

        Parameters
        ----------
        task:
            The ``Task`` to store.  Must have a unique ``id``.

        Returns
        -------
        Task
            A deep copy of the newly stored task.

        Raises
        ------
        ValueError
            If a task with the same ``id`` already exists in the store.
            Fails closed -- never silently overwrites an existing entry.
        """
        if task.id in self._tasks:
            raise ValueError(
                f"Task with id '{task.id}' already exists in the store"
            )
        # Store a deep copy so the caller cannot mutate internal state via the
        # original reference, then return another deep copy.
        self._tasks[task.id] = copy.deepcopy(task)
        return copy.deepcopy(self._tasks[task.id])

    def get(self, task_id: str) -> Task:
        """Retrieve a task by its identifier.

        Parameters
        ----------
        task_id:
            The unique identifier of the task to retrieve.

        Returns
        -------
        Task
            A deep copy of the matching task.

        Raises
        ------
        KeyError
            If no task with *task_id* exists in the store.
        """
        if task_id not in self._tasks:
            raise KeyError(f"No task found with id '{task_id}'")
        return copy.deepcopy(self._tasks[task_id])

    def list_all(self) -> list[Task]:
        """Return all stored tasks in insertion order.

        Returns
        -------
        list[Task]
            A list of deep copies of every stored task.  Returns an empty
            list when the store contains no tasks.
        """
        return [copy.deepcopy(t) for t in self._tasks.values()]

    def update(self, task_id: str, **fields: Any) -> Task:
        """Patch mutable fields on an existing task.

        Validates **all** supplied field names before applying any changes so
        that an invalid name never causes a partial update.  ``updated_at`` is
        always set to ``datetime.now(timezone.utc)`` -- even when *fields* is
        empty.

        Parameters
        ----------
        task_id:
            The identifier of the task to update.
        **fields:
            Keyword arguments whose names must correspond to fields defined on
            the ``Task`` dataclass.

        Returns
        -------
        Task
            A deep copy of the updated task.

        Raises
        ------
        KeyError
            If no task with *task_id* exists in the store.
        AttributeError
            If any key in *fields* is not a valid field name on ``Task``.
        """
        if task_id not in self._tasks:
            raise KeyError(f"No task found with id '{task_id}'")

        # Validate all field names *before* applying any mutations so we
        # never leave the store in a partially-updated state.
        for field_name in fields:
            if field_name not in self._TASK_FIELD_NAMES:
                raise AttributeError(
                    f"Task has no field '{field_name}'"
                )

        task = self._tasks[task_id]

        # Apply caller-supplied field updates.
        for field_name, value in fields.items():
            object.__setattr__(task, field_name, value)

        # Always refresh updated_at -- even when fields is empty.
        object.__setattr__(task, "updated_at", datetime.now(timezone.utc))

        return copy.deepcopy(task)

    def delete(self, task_id: str) -> Task:
        """Remove a task from the store and return it.

        Parameters
        ----------
        task_id:
            The identifier of the task to remove.

        Returns
        -------
        Task
            A deep copy of the removed task.

        Raises
        ------
        KeyError
            If no task with *task_id* exists in the store.
        """
        if task_id not in self._tasks:
            raise KeyError(f"No task found with id '{task_id}'")

        removed = self._tasks.pop(task_id)
        return copy.deepcopy(removed)
