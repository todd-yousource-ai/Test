# Architecture - Validation

## What This Subsystem Does

The Validation subsystem exists to prove the Crafted Dev Agent pipeline end-to-end using the deliberately simple `tasklib` Python library.

Its purpose is not to provide production-grade validation or runtime enforcement. Instead, it validates that the build and merge pipeline can successfully close a dependency chain from documentation to working code with real merges at each step.

The subsystem validates the following outcomes defined by `TRD-TASKLIB`:

- A documentation PR fires the merge gate and downstream PRs recognize the merge.
- A scaffold PR with multiple package directories mirrors files to the local test workspace.
- Code PRs that import from previously-merged PRs resolve those imports locally before CI.
- The full dependency chain closes in order:
  - `docs → scaffold → model → storage → CLI`

Within `tasklib`, this subsystem is expressed through a minimal documentation set, Python package scaffold, task model, task storage layer, and CLI, with the CLI serving as the final dependency consumer in the chain.

## Component Boundaries

The Validation subsystem is bounded strictly by the `TRD-TASKLIB` scope and implementation constraints.

Included responsibilities:

- Define and validate a minimal documentation set:
  - `README`
  - `ARCHITECTURE` overview
  - API reference
- Define and validate a Python package scaffold with subpackages.
- Validate dependency sequencing across implementation stages:
  - documentation
  - scaffold
  - model
  - storage
  - CLI
- Validate that CLI behavior uses the storage layer rather than implementing storage directly.
- Validate that imports from previously merged PRs resolve locally before CI.
- Validate behavior through tests focused on observable outcomes.

Excluded responsibilities:

- Production-grade task management features
- Additional error handling
- Logging
- Configuration
- Features beyond those explicitly specified in the TRD
- Any trust, policy, cryptographic, or conversation-plane enforcement behavior from Forge architecture context not defined in `TRD-TASKLIB`

Although the provided Forge architecture context defines general platform invariants and the CPF subsystem, those elements are not part of the `tasklib` Validation subsystem unless explicitly specified in the TRD. This subsystem therefore remains a minimal library-validation slice only.

## Data Flow

The Validation subsystem validates a staged dependency flow rather than a complex runtime pipeline.

### Build and merge flow

1. Documentation artifacts are authored and merged.
2. The merge gate is expected to fire on the documentation PR.
3. Downstream PRs recognize the merged documentation state.
4. Scaffold artifacts are created with multiple package directories.
5. Scaffold files are mirrored to the local test workspace.
6. Model code is added on top of the scaffold.
7. Storage code imports and uses model code from previously merged work.
8. CLI code imports its store from the storage layer.
9. The full chain is validated end-to-end:
   - `docs → scaffold → model → storage → CLI`

### Runtime interaction flow

The runtime flow is intentionally minimal:

1. The CLI is run as a Python module.
2. A user invokes one of the supported commands:
   - `add`
   - `list`
   - `complete`
3. The CLI delegates persistence behavior to the storage layer.
4. The storage layer manages task retrieval and update behavior.
5. Results are returned to the CLI for confirmation or display.

### Behavioral expectations from functional requirements

- `add` accepts a title and confirms the created task.
- `list` displays all pending and in-progress tasks.
- `complete` accepts a task identifier and confirms completion.
- The CLI must import its store from the storage layer.

## Key Invariants

The Validation subsystem enforces the following invariants from `TRD-TASKLIB`:

- The system is intentionally minimal.
- Implementation must not add features beyond the specification.
- The dependency chain must close completely:
  - `docs → scaffold → model → storage → CLI`
- Later layers must consume earlier merged layers through real imports.
- The scaffold must mirror files to the local test workspace.
- The CLI must consume storage as a dependency and must not implement storage directly.
- Validation quality depends on behavior-oriented tests rather than implementation-detail tests.
- Work decomposition must remain constrained:
  - no more than 3 implementation files per PR
  - no more than 6 acceptance criteria per PR

From the implementation notes, simplicity is itself an invariant. Implementors are expected to resist introducing:

- error handling beyond what is specified
- logging
- configuration
- unspecified extensions

## Failure Modes

A validation failure occurs when any required pipeline or dependency behavior does not hold.

Primary failure modes:

- Documentation PR does not trigger the merge gate.
- Downstream PRs do not recognize a merged upstream documentation PR.
- Scaffold PR does not mirror files to the local test workspace.
- A code PR cannot resolve imports from a previously merged PR locally before CI.
- The dependency chain does not close fully from documentation through CLI.
- The CLI cannot be run as a Python module.
- The CLI `add` command does not accept a title or does not confirm the created task.
- The CLI `list` command does not display all pending and in-progress tasks.
- The CLI `complete` command does not accept a task identifier or does not confirm completion.
- The CLI implements storage behavior directly instead of importing its store from the storage layer.
- Tests validate implementation details instead of required behavior.
- A PR exceeds the decomposition limits defined in the implementation notes.
- Additional non-specified functionality is introduced, violating minimal-scope intent.

The TRD explicitly states there are no open questions and that the specification is complete by design. As a result, ambiguity is not a permitted failure fallback; divergence from the stated scope is itself a defect.

## Dependencies

The Validation subsystem depends only on the components and relationships explicitly described in `TRD-TASKLIB`.

Internal dependency chain:

1. Documentation set
2. Package scaffold
3. Task model
4. Task store
5. CLI

Layer dependency requirements:

- Storage depends on the model layer.
- CLI depends on the storage layer.
- CLI must import its store from storage rather than reimplementing storage.

Execution dependency:

- The CLI must be runnable as a Python module.

Validation dependency:

- Tests must verify behavior of the model, store, and CLI through observable outcomes.

This subsystem does not declare dependencies on CPF, CAL, trust enforcement, policy engines, or other Forge platform subsystems, because those are not part of the `TRD-TASKLIB` specification.