# Architecture

## System Overview

### Product
**tasklib** — a deliberately simple Python task management library.

### Source of architecture
This architecture is derived from **TRD-TASKLIB v1.0** and the loaded architecture context included with the source documents.

### Purpose
The stated purpose of tasklib is **validation**, not production deployment. It exists to prove that the Crafted Dev Agent pipeline can complete a real dependency chain from documentation to scaffold to working code, with merges occurring at each step.

### Scope
The in-scope system elements explicitly described in the TRD are:

- Documentation set
  - README
  - ARCHITECTURE overview
  - API reference
- Python package scaffold
  - with subpackage directories
- Functional package elements implied by the dependency chain and headings
  - model
  - storage
  - CLI
  - package root

### Architectural shape
The tasklib architecture is a small layered Python library with the dependency chain explicitly called out by the TRD:

**docs → scaffold → model → storage → CLI**

This establishes the architectural progression and merge/dependency order used by the validation pipeline.

### Validation goals that shape the architecture
The architecture must support these stated validation goals:

- A documentation PR fires the merge gate and downstream PRs recognize the merge.
- A scaffold PR with multiple package directories mirrors files to the local test workspace.
- Code PRs that import from previously-merged PRs resolve those imports locally before CI.
- The full dependency chain closes: docs → scaffold → model → storage → CLI.

These goals constrain the structure to be:

- decomposed into mergeable stages,
- import-resolvable across previously merged code,
- organized as a Python package with multiple package directories,
- simple enough to validate end-to-end pipeline behavior.

## Subsystem Map

Only subsystems explicitly found in the provided documents are included here.

### tasklib Documentation
**Source basis:** In-scope list and heading `Documentation`

**Responsibilities**
- Define and describe the library through:
  - README
  - ARCHITECTURE overview
  - API reference

**Role in dependency chain**
- First stage in the stated chain: `docs → scaffold → model → storage → CLI`

**Primary outputs**
- Human-readable system description
- Package and API documentation sufficient to drive downstream work

---

### Package Scaffold
**Source basis:** In-scope list and heading `Package Scaffold`

**Responsibilities**
- Provide the Python package scaffold
- Include subpackage directories
- Mirror files to the local test workspace as part of validation

**Role in dependency chain**
- Second stage after documentation
- Structural prerequisite for model, storage, and CLI implementation

**Primary outputs**
- Package directory structure
- Importable package layout for downstream code PRs

---

### Task Model
**Source basis:** Headings `Task Model` and `3.1 Task Model`

**Responsibilities**
- Define the task domain model for the library

**Role in dependency chain**
- Comes after scaffold
- Provides model-layer definitions consumed by later stages

**Primary outputs**
- Task-related Python model code

---

### Task Store
**Source basis:** Headings `Task Store` and `3.2 Task Store`

**Responsibilities**
- Provide storage behavior for tasks

**Role in dependency chain**
- Follows the model stage in the explicit dependency chain
- Depends on prior package/model work being merged and importable

**Primary outputs**
- Storage-layer Python code for task persistence/management

---

### CLI
**Source basis:** Headings `CLI` and `3.3 CLI`

**Responsibilities**
- Expose tasklib functionality through a command-line interface

**Role in dependency chain**
- Final stage in the explicit chain
- Depends on earlier scaffold, model, and storage stages

**Primary outputs**
- CLI-facing Python code

---

### Package Root
**Source basis:** Heading `3.4 Package Root`

**Responsibilities**
- Define package-root behavior or exports for tasklib

**Role in dependency chain**
- Serves as package entry surface within the Python package structure

**Primary outputs**
- Root package module structure and/or exports

---

### Forge architecture context included in source documents
The loaded source also contains a separate injected architecture context for **Forge**, described as:

> a runtime policy enforcement and cryptographic identity platform for enterprise AI agents

This context includes named subsystems such as:

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

However, **TRD-TASKLIB does not place these Forge subsystems inside tasklib’s functional scope**. They are present as injected generation context, not as tasklib requirements. Therefore, they are treated as external contextual material, not internal tasklib subsystems.

## Component Boundaries

This section states boundaries only from the provided documents and the explicit dependency structure. Where the documents do not define implementation behavior, no additional behavior is invented.

### Documentation must never do
- Must never act as executable library code.
- Must never replace the scaffold, model, storage, or CLI implementation stages.
- Must never be treated as the package scaffold itself.

### Package Scaffold must never do
- Must never substitute for task model logic.
- Must never substitute for task storage behavior.
- Must never substitute for CLI behavior.
- Must never violate the requirement for multiple package directories as stated in the validation goal.
- Must never prevent locally resolved imports from previously merged PRs before CI.

### Task Model must never do
- Must never depend on CLI concerns being implemented first, because the dependency chain places CLI later.
- Must never collapse into storage or CLI responsibilities.
- Must never bypass the package scaffold structure required for import resolution.

### Task Store must never do
- Must never precede the model in dependency ordering, because the chain is `model → storage`.
- Must never replace the CLI surface.
- Must never ignore dependency on previously merged/importable model code.

### CLI must never do
- Must never be implemented as an upstream dependency of model or storage, because it is last in the chain.
- Must never assume unavailable imports from unmerged upstream stages.
- Must never replace model or storage responsibilities.

### Package Root must never do
- Must never supersede the existence of the subpackage structure defined by the scaffold.
- Must never merge all subsystem responsibilities into a single undifferentiated module where that would defeat the staged dependency chain.

### Tasklib system boundary
Within the provided TRD, tasklib is:
- a Python task management library,
- intentionally simple,
- intended for pipeline validation.

Therefore, tasklib must never be interpreted from these documents as:
- a production system,
- the Forge runtime policy platform,
- a cryptographic identity platform,
- a runtime enforcement plane.

### Forge contextual subsystems must never be treated as tasklib internals
Because the loaded Forge architecture context is not specified by TRD-TASKLIB as part of tasklib scope, those Forge subsystems must never be assumed to be:
- implemented by tasklib,
- required for tasklib runtime behavior,
- direct dependencies of tasklib unless separately specified.

## Key Data Flows

The provided documents define one explicit architectural flow and several validation-oriented flows.

### 1. Delivery dependency flow
The primary architectural flow explicitly stated by the TRD is:

**Documentation → Scaffold → Model → Storage → CLI**

This is both:
- the implementation dependency chain, and
- the validation chain the pipeline must successfully close.

### 2. Merge-recognition flow
From the validation goals:

1. A documentation PR merges.
2. The merge gate fires.
3. Downstream PRs recognize that merge.

This defines a documentation-to-downstream propagation flow through the pipeline.

### 3. Scaffold mirroring flow
From the validation goals:

1. A scaffold PR introduces multiple package directories.
2. Files are mirrored to the local test workspace.

This defines a packaging/workspace synchronization flow needed for local validation.

### 4. Local import resolution flow
From the validation goals:

1. Previously merged PRs provide upstream code.
2. A downstream code PR imports from that previously merged code.
3. Those imports resolve locally before CI.

This flow is central to the staged architecture, especially across:
- scaffold,
- model,
- storage,
- CLI.

### 5. Functional layering flow
Implied by the dependency chain:

1. The package scaffold establishes importable structure.
2. The task model defines task-layer constructs.
3. The task store uses the model layer.
4. The CLI uses prior library layers.

This is the functional consumption order explicitly supported by the chain.

## Critical Invariants

This section includes only invariants directly supported by the provided documents and loaded standards context.

### Tasklib-specific invariants

- **tasklib is a validation system, not a production system.**
  - Directly stated in the TRD: “It is not a production system.”

- **The complete dependency chain must close end-to-end.**
  - Required chain: `docs → scaffold → model → storage → CLI`

- **Documentation is a first-class architectural stage.**
  - It is explicitly part of the dependency chain and merge validation process.

- **The scaffold must support multiple package directories.**
  - Explicitly required by the validation goal for the scaffold PR.

- **Downstream code must resolve imports from previously merged PRs locally before CI.**
  - This is an explicit validation goal and architectural requirement.

- **Subsystem ordering must be preserved.**
  - Model cannot precede scaffold structurally.
  - Storage cannot precede model.
  - CLI cannot precede storage in the stated dependency chain.

- **The system must remain decomposable into mergeable PR stages.**
  - The TRD’s purpose depends on staged merges being recognized and consumed downstream.

### Invariants from loaded Crafted architecture rules
These rules were included in the loaded source as standards context. They are architecture-level constraints and are reproduced here exactly as applicable standards context:

- Trust must never be inferred implicitly when it can be asserted and verified explicitly.
- Identity, policy, telemetry, and enforcement must remain separable but tightly linked.
- All control decisions must be explainable, observable, and reproducible.
- Crafted components must default to policy enforcement, not policy suggestion.
- Local agents must minimize user friction while preserving strong enforcement guarantees.
- Administrative workflows must be simple, explicit, and understandable in plain language.
- Protocol and enforcement logic must be designed for future scale across endpoint, network, cloud, and AI runtime environments.

### Scope invariant regarding Forge context
- The Forge platform context is present in the loaded source, but **TRD-TASKLIB does not define Forge as part of tasklib architecture**.
- Therefore, no Forge subsystem may be treated as an internal tasklib component unless separately specified in tasklib requirements.