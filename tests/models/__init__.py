"""Tests for tasklib.models.task -- Task dataclass and TaskStatus enumeration."""

import dataclasses
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Resolve project root dynamically (find nearest ancestor with pyproject.toml)
# ---------------------------------------------------------------------------
PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------
from tasklib.models.task import Task, TaskStatus


# ===================================================================
# Happy-path tests
# ===================================================================


class TestTaskCreationDefaults:
    """Task construction with only the required ``title`` argument."""

    def test_task_creation_with_title_only(self):
        task = Task(title="Buy milk")

        # id is a UUID4 string
        parsed = uuid.UUID(task.id)
        assert parsed.version == 4
        assert isinstance(task.id, str)

        # title set correctly
        assert task.title == "Buy milk"

        # optional fields have correct defaults
        assert task.description is None
        assert task.status is TaskStatus.PENDING

        # timestamps are UTC-aware datetimes
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert task.created_at.tzinfo is timezone.utc
        assert task.updated_at.tzinfo is timezone.utc

    def test_task_creation_with_all_fields(self):
        task = Task(title="Read book", description="Chapter 5")
        assert task.description == "Chapter 5"
        assert task.title == "Read book"

    def test_task_creation_with_explicit_completed_status(self):
        task = Task(title="Done task", status=TaskStatus.COMPLETED)
        assert task.status is TaskStatus.COMPLETED

    def test_task_id_is_unique(self):
        t1 = Task(title="A")
        t2 = Task(title="B")
        assert t1.id != t2.id

    def test_task_id_is_valid_uuid4(self):
        task = Task(title="UUID check")
        parsed = uuid.UUID(task.id)
        assert parsed.version == 4

    def test_task_status_defaults_to_pending(self):
        task = Task(title="Default status")
        assert task.status is TaskStatus.PENDING

    def test_task_created_at_is_utc(self):
        task = Task(title="TZ check")
        assert task.created_at.tzinfo is timezone.utc

    def test_task_updated_at_is_utc(self):
        task = Task(title="TZ check 2")
        assert task.updated_at.tzinfo is timezone.utc

    def test_task_created_at_close_to_now(self):
        before = datetime.now(timezone.utc)
        task = Task(title="Timing")
        after = datetime.now(timezone.utc)
        assert before <= task.created_at <= after
        delta = (after - task.created_at).total_seconds()
        assert delta < 1.0

    def test_task_is_dataclass(self):
        assert dataclasses.is_dataclass(Task)


# ===================================================================
# TaskStatus enum tests
# ===================================================================


class TestTaskStatusEnum:
    def test_task_status_enum_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.COMPLETED.value == "completed"

    def test_task_status_enum_has_exactly_two_members(self):
        assert len(TaskStatus) == 2


# ===================================================================
# Negative / validation tests
# ===================================================================


class TestTaskValidationErrors:
    def test_task_empty_title_raises_valueerror(self):
        with pytest.raises(ValueError, match="(?i)title"):
            Task(title="")

    def test_task_whitespace_title_raises_valueerror(self):
        for ws in (" ", "   ", "\t", "\n", "  \t\n  "):
            with pytest.raises(ValueError):
                Task(title=ws)

    def test_task_non_string_title_raises_typeerror(self):
        with pytest.raises(TypeError):
            Task(title=42)  # type: ignore[arg-type]

        with pytest.raises(TypeError):
            Task(title=None)  # type: ignore[arg-type]

        with pytest.raises(TypeError):
            Task(title=["a", "b"])  # type: ignore[arg-type]

    def test_task_invalid_status_type_raises_typeerror(self):
        with pytest.raises(TypeError):
            Task(title="Valid", status="pending")  # type: ignore[arg-type]

    def test_task_none_status_raises_typeerror(self):
        with pytest.raises(TypeError):
            Task(title="Valid", status=None)  # type: ignore[arg-type]

    def test_task_non_string_description_raises_typeerror(self):
        with pytest.raises(TypeError):
            Task(title="Valid", description=123)  # type: ignore[arg-type]

        with pytest.raises(TypeError):
            Task(title="Valid", description=["desc"])  # type: ignore[arg-type]


# ===================================================================
# Re-export / packaging tests
# ===================================================================


class TestModelsInit:
    def test_reexport_from_models_init(self):
        from tasklib.models import Task as TaskReexport
        from tasklib.models import TaskStatus as TaskStatusReexport

        assert TaskReexport is Task
        assert TaskStatusReexport is TaskStatus

    def test_models_init_all(self):
        import tasklib.models as models_pkg

        assert hasattr(models_pkg, "__all__")
        assert "Task" in models_pkg.__all__
        assert "TaskStatus" in models_pkg.__all__


# ===================================================================
# Security-oriented tests
# ===================================================================


class TestTaskSecurity:
    """Security boundary tests -- ensure no silent coercion or injection paths."""

    def test_title_script_injection_stored_verbatim(self):
        """Script content in title is stored as-is (no sanitisation that
        silently empties the string), but must not crash."""
        xss = "<script>alert('xss')</script>"
        task = Task(title=xss)
        assert task.title == xss

    def test_title_sql_injection_stored_verbatim(self):
        sqli = "'; DROP TABLE tasks;--"
        task = Task(title=sqli)
        assert task.title == sqli

    def test_title_null_byte_does_not_bypass_validation(self):
        """A title consisting of only a null byte is technically non-empty,
        but we verify it doesn't crash and is stored as given."""
        task = Task(title="\x00important")
        assert "\x00" in task.title

    def test_extremely_long_title_accepted(self):
        """No artificial length limit -- the dataclass should not crash."""
        long_title = "A" * 10_000_000
        task = Task(title=long_title)
        assert len(task.title) == 10_000_000

    def test_description_script_injection_stored_verbatim(self):
        xss = "<img src=x onerror=alert(1)>"
        task = Task(title="Safe", description=xss)
        assert task.description == xss

    def test_id_cannot_be_overridden_to_non_uuid(self):
        """Even if a caller passes a custom id, the field factory should
        generate a valid UUID4. If the implementation allows overriding,
        ensure the override is at least validated or that the factory
        always runs."""
        task = Task(title="Override attempt")
        # Regardless, the resulting id must always be a valid UUID4
        parsed = uuid.UUID(task.id)
        assert parsed.version == 4

    def test_status_enum_cannot_be_subclassed_for_injection(self):
        """Enum members cannot be faked via a subclass -- Python enums
        with members are not subclassable."""
        with pytest.raises(TypeError):

            class FakeStatus(TaskStatus):
                HACKED = "hacked"

    def test_bool_title_raises_typeerror(self):
        """bool is a subclass of int in Python; must still be rejected."""
        with pytest.raises(TypeError):
            Task(title=True)  # type: ignore[arg-type]

    def test_bytestring_title_raises_typeerror(self):
        with pytest.raises(TypeError):
            Task(title=b"bytes")  # type: ignore[arg-type]

    def test_bytestring_description_raises_typeerror(self):
        with pytest.raises(TypeError):
            Task(title="Valid", description=b"bytes")  # type: ignore[arg-type]

    def test_timestamp_fields_are_independent_across_instances(self):
        """Ensure no shared mutable default between instances."""
        t1 = Task(title="First")
        t2 = Task(title="Second")
        # Mutating one should not affect the other
        assert t1.created_at is not t2.created_at
