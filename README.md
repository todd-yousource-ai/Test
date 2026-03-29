# tasklib — Task Management Library

A deliberately simple Python task management library designed to validate that the Crafted Dev Agent build pipeline can close a complete dependency chain from documentation through scaffold to working code.

## What It Does

tasklib validates the Crafted Dev Agent pipeline end-to-end by exercising a full dependency chain: docs → scaffold → model → storage → CLI. It proves that documentation PRs fire merge gates, scaffold PRs mirror files correctly, and code PRs resolve imports from previously-merged PRs before CI. The library itself is not a production system — it exists to confirm the pipeline works with real merges at each step.

## Key Subsystems

- **Documentation Set** — README, ARCHITECTURE overview, and API reference that trigger the initial merge gate
- **Package Scaffold** — Python package with subpackage directories, mirrored to the local test workspace
- **Model** — Core task data model that downstream code PRs depend on
- **Storage** — Persistence layer that imports from the model, validating cross-PR import resolution
- **CLI** — Command-line interface that closes the dependency chain by consuming storage and model

## Architecture Overview

tasklib follows a linear dependency chain where each layer depends only on the layers before it: documentation is merged first, then the scaffold, then model, storage, and CLI in sequence. Each step validates a specific capability of the Crafted Dev Agent pipeline — merge gate detection, file mirroring, and local import resolution. The architecture is intentionally minimal to isolate pipeline validation from application complexity.

## Repository Structure

```
crafted-docs/          — source TRDs and PRDs
crafted-standards/     — architecture, interfaces, decisions, conventions
CLAUDE.md              — LLM coding instructions (read this first)
src/                   — implementation
tests/                 — test suite
.github/workflows/     — CI
```

## Getting Started

- Read `CLAUDE.md` before writing any code — it contains LLM coding instructions and conventions
- Review `crafted-docs/TRD-TASKLIB.md` to understand the validation goals and dependency chain
- Review `crafted-docs/forge_architecture_context.md` for pipeline architecture context
- The full dependency chain is: docs → scaffold → model → storage → CLI — PRs should follow this order
- Run the test suite in `tests/` to verify import resolution and merge gate behavior

## Documentation

| Document | Location | What It Contains |
|----------|----------|------------------|
| TRD-TASKLIB | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Core TRD defining the task management library, validation goals, and dependency chain |
| Architecture Context | `crafted-docs/forge_architecture_context.md` | Pipeline architecture context for the Crafted Dev Agent build system |

## Where to Go Next

- `CLAUDE.md` — start here before writing any code
- `crafted-standards/ARCHITECTURE.md` — full system architecture
- `crafted-standards/INTERFACES.md` — wire formats and API contracts
- `crafted-docs/` — complete TRDs and PRDs