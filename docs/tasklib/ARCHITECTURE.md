# tasklib -- Architecture

## Overview

`tasklib` is organized as a four-layer dependency chain. Each layer builds on the one below it. The ordering is deliberate: it mirrors the sequence in which the Crafted Dev Agent pipeline produces and merges PRs, validating that each link in the chain resolves cleanly before the next begins.

## Layer Diagram

```
┌─────────────────────────────────────────────────┐
│  Layer 1: docs                                  │
│  README.md, ARCHITECTURE.md, API.md             │
│  Depends on: nothing                            │
├─────────────────────────────────────────────────┤
│  Layer 2: scaffold                              │
│  Package directory tree with __init__.py files  │
│  Depends on: nothing                            │
├─────────────────────────────────────────────────┤
│  Layer 3: model                                 │
│  Task dataclass, TaskStatus enum (task.py)      │
│  Depends on: scaffold                           │
├─────────────────────────────────────────────────┤
│  Layer 4: storage                               │
│  InMemoryTaskStore (store.py)                   │
│  Depends on: model                              │
├─────────────────────────────────────────────────┤
│  Layer 5: CLI                                   │
│  cli.py entry point                             │
│  Depends on: storage, model                     │
└─────────────────────────────────────────────────┘
```

The full dependency chain is:

> **docs → scaffold → model → storage → CLI**

Each arrow represents a "must exist and be merged before" relationship.

## No-Circular-Dependency Invariant

**No circular dependencies are permitted anywhere in the `tasklib` dependency graph.** Lower layers must never import from or depend on higher layers. This invariant is absolute and must hold at all times -- violation constitutes a build failure.

Formally: if layer A depends on layer B, then layer B must **not** depend on layer A, either directly or transitively.

## Dependency Rules

The following table defines the complete set of allowed import relationships between layers. Any import not listed here is **prohibited**.

| Layer | May Import From | Must Not Import From |
|