"""Storage sub-package for tasklib.

Re-exports InMemoryTaskStore so that consumers can write::

    from tasklib.storage import InMemoryTaskStore

without knowing the internal module layout.
"""

from tasklib.storage.memory import InMemoryTaskStore

__all__: list[str] = ["InMemoryTaskStore"]