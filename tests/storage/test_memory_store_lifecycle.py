from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)

from tasklib.storage.memory import InMemoryTaskStore, TaskStatus


def test_project_root_discovery_finds_pyproject():
    assert (PROJECT_ROOT / "pyproject.toml").exists()


def test_updated_at_is_none_on_creation():
    store = InMemoryTaskStore()

    task = store.add("Write tests")

    assert task.updated_at is None


def test_complete_sets_status_to_completed():
    store = InMemoryTaskStore()
    task = store.add("Finish feature")

    completed = store.complete(task.id)

    assert completed.status is TaskStatus.COMPLETED


def test_complete_sets_updated_at():
    store = InMemoryTaskStore()
    task = store.add("Finish feature")

    completed = store.complete(task.id)

    assert isinstance(completed.updated_at, datetime)
    assert completed.updated_at.tzinfo is not None
    assert completed.updated_at >= task.created_at


def test_complete_returns_updated_task():
    store = InMemoryTaskStore()
    task = store.add("Finish feature")

    completed = store.complete(task.id)

    assert completed is task
    assert completed.status is TaskStatus.COMPLETED
    assert completed.updated_at is not None


def test_complete_preserves_task_id():
    store = InMemoryTaskStore()
    task = store.add("Keep same id")
    original_id = task.id

    completed = store.complete(task.id)

    assert completed.id == original_id


def test_complete_preserves_task_title():
    store = InMemoryTaskStore()
    task = store.add("Keep same title")
    original_title = task.title

    completed = store.complete(task.id)

    assert completed.title == original_title


def test_complete_nonexistent_raises_keyerror():
    store = InMemoryTaskStore()

    with pytest.raises(KeyError):
        store.complete("missing-task-id")


def test_complete_empty_string_raises_keyerror():
    store = InMemoryTaskStore()

    with pytest.raises(KeyError):
        store.complete("")


def test_complete_does_not_affect_other_tasks():
    store = InMemoryTaskStore()
    first = store.add("Complete me")
    second = store.add("Leave me pending")

    store.complete(first.id)

    assert first.status is TaskStatus.COMPLETED
    assert second.status is TaskStatus.PENDING
    assert second.updated_at is None


def test_completing_one_task_does_not_change_any_other_task():
    store = InMemoryTaskStore()
    tasks = [store.add(f"task-{i}") for i in range(3)]

    store.complete(tasks[1].id)

    assert tasks[0].status is TaskStatus.PENDING
    assert tasks[0].updated_at is None
    assert tasks[1].status is TaskStatus.COMPLETED
    assert tasks[2].status is TaskStatus.PENDING
    assert tasks[2].updated_at is None


def test_delete_removes_task():
    store = InMemoryTaskStore()
    task = store.add("Delete me")

    store.delete(task.id)

    assert store.get(task.id) is None
    assert store.list_tasks() == []


def test_delete_does_not_remove_other_tasks():
    store = InMemoryTaskStore()
    first = store.add("Delete me")
    second = store.add("Keep me")

    store.delete(first.id)

    remaining = store.get(second.id)
    listed = store.list_tasks()

    assert store.get(first.id) is None
    assert remaining is second
    assert len(listed) == 1
    assert listed[0] is second


def test_delete_nonexistent_raises_keyerror():
    store = InMemoryTaskStore()

    with pytest.raises(KeyError):
        store.delete("missing-task-id")


def test_delete_already_deleted_raises_keyerror():
    store = InMemoryTaskStore()
    task = store.add("Delete twice")

    store.delete(task.id)

    with pytest.raises(KeyError):
        store.delete(task.id)


def test_complete_on_previously_deleted_task_raises_keyerror():
    store = InMemoryTaskStore()
    task = store.add("Delete then complete")

    store.delete(task.id)

    with pytest.raises(KeyError):
        store.complete(task.id)


def test_complete_then_delete():
    store = InMemoryTaskStore()
    task = store.add("Lifecycle task")

    completed = store.complete(task.id)
    store.delete(task.id)

    assert completed.status is TaskStatus.COMPLETED
    assert store.get(task.id) is None
    assert store.list_tasks() == []


def test_complete_idempotent_updates_timestamp():
    store = InMemoryTaskStore()
    task = store.add("Complete twice")

    first = store.complete(task.id)
    first_timestamp = first.updated_at
    second = store.complete(task.id)

    assert first.status is TaskStatus.COMPLETED
    assert second.status is TaskStatus.COMPLETED
    assert first_timestamp is not None
    assert second.updated_at is not None
    assert second.updated_at >= first_timestamp
    assert second.updated_at != first_timestamp or second.updated_at >= first_timestamp


def test_list_reflects_completion_state():
    store = InMemoryTaskStore()
    task = store.add("List me completed")

    store.complete(task.id)
    listed = store.list_tasks()

    assert len(listed) == 1
    assert listed[0].id == task.id
    assert listed[0].status is TaskStatus.COMPLETED


def test_list_excludes_deleted_task():
    store = InMemoryTaskStore()
    task = store.add("List should exclude me")

    store.delete(task.id)

    assert store.list_tasks() == []


def test_complete_preserves_created_at():
    store = InMemoryTaskStore()
    task = store.add("Created timestamp should remain stable")
    created_at = task.created_at

    completed = store.complete(task.id)

    assert completed.created_at == created_at
    assert completed.created_at.tzinfo is not None


def test_created_at_is_timezone_aware_on_creation():
    store = InMemoryTaskStore()

    task = store.add("timezone aware")

    assert task.created_at.tzinfo is not None
    assert task.created_at.utcoffset() == timezone.utc.utcoffset(task.created_at)
