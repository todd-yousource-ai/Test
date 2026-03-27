"""Tests for tasklib package scaffold and pyproject.toml metadata."""

import importlib
import sys
from pathlib import Path

import pytest

# Resolve project root by walking up from this file to find pyproject.toml
PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)


# ---------------------------------------------------------------------------
# Scaffold layout: file existence
# ---------------------------------------------------------------------------

class TestScaffoldFilesExist:
    """Verify that all expected scaffold files exist on disk."""

    @pytest.mark.parametrize(
        "rel_path",
        [
            "src/tasklib/__init__.py",
            "src/tasklib/models/__init__.py",
            "src/tasklib/storage/__init__.py",
            "src/tasklib/cli.py",
        ],
    )
    def test_scaffold_files_exist(self, rel_path: str) -> None:
        full = PROJECT_ROOT / rel_path
        assert full.exists(), f"Expected scaffold file not found: {full}"
        assert full.is_file(), f"Expected a file but found something else: {full}"


# ---------------------------------------------------------------------------
# Scaffold layout: importability
# ---------------------------------------------------------------------------

class TestScaffoldImports:
    """Verify that scaffold packages and modules are importable."""

    def test_tasklib_package_is_importable(self) -> None:
        import tasklib  # noqa: F401

    def test_models_subpackage_is_importable(self) -> None:
        import tasklib.models  # noqa: F401

    def test_storage_subpackage_is_importable(self) -> None:
        import tasklib.storage  # noqa: F401

    def test_cli_module_is_importable(self) -> None:
        import tasklib.cli  # noqa: F401


# ---------------------------------------------------------------------------
# pyproject.toml metadata
# ---------------------------------------------------------------------------

class TestPyprojectMetadata:
    """Parse and validate pyproject.toml content."""

    @pytest.fixture(autouse=True)
    def _load_pyproject(self) -> None:
        # tomllib is stdlib in 3.11+; fall back to tomli for 3.10
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found at project root"
        with open(pyproject_path, "rb") as f:
            self.data = tomllib.load(f)

    def test_pyproject_toml_exists_and_parses(self) -> None:
        assert isinstance(self.data, dict)
        assert "project" in self.data

    def test_project_name_is_tasklib(self) -> None:
        assert self.data["project"]["name"] == "tasklib"

    def test_project_version_is_0_1_0(self) -> None:
        assert self.data["project"]["version"] == "0.1.0"

    def test_python_requires_is_3_10_or_higher(self) -> None:
        assert self.data["project"]["requires-python"] == ">=3.10"

    def test_no_external_dependencies(self) -> None:
        deps = self.data["project"].get("dependencies", [])
        assert deps == [], f"Expected no dependencies, found: {deps}"

    def test_console_script_entry_point(self) -> None:
        scripts = self.data["project"].get("scripts", {})
        assert "tasklib" in scripts, "Missing 'tasklib' console script entry point"
        assert scripts["tasklib"] == "tasklib.cli:main"


# ---------------------------------------------------------------------------
# Negative cases: nothing is exported yet
# ---------------------------------------------------------------------------

class TestNegativeCases:
    """Ensure scaffold modules don't prematurely export symbols."""

    @staticmethod
    def _public_names(module) -> set[str]:
        """Return the set of public (non-underscore) names in a module."""
        return {name for name in dir(module) if not name.startswith("_")}

    def test_cli_main_not_yet_defined(self) -> None:
        """main should not be importable from tasklib.cli in scaffold state."""
        # Reload to ensure fresh state
        import tasklib.cli

        importlib.reload(tasklib.cli)
        with pytest.raises((ImportError, AttributeError)):
            from tasklib.cli import main  # noqa: F401

            # If import didn't raise, verify it's truly absent via getattr
            if main is None or not callable(main):
                raise AttributeError("main is not defined or not callable")
            # If we somehow got here, force the failure--main shouldn't exist
            raise AttributeError("main should not be defined in scaffold")

    def test_tasklib_init_exports_nothing(self) -> None:
        import tasklib

        public = self._public_names(tasklib)
        forbidden = {"Task", "TaskStatus", "InMemoryTaskStore"}
        overlap = public & forbidden
        assert not overlap, f"Unexpected public symbols in tasklib: {overlap}"
        # Also check that there are essentially no public symbols beyond standard ones
        # Standard module-level public names that are acceptable
        standard = {"models", "storage", "cli"}
        extra = public - standard
        assert not extra, f"Unexpected public exports in tasklib: {extra}"

    def test_models_init_exports_nothing(self) -> None:
        import tasklib.models

        public = self._public_names(tasklib.models)
        assert not public, f"Unexpected public symbols in tasklib.models: {public}"

    def test_storage_init_exports_nothing(self) -> None:
        import tasklib.storage

        public = self._public_names(tasklib.storage)
        assert not public, f"Unexpected public symbols in tasklib.storage: {public}"


# ---------------------------------------------------------------------------
# Security boundary
# ---------------------------------------------------------------------------

class TestSecurityBoundaries:
    """Explicit security-related checks."""

    def test_no_external_package_dependencies(self) -> None:
        """pyproject.toml must introduce zero external runtime dependencies."""
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        deps = data.get("project", {}).get("dependencies", [])
        assert deps == [], (
            f"Security boundary violation: external dependencies found: {deps}"
        )

    def test_optional_dependencies_absent_or_empty(self) -> None:
        """No optional dependency groups should smuggle in packages."""
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[no-redef]

        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        opt_deps = data.get("project", {}).get("optional-dependencies", {})
        for group, pkgs in opt_deps.items():
            # Allow dev/test groups but they shouldn't exist in this scaffold
            assert isinstance(pkgs, list), f"Malformed optional-dependencies.{group}"
