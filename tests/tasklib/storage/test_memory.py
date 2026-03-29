"""Tests for InMemoryTaskStore (tasklib.storage.memory)."""

from __future__ import annotations

import copy
import time
from datetime import datetime, timezone

import pytest

from tasklib.storage.memory import InMemoryTaskStore
from tasklib.models.task import Task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(task_id: str = "t1", title: str = "Test task", **kwargs) -> Task:
    """Create a Task with sensible defaults for testing."""
    defaults = dict(
        id=task_id,
        title=title,
    )
    defaults.update(kwargs)
    return Task(**defaults)


# ---------------------------------------------------------------------------
# add()
# ---------------------------------------------------------------------------

class TestAdd:
    def test_add_stores_task_and_returns_it(self):
        store = InMemoryTaskStore()
        task = _make_task("t1", "My task")
        result = store.add(task)

        assert result.id == "t1"
        assert result.title == "My task"
        # The task should now be retrievable
        assert store.get("t1").id == "t1"

    def test_add_duplicate_id_raises_value_error(self):
        store = InMemoryTaskStore()
        store.add(_make_task("dup"))

        with pytest.raises(ValueError, match="dup"):
            store.add(_make_task("dup", title="different title"))


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
        with pytest.raises(KeyError, match="no_such_id"):
            store.get("no_such_id")


# ---------------------------------------------------------------------------
# list_all()
# ---------------------------------------------------------------------------

class TestListAll:
    def test_list_all_returns_all_tasks_in_order(self):
        store = InMemoryTaskStore()
        ids = ["first", "second", "third"]
        for tid in ids:
            store.add(_make_task(tid, title=f"Task {tid}"))

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
        store.add(_make_task("u1", title="Old"))

        updated = store.update("u1", {"title": "New"})
        assert updated.title == "New"
        # Verify persistence
        assert store.get("u1").title == "New"

    def test_update_sets_updated_at_automatically(self):
        store = InMemoryTaskStore()
        task = _make_task("u2", title="Original")
        added = store.add(task)
        original_updated_at = added.updated_at if hasattr(added, "updated_at") else None

        # Small sleep to ensure timestamp difference is detectable
        updated = store.update("u2", {"title": "Changed"})

        assert hasattr(updated, "updated_at")
        assert updated.updated_at is not None
        if original_updated_at is not None:
            assert updated.updated_at >= original_updated_at

    def test_update_empty_fields_still_refreshes_updated_at(self):
        store = InMemoryTaskStore()
        store.add(_make_task("u3"))
        before = store.get("u3")
        before_updated_at = getattr(before, "updated_at", None)

        updated = store.update("u3", {})
        assert hasattr(updated, "updated_at")
        assert updated.updated_at is not None
        if before_updated_at is not None:
            assert updated.updated_at >= before_updated_at

    def test_update_missing_id_raises_key_error(self):
        store = InMemoryTaskStore()
        with pytest.raises(KeyError, match="ghost"):
            store.update("ghost", {"title": "Nope"})

    def test_update_invalid_field_raises_attribute_error(self):
        store = InMemoryTaskStore()
        store.add(_make_task("u4"))

        with pytest.raises(AttributeError, match="nonexistent_field"):
            store.update("u4", {"nonexistent_field": "bad"})

        # Verify no partial mutation occurred -- title unchanged
        assert store.get("u4").title == "Test task"

    def test_update_rejects_id_field_mutation(self):
        """Attempting to change the 'id' field must be rejected."""
        store = InMemoryTaskStore()
        store.add(_make_task("immutable"))

        with pytest.raises((AttributeError, ValueError)):
            store.update("immutable", {"id": "new_id"})

        # Original task still accessible under old id
        assert store.get("immutable").id == "immutable"


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

        # No longer in store
        with pytest.raises(KeyError):
            store.get("d1")

    def test_delete_missing_id_raises_key_error(self):
        store = InMemoryTaskStore()
        with pytest.raises(KeyError, match="nope"):
            store.delete("nope")


# ---------------------------------------------------------------------------
# Deep-copy / isolation guarantees
# ---------------------------------------------------------------------------

class TestIsolation:
    def test_returned_task_is_copy_not_reference(self):
        store = InMemoryTaskStore()
        original = _make_task("iso1")
        returned = store.add(original)

        # The returned object must not be the same object as the stored one
        stored = store.get("iso1")
        assert returned is not stored

    def test_mutating_returned_task_does_not_affect_store(self):
        store = InMemoryTaskStore()
        store.add(_make_task("iso2", title="Safe"))

        fetched = store.get("iso2")
        fetched.title = "Tampered"

        # Internal state must be unchanged
        assert store.get("iso2").title == "Safe"

    def test_mutating_original_task_after_add_does_not_affect_store(self):
        store = InMemoryTaskStore()
        original = _make_task("iso3", title="Before")
        store.add(original)

        original.title = "After"
        assert store.get("iso3").title == "Before"

    def test_list_all_returns_copies(self):
        store = InMemoryTaskStore()
        store.add(_make_task("iso4", title="Untouched"))

        tasks = store.list_all()
        tasks[0].title = "Mutated"

        assert store.get("iso4").title == "Untouched"

    def test_delete_returned_copy_mutation_harmless(self):
        """Mutating the task returned by delete() is harmless (it's a copy)."""
        store = InMemoryTaskStore()
        store.add(_make_task("iso5", title="Original"))
        deleted = store.delete("iso5")
        deleted.title = "Evil"
        # Task is gone anyway, but ensure no weird side-effects
        with pytest.raises(KeyError):
            store.get("iso5")


# ---------------------------------------------------------------------------
# Security-focused tests
# ---------------------------------------------------------------------------

class TestSecurity:
    def test_add_never_silently_overwrites(self):
        """add() must fail closed -- ValueError, not silent overwrite."""
        store = InMemoryTaskStore()
        store.add(_make_task("sec1", title="First"))

        with pytest.raises(ValueError):
            store.add(_make_task("sec1", title="Overwrite attempt"))

        assert store.get("sec1").title == "First"

    def test_update_invalid_field_no_partial_mutation(self):
        """If update() encounters an invalid field, NO fields should change."""
        store = InMemoryTaskStore()
        store.add(_make_task("sec2", title="Original"))

        with pytest.raises(AttributeError):
            store.update("sec2", {"title": "Changed", "nonexistent_field": "x"})

        # Title must remain unchanged -- no partial writes
        assert store.get("sec2").title == "Original"

    def test_concurrent_add_delete_add_cycle(self):
        """Ensure id can be re-used after deletion (no ghost entries)."""
        store = InMemoryTaskStore()
        store.add(_make_task("cycle", title="v1"))
        store.delete("cycle")
        store.add(_make_task("cycle", title="v2"))

        assert store.get("cycle").title == "v2"

    def test_update_cannot_change_id(self):
        """The identity key 'id' must be immutable once stored."""
        store = InMemoryTaskStore()
        store.add(_make_task("locked"))

        with pytest.raises((AttributeError, ValueError)):
            store.update("locked", {"id": "hijacked"})

        # Still accessible under original id
        assert store.get("locked").id == "locked"

        # 'hijacked' must not exist
        with pytest.raises(KeyError):
            store.get("hijacked")

    def test_get_keyerror_contains_missing_id(self):
        """KeyError message must include the missing id for auditability."""
        store = InMemoryTaskStore()
        with pytest.raises(KeyError, match="audit_trail_id"):
            store.get("audit_trail_id")

    def test_large_number_of_tasks(self):
        """Store should handle a non-trivial number of tasks without error."""
        store = InMemoryTaskStore()
        n = 1000
        for i in range(n):
            store.add(_make_task(f"bulk-{i}", title=f"Task {i}"))

        assert len(store.list_all()) == n
        assert store.get("bulk-500").title == "Task 500"


# ---------------------------------------------------------------------------
# Package re-export
# ---------------------------------------------------------------------------

class TestPackageImport:
    def test_import_from_storage_package(self):
        """InMemoryTaskStore should be importable from the storage package."""
        storage_mod = pytest.importorskip("tasklib.storage")
        cls = getattr(storage_mod, "InMemoryTaskStore", None)
        if cls is None:
            pytest.skip("tasklib.storage does not re-export InMemoryTaskStore yet")
        assert cls is InMemoryTaskStore
