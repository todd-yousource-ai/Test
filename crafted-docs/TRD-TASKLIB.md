# TRD-TASKLIB

_Source: `TRD-TASKLIB.docx` — extracted 2026-03-28 20:27 UTC_

---

TRD-TASKLIB

Task Management Library

Version | 1.0
Status | Draft
Author | Todd Gould / YouSource.ai
Date | 2026-03-26
Purpose | Validation TRD — proves Crafted Dev Agent pipeline end-to-end

# 1. Purpose and Scope

This TRD defines a deliberately simple Python task management library (tasklib). It is not a production system. Its purpose is to validate that the Crafted Dev Agent build pipeline can close a complete dependency chain — from documentation through scaffold to working code — with real merges at each step.

Validation goals:

A documentation PR fires the merge gate and downstream PRs recognize the merge

A scaffold PR with multiple package directories mirrors files to the local test workspace

Code PRs that import from previously-merged PRs resolve those imports locally before CI

The full dependency chain closes: docs → scaffold → model → storage → CLI

In scope:

A documentation set: README, ARCHITECTURE overview, API reference

Python package scaffold with subpackage directories

Task model: identifier, title, status, and creation timestamp

In-memory task store: add, retrieve, list, complete, and delete operations

CLI entry point: add, list, and complete commands

Out of scope:

Persistence to disk or any database

Authentication or multi-user support

Any dependency outside the Python standard library

# 2. Architecture

## 2.1 Package Structure

The library follows a standard Python package layout under src/:

src/

tasklib/

__init__.py          — package root, re-exports public API

models/

__init__.py

task.py            — Task dataclass and status enumeration

storage/

__init__.py

store.py           — InMemoryTaskStore

cli.py               — CLI entry point

## 2.2 Dependency Relationships

Each component depends on the components below it. Nothing in the dependency graph is circular.

Component | Depends On | Description
docs | — | README, ARCHITECTURE overview, API reference markdown
scaffold | — | Package directory tree with empty __init__.py files
task.py | scaffold | Task dataclass and TaskStatus enumeration
store.py | task.py | InMemoryTaskStore — imports Task from models
cli.py | store.py | CLI entry point — imports InMemoryTaskStore from storage

# 3. Functional Requirements

## 3.1 Task Model

The task model represents a single unit of work. It must be self-contained and carry enough information to describe its identity, content, lifecycle state, and creation time without reference to any external system.

Fields:

FR-1  Each task has a unique identifier generated automatically on creation.

FR-2  Each task has a title that is required and must be non-empty.

FR-3  Each task has a status that is constrained to a defined set of values: pending, in_progress, and done. The default status at creation is pending.

FR-4  Each task records the time it was created as a numeric timestamp.

Behavior:

FR-5  Task status values must be defined as an enumeration, not as free-form strings, to prevent invalid states.

FR-6  The task model must support serialization to and deserialization from a plain dictionary so it can be stored, logged, or transmitted without external libraries.

FR-7  Constructing a task with an invalid status value must raise an error immediately.

## 3.2 Task Store

The task store manages the collection of tasks in memory for the duration of a process. It is the single source of truth for task state within a session.

FR-8  The store must support adding a new task by title, returning the created task.

FR-9  The store must support retrieving a single task by its identifier, returning nothing if the identifier does not exist.

FR-10  The store must support listing all tasks, ordered by creation time ascending.

FR-11  The store must support listing tasks filtered by a given status.

FR-12  The store must support marking a task as complete by identifier. If the identifier does not exist, the operation must fail with a clear error.

FR-13  The store must support removing a task by identifier, indicating whether the task existed.

FR-14  The store must import the Task type from the models layer, not redefine it.

## 3.3 CLI

The CLI provides a minimal command-line interface for manual interaction with the task store. It is intended for demonstration and validation, not production use.

FR-15  The CLI must be runnable as a Python module.

FR-16  The CLI must support an add command that accepts a title and confirms the created task.

FR-17  The CLI must support a list command that displays all pending and in-progress tasks.

FR-18  The CLI must support a complete command that accepts a task identifier and confirms completion.

FR-19  The CLI must import its store from the storage layer, not implement storage directly.

## 3.4 Package Root

The package root makes the public API accessible at the top level. Consumers should be able to import Task and InMemoryTaskStore directly from tasklib without knowing the internal module structure.

FR-20  The package root must re-export Task and InMemoryTaskStore as its public API.

# 4. Non-Functional Requirements

NFR-1  Zero external dependencies. The implementation must use only the Python standard library.

NFR-2  All modules must be importable without side effects. No code runs at import time beyond class and function definitions.

NFR-3  Every public function and class must have a docstring describing its purpose.

NFR-4  Status values must be referenced via the enumeration throughout the codebase. Magic strings for status are not permitted.

# 5. Acceptance Criteria

These criteria apply to the completed library as a whole, not to individual PRs. The agent is expected to decompose these into per-PR acceptance criteria appropriate to each component.

## Documentation

README.md describes the library purpose, package structure, and provides a working usage example

ARCHITECTURE.md describes the layered design and explains why each layer exists

API.md documents the Task fields, store methods, and CLI commands with enough detail to use them without reading the source

## Package Scaffold

src/tasklib/ and all subpackage directories exist and are importable as Python packages

No subpackage has executable code at import time

## Task Model

A Task can be created with only a title; id, status, and created_at are populated automatically

TaskStatus enumeration prevents construction with invalid status values

A task serialized to a dictionary and then deserialized produces an equivalent task

## Task Store

Tasks added to the store are retrievable by their identifier

Listing all tasks returns them in creation order, oldest first

Completing a task changes its status to done

Completing a non-existent task raises KeyError

Deleting a task returns True; deleting again returns False

## CLI

The add command produces output that includes the new task's identifier and title

The list command shows only tasks that are not yet done

The complete command produces output confirming the task title was completed

All imports resolve correctly assuming the dependency chain has been merged in order

# 6. Implementation Notes

This library is intentionally minimal. Implementors should resist the urge to add error handling, logging, configuration, or features beyond what is specified. The goal is the simplest possible codebase that exercises the full pipeline dependency chain.

The agent should decompose these requirements into no more than 3 implementation files per PR and no more than 6 acceptance criteria per PR. If a natural decomposition would exceed these limits, split the work into a smaller scope before generating code.

Because this is a validation project, test quality matters as much as implementation quality. Tests that check behavior rather than implementation details — for example, testing that a completed task is no longer returned by list_by_status(“pending”) rather than testing internal dictionary keys — will produce more reliable results across the dependency chain.

# 7. Open Questions

None. This specification is complete by design. Ambiguity would undermine the validation purpose.