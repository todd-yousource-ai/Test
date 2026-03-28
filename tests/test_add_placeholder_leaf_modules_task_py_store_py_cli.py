"""Tests for placeholder leaf modules (task.py, store.py, cli.py).

Verifies that each placeholder module:
  - Is importable without error.
  - Has a non-empty __doc__ attribute describing its future purpose.
  - Exports no public symbols (classes, functions, constants, or imports).
  - Produces no stdout or stderr output on import.
  - Contains no code beyond the docstring (AST-level verification).
  - Cannot be exploited via code injection or unexpected side effects.
"""

import ast
import importlib
import pathlib
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Locate project root by walking up from this file to find pyproject.toml
# ---------------------------------------------------------------------------
PROJECT_ROOT = next(
    p for p in pathlib.Path(__file__).resolve().parents
    if (p / "pyproject.toml").exists()
)

# Module import paths and corresponding source file paths (repo-relative).
_MODULES = [
    ("tasklib.models.task", pathlib.Path("src/tasklib/models/task.py")),
    ("tasklib.storage.store", pathlib.Path("src/tasklib/storage/store.py")),
    ("tasklib.cli", pathlib.Path("src/tasklib/cli.py")),
]

_MODULE_NAMES = [m[0] for m in _MODULES]


def _import_fresh(module_name: str) -> types.ModuleType:
    """Import a module, returning the module object."""
    return importlib.import_module(module_name)


def _public_names(mod: types.ModuleType) -> list[str]:
    """Return public (non-dunder) names defined in a module."""
    return [name for name in dir(mod) if not name.startswith("_")]


def _source_path(repo_relative: pathlib.Path) -> pathlib.Path:
    """Resolve a repo-relative path to an absolute path."""
    return PROJECT_ROOT / repo_relative


# ===========================================================================
# Import tests
# ===========================================================================

class TestModuleImportable:
    """Each placeholder module can be imported without error."""

    def test_task_module_importable(self):
        mod = _import_fresh("tasklib.models.task")
        assert mod is not None

    def test_store_module_importable(self):
        mod = _import_fresh("tasklib.storage.store")
        assert mod is not None

    def test_cli_module_importable(self):
        mod = _import_fresh("tasklib.cli")
        assert mod is not None


# ===========================================================================
# Docstring tests
# ===========================================================================

class TestModuleDocstrings:
    """Each placeholder module exposes a non-empty docstring."""

    def test_task_module_has_docstring(self):
        mod = _import_fresh("tasklib.models.task")
        assert isinstance(mod.__doc__, str)
        assert len(mod.__doc__.strip()) > 0

    def test_store_module_has_docstring(self):
        mod = _import_fresh("tasklib.storage.store")
        assert isinstance(mod.__doc__, str)
        assert len(mod.__doc__.strip()) > 0

    def test_cli_module_has_docstring(self):
        mod = _import_fresh("tasklib.cli")
        assert isinstance(mod.__doc__, str)
        assert len(mod.__doc__.strip()) > 0


# ===========================================================================
# No public symbols tests (negative / regression guard)
# ===========================================================================

class TestNoPublicSymbols:
    """Placeholder modules must not export any public names.

    These tests act as a negative-case guard: if someone accidentally adds
    a class, function, variable, or import to a placeholder file, the test
    will catch it.
    """

    def test_task_module_no_public_symbols(self):
        mod = _import_fresh("tasklib.models.task")
        public = _public_names(mod)
        assert public == [], (
            f"tasklib.models.task should have no public symbols, found: {public}"
        )

    def test_store_module_no_public_symbols(self):
        mod = _import_fresh("tasklib.storage.store")
        public = _public_names(mod)
        assert public == [], (
            f"tasklib.storage.store should have no public symbols, found: {public}"
        )

    def test_cli_module_no_public_symbols(self):
        mod = _import_fresh("tasklib.cli")
        public = _public_names(mod)
        assert public == [], (
            f"tasklib.cli should have no public symbols, found: {public}"
        )


# ===========================================================================
# No output on import
# ===========================================================================

class TestImportsProduceNoOutput:
    """Importing all three modules must not print anything."""

    def test_imports_produce_no_output(self, capsys):
        # Force re-import by removing from sys.modules
        saved = {}
        for name, _ in _MODULES:
            parts = name.split(".")
            for i in range(len(parts)):
                key = ".".join(parts[: i + 1])
                if key in sys.modules:
                    saved[key] = sys.modules.pop(key)

        try:
            for name, _ in _MODULES:
                importlib.import_module(name)
            captured = capsys.readouterr()
            assert captured.out == "", f"Unexpected stdout: {captured.out!r}"
            assert captured.err == "", f"Unexpected stderr: {captured.err!r}"
        finally:
            # Restore modules
            sys.modules.update(saved)


# ===========================================================================
# AST-level verification -- no code beyond docstring
# ===========================================================================

class TestSourceFilesContainNoCode:
    """At the AST level, each source file must contain only a single
    expression statement wrapping a string constant (the module docstring).

    This catches import statements, class/function definitions, assignments,
    and any other code that doesn't belong in a placeholder.
    """

    @pytest.mark.parametrize("module_name,rel_path", _MODULES, ids=_MODULE_NAMES)
    def test_source_files_contain_no_code(self, module_name, rel_path):
        source_file = _source_path(rel_path)
        assert source_file.exists(), f"Source file not found: {source_file}"

        source = source_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(source_file))

        # Body should be exactly one node: Expr(value=Constant(value=<str>))
        assert len(tree.body) == 1, (
            f"{rel_path} should have exactly 1 top-level AST node (docstring), "
            f"got {len(tree.body)}: {[type(n).__name__ for n in tree.body]}"
        )

        node = tree.body[0]
        assert isinstance(node, ast.Expr), (
            f"Expected Expr node, got {type(node).__name__}"
        )
        assert isinstance(node.value, ast.Constant), (
            f"Expected Constant inside Expr, got {type(node.value).__name__}"
        )
        assert isinstance(node.value.value, str), (
            f"Expected string constant (docstring), got {type(node.value.value).__name__}"
        )


# ===========================================================================
# Source file existence
# ===========================================================================

class TestSourceFilesExist:
    """Verify that the actual .py files exist on disk at expected paths."""

    @pytest.mark.parametrize("module_name,rel_path", _MODULES, ids=_MODULE_NAMES)
    def test_source_file_exists(self, module_name, rel_path):
        source_file = _source_path(rel_path)
        assert source_file.is_file(), f"Expected file at {source_file}"


# ===========================================================================
# Security tests
# ===========================================================================

class TestSecurityBoundaries:
    """Security-oriented tests for placeholder modules."""

    @pytest.mark.parametrize("module_name,rel_path", _MODULES, ids=_MODULE_NAMES)
    def test_no_exec_eval_compile_in_source(self, module_name, rel_path):
        """Source files must not contain exec/eval/compile calls that could
        enable code injection."""
        source_file = _source_path(rel_path)
        source = source_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(source_file))

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name):
                    assert func.id not in ("exec", "eval", "compile", "__import__"), (
                        f"Dangerous call to {func.id}() found in {rel_path}"
                    )

    @pytest.mark.parametrize("module_name,rel_path", _MODULES, ids=_MODULE_NAMES)
    def test_no_import_statements_in_source(self, module_name, rel_path):
        """Placeholder modules must not import anything -- prevents supply-chain
        side effects at import time."""
        source_file = _source_path(rel_path)
        source = source_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(source_file))

        for node in ast.walk(tree):
            assert not isinstance(node, ast.Import), (
                f"Unexpected 'import' statement in {rel_path}"
            )
            assert not isinstance(node, ast.ImportFrom), (
                f"Unexpected 'from ... import' statement in {rel_path}"
            )

    @pytest.mark.parametrize("module_name,rel_path", _MODULES, ids=_MODULE_NAMES)
    def test_no_os_or_subprocess_references_in_source(self, module_name, rel_path):
        """Source text must not reference os, subprocess, or shutil to guard
        against file-system or process manipulation."""
        source_file = _source_path(rel_path)
        source = source_file.read_text(encoding="utf-8")
        # Only check outside the docstring -- but since the body must be a
        # single docstring Expr, we just verify no Name nodes reference these.
        tree = ast.parse(source, filename=str(source_file))
        dangerous_names = {"os", "subprocess", "shutil", "socket", "ctypes"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                assert node.id not in dangerous_names, (
                    f"Reference to '{node.id}' found in {rel_path}"
                )

    @pytest.mark.parametrize("module_name,rel_path", _MODULES, ids=_MODULE_NAMES)
    def test_no_dunder_all_defined(self, module_name, rel_path):
        """Placeholder modules must not define __all__ -- there's nothing to export."""
        mod = _import_fresh(module_name)
        assert not hasattr(mod, "__all__") or mod.__all__ is None, (
            f"{module_name} should not define __all__"
        )

    @pytest.mark.parametrize("module_name,rel_path", _MODULES, ids=_MODULE_NAMES)
    def test_module_is_not_a_package(self, module_name, rel_path):
        """Each placeholder is a leaf module (file), not a package (directory)."""
        mod = _import_fresh(module_name)
        # Packages have __path__; plain modules do not.
        assert not hasattr(mod, "__path__"), (
            f"{module_name} should be a leaf module, not a package"
        )

    @pytest.mark.parametrize("module_name,rel_path", _MODULES, ids=_MODULE_NAMES)
    def test_source_is_valid_utf8(self, module_name, rel_path):
        """Source files must be valid UTF-8 (no binary payloads disguised as .py)."""
        source_file = _source_path(rel_path)
        raw = source_file.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError:
            pytest.fail(f"{rel_path} contains invalid UTF-8 bytes")

    @pytest.mark.parametrize("module_name,rel_path", _MODULES, ids=_MODULE_NAMES)
    def test_no_null_bytes_in_source(self, module_name, rel_path):
        """Source files must not contain null bytes (potential injection vector)."""
        source_file = _source_path(rel_path)
        raw = source_file.read_bytes()
        assert b"\x00" not in raw, f"Null byte found in {rel_path}"
