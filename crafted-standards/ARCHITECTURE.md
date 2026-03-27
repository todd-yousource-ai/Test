# Architecture

## System Overview

This document describes the architecture of **tasklib**, a deliberately simple **Python task management library** defined by **TRD-TASKLIB v1.0**.

Per the TRD, tasklib is **not a production system**. Its stated purpose is to validate the **Crafted Dev Agent** build pipeline end-to-end by proving that a complete dependency chain can be closed from documentation through scaffold to working code, with real merges at each step.

The validation chain explicitly defined in the TRD is:

**docs → scaffold → model → storage → CLI**

The system scope called out in the TRD includes:

- A documentation set:
  - `README`
  - `ARCHITECTURE` overview
  - API reference
- A Python package scaffold with subpackage directories
- A task model
- A task store
- A CLI
- A package root

From the headings and dependency structure present in the source material, the architecture is organized around the following tasklib subsystems:

- Documentation
- Package Scaffold
- Task Model
- Task Store
- CLI
- Package Root

The included `forge_architecture_context` content describes a separate platform named **Forge** and its subsystems. Because the tasklib TRD defines a different product and scope, Forge content is treated here only as contextual material present in the source set, not as part of the tasklib system architecture.

## Subsystem Map

### Documentation

**Defined by source headings:**
- Documentation
- `1. Purpose and Scope`
- `2. Architecture`
- `5. Acceptance Criteria`
- `6. Implementation Notes`
- `7. Open Questions`

**Role**
- Provides the documentation set required by the TRD:
  - README
  - ARCHITECTURE overview
  - API reference

**Architectural significance**
- Starts the validation dependency chain.
- Must exist as a mergeable documentation layer that downstream work can depend on.

**Inputs**
- TRD-defined scope and requirements.

**Outputs**
- Human-readable system description and interface documentation used by downstream scaffold and code work.

### Package Scaffold

**Defined by source headings:**
- Package Scaffold
- `2.1 Package Structure`
- `2.2 Dependency Relationships`

**Role**
- Establishes the Python package structure and subpackage directories for tasklib.

**Architectural significance**
- Must support the TRD validation goal that a scaffold PR with multiple package directories mirrors files to the local test workspace.

**Inputs**
- Documentation-defined structure.
- Required subsystem decomposition.

**Outputs**
- Python package directories and import structure supporting model, storage, CLI, and package root.

### Task Model

**Defined by source headings:**
- Task Model
- `3.1 Task Model`

**Role**
- Defines the library’s task representation.

**Architectural significance**
- Sits after scaffold in the dependency chain.
- Provides the core domain structure that storage and CLI depend on.

**Inputs**
- Package scaffold and package import layout.

**Outputs**
- Task-domain types or structures consumable by storage and CLI.

### Task Store

**Defined by source headings:**
- Task Store
- `3.2 Task Store`

**Role**
- Provides persistence or storage behavior for tasks.

**Architectural significance**
- Depends on the task model.
- Must be importable by later code PRs before CI, per the TRD validation goals.

**Inputs**
- Task model definitions.

**Outputs**
- Storage operations for task entities used by the CLI.

### CLI

**Defined by source headings:**
- CLI
- `3.3 CLI`

**Role**
- Exposes command-line interaction for the task management library.

**Architectural significance**
- Final executable-facing subsystem in the explicitly stated chain:
  - docs → scaffold → model → storage → CLI

**Inputs**
- Task model
- Task store
- Package root exports/imports as applicable

**Outputs**
- User-invoked task management operations through a command-line interface.

### Package Root

**Defined by source headings:**
- `3.4 Package Root`

**Role**
- Defines the package-level import boundary for tasklib.

**Architectural significance**
- Serves as the top-level Python package surface.
- Supports local import resolution across previously merged PRs before CI.

**Inputs**
- Exposed objects/functions/types from internal subsystems.

**Outputs**
- Stable package import path for downstream code and CLI usage.

## Component Boundaries

The following boundaries are derived from the subsystem decomposition and the explicit dependency chain in the TRD.

### Documentation must never

- Implement runtime library behavior.
- Replace the package scaffold.
- Serve as a substitute for model, storage, CLI, or package-root code.
- Collapse the dependency chain by embedding code artifacts that bypass scaffold or implementation stages.

### Package Scaffold must never

- Define the task domain model itself.
- Implement storage behavior.
- Implement CLI behavior.
- Introduce dependency ordering that violates the stated chain:
  - docs → scaffold → model → storage → CLI

### Task Model must never

- Depend on the CLI.
- Be implemented as a command interface concern.
- Be replaced by storage-specific concerns.
- Skip the scaffold/package structure layer defined earlier in the chain.

### Task Store must never

- Define the task model as a storage side effect.
- Depend on the CLI as an upstream requirement.
- Bypass model-layer imports.
- Violate the dependency ordering by introducing reverse dependencies from storage back to scaffold or docs as executable requirements.

### CLI must never

- Act as the source of truth for the task model.
- Act as the source of truth for storage behavior.
- Reverse the dependency chain by requiring lower layers to depend on it.
- Bypass package-root/import conventions needed for local resolution before CI.

### Package Root must never

- Replace internal subsystem separation.
- Introduce circular import structure across model, storage, and CLI.
- Obscure dependency relationships required for local resolution of previously merged PR imports.
- Become an alternate execution layer independent of the documented subsystem chain.

## Key Data Flows

Only flows directly supported by the provided tasklib TRD are described here.

### 1. Documentation-to-implementation flow

**Flow**
1. Documentation artifacts are created and merged.
2. Downstream PRs recognize the merge.
3. Scaffold and implementation work proceed on top of that merged documentation base.

**Why it matters**
- This is an explicit validation goal:
  - “A documentation PR fires the merge gate and downstream PRs recognize the merge.”

### 2. Scaffold mirroring flow

**Flow**
1. A scaffold PR creates multiple package directories.
2. Those files are mirrored to the local test workspace.
3. Subsequent implementation PRs use that mirrored local structure.

**Why it matters**
- This is explicitly required by the TRD:
  - “A scaffold PR with multiple package directories mirrors files to the local test workspace.”

### 3. Local import resolution flow

**Flow**
1. Earlier PRs merge package structure and dependencies.
2. Later code PRs import from those previously merged PRs.
3. Imports resolve locally before CI executes.

**Why it matters**
- This is an explicit validation goal:
  - “Code PRs that import from previously-merged PRs resolve those imports locally before CI.”

### 4. Domain flow: model to storage to CLI

**Flow**
1. The **Task Model** defines the task representation.
2. The **Task Store** operates on that representation.
3. The **CLI** invokes functionality built on the model and store.

**Why it matters**
- This matches the dependency chain named in the TRD:
  - docs → scaffold → model → storage → CLI

### 5. Package-root exposure flow

**Flow**
1. Internal subsystem code is organized under the scaffolded package structure.
2. The package root exposes or coordinates package-level imports.
3. Downstream code and CLI entry points resolve imports through the package root and package hierarchy.

**Why it matters**
- The TRD explicitly includes `Package Root` as a functional area and emphasizes local import resolution before CI.

## Critical Invariants

These invariants are derived from the tasklib TRD and the architecture rules provided in the source set. Where the architecture rules are general, they are applied only at the level supportable by the tasklib TRD.

### Validation-chain invariants

- The architecture must preserve the explicit dependency chain:

  **docs → scaffold → model → storage → CLI**

- No subsystem may introduce a dependency that reverses or bypasses this chain.
- The end-to-end pipeline validation purpose must remain intact; tasklib exists to prove merge, scaffold, import-resolution, and dependency-chain closure behavior.

### Merge and dependency invariants

- A documentation merge must be recognizable by downstream PRs.
- Scaffold output must be materialized as package directories in the local test workspace.
- Imports from previously merged PRs must resolve locally before CI.
- The architecture must support a complete closure of the dependency chain named in the TRD.

### Structural invariants

- tasklib is a **Python** package-based system.
- The package structure must include subpackage directories, because that is explicitly in scope.
- The architecture must include, at minimum, the functional areas named in the source headings:
  - Task Model
  - Task Store
  - CLI
  - Package Root
  - Documentation
  - Package Scaffold

### Scope invariants

- tasklib is **not a production system**.
- The architecture must remain deliberately simple, consistent with the TRD’s purpose as a validation artifact.
- This document must not elevate external Forge platform subsystems into tasklib runtime components, because the tasklib TRD defines a separate product and scope.

### Crafted architecture rule alignment

Applied conservatively to the tasklib validation library:

- Dependency relationships must remain explicit rather than implicit.
- Control and dependency behavior must be observable enough to validate merge recognition and import resolution.
- Components must remain separable:
  - documentation
  - scaffold
  - model
  - storage
  - CLI
  - package root
- The architecture should favor explainable dependency behavior over hidden coupling, because the TRD’s purpose is pipeline validation rather than production feature density.