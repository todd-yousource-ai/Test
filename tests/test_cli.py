"""Tests for tasklib.cli - CLI entry point with add, list, and complete commands."""

from __future__ import annotations

import argparse
import sys
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Project-root discovery (walk up from this file until pyproject.toml found)
# ---------------------------------------------------------------------------
PROJECT_ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------
from tasklib.cli import (
    _format_task,
    build_parser,
    handle_add,
    handle_complete,
    handle_list,
    main,
)
from tasklib.storage import InMemoryTaskStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_main(argv: list[str]) -> tuple[int, str, str]:
    """Run ``main(argv)`` capturing stdout, stderr and return code.

    Returns (exit_code, stdout_text, stderr_text).
    SystemExit is caught and its code returned; any other exception propagates.
    """
    out, err = StringIO(), StringIO()
    with patch.object(sys, "stdout", out), patch.object(sys, "stderr", err):
        try:
            rc = main(argv)
            if rc is None:
                rc = 0
        except SystemExit as exc:
            rc = exc.code if exc.code is not None else 0
    return rc, out.getvalue(), err.getvalue()


# ===========================================================================
# build_parser
# ===========================================================================

class TestBuildParser:
    def test_build_parser_returns_argument_parser(self):
        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_build_parser_has_exactly_three_subcommands(self):
        parser = build_parser()
        # Walk parser's _subparsers actions to collect registered subcommands
        subparsers_actions = [
            action
            for action in parser._subparsers._actions
            if isinstance(action, argparse._SubParsersAction)
        ]
        assert len(subparsers_actions) == 1, "Expected exactly one _SubParsersAction"
        choices = subparsers_actions[0].choices
        assert set(choices.keys()) == {"add", "list", "complete"}


# ===========================================================================
# add subcommand
# ===========================================================================

class TestAdd:
    def test_add_prints_created_task_with_id_and_title(self):
        rc, out, _ = _run_main(["add", "--title", "Buy milk"])
        assert rc == 0
        assert "Created task" in out
        assert "Buy milk" in out

    def test_add_with_description_creates_task_successfully(self):
        rc, out, _ = _run_main(
            ["add", "--title", "Read book", "--description", "Chapter 5"]
        )
        assert rc == 0
        assert "Read book" in out

    def test_add_without_title_exits_with_error_code_2(self):
        rc, _, _ = _run_main(["add"])
        assert rc == 2


# ===========================================================================
# list subcommand
# ===========================================================================

class TestList:
    def test_list_empty_store_prints_no_tasks_message(self):
        rc, out, _ = _run_main(["list"])
        assert rc == 0
        assert "No tasks" in out

    def test_list_shows_all_tasks_with_status(self):
        """Manually use handle_add + handle_list with a shared store."""
        store = InMemoryTaskStore()
        # Add two tasks via handler
        ns_add1 = argparse.Namespace(title="Task A", description=None)
        ns_add2 = argparse.Namespace(title="Task B", description=None)
        handle_add(ns_add1, store)
        handle_add(ns_add2, store)

        out = StringIO()
        with patch.object(sys, "stdout", out):
            rc = handle_list(argparse.Namespace(), store)

        assert rc == 0
        text = out.getvalue()
        assert "Task A" in text
        assert "Task B" in text
        # Each line should contain a tab-separated status value
        lines = [l for l in text.strip().splitlines() if l.strip()]
        assert len(lines) == 2
        for line in lines:
            parts = line.split("\t")
            assert len(parts) == 3  # id, status, title


# ===========================================================================
# complete subcommand
# ===========================================================================

class TestComplete:
    def test_complete_marks_task_and_prints_confirmation(self):
        store = InMemoryTaskStore()
        ns = argparse.Namespace(title="Finish PR", description=None)
        handle_add(ns, store)
        tasks = store.list_all()
        task_id = str(getattr(tasks[0], "id"))

        out = StringIO()
        with patch.object(sys, "stdout", out):
            rc = handle_complete(argparse.Namespace(task_id=task_id), store)

        assert rc == 0
        assert "Completed" in out.getvalue() or "complete" in out.getvalue().lower()

    def test_complete_nonexistent_id_exits_with_code_1(self):
        store = InMemoryTaskStore()
        err = StringIO()
        with patch.object(sys, "stderr", err):
            rc = handle_complete(
                argparse.Namespace(task_id="nonexistent-999"), store
            )
        assert rc == 1
        assert "nonexistent-999" in err.getvalue() or "not found" in err.getvalue().lower()

    def test_complete_without_task_id_arg_exits_with_code_2(self):
        rc, _, _ = _run_main(["complete"])
        assert rc == 2


# ===========================================================================
# No subcommand / unknown subcommand
# ===========================================================================

class TestNoSubcommand:
    def test_no_subcommand_prints_help_and_exits(self):
        rc, out, err = _run_main([])
        # argparse may exit 2 or the implementation may exit non-zero
        assert rc != 0
        # Usage info should appear in stdout or stderr
        combined = out + err
        assert "usage" in combined.lower() or "help" in combined.lower() or len(combined) > 0

    def test_unknown_subcommand_exits_with_argparse_error(self):
        rc, _, err = _run_main(["frobnicate"])
        assert rc == 2


# ===========================================================================
# main() interface
# ===========================================================================

class TestMain:
    def test_main_callable_with_argv_parameter(self):
        """main() accepts an explicit argv list so callers don't need sys.argv."""
        rc, out, _ = _run_main(["add", "--title", "Callable test"])
        assert rc == 0
        assert "Callable test" in out

    def test_main_returns_zero_on_successful_commands(self):
        rc, _, _ = _run_main(["list"])
        assert rc == 0


# ===========================================================================
# _format_task
# ===========================================================================

class TestFormatTask:
    def test_format_task_renders_all_fields_as_plain_text(self):
        """_format_task should produce a tab-separated line: id\tstatus\ttitle."""
        task = SimpleNamespace(id="abc-123", status="pending", title="Do laundry")
        result = _format_task(task)
        assert "abc-123" in result
        assert "pending" in result
        assert "Do laundry" in result
        # Tab-separated
        parts = result.split("\t")
        assert len(parts) == 3

    def test_format_task_handles_enum_status(self):
        """When status is an enum-like object with a .value attribute."""
        from enum import Enum

        class Status(Enum):
            OPEN = "open"

        task = SimpleNamespace(id="1", status=Status.OPEN, title="Enum task")
        result = _format_task(task)
        assert "open" in result

    def test_format_task_raises_on_missing_attribute(self):
        task = SimpleNamespace(id="1")  # no title, no status
        with pytest.raises(AttributeError):
            _format_task(task)


# ===========================================================================
# Security: plain-text rendering
# ===========================================================================

class TestSecurityPlainText:
    """Ensure user-provided strings are rendered verbatim, not evaluated."""

    @pytest.mark.parametrize(
        "malicious_title",
        [
            "{__import__('os').system('echo pwned')}",
            "$(whoami)",
            "`id`",
            "%s%s%s%s%s",
            "${7*7}",
            "{{config}}",
            "<script>alert(1)</script>",
        ],
    )
    def test_cli_output_renders_title_as_plain_text(self, malicious_title: str):
        rc, out, _ = _run_main(["add", "--title", malicious_title])
        assert rc == 0
        # The malicious string must appear verbatim, not evaluated
        assert malicious_title in out

    def test_cli_output_renders_description_as_plain_text(self):
        desc = "{__import__('os').system('rm -rf /')}"
        rc, out, _ = _run_main(["add", "--title", "Safe", "--description", desc])
        assert rc == 0
        # Description is stored but the add confirmation prints title, just
        # make sure nothing crashed and the command succeeded.
        assert "Safe" in out

    def test_format_task_does_not_evaluate_format_strings(self):
        evil = "{0.__class__.__mro__}"
        task = SimpleNamespace(id="x", status="open", title=evil)
        result = _format_task(task)
        # Must contain the literal string, not its evaluation
        assert evil in result
