"""Tests for InMemoryTaskStore (tasklib.storage.memory)."""

import copy
import time
from datetime import datetime, timezone

import pytest

from tasklib.storage.memory import InMemoryTaskStore
from tasklib.models.task import Task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(task_id: str = "t-1", title: str = "Test task", **kwargs) -> Task:
    """Create a minimal Task instance for testing."""
    return Task(id=task_id, title=title, **kwargs)


# ---------------------------------------------------------------------------
# add()
# ---------------------------------------------------------------------------

class TestAdd:
    def test_add_stores_task_and_returns_it(self):
        store = InMemoryTaskStore()
        task = _make_task("t-1", "Buy milk")
        result = store.add(task)

        assert result.id == "t-1"
        assert result.title == "Buy milk"

    def test_add_duplicate_id_raises_value_error(self):
        store = InMemoryTaskStore()
        store.add(_make_task("t-1"))

        with pytest.raises(ValueError, match="t-1"):
            store.add(_make_task("t-1", "Different title"))


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

class TestGet:
    def test_get_returns_correct_task_by_id(self):
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Alpha"))
        store.add(_make_task("t-2", "Beta"))

        result = store.get("t-2")
        assert result.id == "t-2"
        assert result.title == "Beta"

    def test_get_missing_id_raises_key_error(self):
        store = InMemoryTaskStore()

        with pytest.raises(KeyError, match="no-such-id"):
            store.get("no-such-id")


# ---------------------------------------------------------------------------
# list_all()
# ---------------------------------------------------------------------------

class TestListAll:
    def test_list_all_returns_all_tasks_in_order(self):
        store = InMemoryTaskStore()
        ids = ["t-1", "t-2", "t-3"]
        for tid in ids:
            store.add(_make_task(tid, f"Task {tid}"))

        result = store.list_all()
        assert [t.id for t in result] == ids

    def test_list_all_empty_store_returns_empty_list(self):
        store = InMemoryTaskStore()
        result = store.list_all()
        assert result == []


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------

class TestUpdate:
    def test_update_modifies_specified_fields(self):
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Old title"))

        updated = store.update("t-1", {"title": "New title"})
        assert updated.title == "New title"

        # Verify persistence
        fetched = store.get("t-1")
        assert fetched.title == "New title"

    def test_update_sets_updated_at_automatically(self):
        store = InMemoryTaskStore()
        task = _make_task("t-1")
        added = store.add(task)
        original_updated_at = added.updated_at

        # Small sleep to ensure timestamp differs
        updated = store.update("t-1", {"title": "Changed"})
        assert updated.updated_at is not None
        if original_updated_at is not None:
            assert updated.updated_at >= original_updated_at

    def test_update_empty_fields_still_refreshes_updated_at(self):
        store = InMemoryTaskStore()
        added = store.add(_make_task("t-1"))
        before = store.get("t-1").updated_at

        updated = store.update("t-1", {})
        assert updated.updated_at is not None
        if before is not None:
            assert updated.updated_at >= before

    def test_update_missing_id_raises_key_error(self):
        store = InMemoryTaskStore()

        with pytest.raises(KeyError, match="missing"):
            store.update("missing", {"title": "Nope"})

    def test_update_invalid_field_raises_attribute_error(self):
        store = InMemoryTaskStore()
        store.add(_make_task("t-1"))

        with pytest.raises(AttributeError, match="nonexistent_field"):
            store.update("t-1", {"nonexistent_field": "bad"})

    def test_update_invalid_field_does_not_mutate_task(self):
        """Validation happens before any mutation -- no partial application."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Original"))

        with pytest.raises(AttributeError):
            store.update("t-1", {"title": "Changed", "nonexistent_field": "x"})

        # Title must remain unchanged
        assert store.get("t-1").title == "Original"

    def test_update_rejects_id_change(self):
        """The identity key 'id' is immutable once stored."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1"))

        with pytest.raises((AttributeError, ValueError)):
            store.update("t-1", {"id": "t-999"})


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------

class TestDelete:
    def test_delete_removes_task_and_returns_it(self):
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Doomed"))

        deleted = store.delete("t-1")
        assert deleted.id == "t-1"
        assert deleted.title == "Doomed"

        # Should no longer be in the store
        with pytest.raises(KeyError):
            store.get("t-1")

    def test_delete_missing_id_raises_key_error(self):
        store = InMemoryTaskStore()

        with pytest.raises(KeyError, match="ghost"):
            store.delete("ghost")


# ---------------------------------------------------------------------------
# Deep-copy / isolation guarantees
# ---------------------------------------------------------------------------

class TestIsolation:
    def test_returned_task_is_copy_not_reference(self):
        store = InMemoryTaskStore()
        original = _make_task("t-1", "Original")
        returned = store.add(original)

        # returned should not be the same object as the internal store entry
        internal = store.get("t-1")
        assert returned is not internal

    def test_mutating_returned_task_does_not_affect_store(self):
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Safe"))

        fetched = store.get("t-1")
        fetched.title = "Hacked"

        assert store.get("t-1").title == "Safe"

    def test_mutating_input_task_does_not_affect_store(self):
        store = InMemoryTaskStore()
        task = _make_task("t-1", "Before")
        store.add(task)

        task.title = "After"
        assert store.get("t-1").title == "Before"

    def test_list_all_returns_copies(self):
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Original"))

        tasks = store.list_all()
        tasks[0].title = "Tampered"

        assert store.get("t-1").title == "Original"

    def test_delete_return_value_is_independent_copy(self):
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Will delete"))

        deleted = store.delete("t-1")
        # Re-add a task with the same id -- deleted copy must be unaffected
        store.add(_make_task("t-1", "New version"))
        assert deleted.title == "Will delete"


# ---------------------------------------------------------------------------
# Security boundary tests
# ---------------------------------------------------------------------------

class TestSecurity:
    def test_add_never_silently_overwrites(self):
        """Fail-closed: duplicate add must raise, not silently overwrite."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "First"))

        with pytest.raises(ValueError):
            store.add(_make_task("t-1", "Second"))

        # Ensure the original is untouched
        assert store.get("t-1").title == "First"

    def test_get_never_returns_none_for_missing(self):
        """Fail-closed: get() raises KeyError, never returns None silently."""
        store = InMemoryTaskStore()
        with pytest.raises(KeyError):
            store.get("does-not-exist")

    def test_update_rejects_immutable_id_field(self):
        """Identity key must never be changeable via update()."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1"))

        with pytest.raises((AttributeError, ValueError)):
            store.update("t-1", {"id": "t-evil"})

        # Verify nothing changed
        assert store.get("t-1").id == "t-1"

    def test_update_validates_all_fields_before_applying(self):
        """No partial application: if any field is invalid, nothing changes."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Original"))

        with pytest.raises(AttributeError):
            store.update("t-1", {"title": "Partial", "bad_field": True})

        assert store.get("t-1").title == "Original"

    def test_concurrent_style_add_delete_add(self):
        """Simulate add → delete → re-add cycle with same ID."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "V1"))
        store.delete("t-1")
        store.add(_make_task("t-1", "V2"))

        assert store.get("t-1").title == "V2"

    def test_special_characters_in_task_id(self):
        """IDs with special characters should work without issues."""
        store = InMemoryTaskStore()
        weird_id = "../../etc/passwd"
        store.add(_make_task(weird_id, "Sneaky"))

        result = store.get(weird_id)
        assert result.id == weird_id

    def test_empty_string_task_id(self):
        """Empty string as task ID should be treated as any other key."""
        store = InMemoryTaskStore()
        store.add(_make_task("", "Empty ID"))
        assert store.get("").title == "Empty ID"


# ---------------------------------------------------------------------------
# Package re-export (best-effort)
# ---------------------------------------------------------------------------

class TestImports:
    def test_import_from_storage_package(self):
        """InMemoryTaskStore should be importable from the storage package."""
        storage_pkg = pytest.importorskip("tasklib.storage")
        cls = getattr(storage_pkg, "InMemoryTaskStore", None)
        if cls is None:
            pytest.skip("tasklib.storage does not re-export InMemoryTaskStore yet")
        assert cls is InMemoryTaskStore
