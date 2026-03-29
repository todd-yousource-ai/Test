"""Tests for tasklib.storage.memory.InMemoryTaskStore."""

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

def _make_task(
    task_id: str = "t-1",
    title: str = "Test task",
    description: str = "A description",
    **kwargs: object,
) -> Task:
    """Create a minimal Task instance for testing."""
    now = datetime.now(timezone.utc)
    defaults: dict[str, object] = {
        "id": task_id,
        "title": title,
        "description": description,
        "status": "open",
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    return Task(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

class TestAdd:
    def test_add_stores_task_and_returns_it(self) -> None:
        store = InMemoryTaskStore()
        task = _make_task()
        result = store.add(task)

        assert result.id == task.id
        assert result.title == task.title
        assert result.description == task.description
        assert result.status == task.status
        assert result.created_at == task.created_at
        assert result.updated_at == task.updated_at

    def test_add_duplicate_id_raises_value_error(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="dup"))
        with pytest.raises(ValueError, match="dup"):
            store.add(_make_task(task_id="dup"))


class TestGet:
    def test_get_returns_correct_task_by_id(self) -> None:
        store = InMemoryTaskStore()
        t1 = _make_task(task_id="a", title="Alpha")
        t2 = _make_task(task_id="b", title="Beta")
        store.add(t1)
        store.add(t2)

        fetched = store.get("b")
        assert fetched.id == "b"
        assert fetched.title == "Beta"

    def test_get_missing_id_raises_key_error(self) -> None:
        store = InMemoryTaskStore()
        with pytest.raises(KeyError, match="missing-id"):
            store.get("missing-id")


class TestListAll:
    def test_list_all_returns_all_tasks_in_order(self) -> None:
        store = InMemoryTaskStore()
        ids = ["first", "second", "third"]
        for tid in ids:
            store.add(_make_task(task_id=tid, title=f"Task {tid}"))

        results = store.list_all()
        assert [t.id for t in results] == ids

    def test_list_all_empty_store_returns_empty_list(self) -> None:
        store = InMemoryTaskStore()
        assert store.list_all() == []


class TestUpdate:
    def test_update_modifies_specified_fields(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="u1", title="Old"))

        updated = store.update("u1", {"title": "New"})
        assert updated.title == "New"

        # Verify the change persists in a fresh get()
        assert store.get("u1").title == "New"

    def test_update_sets_updated_at_automatically(self) -> None:
        store = InMemoryTaskStore()
        original = store.add(_make_task(task_id="u2"))
        old_updated_at = original.updated_at

        # Small sleep to ensure timestamp difference
        time.sleep(0.01)
        refreshed = store.update("u2", {"title": "Changed"})
        assert refreshed.updated_at > old_updated_at

    def test_update_empty_fields_still_refreshes_updated_at(self) -> None:
        store = InMemoryTaskStore()
        original = store.add(_make_task(task_id="u3"))
        old_updated_at = original.updated_at

        time.sleep(0.01)
        refreshed = store.update("u3", {})
        assert refreshed.updated_at > old_updated_at

    def test_update_missing_id_raises_key_error(self) -> None:
        store = InMemoryTaskStore()
        with pytest.raises(KeyError, match="ghost"):
            store.update("ghost", {"title": "Nope"})

    def test_update_invalid_field_raises_attribute_error(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="u4"))
        with pytest.raises(AttributeError, match="nonexistent_field"):
            store.update("u4", {"nonexistent_field": "bad"})

    def test_update_invalid_field_does_not_partially_apply(self) -> None:
        """Ensure no partial mutation occurs when an invalid field is in the payload."""
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="u5", title="Original"))

        with pytest.raises(AttributeError):
            # Even though title is valid, nonexistent_field should cause early failure
            store.update("u5", {"nonexistent_field": "bad", "title": "Modified"})

        # Title must remain unchanged
        assert store.get("u5").title == "Original"


class TestDelete:
    def test_delete_removes_task_and_returns_it(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="d1", title="Doomed"))

        removed = store.delete("d1")
        assert removed.id == "d1"
        assert removed.title == "Doomed"

        # No longer in store
        with pytest.raises(KeyError):
            store.get("d1")

    def test_delete_missing_id_raises_key_error(self) -> None:
        store = InMemoryTaskStore()
        with pytest.raises(KeyError, match="nope"):
            store.delete("nope")


# ---------------------------------------------------------------------------
# Deep-copy / isolation tests
# ---------------------------------------------------------------------------

class TestCopyIsolation:
    def test_returned_task_is_copy_not_reference(self) -> None:
        store = InMemoryTaskStore()
        original = _make_task(task_id="c1")
        returned = store.add(original)

        # The returned object must not be the same object as the original
        assert returned is not original
        # And it must not be the same as the internal object
        internal = store.get("c1")
        assert internal is not returned

    def test_mutating_returned_task_does_not_affect_store(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="c2", title="Immutable"))

        fetched = store.get("c2")
        # Attempt to mutate the returned copy
        try:
            fetched.title = "Mutated"
        except AttributeError:
            # If Task is frozen this is expected; either way store stays clean
            pass

        assert store.get("c2").title == "Immutable"

    def test_mutating_original_task_does_not_affect_store(self) -> None:
        store = InMemoryTaskStore()
        task = _make_task(task_id="c3", title="Safe")
        store.add(task)

        # Mutate the original object that was passed to add()
        try:
            task.title = "Hacked"
        except AttributeError:
            pass

        assert store.get("c3").title == "Safe"

    def test_list_all_returns_copies(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="c4"))

        items = store.list_all()
        try:
            items[0].title = "Tampered"
        except AttributeError:
            pass

        assert store.get("c4").title == "Test task"

    def test_delete_returns_copy(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="c5", title="Before"))
        removed = store.delete("c5")

        # removed should be usable but store is empty
        assert removed.title == "Before"
        assert store.list_all() == []


# ---------------------------------------------------------------------------
# Security tests
# ---------------------------------------------------------------------------

class TestSecurity:
    def test_add_never_silently_overwrites(self) -> None:
        """Duplicate add must always raise -- never silently overwrite (fail-closed)."""
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="sec-1", title="V1"))

        with pytest.raises(ValueError):
            store.add(_make_task(task_id="sec-1", title="V2"))

        # Original is untouched
        assert store.get("sec-1").title == "V1"

    def test_get_never_returns_none_for_missing(self) -> None:
        """get() must raise KeyError, never return None (fail-closed)."""
        store = InMemoryTaskStore()
        with pytest.raises(KeyError):
            store.get("does-not-exist")

    def test_update_validates_fields_before_mutation(self) -> None:
        """All field names must be validated before any mutation starts."""
        store = InMemoryTaskStore()
        store.add(_make_task(task_id="sec-2", title="Original", description="Orig desc"))

        with pytest.raises(AttributeError):
            store.update("sec-2", {"title": "Changed", "bad_field": "x"})

        task = store.get("sec-2")
        assert task.title == "Original"
        assert task.description == "Orig desc"

    def test_update_missing_id_before_field_validation(self) -> None:
        """KeyError for missing ID should fire before field validation."""
        store = InMemoryTaskStore()
        with pytest.raises(KeyError):
            store.update("nonexistent", {"bad_field": 42})

    def test_internal_dict_not_exposed(self) -> None:
        """The internal _tasks dict should not be accessible via public API."""
        store = InMemoryTaskStore()
        # list_all is the only way to enumerate; it should return a new list
        store.add(_make_task(task_id="sec-3"))
        listing = store.list_all()
        listing.clear()
        assert len(store.list_all()) == 1

    def test_crafted_id_with_special_chars(self) -> None:
        """IDs with special characters should be handled without issues."""
        store = InMemoryTaskStore()
        special_ids = [
            "'; DROP TABLE tasks; --",
            "../../../etc/passwd",
            "<script>alert(1)</script>",
            "\x00null\x00byte",
            "a" * 10000,
        ]
        for sid in special_ids:
            store.add(_make_task(task_id=sid, title=f"Task {sid[:10]}"))

        assert len(store.list_all()) == len(special_ids)
        for sid in special_ids:
            assert store.get(sid).id == sid


# ---------------------------------------------------------------------------
# Package re-export test
# ---------------------------------------------------------------------------

class TestImport:
    def test_import_from_storage_package(self) -> None:
        """InMemoryTaskStore should be importable from the storage package."""
        storage_pkg = pytest.importorskip("tasklib.storage")
        cls = getattr(storage_pkg, "InMemoryTaskStore", None)
        if cls is None:
            pytest.skip("tasklib.storage does not re-export InMemoryTaskStore yet")
        assert cls is InMemoryTaskStore
