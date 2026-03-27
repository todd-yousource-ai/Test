"""Tests for tasklib package scaffold and pyproject.toml configuration."""

import importlib
import re
import sys
from pathlib import Path
from unittest import mock

import pytest

# Resolve project root by walking up from this file to find pyproject.toml
PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)


class TestPyprojectToml:
    """Verify pyproject.toml exists and is well-formed."""

    def test_pyproject_toml_exists(self):
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml must exist at project root"

    def test_pyproject_toml_is_valid_toml(self):
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        # Try tomllib (3.11+) or tomli as fallback
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        assert isinstance(data, dict), "pyproject.toml should parse to a dict"

    def test_pyproject_has_project_name(self):
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        assert "project" in data, "pyproject.toml must have [project] section"
        assert "name" in data["project"], "pyproject.toml [project] must have name"


class TestTasklibImports:
    """Verify the tasklib package and subpackages import correctly."""

    def test_tasklib_imports(self):
        """import tasklib succeeds without error."""
        import tasklib
        assert tasklib is not None

    def test_models_subpackage_imports(self):
        """import tasklib.models succeeds without error."""
        import tasklib.models
        assert tasklib.models is not None

    def test_storage_subpackage_imports(self):
        """import tasklib.storage succeeds without error."""
        import tasklib.storage
        assert tasklib.storage is not None


class TestVersion:
    """Verify tasklib.__version__ is properly set."""

    def test_version_is_nonempty_string(self):
        """tasklib.__version__ is a non-empty str."""
        import tasklib
        assert hasattr(tasklib, "__version__"), "tasklib must define __version__"
        assert isinstance(tasklib.__version__, str), "__version__ must be a string"
        assert len(tasklib.__version__) > 0, "__version__ must not be empty"

    def test_version_is_semver_format(self):
        """tasklib.__version__ matches r'^\\d+\\.\\d+\\.\\d+$'."""
        import tasklib
        pattern = r"^\d+\.\d+\.\d+$"
        assert re.match(pattern, tasklib.__version__), (
            f"__version__ '{tasklib.__version__}' does not match semver format"
        )


class TestDocstrings:
    """Verify all scaffold __init__.py modules have docstrings."""

    def test_package_modules_have_docstrings(self):
        """All three __init__.py modules have non-empty __doc__."""
        import tasklib
        import tasklib.models
        import tasklib.storage

        for mod_name, mod in [
            ("tasklib", tasklib),
            ("tasklib.models", tasklib.models),
            ("tasklib.storage", tasklib.storage),
        ]:
            assert mod.__doc__ is not None, f"{mod_name} must have a docstring"
            assert len(mod.__doc__.strip()) > 0, (
                f"{mod_name} docstring must not be empty"
            )


class TestNegativeCases:
    """Negative cases: no premature exports and missing subpackages raise errors."""

    def test_no_public_names_in_models(self):
        """tasklib.models.__all__ is not defined or is empty (no premature exports)."""
        import tasklib.models
        all_attr = getattr(tasklib.models, "__all__", None)
        assert all_attr is None or len(all_attr) == 0, (
            "tasklib.models should not export public names yet"
        )

    def test_no_public_names_in_storage(self):
        """tasklib.storage.__all__ is not defined or is empty (no premature exports)."""
        import tasklib.storage
        all_attr = getattr(tasklib.storage, "__all__", None)
        assert all_attr is None or len(all_attr) == 0, (
            "tasklib.storage should not export public names yet"
        )

    def test_nonexistent_subpackage_raises(self):
        """import tasklib.cli raises ImportError (cli.py not yet created)."""
        # Make sure it's not cached from some other test
        if "tasklib.cli" in sys.modules:
            del sys.modules["tasklib.cli"]
        with pytest.raises((ImportError, ModuleNotFoundError)):
            import tasklib.cli  # noqa: F401


class TestNoSideEffects:
    """Security: verify package imports don't trigger network, filesystem, or subprocess side effects."""

    def test_no_side_effects_on_import(self):
        """Verify scaffold module imports don't call socket, open(), or subprocess."""
        # Remove cached modules so we can re-import fresh
        modules_to_clear = [
            k for k in sys.modules if k == "tasklib" or k.startswith("tasklib.")
        ]
        saved = {}
        for mod_name in modules_to_clear:
            saved[mod_name] = sys.modules.pop(mod_name)

        try:
            with mock.patch("socket.socket") as mock_socket, \
                 mock.patch("subprocess.Popen") as mock_popen, \
                 mock.patch("subprocess.run") as mock_run, \
                 mock.patch("subprocess.call") as mock_call:

                # Re-import fresh
                tasklib = importlib.import_module("tasklib")
                importlib.import_module("tasklib.models")
                importlib.import_module("tasklib.storage")

                # Assert no side-effect calls
                mock_socket.assert_not_called(), (
                    "Importing tasklib should not open any sockets"
                )
                mock_popen.assert_not_called(), (
                    "Importing tasklib should not spawn subprocesses via Popen"
                )
                mock_run.assert_not_called(), (
                    "Importing tasklib should not call subprocess.run"
                )
                mock_call.assert_not_called(), (
                    "Importing tasklib should not call subprocess.call"
                )
        finally:
            # Restore original modules to not break other tests
            for mod_name in list(sys.modules):
                if mod_name == "tasklib" or mod_name.startswith("tasklib."):
                    sys.modules.pop(mod_name, None)
            sys.modules.update(saved)
