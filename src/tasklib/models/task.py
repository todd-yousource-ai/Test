"""Task model definitions for tasklib."""

from enum import StrEnum


class TaskStatus(StrEnum):
    """Represents the status of a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"