"""In-memory task store providing CRUD operations for Task objects."""

from __future__ import annotations

import copy
import dataclasses
from datetime import datetime, timezone
from typing import Any

from tasklib.models.task import Task


def _ensure_utc_aware(dt: datetime | None) -> datetime | None:
    """Convert a naive datetime to UTC-aware; pass through aware or None."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _normalize_task_timestamps(task: Task) -> Task:
    """Ensure created_at and updated_at are timezone-aware (UTC)."""
    created = _ensure_utc_aware(task.created_at)
    updated = _ensure_utc_aware(task.updated_at)
    if created is not task.created_at:
        object.__setattr__(task, "created_at", created)
    if updated is not task.updated_at:
        object.__setattr__(task, "updated_at", updated)
    return task


class InMemoryTaskStore:
    """Dict-backed in-memory store for ``Task`` objects."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    @staticmethod
    def _get_task_field_names() -> frozenset[str]:
        return frozenset(f.name for f in dataclasses.fields(Task))

    _IMMUTABLE_FIELDS: frozenset[str] = frozenset({"id"})

    def add(self, task: Task) -> Task:
        if task.id in self._tasks:
            raise ValueError(
                f"Task with id '{task.id}' already exists in the store"
            )
        stored = copy.deepcopy(task)
        _normalize_task_timestamps(stored)
        self._tasks[task.id] = stored
        return copy.deepcopy(stored)

    def get(self, task_id: str) -> Task:
        if task_id not in self._tasks:
            raise KeyError(
                f"Task with id '{task_id}' not found in the store"
            )
        return copy.deepcopy(self._tasks[task_id])

    def list_all(self) -> list[Task]:
        return [copy.deepcopy(task) for task in self._tasks.values()]

    def update(self, task_id: str, **fields: Any) -> Task:
        if task_id not in self._tasks:
            raise KeyError(
                f"Task with id '{task_id}' not found in the store"
            )

        task_field_names = self._get_task_field_names()

        for field_name in fields:
            if field_name not in task_field_names:
                raise AttributeError(
                    f"Task has no field '{field_name}'"
                )
            if field_name in self._IMMUTABLE_FIELDS:
                raise AttributeError(
                    f"Field '{field_name}' is immutable and cannot be updated"
                )

        current = self._tasks[task_id]
        updated = copy.deepcopy(current)

        for field_name, value in fields.items():
            object.__setattr__(updated, field_name, value)

        object.__setattr__(updated, "updated_at", datetime.now(timezone.utc))

        self._tasks[task_id] = updated
        return copy.deepcopy(updated)

    def delete(self, task_id: str) -> Task:
        if task_id not in self._tasks:
            raise KeyError(
                f"Task with id '{task_id}' not found in the store"
            )
        removed = self._tasks.pop(task_id)
        return copy.deepcopy(removed)
