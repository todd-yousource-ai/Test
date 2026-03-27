# Architecture - Validation

## What This Subsystem Does

The Validation subsystem exists to prove that the Crafted Dev Agent pipeline can complete an end-to-end dependency chain using a deliberately simple Python library, `tasklib`.

Its purpose is not production task management. Its purpose is validation of pipeline behavior across merged work items, specifically that:

- a documentation PR fires the merge gate and downstream PRs recognize the merge
- a scaffold PR with multiple package directories mirrors files to the local test workspace
- code PRs that import from previously-merged PRs resolve those imports locally before CI
- the full dependency chain closes: `docs → scaffold → model → storage → CLI`

Within that validation scope, the subsystem defines a minimal task management library with:

- documentation artifacts
- a Python package scaffold
- a task model
- a storage layer
- a CLI layer

The CLI is explicitly intended for demonstration and validation, not production use.

## Component Boundaries

The Validation subsystem is bounded by the requirements of `TRD-TASKLIB` and should remain intentionally minimal.

### Included

- Documentation set:
  - `README`
  - `ARCHITECTURE` overview
  - API reference
- Python package scaffold
- Task model functionality
- Task store functionality
- CLI functionality

### Excluded

Per implementation guidance, the subsystem must not expand beyond specified behavior. In particular, implementors should resist adding:

- error handling beyond what is specified
- logging
- configuration
- extra features not required by the TRD
- production-oriented behavior

### Internal Layering

The subsystem is organized as a dependency chain:

1. Documentation
2. Scaffold
3. Model
4. Storage
5. CLI

The CLI depends on the storage layer. It must not implement storage directly.

## Data Flow

The required operational flow is minimal and centered on manual interaction through the CLI.

### Add Flow

1. The CLI is run as a Python module.
2. The user invokes the `add` command with a task title.
3. The CLI calls into the storage layer.
4. The storage layer creates and stores the task.
5. The CLI confirms the created task.

### List Flow

1. The CLI is run as a Python module.
2. The user invokes the `list` command.
3. The CLI calls into the storage layer.
4. The storage layer returns tasks limited to:
   - pending
   - in-progress
5. The CLI displays those tasks.

### Complete Flow

1. The CLI is run as a Python module.
2. The user invokes the `complete` command with a task identifier.
3. The CLI calls into the storage layer.
4. The storage layer marks the task complete.
5. The CLI confirms completion.

### Pipeline Validation Flow

The subsystem also validates repository and merge behavior:

1. Documentation changes merge first.
2. Scaffold changes merge and mirror package files into the local test workspace.
3. Model changes import correctly from previously merged work.
4. Storage changes depend on the model layer.
5. CLI changes depend on the storage layer.
6. Local import resolution succeeds before CI.
7. The full dependency chain closes successfully.

## Key Invariants

The Validation subsystem enforces the following invariants from the TRD content.

### Validation Purpose Invariants

- The subsystem remains a validation project, not a production system.
- The simplest possible codebase is preferred if it still exercises the full pipeline dependency chain.
- The dependency chain must remain intact: `docs → scaffold → model → storage → CLI`.
- Downstream work must recognize prior merges.
- Imports from previously merged PRs must resolve locally before CI.

### CLI Invariants

From the CLI functional requirements:

- The CLI must be runnable as a Python module.
- The CLI must support:
  - `add`
  - `list`
  - `complete`
- `add` must accept a title and confirm the created task.
- `list` must display all pending and in-progress tasks.
- `complete` must accept a task identifier and confirm completion.
- The CLI must import its store from the storage layer and must not implement storage directly.

### Implementation Invariants

From the implementation notes:

- Do not add unspecified features.
- Do not add logging or configuration.
- Keep decomposition small:
  - no more than 3 implementation files per PR
  - no more than 6 acceptance criteria per PR
- Tests should validate behavior rather than implementation details.

### Applicable Forge Context Invariants

The provided architecture context introduces system-wide invariants relevant to validation-oriented enforcement behavior:

- trust is never inferred implicitly; it must be asserted and verified explicitly
- failures involving trust, identity, policy, or cryptography fail closed
- no silent failure paths
- sensitive operations are authenticated, authorized, and auditable

The same context also describes CPF as:

- a three-tier inspection and classification engine within CAL
- Tier 1: structural validation
- Tier 2: semantic classification
- Tier 3: behavioral analysis
- all tiers run synchronously in the enforcement path
- fail closed

These Forge invariants are architectural context, but `TRD-TASKLIB` does not define `tasklib` components that implement CAL or CPF behavior directly. They therefore serve as surrounding architectural constraints, not as subsystem-local feature requirements.

## Failure Modes

The TRD intentionally minimizes behavior, so failure handling should not be expanded beyond specified scope. The meaningful failure modes for this subsystem are therefore primarily validation failures.

### Pipeline Validation Failures

- A documentation PR does not trigger the merge gate.
- A downstream PR does not recognize a merged predecessor.
- Scaffold output does not mirror correctly to the local test workspace.
- A code PR cannot resolve imports from previously merged work before CI.
- The dependency chain does not close from documentation through CLI.

### CLI Contract Failures

- The CLI cannot be executed as a Python module.
- The `add` command does not accept a title.
- The `add` command does not confirm the created task.
- The `list` command does not display pending and in-progress tasks.
- The `complete` command does not accept a task identifier.
- The `complete` command does not confirm completion.
- The CLI bypasses the storage layer or implements storage directly.

### Quality Failures

- Implementation grows beyond intentionally minimal scope.
- A PR exceeds the decomposition constraints.
- Tests assert implementation details instead of observable behavior.

### Failure Handling Posture

Where validation expectations are not met, the subsystem should be treated as failed for its intended purpose. This is consistent with the surrounding architectural context’s fail-closed posture, even though `TRD-TASKLIB` does not require production-grade enforcement mechanisms.

## Dependencies

The subsystem dependencies are defined by the TRD’s staged architecture and functional requirements.

### Internal Dependencies

- Documentation is the root of the dependency chain.
- Scaffold depends on documentation being established.
- Model depends on scaffold.
- Storage depends on model.
- CLI depends on storage.

### Direct Functional Dependency

- The CLI imports its store from the storage layer.

### Development and Merge Dependencies

- Later PRs depend on earlier merged PRs being visible and resolvable locally.
- Local import resolution must work before CI for code depending on prior merges.

### Architectural Context Dependencies

The injected Forge architecture context references broader platform concepts such as:

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

However, `TRD-TASKLIB` does not specify direct implementation dependencies from the Validation subsystem onto these components. They should not be introduced as code-level dependencies unless separately required by a governing TRD.