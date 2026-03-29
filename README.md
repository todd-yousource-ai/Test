# tasklib — Task Management Library

A deliberately simple Python task management library designed to validate the Crafted Dev Agent build pipeline end-to-end, proving that a complete dependency chain — from documentation through scaffold to working code — closes with real merges at each step.

## What It Does

tasklib validates that the Crafted Dev Agent pipeline can close a complete dependency chain: docs → scaffold → model → storage → CLI. It exercises the full build pipeline to prove that documentation PRs fire merge gates, scaffold PRs mirror files correctly, and code PRs resolve imports from previously-merged PRs before CI. It is not a production system — it is a validation tool for the pipeline itself.

## Key Subsystems

- **Documentation Set** — README, ARCHITECTURE overview, and API reference that initiate the dependency chain
- **Package Scaffold** — Python package structure with subpackage directories, mirrored to the local test workspace
- **Model** — Core task data model that downstream subsystems depend on
- **Storage** — Persistence layer that imports from the model package
- **CLI** — Command-line interface that closes the dependency chain by consuming model and storage

## Architecture Overview

The system follows a strict linear dependency chain: documentation is merged first, triggering scaffold generation, which enables the model layer, then storage, and finally the CLI. Each stage depends on artifacts from the previous merge, validating that the Crafted Dev Agent pipeline correctly recognizes upstream merges and resolves local imports before CI runs. The architecture is intentionally simple to isolate and prove pipeline mechanics.

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
- Review `crafted-docs/TRD-TASKLIB.md` for the full technical requirements
- Review `crafted-docs/forge_architecture_context.md` for pipeline architecture context
- The dependency chain must close in order: docs → scaffold → model → storage → CLI
- Run the test suite in `tests/` to verify the pipeline after changes

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