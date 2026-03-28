"""Tests for the tasklib package scaffold."""

import importlib
import io
import sys
import ast
from pathlib import Path

import pytest

# Resolve project root by walking up from this file until we find pyproject.toml
PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)


class TestImports:
    """Test that all scaffold modules are importable."""

    def test_import_tasklib(self):
        import tasklib

        assert tasklib.__doc__ is not None
        assert isinstance(tasklib.__doc__, str)
        assert len(tasklib.__doc__.strip()) > 0

    def test_import_tasklib_models(self):
        import tasklib.models

        assert tasklib.models.__doc__ is not None
        assert isinstance(tasklib.models.__doc__, str)
        assert len(tasklib.models.__doc__.strip()) > 0

    def test_import_tasklib_storage(self):
        import tasklib.storage

        assert tasklib.storage.__doc__ is not None
        assert isinstance(tasklib.storage.__doc__, str)
        assert len(tasklib.storage.__doc__.strip()) > 0

    def test_import_cli_main(self):
        from tasklib.cli import main

        assert callable(main)


class TestMainFunction:
    """Test the main() placeholder function."""

    def test_main_returns_none(self):
        from tasklib.cli import main

        result = main()
        assert result is None

    def test_main_has_docstring(self):
        from tasklib.cli import main

        assert main.__doc__ is not None
        assert isinstance(main.__doc__, str)
        assert len(main.__doc__.strip()) > 0

    def test_main_accepts_no_args(self):
        from tasklib.cli import main

        with pytest.raises(TypeError):
            main("unexpected_argument")


class TestInitFilesNoExecutableCode:
    """Verify __init__.py files contain only a docstring and nothing else."""

    @pytest.mark.parametrize(
        "init_path",
        [
            "src/tasklib/__init__.py",
            "src/tasklib/models/__init__.py",
            "src/tasklib/storage/__init__.py",
        ],
    )
    def test_init_files_no_executable_code(self, init_path):
        filepath = PROJECT_ROOT / init_path
        assert filepath.exists(), f"{init_path} does not exist"
        source = filepath.read_text(encoding="utf-8")

        tree = ast.parse(source)
        # After stripping the module docstring (first Expr node if it's a Constant str),
        # the remaining body should be empty.
        body = tree.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body = body[1:]

        assert len(body) == 0, (
            f"{init_path} contains executable code beyond docstring: "
            f"{ast.dump(ast.Module(body=body, type_ignores=[]))}"
        )


class TestCliSourceConstraints:
    """Verify cli.py source code constraints."""

    def _get_cli_source(self):
        filepath = PROJECT_ROOT / "src" / "tasklib" / "cli.py"
        assert filepath.exists()
        return filepath.read_text(encoding="utf-8")

    def test_cli_no_imports(self):
        source = self._get_cli_source()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            assert not isinstance(node, ast.Import), (
                "cli.py should not contain import statements"
            )
            assert not isinstance(node, ast.ImportFrom), (
                "cli.py should not contain from...import statements"
            )

    def test_cli_only_main_symbol(self):
        source = self._get_cli_source()
        tree = ast.parse(source)

        # Collect top-level defined names (functions, classes, assignments)
        top_level_names = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                top_level_names.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                top_level_names.append(node.name)
            elif isinstance(node, ast.ClassDef):
                top_level_names.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        top_level_names.append(target.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                top_level_names.append(node.target.id)
            elif isinstance(node, ast.Expr):
                # Docstring -- skip
                pass

        assert top_level_names == ["main"], (
            f"cli.py should define only 'main' as top-level symbol, found: {top_level_names}"
        )


class TestPackageStructure:
    """Verify the package structure matches the TRD."""

    def test_package_structure_matches_trd(self):
        expected_files = [
            "src/tasklib/__init__.py",
            "src/tasklib/models/__init__.py",
            "src/tasklib/storage/__init__.py",
            "src/tasklib/cli.py",
        ]
        for relpath in expected_files:
            filepath = PROJECT_ROOT / relpath
            assert filepath.exists(), f"Expected file {relpath} does not exist"
            assert filepath.is_file(), f"{relpath} exists but is not a file"


class TestNegativeCases:
    """Negative test cases."""

    def test_import_nonexistent_subpackage(self):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("tasklib.nonexistent")


class TestNoSideEffects:
    """Verify importing produces no side effects."""

    def test_no_side_effects_on_import(self):
        # Remove tasklib modules from cache to re-import fresh
        modules_to_remove = [key for key in sys.modules if key.startswith("tasklib")]
        saved_modules = {}
        for mod_name in modules_to_remove:
            saved_modules[mod_name] = sys.modules.pop(mod_name)

        try:
            captured_stdout = io.StringIO()
            captured_stderr = io.StringIO()

            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = captured_stdout
            sys.stderr = captured_stderr

            try:
                importlib.import_module("tasklib")
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            assert captured_stdout.getvalue() == "", (
                f"Importing tasklib produced stdout: {captured_stdout.getvalue()!r}"
            )
            assert captured_stderr.getvalue() == "", (
                f"Importing tasklib produced stderr: {captured_stderr.getvalue()!r}"
            )
        finally:
            # Restore cached modules
            for mod_name, mod in saved_modules.items():
                sys.modules[mod_name] = mod

    def test_no_dangerous_side_effects_on_import(self):
        """Verify no dangerous imports (os, sys, subprocess) exist in scaffold source files."""
        init_files = [
            "src/tasklib/__init__.py",
            "src/tasklib/models/__init__.py",
            "src/tasklib/storage/__init__.py",
        ]

        dangerous_modules = {"os", "sys", "subprocess", "socket", "shutil", "pathlib"}

        for relpath in init_files:
            filepath = PROJECT_ROOT / relpath
            assert filepath.exists(), f"{relpath} does not exist"
            source = filepath.read_text(encoding="utf-8")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert alias.name.split(".")[0] not in dangerous_modules, (
                            f"{relpath} imports dangerous module: {alias.name}"
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        assert node.module.split(".")[0] not in dangerous_modules, (
                            f"{relpath} imports from dangerous module: {node.module}"
                        )

        # Also verify that importing all three produces no stdout/stderr
        modules_to_test = ["tasklib", "tasklib.models", "tasklib.storage"]
        modules_to_remove = [key for key in sys.modules if key.startswith("tasklib")]
        saved_modules = {}
        for mod_name in modules_to_remove:
            saved_modules[mod_name] = sys.modules.pop(mod_name)

        try:
            captured_stdout = io.StringIO()
            captured_stderr = io.StringIO()

            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = captured_stdout
            sys.stderr = captured_stderr

            try:
                for mod_name in modules_to_test:
                    importlib.import_module(mod_name)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            assert captured_stdout.getvalue() == "", (
                f"Importing tasklib packages produced stdout: {captured_stdout.getvalue()!r}"
            )
            assert captured_stderr.getvalue() == "", (
                f"Importing tasklib packages produced stderr: {captured_stderr.getvalue()!r}"
            )
        finally:
            for mod_name, mod in saved_modules.items():
                sys.modules[mod_name] = mod
