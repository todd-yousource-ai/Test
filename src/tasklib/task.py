"""tasklib -- a minimal task management library.

Public API re-exports:
    Task       -- immutable task dataclass
    TaskStatus -- tri-state lifecycle enumeration
"""

__version__ = "1.0.0"

import logging as _logging

_logger = _logging.getLogger(__name__)

try:
    from tasklib.task import Task, TaskStatus
except ImportError as _exc:
    _logger.error("Failed to import tasklib.task: %s", _exc)
    raise

__all__ = ["Task", "TaskStatus"]

_logger.debug("tasklib %s initialised successfully", __version__)