# Tasklib — Crafted Dev Agent Validation Library

A deliberately simple Python task management library designed to validate that the Crafted Dev Agent build pipeline can close a complete dependency chain from documentation through scaffold to working code.

## What It Does

Tasklib validates the Crafted Dev Agent pipeline end-to-end by exercising a full dependency chain: docs → scaffold → model → storage → CLI. It proves that documentation PRs fire merge gates, scaffold PRs mirror files correctly, and code PRs resolve imports from previously-merged PRs before CI. The library exists within the Forge platform ecosystem — a runtime policy enforcement and cryptographic identity platform for enterprise AI agents.

## Key Subsystems

- **Documentation Set** — README, ARCHITECTURE overview, and API reference that trigger the initial merge gate
- **Python Package Scaffold** — Subpackage directories mirrored to the local test workspace
- **Model** — Core data model for task management, resolved via the dependency chain
- **Storage** — Persistence layer that imports from the previously-merged model package
- **CLI** — Command-line interface that closes the full dependency chain
- **CAL (Conversation Abstraction Layer)** — Forge enforcement choke point for all agent-originated actions; no tool call, data read, or agent handoff executes without CAL policy evaluation
- **CPF (Conversation Plane Filter)** — Filtering component within the CAL enforcement plane
- **VTZ Enforcement Plane** — Runtime enforcement layer beneath CAL, above infrastructure

## Architecture Overview

Tasklib's dependency chain is linear and intentional: documentation merges trigger scaffold generation, which enables model code, which storage depends on, which the CLI consumes. This chain validates that the Crafted Dev Agent correctly resolves cross-PR imports and recognizes upstream merges at each step. The broader Forge architecture enforces agent execution via cryptographic identity and operator-defined policy, with CAL sitting above the VTZ enforcement plane and below application orchestration.

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

- Read `CLAUDE.md` before writing or generating any code
- Review `crafted-docs/TRD-TASKLIB.md` to understand the validation goals and dependency chain
- Review `crafted-docs/forge_architecture_context.md` for platform-level context injected into code generation prompts
- The full dependency chain must close in order: docs → scaffold → model → storage → CLI
- Each PR in the chain must resolve imports from previously-merged PRs locally before CI runs

## Documentation

| Document | Location | What It Contains |
|----------|----------|------------------|
| TRD-TASKLIB | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Defines the tasklib validation library — scope, dependency chain, and pipeline validation goals |
| Forge Architecture Context | `crafted-docs/forge_architecture_context.md` | Platform overview, core subsystems (CAL, CPF, VTZ), and architecture context injected into every code generation prompt |

## Where to Go Next

- `CLAUDE.md` — start here before writing any code
- `crafted-standards/ARCHITECTURE.md` — full system architecture
- `crafted-standards/INTERFACES.md` — wire formats and API contracts
- `crafted-docs/` — complete TRDs and PRDs