# Architecture

## System Overview

**Product:** `tasklib`  
**Document basis:** `TRD-TASKLIB`, Version 1.0, Status Draft, dated 2026-03-26.

`tasklib` is a deliberately simple Python task management library. Per the TRD, it is **not a production system**. Its stated purpose is to validate the Crafted Dev Agent build pipeline end-to-end by exercising a complete dependency chain from documentation through scaffold to working code.

The validation goals explicitly defined in the TRD are:

- A documentation PR fires the merge gate and downstream PRs recognize the merge
- A scaffold PR with multiple package directories mirrors files to the local test workspace
- Code PRs that import from previously-merged PRs resolve those imports locally before CI
- The full dependency chain closes: `docs → scaffold → model → storage → CLI`

In scope, the TRD identifies:

- A documentation set:
  - `README`
  - `ARCHITECTURE` overview
  - API reference
- Python package scaffold with subpackage directories
- A task model
- A task store
- A CLI
- A package root

The architecture described here is therefore constrained to the following `tasklib` subsystems named in the loaded source material:

- Documentation
- Package Scaffold
- Task Model
- Task Store
- CLI
- Package Root

No additional runtime services, deployment layers, persistence technologies, networking assumptions, or external integrations are defined in the provided TRD and are therefore not included here.

## Subsystem Map

### Documentation

**Defined by source headings:** `Documentation`

**Purpose:**  
Provides the documentation set explicitly listed in scope:

- `README`
- `ARCHITECTURE` overview
- API reference

**Role in dependency chain:**  
The first stage in the validation sequence:

- `docs → scaffold → model → storage → CLI`

**Primary architectural function:**  
Acts as the initial merge-gated artifact whose successful merge must be recognized by downstream work.

---

### Package Scaffold

**Defined by source headings:** `Package Scaffold`, `2.1 Package Structure`

**Purpose:**  
Provides the Python package scaffold, including subpackage directories.

**TRD-specific validation role:**

- A scaffold PR with multiple package directories mirrors files to the local test workspace

**Primary architectural function:**  
Establishes the filesystem and package layout required for subsequent code stages to import from previously merged components.

---

### Task Model

**Defined by source headings:** `Task Model`, `3.1 Task Model`

**Purpose:**  
Represents task data within the library.

**Role in dependency chain:**  
Occurs after scaffold and before storage:

- `docs → scaffold → model → storage → CLI`

**Primary architectural function:**  
Defines the task representation that downstream storage and CLI layers depend on.

---

### Task Store

**Defined by source headings:** `Task Store`, `3.2 Task Store`

**Purpose:**  
Provides storage behavior for task entities.

**Role in dependency chain:**  
Follows the model and precedes the CLI:

- `docs → scaffold → model → storage → CLI`

**Primary architectural function:**  
Consumes the task model and provides task persistence or task state management for library consumers and the CLI.

---

### CLI

**Defined by source headings:** `CLI`, `3.3 CLI`

**Purpose:**  
Exposes command-line interaction for the task management library.

**Role in dependency chain:**  
Terminal stage of the validation sequence:

- `docs → scaffold → model → storage → CLI`

**Primary architectural function:**  
Depends on earlier layers, especially store and model, to provide user-invocable task operations.

---

### Package Root

**Defined by source headings:** `3.4 Package Root`

**Purpose:**  
Defines the package-level entry surface for `tasklib`.

**Primary architectural function:**  
Serves as the package root boundary for imports and public library exposure.

## Component Boundaries

The boundaries below are derived strictly from the subsystem names, scope, and dependency ordering stated in the TRD.

### Documentation

**Must do:**

- Describe the library through `README`
- Provide an `ARCHITECTURE` overview
- Provide API reference

**Must never do:**

- Implement runtime library behavior
- Replace scaffold, model, storage, CLI, or package-root code
- Introduce dependency direction contrary to the validation chain

---

### Package Scaffold

**Must do:**

- Define the Python package scaffold
- Include subpackage directories
- Mirror files to the local test workspace as part of scaffold validation

**Must never do:**

- Contain the substantive responsibilities of task modeling, storage, or CLI behavior
- Bypass the package structure required for downstream local import resolution
- Collapse multiple package directories into an undefined structure not supported by the TRD

---

### Task Model

**Must do:**

- Define the task representation for the library
- Provide the model layer required before storage and CLI

**Must never do:**

- Own CLI concerns
- Substitute for the storage layer
- Depend on later stages in the chain in a way that reverses `model → storage → CLI`

---

### Task Store

**Must do:**

- Provide the storage subsystem for tasks
- Build on the task model

**Must never do:**

- Redefine the task model as a CLI concern
- Depend on CLI as a prerequisite
- Break the ordered dependency relationship `model → storage`

---

### CLI

**Must do:**

- Provide the command-line interface for `tasklib`
- Consume previously merged and locally resolvable imports from earlier stages

**Must never do:**

- Require the CLI to exist before model or storage
- Reimplement model or store responsibilities as its primary function
- Violate the dependency order by introducing upstream dependency on the CLI

---

### Package Root

**Must do:**

- Provide the package root surface for the library
- Support package-level organization and importability

**Must never do:**

- Obscure or bypass the subpackage structure established by the scaffold
- Invert dependency direction among model, storage, and CLI
- Replace subsystem-specific responsibilities with an undefined monolithic root

## Key Data Flows

The source TRD defines one explicit end-to-end dependency flow and several pipeline behaviors. Those flows are the architecture’s key flows.

### 1. Merge and dependency recognition flow

```text
Documentation PR
  → merge gate fires
  → downstream PRs recognize the merge
```

This is the first validation objective and establishes that documentation artifacts are valid upstream dependencies in the pipeline.

### 2. Scaffold mirroring flow

```text
Scaffold PR
  → multiple package directories created
  → files mirrored to local test workspace
```

This flow validates that package structure produced by the scaffold stage is materialized locally for subsequent stages.

### 3. Local import resolution flow

```text
Previously merged PR outputs
  → available in local workspace
  → later code PR imports resolve locally before CI
```

This is an explicit architectural requirement from the TRD: downstream code must be able to import from previously merged work locally, prior to CI execution.

### 4. Functional dependency chain

```text
Documentation
  → Package Scaffold
  → Task Model
  → Task Store
  → CLI
```

This is the principal subsystem dependency path explicitly named in the TRD:

- `docs → scaffold → model → storage → CLI`

### 5. Runtime/library interaction flow

Derived from subsystem ordering and names only:

```text
CLI
  → Task Store
  → Task Model
```

The CLI is the final layer in the chain, and the store sits between CLI and model. This implies the CLI uses storage capabilities that in turn operate on the task model.

### 6. Package exposure flow

```text
Package Root
  → exposes package-level import surface
  → organizes access to underlying subpackages
```

This follows directly from the existence of a defined `Package Root` subsystem and a scaffold with subpackage directories.

## Critical Invariants

These invariants are derived from the TRD’s stated purpose, scope, and acceptance-oriented validation goals.

### 1. The architecture is validation-oriented, not production-oriented

`tasklib` must be treated as:

- a deliberately simple Python task management library
- not a production system
- a validation artifact for the Crafted Dev Agent build pipeline

### 2. The dependency chain must remain ordered and complete

The architecture must preserve the explicit sequence:

- `docs → scaffold → model → storage → CLI`

No subsystem may be introduced or arranged in a way that breaks this chain.

### 3. Downstream work must recognize upstream merges

A successful documentation merge must be visible to downstream PRs. This is a required pipeline invariant, not an optional behavior.

### 4. Scaffold output must materialize in the local test workspace

The scaffold stage must support:

- multiple package directories
- mirroring of files to the local test workspace

Without this, the scaffold validation goal is not met.

### 5. Imports from previously merged stages must resolve locally before CI

Code created in later stages must be able to import from earlier merged stages in the local environment prior to CI. This is a core architectural invariant of the validation pipeline.

### 6. Model, storage, and CLI must remain distinct stages

The TRD names separate subsystems and headings for:

- Task Model
- Task Store
- CLI

These concerns must remain architecturally distinct enough to preserve the dependency chain and validation semantics.

### 7. The documentation set is part of the system scope

The architecture must include, as in-scope artifacts:

- `README`
- `ARCHITECTURE` overview
- API reference

Documentation is not ancillary in this system; it is an explicit stage in the dependency chain.

### 8. Package structure must support subpackages

Because the TRD explicitly includes:

- Python package scaffold with subpackage directories

the package layout must preserve subpackage-based organization rather than collapsing into a single undefined module surface.

### 9. The package root is a defined boundary

Because `Package Root` is named as its own functional area, package-level exposure must be treated as a distinct architectural concern rather than an incidental detail.

### 10. Architecture content must not exceed the provided TRD scope

No production deployment model, external service integration, persistence backend, network topology, authentication layer, or non-TRD subsystem may be assumed here, because none are specified in the provided source content.