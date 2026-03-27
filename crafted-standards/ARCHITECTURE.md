# Architecture - Validation

## What This Subsystem Does

The Validation subsystem exists to prove that the Crafted Dev Agent pipeline can close a complete dependency chain from documentation to working code with real merges at each step.

For this library, validation is the primary purpose of the system rather than a secondary quality attribute. The subsystem validates that:

- a documentation PR fires the merge gate and downstream PRs recognize the merge
- a scaffold PR with multiple package directories mirrors files to the local test workspace
- code PRs that import from previously-merged PRs resolve those imports locally before CI
- the full dependency chain closes in order: `docs → scaffold → model → storage → CLI`

Within `tasklib`, this subsystem is expressed through a deliberately simple Python task management library whose implementation is intentionally minimal and whose structure is designed to exercise the pipeline end-to-end.

The subsystem also constrains implementation behavior. It is explicitly not a production system and must avoid adding features beyond the specification.

## Component Boundaries

The Validation subsystem covers the artifacts and implementation chain defined in the TRD:

- documentation set
  - `README`
  - `ARCHITECTURE` overview
  - API reference
- Python package scaffold
- task model
- task store
- CLI
- package root

Its boundary is the validation of dependency progression and integration across these components, not production-grade runtime concerns.

Included responsibilities:

- defining the minimal library structure required to exercise the pipeline
- enforcing the staged dependency chain between documentation, scaffold, model, storage, and CLI
- validating that imports from previously merged work resolve locally before CI
- validating that scaffolded package directories are mirrored into the local test workspace
- providing a minimal CLI for manual interaction with the task store

Excluded responsibilities:

- production hardening
- extended error handling
- logging
- configuration systems
- additional features not specified in the TRD
- direct storage implementation inside the CLI

The CLI boundary is explicit: it must use the storage layer and must not implement storage directly.

## Data Flow

The Validation subsystem’s primary flow is a dependency and merge-validation flow rather than a complex runtime data-processing flow.

### Build and merge flow

1. Documentation artifacts are created and merged.
2. The merge gate is triggered by the documentation PR.
3. Downstream PRs detect and recognize that merged state.
4. A scaffold PR creates the package structure, including multiple package directories.
5. Scaffolded files are mirrored to the local test workspace.
6. Code PRs for later layers import from previously merged layers.
7. Those imports must resolve locally before CI executes.
8. The dependency chain completes in this order:
   - documentation
   - scaffold
   - model
   - storage
   - CLI

### Runtime library flow

At runtime, the minimal user-facing flow is:

1. The CLI is run as a Python module.
2. A user invokes a command:
   - `add`
   - `list`
   - `complete`
3. The CLI calls into the storage layer.
4. The storage layer operates on task data defined by the model layer.
5. Results are returned to the CLI for display and confirmation.

### Listing flow

For `list`, the CLI displays:

- pending tasks
- in-progress tasks

Completed tasks are not included in that output requirement.

## Key Invariants

The following invariants are defined directly by the TRD and injected architecture context.

### Validation invariants

- The system exists to validate the Crafted Dev Agent pipeline end-to-end.
- The dependency chain must close completely as `docs → scaffold → model → storage → CLI`.
- Downstream work must depend on and recognize actual prior merges.
- Imports from previously merged PRs must resolve locally before CI.
- The implementation must remain deliberately simple.

### Scope invariants

- This is not a production system.
- Implementors must resist adding:
  - error handling beyond what is specified
  - logging
  - configuration
  - extra features beyond the TRD
- The CLI must import its store from the storage layer and must not implement storage directly.
- The CLI must be runnable as a Python module.
- The `add` command must accept a title and confirm the created task.
- The `list` command must display all pending and in-progress tasks.
- The `complete` command must accept a task identifier and confirm completion.

### Implementation-process invariants

- Work must be decomposed into no more than 3 implementation files per PR.
- Work must be decomposed into no more than 6 acceptance criteria per PR.
- If a decomposition would exceed those limits, it must be split into smaller scope.
- Tests must prioritize behavior over implementation details.

### Forge context invariants

The injected architecture context defines the following global invariants:

- trust is never inferred implicitly; it is asserted and verified explicitly
- all failures involving trust, identity, policy, or cryptography fail closed
- no silent failure paths exist
- all sensitive operations are authenticated, authorized, and auditable

These are global architectural constraints from the provided context. The TRD does not define tasklib-specific trust, identity, policy, or cryptographic mechanisms, so this subsystem does not introduce additional implementations in those areas.

## Failure Modes

The Validation subsystem is designed so that failures expose incomplete dependency closure or boundary violations.

Expected failure modes include:

- documentation merge does not trigger the merge gate
- downstream PRs do not recognize a prior merged dependency
- scaffolded package directories do not mirror into the local test workspace
- a code PR cannot resolve imports from previously merged PRs locally before CI
- the dependency chain does not close in the required order
- the CLI attempts to implement storage directly instead of importing the store from the storage layer
- CLI behavior does not satisfy required commands or confirmations
- tests validate implementation details instead of observable behavior

Given the injected Forge architecture context, failures in enforcement paths are expected to fail closed. The provided CPF context states:

- Tier 1: structural validation
- Tier 2: semantic classification
- Tier 3: behavioral analysis
- all tiers run synchronously in the enforcement path
- failures fail closed

No tasklib-specific CPF component is defined in the TRD, but where Forge enforcement context applies, failure behavior is fail-closed rather than permissive.

## Dependencies

The subsystem dependencies are the ordered library layers defined by the TRD.

### Internal dependency chain

1. documentation
2. scaffold
3. model
4. storage
5. CLI

Each later stage depends on the successful merge and local availability of earlier stages.

### Runtime dependencies

- CLI depends on storage
- storage depends on the task model
- package root exposes package-level access as defined by the package structure
- CLI is invoked as a Python module

### Process and quality dependencies

- local workspace mirroring for scaffold validation
- pre-CI local import resolution for dependent code PRs
- behavior-focused tests

### External architectural context

The provided Forge architecture context references:

- CAL — Conversation Abstraction Layer
- CPF — Conversation Plane Filter
- CTX-ID — Context Identity
- VTZ — Virtual Trust Zone
- DTL — Data Trust Labels
- TrustFlow
- TrustLock
- GCI — Global Context Identifier
- MCP Policy Engine
- Forge Connector SDK
- Forge Agent Template

However, the TRD for `tasklib` does not assign direct implementation responsibility for these components to the Validation subsystem. They are contextual architectural constraints, not subsystem-owned dependencies defined by the tasklib TRD.