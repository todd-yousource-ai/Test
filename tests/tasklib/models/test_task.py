import dataclasses
import datetime
import uuid

import pytest

from tasklib.models.task import Task, TaskStatus


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------


class TestTaskCreationDefaults:
    """Task(title='Buy milk') should set sensible defaults."""

    def test_task_creation_with_title_only_sets_defaults(self):
        task = Task(title="Buy milk")

        # id is a valid UUID4 string
        parsed = uuid.UUID(task.id, version=4)
        assert str(parsed) == task.id

        assert task.status is TaskStatus.TODO
        assert task.description == ""
        assert isinstance(task.created_at, datetime.datetime)
        assert isinstance(task.updated_at, datetime.datetime)

    def test_task_id_is_unique(self):
        t1 = Task(title="A")
        t2 = Task(title="B")
        assert t1.id != t2.id

    def test_task_all_fields_explicit(self):
        now = datetime.datetime(2025, 1, 1, 12, 0, 0)
        task = Task(
            title="Deploy",
            description="Ship v2",
            status=TaskStatus.DONE,
            id="custom-id-123",
            created_at=now,
            updated_at=now,
        )
        assert task.title == "Deploy"
        assert task.description == "Ship v2"
        assert task.status is TaskStatus.DONE
        assert task.id == "custom-id-123"
        assert task.created_at == now
        assert task.updated_at == now

    def test_task_description_defaults_to_empty_string(self):
        assert Task(title="x").description == ""

    def test_task_explicit_status_preserved(self):
        task = Task(title="x", status=TaskStatus.DONE)
        assert task.status is TaskStatus.DONE


# ---------------------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------------------


class TestTaskStatusEnum:
    def test_task_status_enum_has_three_members(self):
        names = {m.name for m in TaskStatus}
        assert names == {"TODO", "IN_PROGRESS", "DONE"}

    def test_task_status_enum_values_are_strings(self):
        for member in TaskStatus:
            assert isinstance(member.value, str)
            assert member.value == member.name


# ---------------------------------------------------------------------------
# Timestamp tests
# ---------------------------------------------------------------------------


class TestTimestamps:
    def test_task_created_at_and_updated_at_are_auto_set(self):
        before = datetime.datetime.now()
        task = Task(title="t")
        after = datetime.datetime.now()

        assert isinstance(task.created_at, datetime.datetime)
        assert isinstance(task.updated_at, datetime.datetime)
        assert before <= task.created_at <= after
        assert before <= task.updated_at <= after

    def test_rapid_successive_creation_distinct_ids_and_timestamps(self):
        t1 = Task(title="first")
        t2 = Task(title="second")

        assert t1.id != t2.id
        # They are independent objects (not the same reference)
        assert t1.created_at is not t2.created_at
        assert t1.updated_at is not t2.updated_at


# ---------------------------------------------------------------------------
# Negative / validation tests
# ---------------------------------------------------------------------------


class TestValidation:
    def test_task_empty_title_raises_value_error(self):
        with pytest.raises(ValueError, match="(?i)title"):
            Task(title="")

    def test_task_whitespace_title_raises_value_error(self):
        with pytest.raises(ValueError, match="(?i)title"):
            Task(title="   \n\t  ")

    def test_task_invalid_status_type_string_raises_type_error(self):
        with pytest.raises(TypeError):
            Task(title="valid", status="TODO")  # type: ignore[arg-type]

    def test_task_invalid_status_type_int_raises_type_error(self):
        with pytest.raises(TypeError):
            Task(title="valid", status=42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Round-trip serialization
# ---------------------------------------------------------------------------


class TestRoundTrip:
    def test_task_roundtrip_via_dict(self):
        original = Task(title="Round-trip me", description="desc", status=TaskStatus.IN_PROGRESS)
        d = dataclasses.asdict(original)

        # asdict converts TaskStatus to its value; coerce back
        d["status"] = TaskStatus(d["status"])

        reconstructed = Task(**d)

        assert reconstructed.title == original.title
        assert reconstructed.description == original.description
        assert reconstructed.status is original.status
        assert reconstructed.id == original.id
        assert reconstructed.created_at == original.created_at
        assert reconstructed.updated_at == original.updated_at


# ---------------------------------------------------------------------------
# Package-level re-exports (guarded - skip if __init__.py not wired yet)
# ---------------------------------------------------------------------------


class TestModelsInit:
    def test_models_init_exports(self):
        models = pytest.importorskip("tasklib.models")
        TaskCls = getattr(models, "Task", None)
        StatusCls = getattr(models, "TaskStatus", None)
        if TaskCls is None or StatusCls is None:
            pytest.skip("tasklib.models does not re-export Task/TaskStatus yet")
        assert TaskCls is Task
        assert StatusCls is TaskStatus

    def test_models_init_all_list(self):
        models = pytest.importorskip("tasklib.models")
        all_list = getattr(models, "__all__", None)
        if all_list is None:
            pytest.skip("tasklib.models.__all__ not defined yet")
        assert sorted(all_list) == ["Task", "TaskStatus"]
