# INTERFACES.md

## Interface Contracts

This document defines the wire formats, API-facing data structures, validation rules, enums, constants, and subsystem interaction contracts derived from the provided TRD materials only.

---

## Per-Subsystem Data Structures

### Subsystem: tasklib

The TRD defines a deliberately simple Python task management library named `tasklib`. It also defines a dependency chain of functional areas:

- docs
- scaffold
- model
- storage
- CLI

Only interfaces explicitly inferable from the TRD are included below.

---

### Documentation Subsystem Structures

The documentation set is explicitly in scope and consists of:

- `README`
- `ARCHITECTURE overview`
- `API reference`

#### `DocumentationSet`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `readme` | string | Yes | Represents README content or path |
| `architecture_overview` | string | Yes | Represents architecture overview content or path |
| `api_reference` | string | Yes | Represents API reference content or path |

#### Notes

- The TRD does not specify whether these are file paths, document bodies, or generated artifacts.
- Therefore, the interface contract only requires presence of these three named documentation artifacts.

---

### Scaffold Subsystem Structures

The scaffold subsystem is described as:

- "Python package scaffold"
- "subpackage directories"
- "mirrors files to the local test workspace"

#### `PackageScaffold`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `package_name` | string | Yes | Expected value: `tasklib` |
| `subpackage_directories` | array<string> | Yes | One or more package subdirectories |
| `mirrored_files` | array<string> | Yes | Files mirrored to local test workspace |

#### `WorkspaceMirror`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `source_files` | array<string> | Yes | Files originating from scaffold |
| `destination_root` | string | Yes | Local test workspace root |
| `mirror_success` | boolean | Yes | Indicates mirror completion |

#### Notes

- The TRD does not define exact directory naming conventions.
- The presence of multiple package directories is required by the validation goals.

---

### Model Subsystem Structures

The TRD names `model` as part of the dependency chain, but does not define concrete model fields.

#### `ModelModule`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `module_name` | string | Yes | Logical module identifier |
| `imports_from_prior_prs` | array<string> | No | Imports expected to resolve locally before CI |

#### Notes

- No task entity schema is specified in the provided TRD excerpt.
- No serialization format for model objects is defined in the TRD.

---

### Storage Subsystem Structures

The TRD names `storage` as part of the dependency chain, but does not define a storage backend, persistence model, or storage record schema.

#### `StorageModule`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `module_name` | string | Yes | Logical module identifier |
| `depends_on_model` | boolean | Yes | True when storage imports or uses model components |

#### Notes

- No file format, database schema, or repository contract is defined in the provided TRD text.

---

### CLI Subsystem Structures

The TRD names `CLI` as the terminal dependency in the chain, but does not define command syntax or argument schema.

#### `CliModule`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `module_name` | string | Yes | Logical module identifier |
| `depends_on_storage` | boolean | Yes | True when CLI imports or uses storage components |

#### Notes

- No command-line flags, exit codes, or stdout/stderr formats are specified in the provided TRD text.

---

### Merge and Dependency Chain Structures

The TRD’s validation goals define a PR-driven dependency workflow.

#### `PullRequestArtifact`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `pr_type` | string | Yes | Must be one of the defined PR types |
| `merged` | boolean | Yes | Indicates merged state |
| `downstream_recognized_merge` | boolean | No | Applicable where downstream PRs consume prior merge state |
| `local_import_resolution` | boolean | No | Applicable for code PRs importing prior merged PR outputs |

#### `DependencyChain`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `stages` | array<string> | Yes | Ordered dependency chain |
| `fully_closed` | boolean | Yes | True only if all dependency stages complete successfully |

#### Required stage order

The TRD explicitly defines the full dependency chain as:

1. `docs`
2. `scaffold`
3. `model`
4. `storage`
5. `CLI`

---

### Forge Architecture Context Structures

The provided materials include architecture context text. This content is included here only where explicit interface-like data can be derived.

---

### Subsystem: CAL — Conversation Abstraction Layer

Defined characteristics:

- Enforcement choke point for all agent-originated action
- No tool call, data read, API invocation, or agent handoff executes without CAL policy evaluation
- Sits above the VTZ enforcement plane, below application orchestration
- Key components:
  - CPF
  - AIR
  - CTX-ID
  - PEE
  - TrustFlow/SIS
  - CAL Verifier Cluster

#### `CalActionEnvelope`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `action_type` | string | Yes | Represents agent-originated action category |
| `policy_evaluated` | boolean | Yes | Must be true before execution |
| `ctx_id` | string | No | Context identifier if present |
| `execution_permitted` | boolean | Yes | Result of CAL policy evaluation |

#### `CalComponentReference`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `component_name` | string | Yes | Must reference one of the named CAL components |

#### Supported CAL component names

- `CPF`
- `AIR`
- `CTX-ID`
- `PEE`
- `TrustFlow/SIS`
- `CAL Verifier Cluster`

---

### Subsystem: CPF — Conversation Plane Filter

The provided content names CPF as a core subsystem but does not define fields, protocol messages, or payload structures.

#### `CpfReference`

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `name` | string | Yes | Expected value: `CPF` |

---

## Cross-Subsystem Protocols

### 1. Documentation-to-Scaffold Merge Recognition Protocol

Derived from validation goal:

- A documentation PR fires the merge gate
- Downstream PRs recognize the merge

#### Contract

1. A `PullRequestArtifact` with `pr_type = "docs"` is merged.
2. Merge state becomes visible to downstream stages.
3. Scaffold and later PRs may proceed only after merge recognition.

#### Preconditions

- Documentation artifacts exist:
  - README
  - ARCHITECTURE overview
  - API reference

#### Postconditions

- `merged = true`
- `downstream_recognized_merge = true`

---

### 2. Scaffold-to-Workspace Mirror Protocol

Derived from validation goal:

- A scaffold PR with multiple package directories mirrors files to the local test workspace

#### Contract

1. A scaffold PR defines a package scaffold with multiple subpackage directories.
2. Files are mirrored from scaffold source to a local test workspace.
3. Success is recorded when all intended files are mirrored.

#### Preconditions

- `subpackage_directories` contains multiple entries.
- `source_files` is non-empty.

#### Postconditions

- `mirror_success = true`
- `mirrored_files` reflects the mirrored outputs

---

### 3. Prior-PR Local Import Resolution Protocol

Derived from validation goal:

- Code PRs that import from previously-merged PRs resolve those imports locally before CI

#### Contract

1. A code PR in `model`, `storage`, or `CLI` imports artifacts from previously merged PRs.
2. Those imports must resolve in the local workspace before CI execution.
3. Import resolution success is recorded per PR artifact.

#### Preconditions

- Required prior PRs are merged.
- Mirrored scaffold artifacts are available locally if needed.

#### Postconditions

- `local_import_resolution = true`

---

### 4. Full Dependency Chain Closure Protocol

Derived from validation goal:

- The full dependency chain closes: docs → scaffold → model → storage → CLI

#### Contract

The chain completes in the following strict order:

1. `docs`
2. `scaffold`
3. `model`
4. `storage`
5. `CLI`

#### Preconditions

- Each prior stage is merged and recognized by downstream stages.
- Local imports resolve before CI for dependent code PRs.

#### Postconditions

- `fully_closed = true`

---

### 5. CAL Policy Evaluation Protocol

Derived from architecture context:

- No tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation

#### Contract

1. An agent-originated action is represented as a `CalActionEnvelope`.
2. CAL policy evaluation occurs before execution.
3. Execution is permitted only when policy evaluation completes successfully.

#### Preconditions

- `action_type` is present.
- The action is agent-originated.

#### Postconditions

- `policy_evaluated = true`
- `execution_permitted` is set

---

## Enums and Constants

### PR Types

```text
docs
scaffold
model
storage
CLI
```

### Dependency Chain Order

```text
docs -> scaffold -> model -> storage -> CLI
```

### Documentation Artifact Names

```text
README
ARCHITECTURE overview
API reference
```

### CAL Component Names

```text
CPF
AIR
CTX-ID
PEE
TrustFlow/SIS
CAL Verifier Cluster
```

### CAL Action Categories

Only categories explicitly named in the provided architecture text are included:

```text
tool_call
data_read
api_invocation
agent_handoff
```

### Platform Constants

#### Platform name

```text
Forge
```

#### tasklib package name

```text
tasklib
```

#### tasklib version

```text
1.0
```

#### tasklib status

```text
Draft
```

#### tasklib date

```text
2026-03-26
```

---

## Validation Rules

### tasklib Validation Rules

#### Documentation rules

1. A valid documentation set MUST include:
   - `README`
   - `ARCHITECTURE overview`
   - `API reference`

2. A documentation PR MUST be capable of triggering a merge gate.

3. Downstream PRs MUST recognize the merged documentation PR before depending on it.

#### Scaffold rules

4. A scaffold PR MUST include multiple package directories.

5. Scaffold files MUST be mirrored to the local test workspace.

6. A scaffold mirror operation MUST report success only if the intended files are mirrored.

#### Import resolution rules

7. Code PRs that import from previously merged PRs MUST resolve those imports locally before CI.

8. Local import resolution applies to downstream code stages in the dependency chain:
   - `model`
   - `storage`
   - `CLI`

#### Dependency chain rules

9. The dependency chain MUST preserve the explicit stage order:

   `docs -> scaffold -> model -> storage -> CLI`

10. A stage MUST NOT be considered complete if required earlier stages are not merged.

11. The full chain is valid only when all stages complete and dependencies close successfully.

---

### CAL Validation Rules

12. Every agent-originated action MUST pass through CAL policy evaluation before execution.

13. The following action classes MUST NOT execute without CAL evaluation:
   - tool call
   - data read
   - API invocation
   - agent handoff

14. CAL operates above the VTZ enforcement plane and below application orchestration, as architectural positioning metadata.

15. CAL component references, where used, MUST be one of:
   - `CPF`
   - `AIR`
   - `CTX-ID`
   - `PEE`
   - `TrustFlow/SIS`
   - `CAL Verifier Cluster`

---

## Wire Format Examples

The TRD does not define a canonical wire encoding. The examples below use JSON as an illustrative interchange format for the documented contracts only.

---

### Example: Documentation Set

```json
{
  "readme": "README.md",
  "architecture_overview": "ARCHITECTURE.md",
  "api_reference": "API_REFERENCE.md"
}
```

---

### Example: Documentation PR Artifact

```json
{
  "pr_type": "docs",
  "merged": true,
  "downstream_recognized_merge": true
}
```

---

### Example: Scaffold Package and Mirror

```json
{
  "package_name": "tasklib",
  "subpackage_directories": [
    "tasklib",
    "tasklib/model",
    "tasklib/storage",
    "tasklib/cli"
  ],
  "mirrored_files": [
    "tasklib/__init__.py",
    "tasklib/model/__init__.py",
    "tasklib/storage/__init__.py",
    "tasklib/cli/__init__.py"
  ]
}
```

```json
{
  "source_files": [
    "tasklib/__init__.py",
    "tasklib/model/__init__.py",
    "tasklib/storage/__init__.py",
    "tasklib/cli/__init__.py"
  ],
  "destination_root": "./local-test-workspace",
  "mirror_success": true
}
```

---

### Example: Model PR With Local Import Resolution

```json
{
  "pr_type": "model",
  "merged": true,
  "downstream_recognized_merge": true,
  "local_import_resolution": true
}
```

---

### Example: Full Dependency Chain

```json
{
  "stages": [
    "docs",
    "scaffold",
    "model",
    "storage",
    "CLI"
  ],
  "fully_closed": true
}
```

---

### Example: CAL Action Envelope

```json
{
  "action_type": "api_invocation",
  "policy_evaluated": true,
  "ctx_id": "ctx-12345",
  "execution_permitted": true
}
```

---

### Example: CAL Component Reference

```json
{
  "component_name": "CPF"
}
```

---

## Explicitly Undefined by the Provided TRDs

The following interfaces are not specified in the provided materials and therefore are intentionally left undefined in this contract:

- Concrete task object schema
- Task identifiers
- Task status lifecycle
- Storage persistence format
- Database schema
- File serialization format
- CLI commands, flags, and exit codes
- Error payload schemas
- Authentication or authorization payloads
- Network transport protocol
- CAL internal message schemas
- CPF-specific payload structure beyond named existence