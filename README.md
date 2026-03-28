# tasklib — Task Management Library

A deliberately simple Python task management library designed to validate that the Crafted Dev Agent build pipeline can close a complete dependency chain from documentation through scaffold to working code.

## What It Does

tasklib validates the Crafted Dev Agent pipeline end-to-end by exercising a full dependency chain: docs → scaffold → model → storage → CLI. It proves that documentation PRs fire merge gates, scaffold PRs mirror files correctly, and code PRs resolve imports from previously-merged PRs before CI. The library itself is not a production system — it exists to confirm the pipeline works with real merges at each step.

## Key Subsystems

- **Documentation Set** — README, ARCHITECTURE overview, and API reference that trigger the initial merge gate
- **Package Scaffold** — Python package with subpackage directories mirrored to the local test workspace
- **Model** — Task data model layer, part of the dependency chain validated by the pipeline
- **Storage** — Persistence layer that depends on the model and validates cross-PR import resolution
- **CLI** — Command-line interface that closes the full dependency chain
- **Merge Gate** — Validates that documentation PR merges are recognized by downstream PRs
- **Local Test Workspace** — Ensures imports from previously-merged PRs resolve locally before CI

## Architecture Overview

tasklib follows a linear dependency chain: documentation is merged first, triggering scaffold generation, which provides the package structure for model, storage, and CLI layers. Each stage depends on artifacts produced by the previous merge, validating that the Crafted Dev Agent pipeline correctly propagates changes across PRs. The system uses this chain to prove that the build pipeline handles real multi-step dependency resolution.

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
- Run the test suite in `tests/` to verify your local environment
- Follow the dependency chain order (docs → scaffold → model → storage → CLI) when making changes

## Documentation

| Document | Location | What It Contains |
|----------|----------|------------------|
| TRD-TASKLIB | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Task management library TRD — validation goals, dependency chain, scope |
| Forge Architecture Context | `crafted-docs/forge_architecture_context.md` | Pipeline architecture context and system overview |

## Where to Go Next

- `CLAUDE.md` — start here before writing any code
- `crafted-standards/ARCHITECTURE.md` — full system architecture
- `crafted-standards/INTERFACES.md` — wire formats and API contracts
- `crafted-docs/` — complete TRDs and PRDs