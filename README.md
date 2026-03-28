# tasklib — Task Management Library

A deliberately simple Python task management library designed to validate that the Crafted Dev Agent build pipeline can close a complete dependency chain from documentation through scaffold to working code.

## What It Does

tasklib validates the Crafted Dev Agent pipeline end-to-end by exercising a full dependency chain: docs → scaffold → model → storage → CLI. It proves that documentation PRs fire merge gates, scaffold PRs mirror files correctly, and code PRs resolve imports from previously-merged PRs before CI. The library itself is not a production system — it exists to confirm the pipeline works with real merges at each step.

## Key Subsystems

- **Documentation Set** — README, ARCHITECTURE overview, and API reference that trigger the initial merge gate
- **Package Scaffold** — Python package with subpackage directories mirrored to the local test workspace
- **Model** — Task data model defining the core domain objects
- **Storage** — Persistence layer for task data
- **CLI** — Command-line interface for interacting with tasks
- **Merge Gate** — Validates that documentation PRs fire downstream recognition and dependency resolution
- **Crafted Dev Agent Pipeline** — Orchestrates the full dependency chain from docs through working code

## Architecture Overview

tasklib follows a linear dependency chain: documentation merges trigger scaffold generation, which establishes the package structure for model, storage, and CLI layers. Each stage depends on the successful merge of the previous stage, with import resolution verified locally before CI runs. The Crafted Dev Agent pipeline orchestrates this sequence, using merge gates to enforce ordering.

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
- Review `TRD-TASKLIB` in `crafted-docs/` to understand the validation goals and dependency chain
- The full build sequence is: docs → scaffold → model → storage → CLI — each stage must merge before the next begins
- Run tests locally to confirm import resolution before pushing to CI
- Check `crafted-standards/` for architecture decisions and interface contracts

## Documentation

| Document | Location | What It Contains |
|----------|----------|------------------|
| TRD-TASKLIB | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Core TRD defining the task management library scope, validation goals, and dependency chain |
| Architecture Context | `crafted-docs/forge_architecture_context.md` | Crafted Dev Agent architecture context and system overview |

## Where to Go Next

- `CLAUDE.md` — start here before writing any code
- `crafted-standards/ARCHITECTURE.md` — full system architecture
- `crafted-standards/INTERFACES.md` — wire formats and API contracts
- `crafted-docs/` — complete TRDs and PRDs