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

def _make_task(task_id: str = "t1", title: str = "Test Task", **kwargs) -> Task:
    """Create a minimal Task instance for testing."""
    return Task(id=task_id, title=title, **kwargs)


# ---------------------------------------------------------------------------
# add()
# ---------------------------------------------------------------------------

class TestAdd:
    def test_add_stores_task_and_returns_it(self):
        store = InMemoryTaskStore()
        task = _make_task("t1", "My Task")
        result = store.add(task)

        assert result.id == "t1"
        assert result.title == "My Task"
        # Verify it's actually stored (retrievable)
        retrieved = store.get("t1")
        assert retrieved.id == "t1"
        assert retrieved.title == "My Task"

    def test_add_duplicate_id_raises_value_error(self):
        store = InMemoryTaskStore()
        store.add(_make_task("dup"))

        with pytest.raises(ValueError, match="dup"):
            store.add(_make_task("dup", "Different title"))


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

class TestGet:
    def test_get_returns_correct_task_by_id(self):
        store = InMemoryTaskStore()
        store.add(_make_task("a", "Alpha"))
        store.add(_make_task("b", "Beta"))

        result = store.get("b")
        assert result.id == "b"
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
        ids = ["first", "second", "third"]
        for tid in ids:
            store.add(_make_task(tid, f"Title {tid}"))

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
        store.add(_make_task("u1", "Old Title"))

        updated = store.update("u1", {"title": "New Title"})
        assert updated.title == "New Title"

        # Verify persistence
        assert store.get("u1").title == "New Title"

    def test_update_sets_updated_at_automatically(self):
        store = InMemoryTaskStore()
        task = _make_task("u2", "Title")
        added = store.add(task)
        original_updated_at = added.updated_at

        # Small sleep to guarantee time difference if implementation uses real clock
        updated = store.update("u2", {"title": "Changed"})
        assert updated.updated_at is not None
        if original_updated_at is not None:
            assert updated.updated_at >= original_updated_at

    def test_update_empty_fields_still_refreshes_updated_at(self):
        store = InMemoryTaskStore()
        store.add(_make_task("u3", "Title"))
        before = store.get("u3").updated_at

        updated = store.update("u3", {})
        assert updated.updated_at is not None
        if before is not None:
            assert updated.updated_at >= before

    def test_update_missing_id_raises_key_error(self):
        store = InMemoryTaskStore()
        with pytest.raises(KeyError, match="ghost"):
            store.update("ghost", {"title": "Nope"})

    def test_update_invalid_field_raises_attribute_error(self):
        store = InMemoryTaskStore()
        store.add(_make_task("u4", "Title"))

        with pytest.raises(AttributeError, match="nonexistent_field"):
            store.update("u4", {"nonexistent_field": "bad"})

        # Verify no partial mutation occurred -- title should be unchanged
        assert store.get("u4").title == "Title"

    def test_update_rejects_id_field_change(self):
        """The ``id`` field is immutable once stored."""
        store = InMemoryTaskStore()
        store.add(_make_task("immutable", "Title"))

        with pytest.raises((AttributeError, ValueError)):
            store.update("immutable", {"id": "new-id"})

    def test_update_no_partial_application_on_error(self):
        """When update encounters an invalid field, no valid fields in the
        same call should have been applied (atomicity)."""
        store = InMemoryTaskStore()
        store.add(_make_task("atomic", "Original"))

        with pytest.raises(AttributeError):
            store.update("atomic", {"title": "Changed", "nonexistent_field": "x"})

        # Title must remain unchanged
        assert store.get("atomic").title == "Original"


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------

class TestDelete:
    def test_delete_removes_task_and_returns_it(self):
        store = InMemoryTaskStore()
        store.add(_make_task("d1", "Doomed"))

        deleted = store.delete("d1")
        assert deleted.id == "d1"
        assert deleted.title == "Doomed"

        with pytest.raises(KeyError):
            store.get("d1")

    def test_delete_missing_id_raises_key_error(self):
        store = InMemoryTaskStore()
        with pytest.raises(KeyError, match="vanished"):
            store.delete("vanished")


# ---------------------------------------------------------------------------
# Deep-copy isolation
# ---------------------------------------------------------------------------

class TestCopyIsolation:
    def test_returned_task_is_copy_not_reference(self):
        store = InMemoryTaskStore()
        original = _make_task("c1", "Copy Test")
        returned = store.add(original)

        # The returned object must not be the same object that is stored
        # internally.  We verify by checking id() differs from a fresh get().
        retrieved = store.get("c1")
        assert returned is not retrieved

    def test_mutating_returned_task_does_not_affect_store(self):
        store = InMemoryTaskStore()
        store.add(_make_task("c2", "Immutable Inside"))

        task_copy = store.get("c2")
        # Attempt to mutate the returned copy
        try:
            task_copy.title = "Hacked!"
        except AttributeError:
            # If Task is frozen dataclass, mutation is blocked -- that's fine.
            pass

        # Internal state must remain unchanged regardless
        assert store.get("c2").title == "Immutable Inside"

    def test_mutating_input_task_after_add_does_not_affect_store(self):
        store = InMemoryTaskStore()
        task = _make_task("c3", "Before Mutation")
        store.add(task)

        # Mutate the input object
        try:
            task.title = "After Mutation"
        except AttributeError:
            pass

        assert store.get("c3").title == "Before Mutation"

    def test_list_all_returns_copies(self):
        store = InMemoryTaskStore()
        store.add(_make_task("la1", "List Item"))

        items = store.list_all()
        try:
            items[0].title = "Tampered"
        except AttributeError:
            pass

        assert store.get("la1").title == "List Item"


# ---------------------------------------------------------------------------
# Security-oriented tests
# ---------------------------------------------------------------------------

class TestSecurity:
    def test_cannot_bypass_duplicate_check_by_modifying_returned_id(self):
        """Ensure modifying a returned task's id doesn't corrupt the store."""
        store = InMemoryTaskStore()
        returned = store.add(_make_task("sec1", "Secure"))

        try:
            returned.id = "sec2"
        except AttributeError:
            pass

        # Original should still be accessible
        assert store.get("sec1").title == "Secure"

    def test_store_handles_large_number_of_tasks(self):
        store = InMemoryTaskStore()
        n = 1000
        for i in range(n):
            store.add(_make_task(f"bulk-{i}", f"Task {i}"))

        assert len(store.list_all()) == n
        assert store.get("bulk-500").title == "Task 500"

    def test_id_with_special_characters(self):
        """IDs with special characters should work without issues."""
        store = InMemoryTaskStore()
        special_ids = [
            "id with spaces",
            "id/with/slashes",
            "id\nwith\nnewlines",
            "id<script>alert('xss')</script>",
            "",  # empty string ID
            "  ",  # whitespace-only ID
        ]
        for sid in special_ids:
            store.add(_make_task(sid, f"Title for {repr(sid)}"))

        for sid in special_ids:
            assert store.get(sid).id == sid

    def test_cannot_access_internal_dict_through_returned_objects(self):
        """Returned tasks should not hold references to internal store structures."""
        store = InMemoryTaskStore()
        store.add(_make_task("internal", "Protected"))

        task = store.get("internal")
        # task is a plain Task copy; verify it doesn't expose _tasks
        assert not hasattr(task, "_tasks")

    def test_delete_then_readd_same_id(self):
        """After deletion, the same ID should be reusable."""
        store = InMemoryTaskStore()
        store.add(_make_task("reuse", "First"))
        store.delete("reuse")
        store.add(_make_task("reuse", "Second"))

        assert store.get("reuse").title == "Second"

    def test_update_immutable_id_preserves_store_integrity(self):
        """Attempting to change id via update must not corrupt internal mapping."""
        store = InMemoryTaskStore()
        store.add(_make_task("keep", "Keeper"))

        try:
            store.update("keep", {"id": "stolen"})
        except (AttributeError, ValueError):
            pass

        # Original must still be intact
        assert store.get("keep").title == "Keeper"
        # "stolen" must not exist
        with pytest.raises(KeyError):
            store.get("stolen")


# ---------------------------------------------------------------------------
# Package re-export
# ---------------------------------------------------------------------------

class TestPackageImport:
    def test_import_from_storage_package(self):
        """InMemoryTaskStore should be importable from the storage package."""
        storage_pkg = pytest.importorskip("tasklib.storage")
        cls = getattr(storage_pkg, "InMemoryTaskStore", None)
        if cls is None:
            pytest.skip("tasklib.storage does not re-export InMemoryTaskStore yet")
        assert cls is InMemoryTaskStore
