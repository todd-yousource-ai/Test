"""Scaffold import verification tests for the tasklib package.

Validates that all scaffold modules laid down in the package scaffold PRs
are importable, side-effect-free, and do not leak unexpected public names.

Security assumptions:
    - All imports use importlib.import_module to isolate import failures
      as test failures rather than collection errors.
    - No third-party dependencies beyond pytest.
    - Tests fail closed: any unexpected public name causes an explicit
      assertion failure with full diagnostic context.

Failure behavior:
    - Import failures surface as clear test failures with the module path.
    - Public-name leakage is reported with the module path and surplus names.
    - Non-existent module imports must raise ModuleNotFoundError (fail closed).
"""

import importlib
import sys
from typing import Set

import pytest


#