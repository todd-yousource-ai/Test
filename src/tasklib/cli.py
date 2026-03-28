"""Command-line interface for the task library.

Security assumptions:
- All command-line input is untrusted and is parsed strictly via argparse.
- User-provided strings are rendered as plain text only and are never executed.

Failure behavior:
- Argument parsing errors are handled by argparse and exit with code 2.
- Missing task identifiers fail closed with an explicit stderr message and exit code 1.
- Unexpected store or model errors are not swallowed; they surface to the caller.
"""

from __future__ import annotations

import argparse
import sys

from tasklib.storage import InMemoryTaskStore


def _extract_task_id(task: object) -> str:
    """Return the task identifier from a task-like object.

    Failure behavior:
    - Raises AttributeError if the task does not expose an ``id`` attribute.
    - Does not infer alternate identifier fields to avoid ambiguous behavior.
    """
    return str(getattr(task, "id"))


def _extract_task_title(task: object) -> str:
    """Return the task title from a task-like object.

    Failure behavior:
    - Raises AttributeError if the task does not expose a ``title`` attribute.
    """
    return str(getattr(task, "title"))


def _extract_task_status(task: object) -> str:
    """Return a human-readable status value from a task-like object.

    Failure behavior:
    - Raises AttributeError if the task does not expose a ``status`` attribute.
    """
    status = getattr(task, "status")
    return str(getattr(status, "value", status))


def _format_task(task: object) -> str:
    """Format a task for human-readable CLI output.

    Security assumptions:
    - Task fields are treated as untrusted plain text and interpolated without
      evaluation or shell interpretation.

    Failure behavior:
    - Raises AttributeError if required task attributes are absent.
    """
    return f"{_extract_task_id(task)}\t{_extract_task_status(task)}\t{_extract_task_title(task)}"


def handle_add(args: argparse.Namespace, store: InMemoryTaskStore) -> int:
    """Create a task from parsed CLI arguments.

    Failure behavior:
    - Propagates store errors with full context rather than failing silently.
    """
    description = getattr(args, "description", None)
    task = store.add(args.title, description=description)
    print(f"Created task {_extract_task_id(task)}: {_extract_task_title(task)}")
    return 0


def handle_list(args: argparse.Namespace, store: InMemoryTaskStore) -> int:
    """List tasks in a grep-friendly plain-text format.

    Failure behavior:
    - Propagates store errors with full context rather than failing silently.
    """
    del args
    tasks = store.list_all()
    if not tasks:
        print("No tasks found.")
        return 0

    for task in tasks:
        print(_format_task(task))
    return 0


def handle_complete(args: argparse.Namespace, store: InMemoryTaskStore) -> int:
    """Mark a task as complete.

    Failure behavior:
    - If the task cannot be found, writes an explicit error to stderr and
      returns exit code 1.
    - Propagates unexpected store errors rather than swallowing them.
    """
    task = store.get(args.task_id)
    if task is None:
        print(f"Task not found: {args.task_id}", file=sys.stderr)
        return 1

    completed_task = store.complete(args.task_id)
    if completed_task is None:
        print(f"Task not found: {args.task_id}", file=sys.stderr)
        return 1

    print(f"Completed task {_extract_task_id(completed_task)}: {_extract_task_title(completed_task)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Security assumptions:
    - Only the declared subcommands and arguments are accepted.
    - Unrecognized input is rejected by argparse.

    Failure behavior:
    - Parser validation errors are delegated to argparse, which exits with code 2.
    """
    parser = argparse.ArgumentParser(prog="tasklib")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--description")
    add_parser.set_defaults(func=handle_add)

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=handle_list)

    complete_parser = subparsers.add_parser("complete")
    complete_parser.add_argument("task_id")
    complete_parser.set_defaults(func=handle_complete)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point suitable for console_scripts and module execution.

    Security assumptions:
    - A fresh in-memory store is created per invocation to avoid shared mutable
      global state across runs.

    Failure behavior:
    - Returns handler exit codes directly.
    - If no subcommand is provided, prints help and returns 0.
    - Does not suppress unexpected exceptions.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    store = InMemoryTaskStore()
    return int(args.func(args, store))


if __name__ == "__main__":
    raise SystemExit(main())