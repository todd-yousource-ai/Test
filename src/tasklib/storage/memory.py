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
            A deep copy of the stored task.

        Raises
        ------
        KeyError
            If no task with *task_id* exists.  Fails closed -- never returns
            ``None`` silently.
        """
        if task_id not in self._tasks:
            raise KeyError(
                f"Task with id '{task_id}' not found in the store"
            )
        return copy.deepcopy(self._tasks[task_id])

    def list_all(self) -> list[Task]:
        """Return a list of all stored tasks in insertion order.

        Returns
        -------
        list[Task]
            Deep copies of every task in the store.  Returns an empty list
            when the store contains no tasks.
        """
        return [copy.deepcopy(task) for task in self._tasks.values()]

    def update(self, task_id: str, fields: dict[str, Any] | None = None, **kwargs: Any) -> Task:
        """Patch mutable fields on an existing task.

        Accepts fields either as a dictionary first argument or as keyword
        arguments (supporting both calling conventions used in the test suite).
        Automatically sets ``updated_at`` to the current UTC time regardless
        of whether any other fields are provided.

        Parameters
        ----------
        task_id:
            The unique identifier of the task to update.
        fields:
            Optional dictionary of field names to new values.
        **kwargs:
            Additional field names to new values (merged with *fields*).

        Returns
        -------
        Task
            A deep copy of the updated task.

        Raises
        ------
        KeyError
            If no task with *task_id* exists.  Fails closed.
        AttributeError
            If any key in *fields* / *kwargs* is not a valid field on ``Task``.
            Validation runs before any mutation -- no partial updates on error.
        """
        if task_id not in self._tasks:
            raise KeyError(
                f"Task with id '{task_id}' not found in the store"
            )

        # Merge both sources of field updates.
        merged: dict[str, Any] = {}
        if fields is not None:
            merged.update(fields)
        merged.update(kwargs)

        # Validate all field names BEFORE applying any changes.  This prevents
        # partial updates when an invalid name is present.
        for field_name in merged:
            if field_name not in self._TASK_FIELD_NAMES:
                raise AttributeError(
                    f"Task has no field '{field_name}'"
                )

        task = self._tasks[task_id]

        # Apply requested field changes via dataclasses.replace for safety.
        # Always set updated_at to current UTC time.
        replace_kwargs: dict[str, Any] = dict(merged)
        replace_kwargs["updated_at"] = datetime.now(timezone.utc)

        updated_task = dataclasses.replace(task, **replace_kwargs)
        self._tasks[task_id] = updated_task
        return copy.deepcopy(updated_task)

    def delete(self, task_id: str) -> Task:
        """Remove and return a task by its identifier.

        Parameters
        ----------
        task_id:
            The unique identifier of the task to delete.

        Returns
        -------
        Task
            A deep copy of the removed task.

        Raises
        ------
        KeyError
            If no task with *task_id* exists.  Fails closed -- never silently
            ignores a missing ID.
        """
        if task_id not in self._tasks:
            raise KeyError(
                f"Task with id '{task_id}' not found in the store"
            )
        removed = self._tasks.pop(task_id)
        return copy.deepcopy(removed)
