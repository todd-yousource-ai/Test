# tasklib Architecture

This document describes the layered architecture, package directory structure, inter-layer dependency rules, and design rationale.

For the library overview and quickstart, see [README.md](README.md).
For the complete public API reference, see [API.md](API.md).

## Overview

tasklib is organized into three layers with strictly controlled dependencies. Each layer has a single responsibility and communicates only with the layer directly below it.

## Three-Layer Architecture

```
┌─────────────────────────────────┐
│            CLI Layer            │   User-facing command-line interface
│          (cli.py)               │   Depends on: Storage
├─────────────────────────────────┤
│         Storage Layer           │   In-memory task persistence
│     (storage/store.py)          │   Depends on: Model
├─────────────────────────────────┤
│          Model Layer            │   Core data types and enumerations
│      (models/task.py)           │   Depends on: nothing
└─────────────────────────────────┘
```

### Model Layer

Defines the core data types: `TaskStatus` enumeration and `Task` dataclass. Has **no internal dependencies** -- depends only on the Python standard library (`dataclasses`, `enum`, `datetime`, `uuid`).

**Responsibility:** Define what a task is -- its identity, content, status, and creation time.

**Location:** `src/tasklib/models/task.py`

### Storage Layer

Provides `InMemoryTaskStore`, which manages a collection of `Task` objects in memory. Depends on the **Model** layer to create and manipulate `Task` instances.

**Responsibility:** Create, retrieve, list, complete, and delete tasks.

**Location:** `src/tasklib/storage/store.py`

### CLI Layer

Provides a command-line interface for interacting with the task store. Depends on the **Storage** layer (and transitively on Model) to execute user commands.

**Responsibility:** Parse command-line arguments and translate them into store operations.

**Location:** `src/tasklib/cli.py`

**Entry point:** `src/tasklib/__main__.py` -- delegates to `cli.py`, enabling `python -m tasklib` invocation.

## Package Directory Structure

Complete package layout under `src/` as defined in TRD-TASKLIB section 2.1:

```
src/
  tasklib/
    __init__.py              -- Package root, re-exports public API
    __main__.py              -- Module execution entry point (python -m tasklib)
    models/
      __init__.py            -- Models subpackage init
      task.py                -- Task dataclass and TaskStatus enumeration
    storage/
      __init__.py            -- Storage subpackage init
      store.py               -- InMemoryTaskStore
    cli.py                   -- CLI implementation
```

### File Purposes

| File | Purpose |
|