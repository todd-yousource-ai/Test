# Architecture

## System Overview

This codebase implements **tasklib**, a deliberately simple **Python task management library** defined in **TRD-TASKLIB v1.0**.

Its stated purpose is **validation of the Crafted Dev Agent pipeline end-to-end**, not delivery of a production task system. The architecture is therefore driven by pipeline validation requirements rather than operational scale or feature breadth.

From the TRD, the dependency chain to be validated is:

**documentation → scaffold → model → storage → CLI**

The system scope includes:

- A **documentation set**
  - README
  - ARCHITECTURE overview
  - API reference
- A **Python package scaffold**
  - With subpackage directories
- A **Task Model**
- A **Task Store**
- A **CLI**
- A **Package Root**

The architectural intent explicitly supports these validation goals:

- A documentation PR triggers the merge gate and downstream PRs recognize the merge
- A scaffold PR with multiple package directories mirrors files to the local test workspace
- Code PRs importing from previously merged PRs resolve those imports locally before CI
- The full dependency chain closes successfully across all layers

The loaded source material also includes a separate **Forge Architecture Context** describing the Forge platform and its subsystems. That material is platform context injected into prompts, but the only product defined by the TRD here is **tasklib**. No tasklib requirement states that Forge runtime subsystems are implemented inside this codebase. Accordingly, this architecture treats **tasklib** as the primary system and records Forge items only as externally provided context found in the loaded documents.

## Subsystem Map

### tasklib Documentation

**Defined by TRD headings and scope**

Includes:

- README
- ARCHITECTURE overview
- API reference

Role:

- Establishes the documented contract for the library
- Serves as the first stage in the validation dependency chain
- Provides source material for scaffold and code stages downstream

Inputs:

- TRD-defined library purpose and requirements

Outputs:

- Human-readable documentation artifacts consumed by later pipeline stages

Dependencies:

- None inside the code dependency chain; it is the upstream source

---

### Package Scaffold

**Defined by TRD scope and headings**

Includes:

- Python package scaffold
- Multiple package/subpackage directories

Role:

- Creates the package and directory structure required for imports and local workspace mirroring
- Enables later code PRs to import from previously merged structures before CI

Inputs:

- Documentation-defined package intent
- TRD package structure expectations

Outputs:

- Package directories and module layout used by model, storage, CLI, and package root

Dependencies:

- Documentation

---

### Task Model

**Defined by heading `3.1 Task Model`**

Role:

- Defines the task domain object(s) for the library
- Provides the data representation consumed by storage and CLI layers

Inputs:

- Package scaffold
- Functional requirements for task representation

Outputs:

- Task-related Python model interfaces/types consumed by the store and exposed through package root and CLI

Dependencies:

- Scaffold

---

### Task Store

**Defined by heading `3.2 Task Store`**

Role:

- Provides storage behavior for task entities defined by the Task Model
- Acts as the persistence/manipulation layer between model and CLI

Inputs:

- Task Model

Outputs:

- Storage operations over tasks for use by higher-level interfaces

Dependencies:

- Task Model
- Scaffold

---

### CLI

**Defined by heading `3.3 CLI` and dependency chain**

Role:

- Exposes task library functionality through a command-line interface
- Sits at the end of the dependency chain and validates that all prior layers integrate correctly

Inputs:

- Task Model
- Task Store
- Package Root exports

Outputs:

- Command-line invocation surface for library operations

Dependencies:

- Task Store
- Task Model
- Package Root
- Scaffold

---

### Package Root

**Defined by heading `3.4 Package Root`**

Role:

- Defines top-level package exports and import surface
- Provides stable import paths used by downstream components and tests

Inputs:

- Task Model
- Task Store
- Potentially CLI-facing public APIs as exposed library symbols

Outputs:

- Root-level import contract for consumers and internal code PR dependency resolution

Dependencies:

- Scaffold
- Model
- Store

---

### Forge Platform Context

**Found in loaded prompt context, not in tasklib TRD scope**

The loaded documents contain a separate architecture context for **Forge**, described as:

> a runtime policy enforcement and cryptographic identity platform for enterprise AI agents

Core subsystems explicitly named in the provided content:

- VTZ — Virtual Trust Zone
- CAL — Conversation Abstraction Layer
- CPF — Conversation Plane Filter
- CTX-ID — Context Identity
- GCI — Global Context Identifier
- DTL — Data Trust Labels
- TrustFlow
- TrustLock
- MCP Policy Engine
- Forge Agent
- Forge CAL
- Forge Connector SDK
- AI Model Router / Token Optimizer
- Forge Agent Template

Because no tasklib requirement binds these subsystems into the library implementation, they are not treated as internal tasklib subsystems. They remain external architecture context present in the source documents.

## Component Boundaries

### Documentation must never

- Contain executable implementation logic that substitutes for scaffold, model, store, or CLI code
- Bypass the documented dependency chain
- Define undocumented behavior not grounded in the TRD

### Package Scaffold must never

- Implement domain behavior that belongs to Task Model, Task Store, or CLI
- Collapse multiple package directories into an ad hoc structure inconsistent with the scaffold requirement
- Break local import resolution expected by downstream PR validation

### Task Model must never

- Take on storage responsibilities
- Become coupled to CLI concerns
- Depend on CLI code
- Rely on undocumented package paths outside the scaffold/package-root contract

### Task Store must never

- Redefine the task domain independently of the Task Model
- Embed CLI-specific logic
- Bypass model-defined task representations

### CLI must never

- Serve as the source of truth for task data structures
- Reimplement storage internals that belong in Task Store
- Depend on undocumented or unstable imports outside the package root/scaffold structure

### Package Root must never

- Introduce alternate behavior separate from underlying model/store implementations without documentation
- Break stable import paths required for downstream PR import resolution
- Replace subsystem boundaries with monolithic implicit imports

### Forge Platform Context subsystems must never be assumed to be part of tasklib

Based on the provided TRD, tasklib must not be described as implementing:

- CAL enforcement
- CPF policy filtering
- VTZ enforcement plane behavior
- Cryptographic identity workflows
- Forge-specific policy or trust services

Those capabilities appear only in external architecture context and are not in tasklib scope.

## Key Data Flows

## 1. Documentation-to-Implementation Validation Flow

1. Documentation artifacts are established first:
   - README
   - ARCHITECTURE overview
   - API reference
2. The documentation PR merges
3. Downstream PRs recognize that merge
4. Scaffold and implementation stages proceed based on the merged contract

Purpose from TRD:

- Validate that documentation participates in the dependency chain and merge gating

---

## 2. Scaffold-to-Workspace Flow

1. A scaffold PR creates the Python package scaffold
2. The scaffold includes multiple package directories
3. Files are mirrored to the local test workspace
4. Later code PRs consume that mirrored package structure

Purpose from TRD:

- Validate workspace mirroring and package structure propagation

---

## 3. Import Resolution Flow

1. Earlier PRs merge scaffold and foundational modules
2. Later code PRs import from those previously merged PRs
3. Those imports resolve locally before CI executes
4. The pipeline verifies dependency closure across stages

Purpose from TRD:

- Validate local dependency resolution before CI

---

## 4. Runtime Library Flow

At the functional level implied by the subsystem headings:

1. The **Task Model** defines task entities
2. The **Task Store** operates on those task entities
3. The **Package Root** exposes stable imports over library functionality
4. The **CLI** consumes the model/store/package-root surface to provide command-line access

This is the concrete implementation flow corresponding to:

**model → storage → CLI**

---

## 5. End-to-End Dependency Closure Flow

The complete required sequence is explicitly:

1. Documentation
2. Scaffold
3. Model
4. Storage
5. CLI

Successful architecture requires each stage to depend only on earlier validated stages, so the full chain can close end-to-end.

## Critical Invariants

The following invariants are directly derived from the provided documents.

### tasklib invariants

- The product is **tasklib**, a **Python task management library**
- The system is **deliberately simple**
- The system is **not a production system**
- The primary architectural objective is **pipeline validation**
- The dependency chain must remain:

  **documentation → scaffold → model → storage → CLI**

- Documentation must exist as a first-class subsystem and include:
  - README
  - ARCHITECTURE overview
  - API reference
- The scaffold must support:
  - Python package structure
  - Multiple package/subpackage directories
  - Local workspace mirroring
- Later code must be able to:
  - import from previously merged PRs
  - resolve those imports locally before CI
- The library architecture must include, at minimum:
  - Task Model
  - Task Store
  - CLI
  - Package Root

### Boundaries implied by the dependency chain

- No downstream layer may become the prerequisite for an upstream layer
- CLI must remain downstream of model and storage
- Storage must remain downstream of model
- Package structure must exist before code depending on it
- Import contracts must remain stable enough for PR-chain validation

### Crafted Architecture Rules present in the loaded standards

These rules are included in the loaded source and therefore recorded as architectural constraints from standards context:

- Trust must never be inferred implicitly when it can be asserted and verified explicitly.
- Identity, policy, telemetry, and enforcement must remain separable but tightly linked.
- All control decisions must be explainable, observable, and reproducible.
- Crafted components must default to policy enforcement, not policy suggestion.
- Local agents must minimize user friction while preserving strong enforcement guarantees.
- Administrative workflows must be simple, explicit, and understandable in plain language.
- Protocol and enforcement logic must be designed for future scale across endpoint, network, cloud, and AI runtime environments.

Because the tasklib TRD does not define trust, identity, policy, telemetry, or enforcement features for this library, these standards are preserved as loaded architectural rules but do not expand tasklib’s implementation scope beyond the TRD.

### Forge context invariants present in loaded source

The provided Forge context states:

- Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents
- CAL is the enforcement choke point for all agent-originated action
- No tool call, data read, API invocation, or agent handoff executes without CAL policy evaluation
- CAL sits above the VTZ enforcement plane and below application orchestration

These are valid invariants for the Forge context included in the loaded documents, but they are not tasklib subsystem requirements unless additional TRD/PRD material explicitly binds them into this codebase.