# Architecture

## System Overview

This repository is defined by **TRD-TASKLIB**, which specifies a deliberately simple Python task management library named **tasklib**.

Per the TRD, tasklib is **not a production system**. Its explicit purpose is to validate the **Crafted Dev Agent** build pipeline end-to-end by proving that a complete dependency chain can be closed through real merges:

- documentation → scaffold → model → storage → CLI

The TRD scope includes:

- Documentation set:
  - README
  - ARCHITECTURE overview
  - API reference
- Python package scaffold with subpackage directories
- A task model
- A task store
- A CLI
- Package root behavior

The architecture described here is therefore constrained to the subsystems explicitly named in the source material:

- Documentation
- Package Scaffold
- Task Model
- Task Store
- CLI
- Package Root

The source corpus also includes a separately injected **Forge Architecture Context**. That context describes the Forge platform and its subsystem vocabulary, but it is not the product defined by TRD-TASKLIB. Because this architecture must be derived entirely from the provided documents without invention, Forge is treated here only as external contextual material, not as part of the tasklib system architecture.

## Subsystem Map

### Documentation

**Role**
- Provides the documentation set required by the TRD.

**Defined artifacts**
- README
- ARCHITECTURE overview
- API reference

**Purpose in the dependency chain**
- First stage in the validation flow
- Used to prove that a documentation PR fires the merge gate and that downstream PRs recognize the merge

### Package Scaffold

**Role**
- Establishes the Python package scaffold for tasklib

**Defined characteristics**
- Python package scaffold
- Multiple package directories / subpackage directories

**Purpose in the dependency chain**
- Second stage after documentation
- Used to prove that a scaffold PR with multiple package directories mirrors files to the local test workspace

### Task Model

**Role**
- Defines the task data model for the library

**Purpose in the dependency chain**
- Depends on prior scaffold and documentation stages
- Serves as an upstream dependency for storage and CLI stages

### Task Store

**Role**
- Provides task storage functionality

**Purpose in the dependency chain**
- Depends on earlier merged model code
- Used to prove that code PRs importing from previously merged PRs resolve those imports locally before CI

### CLI

**Role**
- Exposes command-line interaction for tasklib

**Purpose in the dependency chain**
- Final functional stage in the declared dependency chain
- Depends on prior documentation, scaffold, model, and storage stages

### Package Root

**Role**
- Defines package root behavior

**Purpose in the architecture**
- Serves as the package-level entry boundary named explicitly in the TRD headings

## Component Boundaries

The following boundaries are limited to what can be stated directly from the TRD structure and validation goals.

### Documentation must never do

- Must never serve as executable implementation of the task model, store, or CLI
- Must never bypass the merge-gated dependency chain described in the TRD

### Package Scaffold must never do

- Must never replace functional implementation of the model, storage, or CLI
- Must never collapse the required multi-package / subpackage directory structure where that structure is part of scaffold validation
- Must never break local workspace mirroring required by the scaffold validation goal

### Task Model must never do

- Must never assume package structure that is not provided by the scaffold stage
- Must never bypass the dependency ordering in which model follows docs and scaffold
- Must never depend on CLI as an upstream prerequisite, because CLI is downstream in the declared chain

### Task Store must never do

- Must never redefine the task model boundary that it depends on
- Must never assume unresolved imports from prior merged PRs; the TRD explicitly requires local import resolution before CI
- Must never invert the dependency chain by requiring CLI before storage exists

### CLI must never do

- Must never bypass model and storage dependencies in the declared chain
- Must never be treated as upstream of model or storage
- Must never violate the end-to-end validation objective that the full chain closes through real merges

### Package Root must never do

- Must never obscure or invalidate subpackage organization established by the scaffold
- Must never introduce dependency ordering contrary to the documented chain:
  - docs → scaffold → model → storage → CLI

## Key Data Flows

## 1. Documentation-driven build flow

1. Documentation artifacts are created or updated:
   - README
   - ARCHITECTURE overview
   - API reference
2. A documentation PR is merged
3. The merge gate fires
4. Downstream PRs recognize that merge

This is a required validation flow stated explicitly in the TRD.

## 2. Scaffold mirroring flow

1. The package scaffold is introduced with multiple package directories / subpackage directories
2. A scaffold PR is merged
3. Files are mirrored to the local test workspace

This flow validates local workspace propagation for subsequent dependent stages.

## 3. Code dependency resolution flow

1. Earlier PRs provide upstream code artifacts
2. Later PRs import from those previously merged PRs
3. Those imports resolve locally before CI

This is the key code-integration validation behavior called out in the TRD.

## 4. Functional dependency chain flow

The full implementation dependency chain is explicitly:

1. Documentation
2. Scaffold
3. Model
4. Storage
5. CLI

The architecture must preserve this ordering.

## Critical Invariants

The following invariants are directly supported by the TRD and the provided standards text.

### Tasklib invariants from TRD-TASKLIB

- The system is a **Python task management library** named **tasklib**
- The system is **deliberately simple**
- The system is **not a production system**
- The architecture exists to validate the **Crafted Dev Agent pipeline end-to-end**
- The dependency chain must close completely as:
  - docs → scaffold → model → storage → CLI
- Documentation merges must be observable by downstream PRs
- Scaffold changes with multiple package directories must mirror into the local test workspace
- Code in downstream PRs must resolve imports from previously merged PRs locally before CI

### Repository architecture invariants from the required structure

- The repository must contain architecture-relevant coverage for:
  - Documentation
  - Package Scaffold
  - Task Model
  - Task Store
  - CLI
  - Package Root
- Subsystems must remain separable according to the dependency ordering implied by the TRD headings and validation chain

### Applicable crafted architecture rules from standards

These rules are present in the loaded standards and therefore apply as repository-level architecture constraints:

- Trust must never be inferred implicitly when it can be asserted and verified explicitly.
- Identity, policy, telemetry, and enforcement must remain separable but tightly linked.
- All control decisions must be explainable, observable, and reproducible.
- Crafted components must default to policy enforcement, not policy suggestion.
- Local agents must minimize user friction while preserving strong enforcement guarantees.
- Administrative workflows must be simple, explicit, and understandable in plain language.
- Protocol and enforcement logic must be designed for future scale across endpoint, network, cloud, and AI runtime environments.

Because TRD-TASKLIB does not define trust, identity, policy, telemetry, or enforcement mechanisms inside tasklib itself, these standards are recorded here only as inherited architectural rules from the loaded source material, not as evidence of additional tasklib subsystems.