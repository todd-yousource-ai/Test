# Architecture

## System Overview

**Product:** `tasklib`  
**Document source:** TRD-TASKLIB v1.0 (Draft), dated 2026-03-26

`tasklib` is a deliberately simple Python task management library. The TRD states that it is **not a production system**. Its stated purpose is to validate the Crafted Dev Agent pipeline end-to-end by exercising a complete dependency chain from documentation through scaffold to working code, with real merges at each step.

The architecture described by the TRD is intentionally minimal and organized around the dependency chain explicitly called out in scope and validation goals:

- documentation
- scaffold
- model
- storage
- CLI

The system is therefore a small Python package with a package root and subpackages sufficient to support:

- documentation artifacts
- a Python package scaffold with multiple package directories
- a task model
- a task store
- a CLI

The TRD also defines package-level dependency expectations. Code introduced in later steps must be able to import from previously merged steps locally before CI, and the full chain must close in the order:

**docs → scaffold → model → storage → CLI**

This ordering is the core architectural constraint of the codebase.

## Subsystem Map

The following subsystem entries are derived only from the loaded TRD headings and body content.

### Documentation

**Purpose:**  
Provide the documentation set required by the TRD.

**Defined artifacts:**

- `README`
- `ARCHITECTURE` overview
- API reference

**Architectural role:**  
Documentation is the first stage in the dependency chain and exists to validate that a documentation PR triggers the merge gate and that downstream PRs recognize the merge.

**Depends on:**  
No prior subsystem in the documented dependency chain.

**Consumed by:**  
Scaffold and all downstream implementation work as the authoritative description of system intent.

---

### Package Scaffold

**Purpose:**  
Provide the Python package scaffold and package directory structure.

**Defined characteristics:**

- Python package scaffold
- subpackage directories
- multiple package directories are explicitly mentioned in validation goals

**Architectural role:**  
The scaffold establishes the importable package layout that downstream code depends on. The TRD specifically requires that a scaffold PR with multiple package directories mirror files to the local test workspace.

**Depends on:**  
Documentation

**Consumed by:**  
Task Model, Task Store, CLI

---

### Task Model

**Purpose:**  
Define the task representation for the library.

**Architectural role:**  
The model layer provides the core library data structure(s) for tasks and sits before storage in the dependency chain.

**Depends on:**  
Package Scaffold

**Consumed by:**  
Task Store, CLI, Package Root

---

### Task Store

**Purpose:**  
Provide storage behavior for tasks.

**Architectural role:**  
The storage layer manages persistence or storage operations for task entities defined by the model. It is downstream of the model and upstream of the CLI in the explicit dependency chain.

**Depends on:**  
Task Model

**Consumed by:**  
CLI, Package Root

---

### CLI

**Purpose:**  
Expose task management operations through a command-line interface.

**Architectural role:**  
The CLI is the final layer in the explicit dependency chain and exercises imports from prior merged work.

**Depends on:**  
Task Store  
Task Model  
Package Scaffold

**Consumed by:**  
End users and validation of the complete pipeline closure

---

### Package Root

**Purpose:**  
Provide the package-level root surface referenced in the TRD headings.

**Architectural role:**  
The package root is a top-level Python package boundary that ties the library together as an importable unit.

**Depends on:**  
Package Scaffold and whichever lower-level package modules are re-exposed from the root

**Consumed by:**  
Library consumers and potentially the CLI, depending on package organization

## Component Boundaries

This section captures what each subsystem must not do, based strictly on the TRD’s scope, dependency ordering, and stated validation purpose.

### Documentation boundaries

Documentation must never:

- act as executable implementation of model, storage, or CLI behavior
- bypass the documented dependency chain
- substitute for scaffolded package structure

Its role is descriptive and gating, not executable.

---

### Package Scaffold boundaries

Package Scaffold must never:

- implement task business behavior that belongs to the Task Model
- implement storage logic that belongs to the Task Store
- implement command behavior that belongs to the CLI

Its role is structural: establish package directories and importable module layout.

---

### Task Model boundaries

Task Model must never:

- perform storage responsibilities assigned to the Task Store
- implement command parsing or command execution behavior assigned to the CLI
- depend on the CLI, because the dependency chain places model before CLI

Its role is to define the task representation and related model semantics only.

---

### Task Store boundaries

Task Store must never:

- redefine the task representation owned by the Task Model
- implement CLI concerns such as command parsing or terminal interaction
- introduce dependency on the CLI, because storage precedes CLI in the chain

Its role is storage behavior over model-defined task entities.

---

### CLI boundaries

CLI must never:

- own the canonical task data structure instead of consuming the Task Model
- replace or subsume storage responsibilities of the Task Store
- violate the dependency chain by serving as an upstream dependency of model or storage

Its role is interface and orchestration over lower-level library components.

---

### Package Root boundaries

Package Root must never:

- become an independent implementation layer separate from the documented subsystems
- invert dependencies by forcing lower layers to depend on package-root convenience exports
- replace subsystem ownership of model, storage, or CLI responsibilities

Its role is packaging and top-level library exposure.

## Key Data Flows

The loaded TRD does not provide detailed runtime sequence diagrams or protocol definitions. The following flows are the explicit architectural flows that can be derived from the documented dependency structure and validation goals.

### 1. Documentation-to-implementation flow

1. Documentation artifacts are created or updated.
2. A documentation PR triggers the merge gate.
3. Downstream PRs recognize the merged documentation.
4. Implementation proceeds according to the documented dependency order.

**Architectural significance:**  
Documentation is the first-class upstream input to the rest of the system.

---

### 2. Scaffold propagation flow

1. The package scaffold is introduced with multiple package directories.
2. Files are mirrored to the local test workspace.
3. Downstream code imports from scaffolded package locations.

**Architectural significance:**  
Local workspace mirroring is required to validate import resolution prior to CI.

---

### 3. Model-to-storage flow

1. Task entities are defined in the Task Model.
2. Task Store imports and uses the Task Model.
3. Storage behavior operates on model-defined task entities.

**Architectural significance:**  
Storage is downstream of model and must not redefine task structure independently.

---

### 4. Storage-to-CLI flow

1. CLI imports from previously merged components.
2. CLI uses Task Store operations.
3. Task Store uses Task Model definitions.

**Architectural significance:**  
This validates the documented dependency chain and local import resolution before CI.

---

### 5. End-to-end dependency closure flow

1. Documentation establishes intended architecture.
2. Scaffold establishes package layout.
3. Model defines task entities.
4. Storage implements task persistence/storage behavior.
5. CLI consumes lower layers.

**Required order:**  
**docs → scaffold → model → storage → CLI**

This is the primary end-to-end architectural flow in the TRD.

## Critical Invariants

These are the architecture-level invariants explicitly supported by the provided TRD content.

### 1. The system is a library-first Python package

The TRD defines the product as a **Python task management library**. The architecture must therefore remain package-oriented, with the CLI as a subsystem layered on top of library components rather than the sole implementation surface.

### 2. The system is intentionally simple

The TRD describes the system as a deliberately simple validation project and explicitly states it is not a production system. Architecture should therefore remain minimal and directly traceable to validation needs.

### 3. Dependency order is mandatory

The full dependency chain must close in this exact order:

**docs → scaffold → model → storage → CLI**

No subsystem may introduce reverse coupling that violates this order.

### 4. Downstream code must resolve imports from previously merged work locally before CI

This is an explicit validation goal. The architecture must preserve import boundaries and package layout such that local resolution works before CI execution.

### 5. Multiple package directories are part of the scaffold contract

The TRD explicitly calls out a scaffold PR with multiple package directories and local mirroring behavior. Package structure is therefore not incidental; it is part of the validation architecture.

### 6. Documentation is part of the functional dependency chain

README, ARCHITECTURE overview, and API reference are not ancillary artifacts. They are explicitly in scope and form the first stage of the pipeline the TRD is validating.

### 7. Model, storage, and CLI are distinct subsystems

The headings and dependency chain establish these as separate architectural units. Their responsibilities must remain separable:

- Task Model defines task entities
- Task Store handles storage behavior
- CLI provides command-line interaction

### 8. Architecture exists to validate the Crafted Dev Agent pipeline end-to-end

The purpose of the system is not generalized task-management feature breadth. The architecture must primarily support merge-gate validation, scaffold mirroring, local import resolution, and complete dependency-chain closure.