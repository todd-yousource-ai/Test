# Crafted Dev Agent — Task Management Library

A deliberately simple Python task management library (`tasklib`) designed to validate that the Crafted Dev Agent build pipeline can close a complete dependency chain from documentation through scaffold to working code.

## What It Does

`tasklib` validates the Crafted Dev Agent pipeline end-to-end by proving that documentation PRs fire merge gates, scaffold PRs mirror files correctly, and code PRs resolve imports from previously-merged PRs before CI. It exercises a full dependency chain — docs → scaffold → model → storage → CLI — ensuring each step produces real merges that downstream steps recognize. The library itself is not a production system; it exists to prove the pipeline works.

## Key Subsystems

- **Documentation Set** — README, ARCHITECTURE overview, and API reference that initiate the dependency chain
- **Python Package Scaffold** — Subpackage directory structure mirrored to the local test workspace
- **Model** — Core task data model consumed by downstream packages
- **Storage** — Persistence layer that imports from the model package
- **CLI** — Command-line interface that closes the dependency chain by importing from storage and model
- **CAL (Conversation Abstraction Layer)** — Enforcement choke point for all agent-originated actions; no tool call, data read, or agent handoff executes without CAL policy evaluation
- **CPF (Conversation Plane Filter)** — Filtering component within the CAL enforcement plane
- **Forge Runtime** — Runtime policy enforcement and cryptographic identity platform for enterprise AI agents, enforcing execution below the application stack

## Architecture Overview

The `tasklib` dependency chain is strictly linear: documentation merges trigger scaffold generation, which enables model, storage, and CLI code PRs to resolve imports against previously-merged packages. The Forge architecture context underpins the agent pipeline itself — CAL acts as the enforcement choke point sitting above the VTZ enforcement plane and below application orchestration, ensuring every agent action passes through policy evaluation. Together, these layers validate that cryptographic identity and operator-defined policy govern the full build lifecycle.

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

- Read `CLAUDE.md` before writing any code — it contains LLM coding instructions and repo conventions
- Review `crafted-docs/TRD-TASKLIB.md` to understand the validation goals and dependency chain
- Review `crafted-docs/forge_architecture_context.md` for the runtime enforcement architecture
- The dependency chain must close in order: docs → scaffold → model → storage → CLI
- Ensure each PR's imports resolve against previously-merged packages before pushing to CI

## Documentation

| Document | Location | What It Contains |
|----------|----------|------------------|
| TRD-TASKLIB | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Task management library spec; defines the validation dependency chain and pipeline goals |
| Forge Architecture Context | `crafted-docs/forge_architecture_context.md` | Platform overview, core subsystems (CAL, CPF), and runtime policy enforcement architecture |

## Where to Go Next

- `CLAUDE.md` — start here before writing any code
- `crafted-standards/ARCHITECTURE.md` — full system architecture
- `crafted-standards/INTERFACES.md` — wire formats and API contracts
- `crafted-docs/` — complete TRDs and PRDs