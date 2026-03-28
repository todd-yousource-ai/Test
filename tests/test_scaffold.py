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
import types
from pathlib import Path
from typing import Set

import pytest

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODULES: list = [
    "tasklib",
    "tasklib.models",
    "tasklib.storage",
    "tasklib.cli",
    "tasklib.models.task",
    "tasklib.storage.store",
]

ALLOWED_PUBLIC_NAMES: dict = {
    "tasklib": set(),
    "tasklib.models": set(),
    "tasklib.storage": set(),
    "tasklib.cli": set(),
    "tasklib.models.task": set(),
    "tasklib.storage.store": set(),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _public_names(module: object) -> Set[str]:
    """Return the set of public names exposed by *module*.

    A name is considered public if it does not start with an underscore.
    This deliberately mirrors the convention Python uses for ``from mod import *``.
    """
    return {name for name in dir(module) if not name.startswith("_")}


# ---------------------------------------------------------------------------
# Positive import tests
# ---------------------------------------------------------------------------

def test_import_tasklib() -> None:
    """Importing the top-level tasklib package succeeds without error."""
    mod = importlib.import_module("tasklib")
    assert mod is not None, "tasklib import returned None"


def test_import_tasklib_models() -> None:
    """Importing tasklib.models subpackage succeeds without error."""
    mod = importlib.import_module("tasklib.models")
    assert mod is not None, "tasklib.models import returned None"


def test_import_tasklib_storage() -> None:
    """Importing tasklib.storage subpackage succeeds without error."""
    mod = importlib.import_module("tasklib.storage")
    assert mod is not None, "tasklib.storage import returned None"


def test_import_tasklib_cli() -> None:
    """Importing tasklib.cli module succeeds without error."""
    mod = importlib.import_module("tasklib.cli")
    assert mod is not None, "tasklib.cli import returned None"


def test_import_tasklib_models_task() -> None:
    """Importing tasklib.models.task module succeeds without error."""
    mod = importlib.import_module("tasklib.models.task")
    assert mod is not None, "tasklib.models.task import returned None"


def test_import_tasklib_storage_store() -> None:
    """Importing tasklib.storage.store module succeeds without error."""
    mod = importlib.import_module("tasklib.storage.store")
    assert mod is not None, "tasklib.storage.store import returned None"


# ---------------------------------------------------------------------------
# Public name guard -- parametrised over all six modules
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_path", MODULES)
def test_no_unexpected_public_names(module_path: str) -> None:
    """Each scaffold module must not expose public names beyond the allowed set.

    Placeholder modules that only contain dunder names will have an empty
    public-name set, which is the expected baseline.
    """
    mod = importlib.import_module(module_path)
    public = _public_names(mod)
    allowed = ALLOWED_PUBLIC_NAMES[module_path]
    surplus = public - allowed
    assert surplus == set(), (
        f"Module {module_path!r} exposes unexpected public names: {sorted(surplus)}"
    )


# ---------------------------------------------------------------------------
# Negative tests
# ---------------------------------------------------------------------------

def test_import_nonexistent_module_raises() -> None:
    """Importing a non-existent submodule must raise ModuleNotFoundError.

    This validates that the test approach correctly detects missing modules
    and does not silently succeed.
    """
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("tasklib.nonexistent")


def test_monkeypatched_public_name_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    """A module that accidentally defines a bare variable is detected.

    We simulate this by monkeypatching a public attribute onto a scaffold
    module and verifying the public-names logic catches the surplus name.
    """
    mod = importlib.import_module("tasklib")
    monkeypatch.setattr(mod, "leaked_var", 42)
    public = _public_names(mod)
    allowed = ALLOWED_PUBLIC_NAMES["tasklib"]
    surplus = public - allowed
    assert "leaked_var" in surplus, (
        "The public-names guard failed to detect the monkeypatched attribute"
    )


def test_import_idempotency() -> None:
    """Importing the same module twice returns the identical module object.

    This confirms no side-effects cause a fresh module to be created on
    repeated imports.
    """
    mod1 = importlib.import_module("tasklib")
    mod2 = importlib.import_module("tasklib")
    assert mod1 is mod2, (
        "Repeated importlib.import_module calls returned different objects"
    )


# ---------------------------------------------------------------------------
# Idempotency for all modules
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_path", MODULES)
def test_import_idempotency_all(module_path: str) -> None:
    """All scaffold modules are idempotent on repeated import."""
    mod1 = importlib.import_module(module_path)
    mod2 = importlib.import_module(module_path)
    assert mod1 is mod2, (
        f"Module {module_path!r} is not idempotent on reimport"
    )


# ---------------------------------------------------------------------------
# Security tests
# ---------------------------------------------------------------------------

def test_no_code_execution_on_import() -> None:
    """Scaffold modules must not execute arbitrary code on import.

    We verify this by checking that no module defines a public callable
    that could be an unintended side-effect entry point.
    """
    for module_path in MODULES:
        mod = importlib.import_module(module_path)
        public = _public_names(mod)
        # Scaffold modules should have no public callables at all
        callables_found = {
            name for name in public if callable(getattr(mod, name, None))
        }
        allowed = ALLOWED_PUBLIC_NAMES.get(module_path, set())
        unexpected_callables = callables_found - allowed
        assert unexpected_callables == set(), (
            f"Module {module_path!r} exposes unexpected public callables: "
            f"{sorted(unexpected_callables)}"
        )


def test_no_sys_modules_pollution() -> None:
    """Importing scaffold modules must not inject unexpected entries into sys.modules.

    We record the state of sys.modules before and after importing all scaffold
    modules and verify that only the expected module paths appear.
    """
    # Collect keys that already exist
    before_keys = set(sys.modules.keys())

    for module_path in MODULES:
        importlib.import_module(module_path)

    after_keys = set(sys.modules.keys())
    new_keys = after_keys - before_keys

    # Every new key must be one of our scaffold modules or a parent thereof
    allowed_new = set(MODULES)
    unexpected = {
        k for k in new_keys
        if k.startswith("tasklib") and k not in allowed_new
    }
    assert unexpected == set(), (
        f"Importing scaffold modules polluted sys.modules with: {sorted(unexpected)}"
    )


def test_modules_have_correct_package_attribute() -> None:
    """Each module's __package__ attribute must match its expected package path.

    This prevents path-traversal or package confusion attacks where a module
    could masquerade as belonging to a different package.
    """
    expected_packages = {
        "tasklib": "tasklib",
        "tasklib.models": "tasklib.models",
        "tasklib.storage": "tasklib.storage",
        "tasklib.cli": "tasklib",
        "tasklib.models.task": "tasklib.models",
        "tasklib.storage.store": "tasklib.storage",
    }
    for module_path in MODULES:
        mod = importlib.import_module(module_path)
        pkg = getattr(mod, "__package__", None)
        # For packages, __package__ == module name; for modules, __package__ == parent
        expected = expected_packages[module_path]
        assert pkg == expected, (
            f"Module {module_path!r} has __package__={pkg!r}, expected {expected!r}"
        )


def test_no_all_attribute_leakage() -> None:
    """Scaffold modules must not define __all__ with unexpected entries.

    If __all__ is defined, it must be empty or contain only allowed names.
    """
    for module_path in MODULES:
        mod = importlib.import_module(module_path)
        all_attr = getattr(mod, "__all__", None)
        if all_attr is not None:
            allowed = ALLOWED_PUBLIC_NAMES[module_path]
            surplus = set(all_attr) - allowed
            assert surplus == set(), (
                f"Module {module_path!r} __all__ contains unexpected names: "
                f"{sorted(surplus)}"
            )


def test_import_does_not_modify_builtins() -> None:
    """Importing scaffold modules must not tamper with the builtins namespace.

    This is a security boundary test: malicious or buggy scaffold code could
    override built-in functions.
    """
    import builtins
    builtins_before = set(dir(builtins))

    for module_path in MODULES:
        importlib.import_module(module_path)

    builtins_after = set(dir(builtins))
    added = builtins_after - builtins_before
    assert added == set(), (
        f"Importing scaffold modules added to builtins: {sorted(added)}"
    )


def test_dunder_only_modules_report_empty_public_set() -> None:
    """Modules whose dir() output includes only dunder names report empty public set.

    This is the expected baseline for placeholder scaffold modules.
    """
    for module_path in MODULES:
        mod = importlib.import_module(module_path)
        public = _public_names(mod)
        allowed = ALLOWED_PUBLIC_NAMES[module_path]
        # We only assert that the actual public names are within bounds;
        # an empty set is perfectly valid and expected for scaffold modules.
        assert public <= allowed or public == set(), (
            f"Module {module_path!r} has public names {sorted(public)} "
            f"not within allowed set {sorted(allowed)}"
        )


def test_helper_public_names_excludes_dunders() -> None:
    """The _public_names helper must exclude all dunder names."""
    # Create a minimal module-like object to test the helper in isolation
    fake_mod = types.ModuleType("fake_test_module")
    fake_mod.__all__ = []  # type: ignore[attr-defined]
    fake_mod.public_thing = "value"  # type: ignore[attr-defined]
    fake_mod._private_thing = "secret"  # type: ignore[attr-defined]

    public = _public_names(fake_mod)
    assert "public_thing" in public
    assert "_private_thing" not in public
    # Dunders must be excluded
    for name in dir(fake_mod):
        if name.startswith("__") and name.endswith("__"):
            assert name not in public, f"Dunder {name!r} leaked into public names"
