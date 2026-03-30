"""CLI entry point for tasklib providing command-line task management.

Security assumptions:
- All input arrives via argparse which handles basic validation and escaping.
- No secrets or credentials are involved in this module.
- The in-memory store has no persistence; each invocation starts fresh.
- All errors are surfaced explicitly to stderr with non-zero exit codes.
- No shell execution or external process invocation occurs.

Failure behavior:
- Invalid subcommand or missing arguments: argparse prints usage to stderr, exit 2.
- No subcommand provided: help printed to stderr, exit 1.
- Non-existent task_id on update/delete: error to stderr, exit 1.
- Invalid status value on update: error to stderr, exit 1.
- Unexpected exceptions propagate without suppression.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from tasklib.models.task import TaskStatus
from tasklib.storage.memory import InMemoryTaskStore


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser with four subcommands.

    Subcommands:
        add     -- Create a new task with a title and optional description.
        list    -- List all tasks in the store.
        update  -- Update the status of an existing task.
        delete  -- Delete an existing task by id.

    Returns:
        Fully configured ``argparse.ArgumentParser``.
    """
    parser = argparse.ArgumentParser(
        prog="tasklib",
        description="Task management CLI for tasklib.",
    )

    subparsers = parser.add_subparsers(dest="command")

    # add subcommand
    add_parser = subparsers.add_parser("add", help="Create a new task.")
    add_parser.add_argument("title", help="Title of the task.")
    add_parser.add_argument(
        "--description", default="", help="Optional description of the task."
    )

    # list subcommand
    subparsers.add_parser("list", help="List all tasks.")

    # update subcommand
    update_parser = subparsers.add_parser(
        "update", help="Update the status of an existing task."
    )
    update_parser.add_argument("task_id", help="ID of the task to update.")
    update_parser.add_argument(
        "status",
        help="New status for the task (todo, in_progress, done).",
    )

    # delete subcommand
    delete_parser = subparsers.add_parser(
        "delete", help="Delete an existing task by id."
    )
    delete_parser.add_argument("task_id", help="ID of the task to delete.")

    return parser


def handle_add(args: argparse.Namespace, store: InMemoryTaskStore) -> int:
    """Handle the 'add' subcommand.

    Creates a new task with the given title and optional description,
    adds it to the store, and prints the created task to stdout.

    Returns:
        0 on success.
    """
    task = store.add(args.title, args.description)
    print(f"{task.task_id} {task.title} {task.status.value}")
    return 0


def handle_list(args: argparse.Namespace, store: InMemoryTaskStore) -> int:
    """Handle the 'list' subcommand.

    Lists all tasks currently in the store, printing each task's
    id, title, and status to stdout. Prints 'No tasks found.' if
    the store is empty.

    Returns:
        0 on success.
    """
    tasks = store.list_tasks()
    if not tasks:
        print("No tasks found.")
    else:
        for task in tasks:
            print(f"{task.task_id} {task.title} {task.status.value}")
    return 0


def handle_update(args: argparse.Namespace, store: InMemoryTaskStore) -> int:
    """Handle the 'update' subcommand.

    Updates the status of an existing task identified by task_id.

    Returns:
        0 on success, 1 on error (invalid status or non-existent task).
    """
    # Validate status value
    try:
        new_status = TaskStatus(args.status)
    except ValueError:
        valid = ", ".join(s.value for s in TaskStatus)
        print(
            f"Error: Invalid status '{args.status}'. Valid values: {valid}",
            file=sys.stderr,
        )
        return 1

    task = store.update_status(args.task_id, new_status)
    if task is None:
        print(
            f"Error: Task with id '{args.task_id}' not found.",
            file=sys.stderr,
        )
        return 1

    print(f"{task.task_id} {task.status.value}")
    return 0


def handle_delete(args: argparse.Namespace, store: InMemoryTaskStore) -> int:
    """Handle the 'delete' subcommand.

    Deletes an existing task identified by task_id.

    Returns:
        0 on success, 1 if the task does not exist.
    """
    result = store.delete(args.task_id)
    if not result:
        print(
            f"Error: Task with id '{args.task_id}' not found.",
            file=sys.stderr,
        )
        return 1

    print(f"Deleted {args.task_id}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Main entry point for the tasklib CLI.

    Parses arguments, dispatches to the appropriate handler, and returns
    an integer exit code.

    Args:
        argv: Command-line arguments. Defaults to ``sys.argv[1:]``.

    Returns:
        Integer exit code (0 for success, non-zero for errors).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help(sys.stderr)
        return 1

    store = InMemoryTaskStore()

    handlers = {
        "add": handle_add,
        "list": handle_list,
        "update": handle_update,
        "delete": handle_delete,
    }

    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help(sys.stderr)
        return 1

    return handler(args, store)


if __name__ == "__main__":
    sys.exit(main())
