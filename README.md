# tasklib — Task Management Library

A deliberately simple Python task management library designed to validate the Crafted Dev Agent build pipeline end-to-end, proving that a complete dependency chain — from documentation through scaffold to working code — closes with real merges at each step.

## What It Does

tasklib validates that the Crafted Dev Agent pipeline can process a full dependency chain: docs → scaffold → model → storage → CLI. It exercises merge gates, downstream PR recognition, multi-package scaffolding, and cross-PR import resolution in a local test workspace. It is not a production system — it exists to prove the pipeline works.

## Key Subsystems

- **Documentation Set** — README, ARCHITECTURE overview, and API reference that trigger the initial merge gate
- **Package Scaffold** — Python package structure with subpackage directories, mirrored to the local test workspace
- **Model** — Task data model defining the core domain objects
- **Storage** — Persistence layer for task data
- **CLI** — Command-line interface for interacting with tasks
- **Merge Gate** — Validates that documentation PRs fire correctly and downstream PRs recognize the merge
- **Dependency Chain** — Ensures the full build sequence (docs → scaffold → model → storage → CLI) closes without broken imports

## Architecture Overview

tasklib is structured as a linear dependency chain where each stage depends on artifacts produced by the previous stage. Documentation merges trigger scaffold generation, which produces the package directories that model, storage, and CLI code depend on. Cross-PR import resolution ensures that code PRs referencing previously-merged PRs can resolve imports locally before CI runs.

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

- Read `CLAUDE.md` before writing any code — it contains LLM coding instructions and project conventions
- Review `crafted-docs/TRD-TASKLIB.md` for the full technical requirements
- Review `crafted-docs/forge_architecture_context.md` for pipeline architecture context
- Run the test suite in `tests/` to verify your local environment
- Follow the dependency chain order (docs → scaffold → model → storage → CLI) when contributing

## Documentation

| Document | Location | What It Contains |
|----------|----------|------------------|
| TRD-TASKLIB | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Full technical requirements for the task management library and pipeline validation goals |
| Architecture Context | `crafted-docs/forge_architecture_context.md` | Pipeline architecture context and system design |

## Where to Go Next

- `CLAUDE.md` — start here before writing any code
- `crafted-standards/ARCHITECTURE.md` — full system architecture
- `crafted-standards/INTERFACES.md` — wire formats and API contracts
- `crafted-docs/` — complete TRDs and PRDs