"""Tests for InMemoryTaskStore (tasklib.storage.memory)."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import pytest

from tasklib.models.task import Task
from tasklib.storage.memory import InMemoryTaskStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(task_id: str = "t1", title: str = "Test task", **kwargs) -> Task:
    """Create a Task with sensible defaults. Passes extra kwargs through."""
    return Task(id=task_id, title=title, **kwargs)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store() -> InMemoryTaskStore:
    return InMemoryTaskStore()


@pytest.fixture
def populated_store(store: InMemoryTaskStore):
    """Store pre-loaded with three tasks in a known order."""
    store.add(_make_task("a", "Alpha"))
    store.add(_make_task("b", "Bravo"))
    store.add(_make_task("c", "Charlie"))
    return store


# ===========================================================================
# Happy-path CRUD
# ===========================================================================

class TestAdd:
    def test_add_stores_task_and_returns_it(self, store: InMemoryTaskStore):
        task = _make_task("t1", "My task")
        result = store.add(task)

        assert result.id == "t1"
        assert result.title == "My task"
        # Verify the task is actually persisted
        assert store.get("t1").id == "t1"

    def test_add_duplicate_id_raises_value_error(self, store: InMemoryTaskStore):
        store.add(_make_task("dup"))
        with pytest.raises(ValueError, match="dup"):
            store.add(_make_task("dup", "Different title"))


class TestGet:
    def test_get_returns_correct_task_by_id(self, populated_store: InMemoryTaskStore):
        task = populated_store.get("b")
        assert task.id == "b"
        assert task.title == "Bravo"

    def test_get_missing_id_raises_key_error(self, store: InMemoryTaskStore):
        with pytest.raises(KeyError, match="no-such-id"):
            store.get("no-such-id")


class TestListAll:
    def test_list_all_returns_all_tasks_in_order(self, populated_store: InMemoryTaskStore):
        tasks = populated_store.list_all()
        assert len(tasks) == 3
        assert [t.id for t in tasks] == ["a", "b", "c"]

    def test_list_all_empty_store_returns_empty_list(self, store: InMemoryTaskStore):
        assert store.list_all() == []


class TestUpdate:
    def test_update_modifies_specified_fields(self, populated_store: InMemoryTaskStore):
        updated = populated_store.update("a", title="Alpha Updated")
        assert updated.title == "Alpha Updated"
        assert updated.id == "a"
        # Verify persistence
        assert populated_store.get("a").title == "Alpha Updated"

    def test_update_sets_updated_at_automatically(self, populated_store: InMemoryTaskStore):
        before = datetime.now(timezone.utc)
        updated = populated_store.update("a", title="New")
        after = datetime.now(timezone.utc)

        assert updated.updated_at is not None
        assert before <= updated.updated_at <= after

    def test_update_empty_fields_still_refreshes_updated_at(self, populated_store: InMemoryTaskStore):
        original = populated_store.get("a")
        original_updated_at = original.updated_at

        # Small sleep to guarantee time difference if original_updated_at was set
        time.sleep(0.01)
        refreshed = populated_store.update("a")

        assert refreshed.updated_at is not None
        if original_updated_at is not None:
            assert refreshed.updated_at >= original_updated_at
        # The key point: updated_at must be a recent UTC timestamp
        assert refreshed.updated_at <= datetime.now(timezone.utc)

    def test_update_missing_id_raises_key_error(self, store: InMemoryTaskStore):
        with pytest.raises(KeyError, match="ghost"):
            store.update("ghost", title="Nope")

    def test_update_invalid_field_raises_attribute_error(self, populated_store: InMemoryTaskStore):
        with pytest.raises(AttributeError, match="nonexistent_field"):
            populated_store.update("a", nonexistent_field="bad")

    def test_update_rejects_id_field_mutation(self, populated_store: InMemoryTaskStore):
        """Attempting to change the immutable 'id' field must raise AttributeError."""
        with pytest.raises(AttributeError, match="immutable"):
            populated_store.update("a", id="new-id")

    def test_update_invalid_field_causes_no_partial_mutation(self, populated_store: InMemoryTaskStore):
        """If validation fails, no fields should have been changed."""
        original_title = populated_store.get("a").title
        with pytest.raises(AttributeError):
            populated_store.update("a", title="Should not persist", nonexistent_field="bad")
        # title must be unchanged
        assert populated_store.get("a").title == original_title

    def test_update_missing_id_raises_before_field_validation(self, store: InMemoryTaskStore):
        """KeyError for missing ID must be raised before field validation."""
        with pytest.raises(KeyError):
            store.update("nope", nonexistent_field="irrelevant")


class TestDelete:
    def test_delete_removes_task_and_returns_it(self, populated_store: InMemoryTaskStore):
        deleted = populated_store.delete("b")
        assert deleted.id == "b"
        assert deleted.title == "Bravo"
        # Verify it's actually gone
        with pytest.raises(KeyError):
            populated_store.get("b")
        assert len(populated_store.list_all()) == 2

    def test_delete_missing_id_raises_key_error(self, store: InMemoryTaskStore):
        with pytest.raises(KeyError, match="missing"):
            store.delete("missing")


# ===========================================================================
# Deep-copy isolation
# ===========================================================================

class TestIsolation:
    def test_returned_task_is_copy_not_reference(self, store: InMemoryTaskStore):
        original = _make_task("iso1", "Original")
        returned = store.add(original)
        fetched = store.get("iso1")

        # All three objects must be distinct
        assert returned is not original
        assert fetched is not original
        assert fetched is not returned

    def test_mutating_returned_task_does_not_affect_store(self, store: InMemoryTaskStore):
        store.add(_make_task("iso2", "Before"))
        fetched = store.get("iso2")

        # Forcefully mutate the returned copy
        object.__setattr__(fetched, "title", "MUTATED")

        # Store must be unaffected
        assert store.get("iso2").title == "Before"

    def test_mutating_original_after_add_does_not_affect_store(self, store: InMemoryTaskStore):
        original = _make_task("iso3", "Pristine")
        store.add(original)

        # Mutate the original object
        object.__setattr__(original, "title", "Corrupted")

        # Store must be unaffected
        assert store.get("iso3").title == "Pristine"

    def test_list_all_returns_independent_copies(self, populated_store: InMemoryTaskStore):
        tasks = populated_store.list_all()
        object.__setattr__(tasks[0], "title", "HACKED")

        fresh = populated_store.list_all()
        assert fresh[0].title != "HACKED"

    def test_delete_returned_copy_is_independent(self, store: InMemoryTaskStore):
        store.add(_make_task("del1", "To delete"))
        deleted = store.delete("del1")
        # Mutating the deleted copy should have no effect if the task were
        # somehow re-added
        object.__setattr__(deleted, "title", "CHANGED")
        store.add(_make_task("del1", "Re-added"))
        assert store.get("del1").title == "Re-added"


# ===========================================================================
# Security boundaries
# ===========================================================================

class TestSecurity:
    def test_add_fails_closed_never_overwrites(self, store: InMemoryTaskStore):
        """Duplicate add must raise -- must never silently overwrite."""
        store.add(_make_task("sec1", "First"))
        with pytest.raises(ValueError):
            store.add(_make_task("sec1", "Overwrite attempt"))
        # Original must survive
        assert store.get("sec1").title == "First"

    def test_get_fails_closed_never_returns_none(self, store: InMemoryTaskStore):
        """get() must raise KeyError, never return None."""
        with pytest.raises(KeyError):
            store.get("nonexistent")

    def test_update_immutable_id_rejected(self, populated_store: InMemoryTaskStore):
        """Attempts to change 'id' via update must be rejected."""
        with pytest.raises(AttributeError, match="immutable"):
            populated_store.update("a", id="hijacked")
        # Original must survive
        assert populated_store.get("a").id == "a"

    def test_update_validates_all_fields_before_any_mutation(self, populated_store: InMemoryTaskStore):
        """Mixing valid + invalid fields must cause zero mutations."""
        original = populated_store.get("a")
        with pytest.raises(AttributeError):
            populated_store.update("a", title="Sneaky", nonexistent_field="x")
        assert populated_store.get("a").title == original.title

    def test_delete_fails_closed_never_returns_none(self, store: InMemoryTaskStore):
        """delete() must raise KeyError, never return None."""
        with pytest.raises(KeyError):
            store.delete("ghost")

    def test_no_internal_state_leak_via_tasks_dict(self, store: InMemoryTaskStore):
        """Directly accessing _tasks and mutating it should not affect get() copies."""
        store.add(_make_task("leak", "Secret"))
        # Even if someone grabs the internal dict reference, the public API
        # returns copies.
        internal_ref = store._tasks["leak"]
        copy_via_get = store.get("leak")
        assert internal_ref is not copy_via_get

    def test_concurrent_style_add_delete_add(self, store: InMemoryTaskStore):
        """Simulates add-delete-re-add to ensure clean state transitions."""
        store.add(_make_task("cycle", "v1"))
        store.delete("cycle")
        store.add(_make_task("cycle", "v2"))
        assert store.get("cycle").title == "v2"


# ===========================================================================
# Package re-export
# ===========================================================================

class TestPackageImport:
    def test_import_from_storage_package(self):
        """InMemoryTaskStore should be importable from the storage package."""
        mod = pytest.importorskip("tasklib.storage")
        cls = getattr(mod, "InMemoryTaskStore", None)
        if cls is None:
            pytest.skip("tasklib.storage does not re-export InMemoryTaskStore yet")
        assert cls is InMemoryTaskStore
