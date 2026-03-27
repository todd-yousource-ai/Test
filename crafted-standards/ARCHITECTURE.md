# Architecture - Validation

## What This Subsystem Does

The Validation subsystem exists to prove the Crafted Dev Agent pipeline end-to-end using the deliberately simple `tasklib` library defined in `TRD-TASKLIB`.

Its purpose is not to provide production-grade task management. It exists to validate that the full dependency chain can be closed through real merges and downstream consumption:

- documentation triggers the merge gate and downstream PRs recognize the merge
- scaffold PRs with multiple package directories mirror files to the local test workspace
- code PRs can import from previously merged PRs and resolve those imports locally before CI
- the dependency chain completes in order: `docs → scaffold → model → storage → CLI`

Within that validation objective, the subsystem covers:

- a documentation set including `README`, `ARCHITECTURE` overview, and API reference
- a Python package scaffold
- a minimal task model
- a storage layer for tasks
- a CLI for manual interaction with the task store

The CLI is explicitly intended for demonstration and validation, not production use.

## Component Boundaries

The Validation subsystem is bounded by the functionality specified in `TRD-TASKLIB` and should remain intentionally minimal.

### Inside the subsystem

- Documentation artifacts for the library
- Python package scaffold
- Task model
- Task store
- CLI runnable as a Python module

### Outside the subsystem

Per implementation guidance, the subsystem must not expand beyond what is specified. It should not introduce:

- extra error handling
- logging
- configuration
- additional features beyond the documented requirements
- direct storage logic inside the CLI

### Internal boundary rules

- The CLI consumes the storage layer; it does not implement storage directly.
- Later stages depend on previously merged stages.
- The subsystem should be decomposed so implementation work stays within:
  - no more than 3 implementation files per PR
  - no more than 6 acceptance criteria per PR

These constraints are part of the validation design because the goal is to exercise merge ordering and dependency recognition across small, real increments.

## Data Flow

The subsystem’s data flow follows the staged dependency chain defined in the TRD.

### Build and merge flow

1. Documentation is created and merged.
2. Scaffold is created and merged.
3. Model code is added against the scaffold.
4. Storage code imports and uses the model.
5. CLI code imports and uses the storage layer.

This ordering is required to validate that downstream PRs recognize prior merges and that local import resolution works before CI.

### Runtime flow

For manual task interaction:

1. The CLI is invoked as a Python module.
2. A CLI command is selected:
   - `add`
   - `list`
   - `complete`
3. The CLI calls into the task store.
4. The task store reads or updates task state.
5. The CLI reports the result to the user.

### Command-specific flow

- `add`
  - accepts a title
  - creates a task through the store
  - confirms the created task

- `list`
  - retrieves tasks from the store
  - displays all tasks whose status is `pending` or `in-progress`

- `complete`
  - accepts a task identifier
  - marks the task complete through the store
  - confirms completion

## Key Invariants

The Validation subsystem enforces the following invariants derived from the TRD and injected architecture context.

### Validation invariants

- The subsystem remains intentionally minimal.
- The implementation must not add unspecified features.
- The dependency chain must close in the defined order:
  - `docs → scaffold → model → storage → CLI`
- The CLI must import its store from the storage layer.
- The CLI must be runnable as a Python module.
- The `list` command displays only `pending` and `in-progress` tasks.
- Behavior-oriented validation is preferred over implementation-detail testing.

### Process invariants

- Work must be decomposed into small PRs.
- Each PR must contain no more than 3 implementation files.
- Each PR must contain no more than 6 acceptance criteria.

### Global architecture invariants from injected context

These are broader architectural constraints that apply wherever relevant:

- trust is never inferred implicitly; it is asserted and verified explicitly
- failures involving trust, identity, policy, or cryptography fail closed
- there are no silent failure paths
- sensitive operations are authenticated, authorized, and auditable

The provided TRD does not define trust, identity, policy, or cryptographic mechanisms for `tasklib`, so these invariants serve as ambient architectural constraints rather than introducing new functional scope.

## Failure Modes

The subsystem is designed to detect validation failures in pipeline construction and dependency closure.

### Pipeline validation failures

- A documentation PR does not trigger the merge gate correctly.
- Downstream PRs do not recognize an upstream merge.
- Scaffold files do not mirror to the local test workspace.
- A code PR cannot resolve imports from previously merged PRs before CI.
- The dependency chain does not close from documentation through CLI.

### Functional failures

- The CLI cannot run as a Python module.
- The `add` command does not accept a title or does not confirm task creation.
- The `list` command fails to display all `pending` and `in-progress` tasks.
- The `complete` command does not accept a task identifier or does not confirm completion.
- The CLI bypasses the storage layer and implements storage directly.

### Constraint violations

- The implementation introduces non-required functionality.
- A PR exceeds the limit of 3 implementation files.
- A PR exceeds the limit of 6 acceptance criteria.
- Tests validate implementation details instead of behavior.

### Architectural handling expectations

From the injected architecture context, relevant failures should not be silent and should fail closed where trust, identity, policy, or cryptographic concerns apply. The TRD does not define such mechanisms for this subsystem, so no additional enforcement components are introduced here.

## Dependencies

The subsystem dependency structure is explicitly linear and must remain so for validation purposes.

### Primary dependency chain

- Documentation
- Scaffold
- Model
- Storage
- CLI

### Component dependency rules

- Storage depends on the model.
- CLI depends on storage.
- CLI must import the store from the storage layer.

### Environmental dependency assumptions

- Python execution environment capable of running the CLI as a module
- Local workspace setup that mirrors scaffold PR files
- Merge and PR flow capable of demonstrating downstream recognition of prior merges
- Local import resolution before CI for code PR validation

### Non-dependencies

The subsystem should not depend on additional production concerns not specified in the TRD, including:

- logging frameworks
- configuration systems
- expanded error-management infrastructure
- extra service layers beyond model, storage, and CLI