# tasklib Architecture

## Overview

tasklib exists to validate the Crafted Dev Agent build pipeline end-to-end. Its architecture is intentionally layered so that each layer is delivered as a separate PR, each PR fires its own merge gate, and each gate must pass before downstream PRs can proceed. This proves that the pipeline correctly handles multi-step dependency chains with real merges at every step.

## Five-Layer Dependency Chain

The build is organized into five layers, each corresponding to a single PR:

```
┌─────────────────────────────────────────────────┐
│  Layer 5: CLI                                   │
│  cli.py -- add, list, complete subcommands       │
│  Depends on: storage                            │
├─────────────────────────────────────────────────┤
│  Layer 4: Storage                               │
│  storage/store.py -- InMemoryTaskStore           │
│  Depends on: model                              │
├─────────────────────────────────────────────────┤
│  Layer 3: Model                                 │
│  models/task.py -- Task dataclass, TaskStatus    │
│  Depends on: scaffold                           │
├─────────────────────────────────────────────────┤
│  Layer 2: Scaffold                              │
│  Package directory tree with __init__.py files  │
│  Depends on: docs                               │
├─────────────────────────────────────────────────┤
│  Layer 1: Docs                                  │
│  README.md, ARCHITECTURE.md, API.md             │
│  Depends on: -- (chain root)                     │
└─────────────────────────────────────────────────┘
```

**Merge order (bottom to top):** docs → scaffold → model → storage → CLI

Each layer is a separate PR with its own merge gate. No layer can merge until the layer below it has merged successfully.

## Layer Descriptions

### Layer 1 -- Docs (this PR)

**What it contains:** `docs/tasklib/README.md`, `docs/tasklib/ARCHITECTURE.md`, `docs/tasklib/API.md`.

**What it validates:** The merge gate fires and passes for a docs-only PR that contains no code and no tests. This proves the pipeline does not require executable artifacts to function.

**Depends on:** Nothing. This is the chain root.

### Layer 2 -- Scaffold

**What it contains:** The `src/tasklib/` directory tree with empty `__init__.py` files for the package root, `models/`, and `storage/` subpackages.

**What it validates:** The merge gate fires and passes for a structural-only PR that creates directories and empty init files. The package is importable but contains no logic.

**Depends on:** Docs (Layer 1).

### Layer 3 -- Model

**What it contains:** `src/tasklib/models/task.py` defining the `TaskStatus` enumeration and the `Task` dataclass.

**What it validates:** The first code PR in the chain. Proves that the pipeline can run tests against a model layer that has no dependencies beyond the standard library. The `Task` dataclass and `TaskStatus` enum become importable.

**Depends on:** Scaffold (Layer 2).

### Layer 4 -- Storage

**What it contains:** `src/tasklib/storage/store.py` defining `InMemoryTaskStore` with `add`, `get`, `list_all`, `complete`, and `delete` methods.

**What it validates:** A code PR that depends on the model layer. Proves the pipeline correctly resolves intra-package imports across PR boundaries.

**Depends on:** Model (Layer 3).

### Layer 5 -- CLI

**What it contains:** `src/tasklib/cli.py` providing `add`, `list`, and `complete` subcommands.

**What it validates:** The final layer in the chain. Proves the full dependency chain closes: documentation → structure → model → storage → user-facing interface, all merged through individual gates.

**Depends on:** Storage (Layer 4).

## Dependency Diagram (ASCII)

```
  docs
    │
    ▼
  scaffold
    │
    ▼
  model (Task, TaskStatus)
    │
    ▼
  storage (InMemoryTaskStore)
    │
    ▼
  CLI (add, list, complete)
```

Nothing in the dependency graph is circular. Each component depends only on the components below it.

## Public API Surface

The package root `tasklib.__init__` re-exports the two primary public symbols:

| Symbol             | Source Module              | Description                              |
|