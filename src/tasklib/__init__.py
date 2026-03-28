"""tasklib -- A lightweight task management library for validation.

This package provides a simple task management API including data models,
in-memory storage, and a CLI interface. It exists to validate that the
Crafted Dev Agent build pipeline can close a complete dependency chain
from documentation through scaffold to working code.

This __init__.py is deliberately minimal: no imports, no executable code,
no side effects at import time. Public API re-exports will be added by
downstream PRs once the underlying modules exist.
"""

__all__ = []