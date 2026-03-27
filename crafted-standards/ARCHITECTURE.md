# Architecture - Validation

## What This Subsystem Does

The Validation subsystem exists to prove the Crafted Dev Agent pipeline end-to-end using the deliberately simple `tasklib` Python library defined in `TRD-TASKLIB`.

Its purpose is not to provide production-grade validation infrastructure. Its purpose is to exercise and verify the full dependency chain from documentation through scaffold to working code, with real merges at each step.

Within that scope, the subsystem validates that:

- a documentation PR fires the merge gate and downstream PRs recognize the merge
- a scaffold PR with multiple package directories mirrors files to the local test workspace
- code PRs that import from previously-merged PRs resolve those imports locally before CI
- the full dependency chain closes as `docs → scaffold → model → storage → CLI`

The concrete validation target is a minimal task management library consisting of:

- documentation
- Python package scaffold
- task model
- task storage
- CLI

The subsystem therefore enforces that implementation proceeds through the documented dependency sequence and that each layer consumes previously merged outputs rather than bypassing them.

## Component Boundaries

The Validation subsystem is bounded by the artifacts and dependency chain defined in `TRD-TASKLIB`.

Included within this subsystem:

- documentation set:
  - `README`
  - `ARCHITECTURE` overview
  - API reference
- Python package scaffold
- task model
- task store
- CLI

Layer boundaries defined by the TRD:

- **Documentation layer**
  - establishes the initial merge event in the chain
  - provides the required project documentation artifacts
- **Scaffold layer**
  - provides package structure and local workspace mirroring behavior
  - must exist before implementation layers that depend on imports
- **Model layer**
  - defines the task model
- **Storage layer**
  - provides the task store
- **CLI layer**
  - provides manual interaction with the task store
  - must import its store from the storage layer
  - must not implement storage directly

Explicit subsystem boundary constraints:

- The subsystem is a validation project, not a production system.
- Implementors must not add features beyond what is specified.
- Implementors should resist adding:
  - error handling
  - logging
  - configuration
  - unspecified features

This means the subsystem boundary excludes production concerns not named in the TRD.

## Data Flow

The Validation subsystem’s primary flow is a dependency-validation flow rather than a complex runtime processing pipeline.

### 1. Documentation-to-merge flow

1. Documentation artifacts are created.
2. A documentation PR is merged.
3. The merge gate fires.
4. Downstream PRs recognize that merged state.

This validates that documentation changes can initiate and unblock the dependency chain.

### 2. Scaffold-to-workspace flow

1. A scaffold PR introduces the Python package scaffold.
2. The scaffold includes multiple package directories.
3. Files are mirrored to the local test workspace.

This validates that later implementation PRs have the expected local package layout available before CI.

### 3. Import-resolution flow

1. A later code PR depends on code from a previously merged PR.
2. That PR imports from the earlier merged package content.
3. Imports resolve locally before CI.

This validates local dependency closure across merged PR boundaries.

### 4. Full implementation chain

The required chain is:

1. `docs`
2. `scaffold`
3. `model`
4. `storage`
5. `CLI`

Each stage depends on prior merged artifacts. The subsystem validates that the chain closes completely.

### 5. CLI runtime flow

At runtime, the CLI provides minimal manual interaction with the task store:

- the CLI is runnable as a Python module
- `add` accepts a title and confirms the created task
- `list` displays all pending and in-progress tasks
- `complete` accepts a task identifier and confirms completion

The required dependency path for CLI behavior is:

- CLI command
- import of store from storage layer
- task store operation
- task model/state returned to CLI
- CLI confirmation or listing output

The CLI may not short-circuit this path by implementing storage internally.

## Key Invariants

The Validation subsystem is governed by invariants from `TRD-TASKLIB` and the injected architecture context.

### TRD-defined invariants

- The project is intentionally minimal.
- The system is for validation, not production use.
- The simplest possible codebase must be preserved.
- The dependency chain must close as:
  - `docs → scaffold → model → storage → CLI`
- The CLI must import its store from the storage layer.
- The CLI must not implement storage directly.
- Tests must check behavior rather than implementation details.
- Work decomposition must stay within:
  - no more than 3 implementation files per PR
  - no more than 6 acceptance criteria per PR

### Injected architecture-context invariants

The provided architecture context defines the following global invariants:

- trust is never inferred implicitly; it must be asserted and verified explicitly
- all failures involving trust, identity, policy, or cryptography fail closed
- no silent failure paths anywhere
- all sensitive operations are authenticated, authorized, and auditable

The same context also defines a validation pattern in `CPF — Conversation Plane Filter`:

- three-tier inspection and classification engine
- Tier 1: structural validation
- Tier 2: semantic classification
- Tier 3: behavioral analysis
- all tiers run synchronously in the enforcement path
- fail closed

Only the validation properties explicitly provided by that context can be carried into this subsystem architecture. No additional CAL/CPF behaviors should be invented beyond those stated.

## Failure Modes

The TRD intentionally minimizes implementation complexity, but the subsystem still has clear validation failure modes.

### Dependency-chain failures

- documentation PR does not trigger the merge gate
- downstream PRs do not recognize the merged documentation state
- scaffold PR does not mirror files to the local test workspace
- code PR imports from previously merged PRs fail to resolve locally before CI
- the end-to-end chain does not close through all required stages:
  - `docs`
  - `scaffold`
  - `model`
  - `storage`
  - `CLI`

### Boundary violations

- the CLI implements storage directly instead of importing from the storage layer
- implementation adds features outside the specified scope
- implementation introduces production-oriented concerns not requested by the TRD
- decomposition exceeds:
  - 3 implementation files per PR
  - 6 acceptance criteria per PR

### Behavioral-validation failures

- tests verify implementation details instead of externally observable behavior
- completed tasks remain visible in status-based listing where behavior should exclude them
- CLI commands do not provide the specified confirmations or listings

### Architecture-context failures

From the injected context, validation-related failures must be treated as fail-closed where trust, identity, policy, or cryptography are involved, and no silent failure paths are permitted.

## Dependencies

The Validation subsystem depends only on artifacts and relationships explicitly described in the provided source material.

### Primary specification dependency

- `TRD-TASKLIB`

### Internal dependency chain

- documentation
- scaffold
- model
- storage
- CLI

### Runtime dependency relationship

- CLI depends on the storage layer
- storage depends on the model layer
- later PRs may depend on previously merged PR outputs through local imports

### Documentation dependencies

The documentation set required by the TRD is:

- `README`
- `ARCHITECTURE` overview
- API reference

### Architecture-context dependency

The subsystem is also informed by the injected `forge_architecture_context`, specifically:

- global trust and failure invariants
- `CPF — Conversation Plane Filter` validation characteristics

No other subsystem dependencies are defined in the provided TRD content.