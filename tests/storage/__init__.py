"""Tests for tasklib.storage.memory.InMemoryTaskStore."""

from __future__ import annotations

import pytest
from pathlib import Path

# Verify project root resolution
PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)

from tasklib.storage.memory import InMemoryTaskStore


class TestAdd:
    """Tests for InMemoryTaskStore.add()."""

    def test_add_returns_task_with_correct_title(self):
        store = InMemoryTaskStore()
        task = store.add("Buy milk")
        assert task.title == "Buy milk"

    def test_add_returns_task_with_pending_status(self):
        from tasklib.models.task import TaskStatus

        store = InMemoryTaskStore()
        task = store.add("Buy milk")
        assert task.status == TaskStatus.PENDING

    def test_add_returns_task_with_generated_id(self):
        store = InMemoryTaskStore()
        task = store.add("Buy milk")
        assert isinstance(task.id, str)
        assert len(task.id) > 0

    def test_add_multiple_tasks_have_unique_ids(self):
        store = InMemoryTaskStore()
        task1 = store.add("Task one")
        task2 = store.add("Task two")
        assert task1.id != task2.id

    def test_add_empty_title_raises_valueerror(self):
        store = InMemoryTaskStore()
        with pytest.raises(ValueError):
            store.add("")

    def test_add_whitespace_only_title_raises_valueerror(self):
        store = InMemoryTaskStore()
        with pytest.raises(ValueError):
            store.add("   ")

    def test_add_tabs_and_newlines_only_raises_valueerror(self):
        store = InMemoryTaskStore()
        with pytest.raises(ValueError):
            store.add("\t\n  \r")

    def test_add_non_string_title_raises_typeerror(self):
        store = InMemoryTaskStore()
        with pytest.raises(TypeError):
            store.add(42)  # type: ignore[arg-type]

    def test_add_none_title_raises_typeerror(self):
        store = InMemoryTaskStore()
        with pytest.raises(TypeError):
            store.add(None)  # type: ignore[arg-type]

    def test_add_list_title_raises_typeerror(self):
        store = InMemoryTaskStore()
        with pytest.raises(TypeError):
            store.add(["a", "b"])  # type: ignore[arg-type]


class TestGet:
    """Tests for InMemoryTaskStore.get()."""

    def test_get_returns_stored_task(self):
        store = InMemoryTaskStore()
        added = store.add("My task")
        retrieved = store.get(added.id)
        assert retrieved is added

    def test_get_missing_raises_keyerror(self):
        store = InMemoryTaskStore()
        with pytest.raises(KeyError):
            store.get("nonexistent-id-123")

    def test_get_keyerror_message_contains_task_id(self):
        store = InMemoryTaskStore()
        missing_id = "missing-abc-456"
        with pytest.raises(KeyError, match=missing_id):
            store.get(missing_id)

    def test_get_none_id_raises_error(self):
        """get() with None should not silently succeed."""
        store = InMemoryTaskStore()
        with pytest.raises((KeyError, TypeError)):
            store.get(None)  # type: ignore[arg-type]

    def test_get_empty_string_id_raises_keyerror(self):
        store = InMemoryTaskStore()
        with pytest.raises(KeyError):
            store.get("")


class TestListAll:
    """Tests for InMemoryTaskStore.list_all()."""

    def test_list_all_empty_store(self):
        store = InMemoryTaskStore()
        result = store.list_all()
        assert result == []

    def test_list_all_returns_all_added_tasks(self):
        store = InMemoryTaskStore()
        store.add("Task 1")
        store.add("Task 2")
        store.add("Task 3")
        result = store.list_all()
        assert len(result) == 3

    def test_list_all_preserves_insertion_order(self):
        store = InMemoryTaskStore()
        t1 = store.add("First")
        t2 = store.add("Second")
        t3 = store.add("Third")
        result = store.list_all()
        assert [t.id for t in result] == [t1.id, t2.id, t3.id]

    def test_list_all_returns_new_list_each_call(self):
        store = InMemoryTaskStore()
        store.add("A task")
        list1 = store.list_all()
        list2 = store.list_all()
        assert list1 is not list2
        assert list1 == list2

    def test_list_all_mutation_does_not_affect_store(self):
        """Mutating the returned list should not change internal state."""
        store = InMemoryTaskStore()
        store.add("Keep me")
        result = store.list_all()
        result.clear()
        assert len(store.list_all()) == 1


class TestStoreIndependence:
    """Tests ensuring separate store instances don't share state."""

    def test_store_instances_are_independent(self):
        store1 = InMemoryTaskStore()
        store2 = InMemoryTaskStore()
        store1.add("Only in store1")
        assert len(store1.list_all()) == 1
        assert len(store2.list_all()) == 0


class TestImport:
    """Tests for import resolution."""

    def test_import_from_tasklib_storage(self):
        from tasklib.storage import InMemoryTaskStore as Imported

        assert Imported is InMemoryTaskStore

    def test_impl_file_exists(self):
        impl_path = PROJECT_ROOT / "src" / "tasklib" / "storage" / "memory.py"
        assert impl_path.exists(), f"Implementation file not found at {impl_path}"


class TestSecurity:
    """Security-oriented tests."""

    def test_internal_dict_not_directly_accessible_via_tasks(self):
        """The internal _tasks dict should not be easily tampered with
        through the public API."""
        store = InMemoryTaskStore()
        task = store.add("Legit task")
        # Accessing the internal dict directly should not be encouraged,
        # but we verify that public API doesn't leak mutable references
        # to the internal dict.
        listed = store.list_all()
        # The list itself is a copy, not the internal dict values view
        assert type(listed) is list

    def test_add_extremely_long_title_succeeds(self):
        """No artificial limit on title length -- store should handle it."""
        store = InMemoryTaskStore()
        long_title = "A" * 100_000
        task = store.add(long_title)
        assert task.title == long_title

    def test_add_special_characters_in_title(self):
        """Titles with special/unicode characters should be stored faithfully."""
        store = InMemoryTaskStore()
        special = "'; DROP TABLE tasks;-- 🔥 <script>alert('xss')</script>"
        task = store.add(special)
        assert task.title == special
        retrieved = store.get(task.id)
        assert retrieved.title == special

    def test_add_unicode_title(self):
        store = InMemoryTaskStore()
        task = store.add("日本語タスク 🇯🇵")
        assert task.title == "日本語タスク 🇯🇵"

    def test_get_with_crafted_id_does_not_crash(self):
        """Passing odd strings as task_id should raise KeyError, not crash."""
        store = InMemoryTaskStore()
        crafted_ids = [
            "../../../etc/passwd",
            "\x00null\x00byte",
            "a" * 1_000_000,
            "'; DROP TABLE--",
        ]
        for cid in crafted_ids:
            with pytest.raises(KeyError):
                store.get(cid)

    def test_task_ids_are_not_sequential_integers(self):
        """IDs should not be trivially guessable sequential integers."""
        store = InMemoryTaskStore()
        t1 = store.add("First")
        t2 = store.add("Second")
        # If IDs were "1", "2", etc., that's predictable. We check they
        # are not simply incrementing small integers.
        try:
            id1_int = int(t1.id)
            id2_int = int(t2.id)
            # If both parse as ints and are sequential, flag it
            assert not (id2_int == id1_int + 1 and id1_int < 100), (
                "Task IDs appear to be trivially sequential integers"
            )
        except ValueError:
            # Not integers at all -- good, they're likely UUIDs or similar
            pass

    def test_cannot_overwrite_existing_task_via_add(self):
        """Each add() must create a new task; no ID collision."""
        store = InMemoryTaskStore()
        ids = set()
        for i in range(100):
            task = store.add(f"Task {i}")
            ids.add(task.id)
        assert len(ids) == 100

    def test_boolean_title_raises_typeerror(self):
        """bool is a subclass of int in Python; ensure it's rejected."""
        store = InMemoryTaskStore()
        with pytest.raises(TypeError):
            store.add(True)  # type: ignore[arg-type]
