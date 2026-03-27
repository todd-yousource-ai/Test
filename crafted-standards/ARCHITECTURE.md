# Architecture - Validation

## What This Subsystem Does

The Validation subsystem is a deliberately minimal Python task management library (`tasklib`) whose sole purpose is to prove that the Crafted Dev Agent build pipeline can close a complete dependency chain end-to-end. It is not a production system. It exercises the full pipeline from documentation through scaffold to working code, verifying that:

- A documentation PR fires the merge gate and downstream PRs recognize the merge.
- A scaffold PR with multiple package directories mirrors files to the local test workspace.
- Code PRs that import from previously-merged PRs resolve those imports locally before CI.
- The full dependency chain closes in order: **docs → scaffold → model → storage → CLI**.

Test quality is treated as equal to implementation quality. Tests must check behavior (e.g., a completed task no longer appears in `list_by_status("pending")`) rather than implementation internals.

## Component Boundaries

The subsystem comprises three implementation layers and a documentation set, each scoped to its own pipeline stage:

### Documentation Set
- README, ARCHITECTURE overview, API reference.
- First link in the dependency chain; its merge fires the gate for all downstream PRs.

### Task Model (`tasklib.model`)
- Defines the task data structure.
- No dependency on storage or CLI.
- Specified by FR requirements in TRD-TASKLIB §3.1.

### Task Store (`tasklib.storage`)
- Provides in-memory task persistence and retrieval.
- Depends on the Task Model.
- Specified by FR requirements in TRD-TASKLIB §3.2.

### CLI (`tasklib.cli`)
- Minimal command-line interface runnable as a Python module.
- Supports three commands: `add`, `list`, `complete`.
- **Must import its store from the storage layer** — it does not implement storage directly (FR-19).
- Specified by FR requirements in TRD-TASKLIB §3.3 (FR-15 through FR-19).

### Decomposition Constraints
- No more than **3 implementation files per PR**.
- No more than **6 acceptance criteria per PR**.
- If a natural decomposition exceeds these limits, the work must be split into a smaller scope before generating code.

## Data Flow

```
Documentation PR
      │
      ▼  (merge gate fires)
Scaffold PR  ──►  creates package directories: tasklib/, tasklib/model/, tasklib/storage/, tasklib/cli/
      │
      ▼  (merge recognized by downstream)
Task Model PR  ──►  tasklib.model defines task data structure
      │
      ▼  (import resolved locally before CI)
Task Store PR  ──►  tasklib.storage imports from tasklib.model
      │
      ▼  (import resolved locally before CI)
CLI PR  ──►  tasklib.cli imports store from tasklib.storage
```

Each stage depends on the prior stage's merge being visible. The pipeline validates that cross-PR imports resolve correctly at each link.

Within the running library, runtime data flow is:

```
User (CLI command) → tasklib.cli → tasklib.storage → tasklib.model (task instances)
```

- `add` command: CLI creates a task via the store, confirms creation.
- `list` command: CLI queries the store for pending and in-progress tasks, displays them.
- `complete` command: CLI marks a task as complete via the store using a task identifier, confirms completion.

## Key Invariants

1. **Dependency chain must be linear and complete.** The chain docs → scaffold → model → storage → CLI must close with no skipped links. Each PR depends on the merge of its predecessor.
2. **Storage is the single source of task state.** The CLI must never implement storage directly; it must import from the storage layer (FR-19).
3. **No feature creep.** The library must not include error handling, logging, configuration, or features beyond what TRD-TASKLIB specifies. The goal is the simplest possible codebase that exercises the full pipeline.
4. **Behavioral tests only.** Tests assert on observable behavior, not implementation details.
5. **Specification is complete.** There are no open questions by design. Ambiguity would undermine the validation purpose.
6. **Fail closed on trust and policy operations.** Per Forge platform invariants, all failures involving trust, identity, policy, or cryptography fail closed. No silent failure paths exist.

## Failure Modes

| Failure | Behavior | Rationale |
|---|---|---|
| Downstream PR submitted before upstream merge is visible | PR must not proceed; import resolution fails before CI | Validates merge-gate propagation |
| Scaffold PR does not mirror expected directories to local test workspace | Subsequent PRs cannot locate package paths; build fails | Validates workspace mirroring |
| CLI imports storage implementation directly (bypasses `tasklib.storage`) | Violates FR-19; must be rejected at review | Enforces layered dependency |
| PR exceeds 3 implementation files or 6 acceptance criteria | Must be split before code generation | Enforces decomposition constraints from §6 |
| Any trust or policy check failure in the pipeline | Fail closed; no silent pass-through | Forge platform invariant |

## Dependencies

- **Upstream:** Crafted Dev Agent merge-gate infrastructure (provides PR lifecycle, merge detection, workspace mirroring).
- **Internal (linear):**
  - `tasklib.cli` → `tasklib.storage` → `tasklib.model`
- **External:** Python standard library only. No third-party packages are specified or permitted.
- **Platform:** Forge platform invariants apply — trust is never inferred implicitly, all failures fail closed, no silent failure paths.