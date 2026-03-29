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
* ``update()`` rejects attempts to change the ``id`` field -- the identity key
  is immutable once a task is stored.
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

    # -- Immutable identity fields that update() must reject -----------------

    _IMMUTABLE_FIELDS: frozenset[str] = frozenset({"id"})

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
            If no task with the given ``task_id`` exists.  Fails closed --
            never returns ``None`` silently.
        """
        if task_id not in self._tasks:
            raise KeyError(
                f"No task with id '{task_id}' exists in the store"
            )
        return copy.deepcopy(self._tasks[task_id])

    def list_all(self) -> list[Task]:
        """Return a list of all stored tasks in insertion order.

        Returns
        -------
        list[Task]
            Deep copies of every task in the store, ordered by insertion time
            (oldest first).  Returns an empty list when the store is empty.
        """
        return [copy.deepcopy(task) for task in self._tasks.values()]

    def update(self, task_id: str, **fields: Any) -> Task:
        """Patch mutable fields on an existing task.

        Validates that every key in *fields* corresponds to an actual field on
        the ``Task`` dataclass **before** applying any mutations.  This
        prevents partial updates when an invalid field name is supplied.

        Immutable identity fields (e.g. ``id``) cannot be changed via
        ``update()``.  Attempting to do so raises ``AttributeError``.

        The ``updated_at`` timestamp is always refreshed to the current UTC
        time, even when *fields* is empty.

        Parameters
        ----------
        task_id:
            The unique identifier of the task to update.
        **fields:
            Keyword arguments whose keys are ``Task`` field names and whose
            values are the new values to set.

        Returns
        -------
        Task
            A deep copy of the updated task.

        Raises
        ------
        KeyError
            If no task with the given ``task_id`` exists.
        AttributeError
            If any key in *fields* is not a valid ``Task`` field name, or if
            an immutable identity field (such as ``id``) is included.  Raised
            before any mutation occurs -- no partial application.
        """
        if task_id not in self._tasks:
            raise KeyError(
                f"No task with id '{task_id}' exists in the store"
            )

        # Validate all field names before applying any changes.
        for field_name in fields:
            if field_name not in self._TASK_FIELD_NAMES:
                raise AttributeError(
                    f"Task has no field '{field_name}'"
                )
            if field_name in self._IMMUTABLE_FIELDS:
                raise AttributeError(
                    f"Field '{field_name}' is immutable and cannot be updated"
                )

        task = self._tasks[task_id]

        # Build the replacement kwargs: start with current values, overlay
        # caller-supplied fields, then force updated_at.
        current = {f.name: getattr(task, f.name) for f in dataclasses.fields(task)}
        current.update(fields)
        current["updated_at"] = datetime.now(timezone.utc)

        updated_task = Task(**current)
        self._tasks[task_id] = updated_task
        return copy.deepcopy(updated_task)

    def delete(self, task_id: str) -> Task:
        """Remove a task from the store and return it.

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
            If no task with the given ``task_id`` exists.  Fails closed --
            never returns ``None`` silently.
        """
        if task_id not in self._tasks:
            raise KeyError(
                f"No task with id '{task_id}' exists in the store"
            )
        removed = self._tasks.pop(task_id)
        return copy.deepcopy(removed)
