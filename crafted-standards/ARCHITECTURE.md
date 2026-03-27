# Architecture

## System Overview

**Product:** `tasklib`  
**Document basis:** TRD-TASKLIB v1.0 (Draft), dated 2026-03-26.

`tasklib` is a deliberately simple **Python task management library**. Per the TRD, it is **not a production system**. Its stated purpose is to validate the Crafted Dev Agent build pipeline end-to-end by exercising a full dependency chain from documentation through scaffold to working code with real merges at each step.

The validation chain explicitly defined in the TRD is:

- `docs → scaffold → model → storage → CLI`

The system scope includes:

- A documentation set:
  - `README`
  - `ARCHITECTURE` overview
  - API reference
- A Python package scaffold with subpackage directories
- A task model
- A task store
- A CLI
- A package root

From the headings and dependency relationships present in the provided material, the architecture for `tasklib` is a small layered Python package composed of the following subsystems:

- Documentation
- Package Scaffold
- Task Model
- Task Store
- CLI
- Package Root

The architecture is intentionally simple and linear. Each later subsystem depends on earlier merged artifacts being available locally before CI, which is itself one of the validation goals.

## Subsystem Map

### Documentation

**Purpose**  
Provides the documentation set explicitly listed as in scope:

- README
- ARCHITECTURE overview
- API reference

**Responsibilities**

- Define and describe the library
- Describe architecture at a high level
- Expose API-facing documentation for consumers
- Serve as the first stage in the documented dependency chain

**Inputs / Outputs**

- Inputs: TRD requirements
- Outputs: documentation artifacts consumed by humans and used to validate the docs stage of the pipeline

**Dependencies**

- None required by the stated dependency chain

---

### Package Scaffold

**Purpose**  
Establishes the Python package structure and subpackage directories required for subsequent implementation.

**Responsibilities**

- Create the Python package scaffold
- Provide multiple package directories as required by the scaffold validation goal
- Mirror files to the local test workspace as part of pipeline validation

**Inputs / Outputs**

- Inputs: documentation-defined package intent and TRD scope
- Outputs: package directories and scaffolded files used by model, storage, CLI, and package root

**Dependencies**

- Depends on Documentation in the explicit chain:
  - `docs → scaffold`

---

### Task Model

**Purpose**  
Defines the task domain model for the library.

**Responsibilities**

- Represent task data
- Provide the model layer referenced in the dependency chain
- Serve as the data contract used by storage and potentially exposed through the package root and CLI

**Inputs / Outputs**

- Inputs: scaffolded package structure
- Outputs: model definitions consumed by storage, CLI, and package root

**Dependencies**

- Depends on Package Scaffold:
  - `scaffold → model`

---

### Task Store

**Purpose**  
Implements storage for tasks.

**Responsibilities**

- Provide task persistence/storage behavior
- Operate on the Task Model
- Serve as the backing subsystem for CLI interactions

**Inputs / Outputs**

- Inputs: task model definitions
- Outputs: stored/retrieved task data for CLI and library consumers

**Dependencies**

- Depends on Task Model:
  - `model → storage`

---

### CLI

**Purpose**  
Provides a command-line interface for interacting with the task library.

**Responsibilities**

- Expose task operations through a command-line interface
- Consume the task store
- Validate that imports from previously merged PRs resolve locally before CI, per the TRD validation goals

**Inputs / Outputs**

- Inputs: task store functionality and task model transitively
- Outputs: command-line interactions with the task management library

**Dependencies**

- Depends on Task Store:
  - `storage → CLI`

---

### Package Root

**Purpose**  
Defines the top-level package interface.

**Responsibilities**

- Expose the package root behavior referenced in the functional requirements headings
- Provide import surface for consumers of the library
- Aggregate or re-export package-level interfaces as defined by implementation

**Inputs / Outputs**

- Inputs: underlying package subsystems
- Outputs: top-level package import surface

**Dependencies**

- The provided material lists Package Root as a functional area but does not explicitly place it in the chain beyond being part of the Python package structure. It must remain consistent with the scaffold and implemented subsystems.

## Component Boundaries

This section states what each subsystem must **not** do, derived from the explicit subsystem separation in the TRD and its dependency chain.

### Documentation — must never

- Implement runtime library behavior
- Act as package scaffold
- Contain model, storage, or CLI logic
- Replace API behavior with undocumented assumptions

### Package Scaffold — must never

- Define business behavior beyond package structure
- Substitute for the task model
- Implement storage semantics
- Implement CLI command behavior
- Collapse package boundaries that are needed to validate multi-package-directory mirroring

### Task Model — must never

- Perform storage responsibilities
- Contain CLI interaction logic
- Depend on CLI
- Be coupled to documentation artifacts for runtime behavior

### Task Store — must never

- Redefine the task model independently of the model layer
- Implement CLI parsing or presentation behavior
- Bypass model-layer definitions
- Depend on downstream CLI behavior for core storage operation

### CLI — must never

- Reimplement storage internals instead of using the task store
- Redefine the task model independently
- Depend on undocumented local-only assumptions that bypass import resolution requirements
- Collapse the layered dependency order defined by the TRD

### Package Root — must never

- Introduce a parallel domain model separate from Task Model
- Duplicate storage implementation
- Duplicate CLI implementation
- Violate the package structure established by the scaffold

## Key Data Flows

### 1. Documentation-to-Implementation Flow

**Flow**
1. Documentation artifacts are created
2. The merge gate fires on the documentation PR
3. Downstream PRs recognize the merged documentation state
4. Scaffold and later implementation stages proceed based on the merged dependency chain

**Architectural significance**
- Validates the first stage of the end-to-end pipeline
- Establishes docs as a real dependency in the merge sequence

---

### 2. Scaffold Propagation Flow

**Flow**
1. Package scaffold defines multiple package directories
2. Scaffold PR is merged
3. Files are mirrored to the local test workspace
4. Later implementation PRs use the mirrored scaffold locally

**Architectural significance**
- Confirms that structural package artifacts are available before later code stages
- Ensures downstream implementation occurs against real package paths

---

### 3. Model-to-Storage Flow

**Flow**
1. Task Model defines task representation
2. Task Store imports and uses the Task Model
3. Storage operations operate on model-defined task data

**Architectural significance**
- Establishes model as the data contract
- Prevents storage from becoming the source of truth for task structure

---

### 4. Storage-to-CLI Flow

**Flow**
1. Task Store provides task access/manipulation behavior
2. CLI imports the Task Store
3. CLI exposes task operations via command-line commands

**Architectural significance**
- Confirms the final implementation stage in the chain
- Ensures command execution is layered over storage rather than duplicating it

---

### 5. Local Import Resolution Flow

**Flow**
1. Earlier PRs merge in dependency order
2. Later PRs import from previously merged components
3. Those imports resolve locally before CI

**Architectural significance**
- This is an explicit validation goal in the TRD
- The architecture therefore depends on strict package boundaries and deterministic dependency ordering

## Critical Invariants

The following invariants are directly supported by the provided TRD and loaded headings.

1. **`tasklib` is a validation library, not a production system.**  
   Architecture and implementation must remain aligned with the stated purpose: validating the Crafted Dev Agent pipeline end-to-end.

2. **The full dependency chain must close in this order:**  
   `docs → scaffold → model → storage → CLI`

3. **Documentation is a first-class architectural artifact.**  
   The documentation PR must trigger merge-gate behavior and be recognized by downstream PRs.

4. **Package scaffold must exist before implementation layers depend on it.**  
   Multiple package directories must be present and mirrored to the local test workspace.

5. **Later components must import from previously merged components locally before CI.**  
   This is an explicit architectural requirement of the validation pipeline.

6. **Task Store must depend on Task Model, not redefine it.**  
   The presence of separate functional areas for Task Model and Task Store implies a required boundary between data definition and storage behavior.

7. **CLI must depend on storage/model layers rather than bypass them.**  
   The explicit chain ending in CLI requires CLI to sit downstream of the implementation layers.

8. **Package Root is a distinct functional area and must remain consistent with the package scaffold.**  
   It must not violate the structural package boundaries established earlier in the chain.

9. **Architecture documentation must remain within stated scope only.**  
   The TRD describes a deliberately simple Python task management library; no additional production-scale subsystems are in scope based on the provided documents.