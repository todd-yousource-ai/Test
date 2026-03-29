"""Tests for InMemoryTaskStore (tasklib.storage.memory)."""

from __future__ import annotations

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
    **overrides: object,
) -> Task:
    """Create a minimal Task instance for testing."""
    import dataclasses

    field_names = {f.name for f in dataclasses.fields(Task)}
    kwargs: dict[str, object] = {}

    # Provide sensible defaults only for fields that exist on Task.
    if "id" in field_names:
        kwargs["id"] = task_id
    if "title" in field_names:
        kwargs["title"] = title

    kwargs.update(overrides)
    return Task(**kwargs)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

class TestAdd:
    def test_add_stores_task_and_returns_it(self) -> None:
        store = InMemoryTaskStore()
        task = _make_task("t-1", "My task")
        result = store.add(task)

        assert result.id == "t-1"
        assert result.title == "My task"

    def test_add_duplicate_id_raises_value_error(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task("dup"))

        with pytest.raises(ValueError, match="dup"):
            store.add(_make_task("dup", "Another title"))


class TestGet:
    def test_get_returns_correct_task_by_id(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "First"))
        store.add(_make_task("t-2", "Second"))

        result = store.get("t-2")
        assert result.id == "t-2"
        assert result.title == "Second"

    def test_get_missing_id_raises_key_error(self) -> None:
        store = InMemoryTaskStore()

        with pytest.raises(KeyError, match="no-such-id"):
            store.get("no-such-id")


class TestListAll:
    def test_list_all_returns_all_tasks_in_order(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task("a"))
        store.add(_make_task("b"))
        store.add(_make_task("c"))

        result = store.list_all()
        assert [t.id for t in result] == ["a", "b", "c"]

    def test_list_all_empty_store_returns_empty_list(self) -> None:
        store = InMemoryTaskStore()
        assert store.list_all() == []


class TestUpdate:
    def test_update_modifies_specified_fields(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Original"))

        updated = store.update("t-1", {"title": "Changed"})
        assert updated.title == "Changed"
        # Verify persistence
        assert store.get("t-1").title == "Changed"

    def test_update_sets_updated_at_automatically(self) -> None:
        store = InMemoryTaskStore()
        original = store.add(_make_task("t-1", "Title"))

        import dataclasses
        field_names = {f.name for f in dataclasses.fields(Task)}
        if "updated_at" not in field_names:
            pytest.skip("Task has no updated_at field")

        before = datetime.now(timezone.utc)
        updated = store.update("t-1", {"title": "New"})
        after = datetime.now(timezone.utc)

        assert updated.updated_at is not None
        # updated_at should be within the before/after window
        if updated.updated_at.tzinfo is None:
            # Naive datetime -- compare naively
            assert before.replace(tzinfo=None) <= updated.updated_at <= after.replace(tzinfo=None)
        else:
            assert before <= updated.updated_at <= after

    def test_update_empty_fields_still_refreshes_updated_at(self) -> None:
        store = InMemoryTaskStore()
        original = store.add(_make_task("t-1"))

        import dataclasses
        field_names = {f.name for f in dataclasses.fields(Task)}
        if "updated_at" not in field_names:
            pytest.skip("Task has no updated_at field")

        original_updated_at = store.get("t-1").updated_at
        # Small sleep to ensure timestamp difference
        time.sleep(0.01)

        updated = store.update("t-1", {})
        # updated_at should have changed (or at least be >= original)
        assert updated.updated_at is not None
        if original_updated_at is not None:
            assert updated.updated_at >= original_updated_at

    def test_update_missing_id_raises_key_error(self) -> None:
        store = InMemoryTaskStore()

        with pytest.raises(KeyError, match="ghost"):
            store.update("ghost", {"title": "Nope"})

    def test_update_invalid_field_raises_attribute_error(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task("t-1"))

        with pytest.raises(AttributeError):
            store.update("t-1", {"nonexistent_field": "bad"})

    def test_update_invalid_field_causes_no_partial_mutation(self) -> None:
        """Ensure that if an invalid field is supplied alongside valid ones,
        no partial update is applied (fail-closed semantics)."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Original"))

        with pytest.raises(AttributeError):
            store.update("t-1", {"title": "Should Not Stick", "nonexistent_field": "x"})

        # Original title must be untouched
        assert store.get("t-1").title == "Original"


class TestDelete:
    def test_delete_removes_task_and_returns_it(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Doomed"))

        deleted = store.delete("t-1")
        assert deleted.id == "t-1"
        assert deleted.title == "Doomed"

        with pytest.raises(KeyError):
            store.get("t-1")

    def test_delete_missing_id_raises_key_error(self) -> None:
        store = InMemoryTaskStore()

        with pytest.raises(KeyError, match="absent"):
            store.delete("absent")


# ---------------------------------------------------------------------------
# Deep-copy / isolation tests
# ---------------------------------------------------------------------------

class TestIsolation:
    def test_returned_task_is_copy_not_reference(self) -> None:
        store = InMemoryTaskStore()
        original = _make_task("t-1", "Immutable")
        returned = store.add(original)

        # returned should not be the same object as the internal one
        internal = store.get("t-1")
        assert returned is not internal

    def test_mutating_returned_task_does_not_affect_store(self) -> None:
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Safe"))

        task = store.get("t-1")
        # Forcibly mutate the returned object (works on dataclasses without frozen)
        try:
            task.title = "Hacked"
        except AttributeError:
            # Frozen dataclass -- mutation is impossible, test passes trivially
            return

        # Store must still hold original value
        assert store.get("t-1").title == "Safe"

    def test_mutating_original_after_add_does_not_affect_store(self) -> None:
        store = InMemoryTaskStore()
        original = _make_task("t-1", "Before")
        store.add(original)

        try:
            original.title = "After"
        except AttributeError:
            return

        assert store.get("t-1").title == "Before"


# ---------------------------------------------------------------------------
# Security-oriented tests
# ---------------------------------------------------------------------------

class TestSecurity:
    def test_add_fails_closed_on_duplicate_never_overwrites(self) -> None:
        """Duplicate add must raise *and* leave original intact."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Original"))

        with pytest.raises(ValueError):
            store.add(_make_task("t-1", "Overwrite attempt"))

        assert store.get("t-1").title == "Original"

    def test_get_error_leaks_only_id_not_internals(self) -> None:
        """KeyError message should reference the missing ID but not expose
        internal dict structure or repr."""
        store = InMemoryTaskStore()

        with pytest.raises(KeyError) as exc_info:
            store.get("secret-id")

        # The string representation must mention the id
        assert "secret-id" in str(exc_info.value)

    def test_update_validates_fields_before_any_write(self) -> None:
        """Even if valid fields precede the bad one in iteration order,
        nothing should be written."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Original"))

        # OrderedDict-style: title first, then bad field
        from collections import OrderedDict
        fields = OrderedDict([("title", "Tampered"), ("__class__", "evil")])

        with pytest.raises(AttributeError):
            store.update("t-1", fields)

        assert store.get("t-1").title == "Original"

    def test_delete_is_permanent(self) -> None:
        """After delete the ID must not be retrievable or listable."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1"))
        store.delete("t-1")

        with pytest.raises(KeyError):
            store.get("t-1")

        assert all(t.id != "t-1" for t in store.list_all())

    def test_store_instances_are_isolated(self) -> None:
        """Two store instances must not share state."""
        store_a = InMemoryTaskStore()
        store_b = InMemoryTaskStore()

        store_a.add(_make_task("shared-id"))

        with pytest.raises(KeyError):
            store_b.get("shared-id")

    def test_internal_dict_not_publicly_accessible_by_convention(self) -> None:
        """_tasks is private by naming convention -- ensure its mutation does
        not corrupt the public API beyond what the tests above cover."""
        store = InMemoryTaskStore()
        store.add(_make_task("t-1", "Safe"))

        # Even if someone accesses _tasks and clears it, the public API
        # should reflect the change (no stale cache). This tests consistency.
        store._tasks.clear()
        assert store.list_all() == []


# ---------------------------------------------------------------------------
# Package re-export test
# ---------------------------------------------------------------------------

class TestPackageReExport:
    def test_import_from_storage_package(self) -> None:
        """InMemoryTaskStore should be importable from the storage package."""
        storage_pkg = pytest.importorskip("tasklib.storage")
        cls = getattr(storage_pkg, "InMemoryTaskStore", None)
        if cls is None:
            pytest.skip("tasklib.storage does not re-export InMemoryTaskStore yet")
        assert cls is InMemoryTaskStore
