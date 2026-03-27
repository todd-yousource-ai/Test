# Architecture

## System Overview

`tasklib` is a deliberately simple Python task management library defined by **TRD-TASKLIB**. It is explicitly **not a production system**. Its stated purpose is to validate the Crafted Dev Agent pipeline end-to-end by proving that a complete dependency chain can be closed from documentation through scaffold to working code, with real merges at each step.

The architecture described by the source document is therefore both:

- a **functional task management library**, and
- a **pipeline validation artifact** whose package and dependency structure are part of the intended design.

The documented validation chain is:

**docs → scaffold → model → storage → CLI**

From the loaded material, the system consists of these in-scope elements:

- A documentation set:
  - `README`
  - `ARCHITECTURE` overview
  - API reference
- A Python package scaffold with subpackage directories
- A task model
- A task store
- A CLI
- A package root

The TRD headings also define the main architectural decomposition:

- Documentation
- Package Scaffold
- Task Model
- Task Store
- CLI
- Package Root

The source content does not define any network services, persistence engines beyond a task store abstraction, distributed components, background workers, or production deployment topology. No such elements are included here.

## Subsystem Map

### Documentation

**Source basis:** “In scope: A documentation set: README, ARCHITECTURE overview, API reference”

**Role**
Defines and describes the library and serves as the first stage in the validation dependency chain.

**Architectural significance**
A documentation PR is expected to trigger the merge gate and to be recognized by downstream PRs. This makes documentation an explicit subsystem in the pipeline architecture, not just supporting material.

**Contained artifacts**
- README
- Architecture overview
- API reference

---

### Package Scaffold

**Source basis:** “Python package scaffold with subpackage dire…” and validation goal: “A scaffold PR with multiple package directories mirrors files to the local test workspace”

**Role**
Provides the package directory structure required for subsequent implementation stages.

**Architectural significance**
The scaffold establishes the physical module boundaries needed by later code PRs. It also validates that multiple package directories are mirrored into the local test workspace.

**Contained artifacts**
- Python package directories
- Subpackage layout required by model, storage, and CLI stages

---

### Task Model

**Source basis:** headings include “Task Model” and section “3.1 Task Model”

**Role**
Defines the task representation used by the library.

**Architectural significance**
This subsystem is a distinct stage in the dependency chain and is upstream of storage and CLI.

**Dependencies**
- Depends on scaffold
- Is depended on by storage and CLI, per the chain `model → storage → CLI`

---

### Task Store

**Source basis:** headings include “Task Store” and section “3.2 Task Store”

**Role**
Provides storage behavior for tasks.

**Architectural significance**
Storage is a separate subsystem that follows the model stage in the dependency chain and precedes the CLI stage.

**Dependencies**
- Depends on task model
- Is depended on by CLI

---

### CLI

**Source basis:** headings include “CLI” and section “3.3 CLI”

**Role**
Exposes command-line interaction with the task management library.

**Architectural significance**
CLI is the terminal stage of the documented dependency chain and validates that imports from previously merged PRs resolve locally before CI.

**Dependencies**
- Depends on model and/or storage as established by the chain
- Depends on package scaffold being present

---

### Package Root

**Source basis:** heading “3.4 Package Root”

**Role**
Defines the top-level package surface of the library.

**Architectural significance**
Acts as the library entry boundary for imports and organizes exposure of package functionality.

**Dependencies**
Not separately specified in the source content beyond its inclusion as a functional area.

## Component Boundaries

The following boundaries are derived strictly from the subsystem names, the documented scope, and the dependency chain.

### Documentation must never

- Implement runtime behavior
- Substitute for package scaffold, model, storage, CLI, or package root code
- Bypass the documented merge-gated dependency chain

### Package Scaffold must never

- Define task semantics that belong to the task model
- Implement storage behavior that belongs to the task store
- Implement command behavior that belongs to the CLI
- Collapse multiple package directories into a structure inconsistent with the scaffold validation goal

### Task Model must never

- Own storage concerns assigned to the task store
- Own command-line concerns assigned to the CLI
- Depend on downstream CLI components, because the documented dependency chain places model before CLI

### Task Store must never

- Redefine the task representation owned by the task model
- Assume CLI responsibilities
- Reverse the dependency direction by requiring CLI in order to function

### CLI must never

- Become the source of truth for task data structures if those belong to the task model
- Become the storage layer if storage belongs to the task store
- Violate the dependency ordering established by the chain `docs → scaffold → model → storage → CLI`

### Package Root must never

- Obscure or contradict the package organization established by the scaffold
- Redefine subsystem responsibilities already assigned to model, storage, or CLI
- Introduce undeclared architectural stages not present in the TRD

## Key Data Flows

Only the flows explicitly supported by the TRD structure and validation goals are included.

### 1. Documentation-to-implementation flow

**Flow**
Documentation artifacts are created first and merged first, enabling downstream work.

**Sequence**
1. Documentation PR is created
2. Merge gate fires
3. Downstream PRs recognize the merge

**Purpose**
Validates pipeline behavior from documentation into implementation stages.

---

### 2. Scaffold propagation flow

**Flow**
Scaffolded package directories are mirrored to the local test workspace.

**Sequence**
1. Scaffold PR introduces multiple package directories
2. Files are mirrored to the local test workspace
3. Later stages build against the mirrored local structure

**Purpose**
Validates package structure propagation before code implementation stages rely on it.

---

### 3. Dependency-resolution flow

**Flow**
Later code stages import from previously merged stages and must resolve those imports locally before CI.

**Sequence**
1. Earlier PRs merge
2. Later PRs import from those merged packages/modules
3. Imports resolve in the local workspace before CI executes

**Purpose**
Validates real dependency closure across staged implementation.

---

### 4. Functional library flow

**Flow**
Task data is defined by the task model, managed by the task store, and exposed through the CLI.

**Sequence**
1. Task model defines task representation
2. Task store operates on that representation
3. CLI invokes library behavior using upstream components

**Purpose**
Matches the documented functional decomposition and dependency order.

## Critical Invariants

The following invariants are directly supported by the provided TRD and loaded standards.

### Pipeline invariants

- The dependency chain must close in the documented order:  
  **docs → scaffold → model → storage → CLI**
- Downstream stages must recognize prior merges.
- Code PRs that import from previously merged PRs must resolve those imports locally before CI.
- Scaffold changes with multiple package directories must mirror correctly into the local test workspace.

### Structural invariants

- The architecture remains a **Python task management library** named `tasklib`.
- The system remains within the documented scope:
  - documentation set
  - package scaffold
  - task model
  - task store
  - CLI
  - package root
- No production-system assumptions are introduced, because the TRD explicitly states it is not a production system.
- Subsystems respect the documented decomposition and dependency relationships implied by the staged chain and section structure.

### Standards-derived invariants

From the loaded architecture rules, the following apply as general architecture constraints:

- Trust must never be inferred implicitly when it can be asserted and verified explicitly.
- Identity, policy, telemetry, and enforcement must remain separable but tightly linked.
- All control decisions must be explainable, observable, and reproducible.
- Crafted components must default to policy enforcement, not policy suggestion.
- Local agents must minimize user friction while preserving strong enforcement guarantees.
- Administrative workflows must be simple, explicit, and understandable in plain language.
- Protocol and enforcement logic must be designed for future scale across endpoint, network, cloud, and AI runtime environments.

These rules are present in the loaded source material as standards, but the `tasklib` TRD does not map them to any specific `tasklib` component. Therefore they are retained only as applicable global architecture rules from the provided documents, without inventing additional tasklib-specific enforcement subsystems.