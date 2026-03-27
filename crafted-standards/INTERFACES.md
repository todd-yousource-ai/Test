# INTERFACES.md

## Interface Contracts

This document defines the wire formats, API-facing structures, validation rules, and subsystem boundaries derived solely from the provided TRD materials.

---

## Scope

The provided TRD content defines a deliberately simple Python task management library named `tasklib`, intended to validate an end-to-end Crafted Dev Agent pipeline.

The documented dependency chain is:

`docs → scaffold → model → storage → CLI`

From the TRD, the only explicitly derivable subsystems are:

- Documentation
- Scaffold
- Model
- Storage
- CLI

No network protocol, persistence encoding, RPC mechanism, or external service contract is specified in the provided TRDs. Therefore, this document defines only the interfaces that are directly implied by the TRD text and avoids introducing unstated transport or implementation details.

---

## Per-Subsystem Data Structures

### 1. Documentation Subsystem

The TRD explicitly lists a documentation set consisting of:

- `README`
- `ARCHITECTURE overview`
- `API reference`

#### Data Structure: DocumentationSet

| Field | Type | Constraints |
|---|---|---|
| `readme` | `DocumentRef` | Required |
| `architecture_overview` | `DocumentRef` | Required |
| `api_reference` | `DocumentRef` | Required |

#### Data Structure: DocumentRef

| Field | Type | Constraints |
|---|---|---|
| `name` | `string` | Required; one of `README`, `ARCHITECTURE`, `API_REFERENCE` |
| `path` | `string` | Required; repository-relative path |
| `status` | `string` | Optional; unconstrained by TRD |

---

### 2. Scaffold Subsystem

The TRD specifies:

- a Python package scaffold
- multiple package directories
- mirror behavior to the local test workspace

#### Data Structure: PythonPackageScaffold

| Field | Type | Constraints |
|---|---|---|
| `package_directories` | `list[string]` | Required; one or more package directory paths |
| `mirrored_to_local_test_workspace` | `boolean` | Required |
| `source_root` | `string` | Optional; repository-relative path if present |
| `workspace_root` | `string` | Optional; local test workspace path if present |

#### Data Structure: ScaffoldMirrorOperation

| Field | Type | Constraints |
|---|---|---|
| `source_path` | `string` | Required |
| `destination_path` | `string` | Required |
| `recursive` | `boolean` | Required |
| `status` | `string` | Optional; unconstrained by TRD |

---

### 3. Model Subsystem

The TRD names a `model` stage in the dependency chain, but does not provide concrete fields or schema for task entities.

Because the library is a task management library, the only safe derivation is that a task model exists. No specific fields such as `id`, `title`, `status`, or timestamps are stated in the TRD. Therefore, the model contract is intentionally minimal.

#### Data Structure: TaskModel

| Field | Type | Constraints |
|---|---|---|
| `type` | `string` | Required; must be `task` |

#### Data Structure: ModelModuleContract

| Field | Type | Constraints |
|---|---|---|
| `module_name` | `string` | Required; expected to identify model package/module |
| `imports_resolvable_locally` | `boolean` | Required; code PR imports from previously merged PRs must resolve locally before CI |

---

### 4. Storage Subsystem

The TRD names a `storage` stage in the dependency chain, but does not define persistence media, storage engines, or serialization.

Only a minimal subsystem contract can be derived.

#### Data Structure: StorageModuleContract

| Field | Type | Constraints |
|---|---|---|
| `module_name` | `string` | Required; expected to identify storage package/module |
| `depends_on_model` | `boolean` | Required; implied by dependency chain ordering |
| `imports_resolvable_locally` | `boolean` | Required; must resolve locally before CI |

---

### 5. CLI Subsystem

The TRD names a `CLI` stage in the dependency chain, but provides no command list, option schema, or I/O encoding.

Only the dependency-facing interface can be documented.

#### Data Structure: CliModuleContract

| Field | Type | Constraints |
|---|---|---|
| `module_name` | `string` | Required; expected to identify CLI package/module |
| `depends_on_storage` | `boolean` | Required; implied by dependency chain ordering |
| `imports_resolvable_locally` | `boolean` | Required; must resolve locally before CI |

---

### 6. Pipeline / PR Validation Subsystem

The TRD explicitly defines validation goals around merge behavior and dependency recognition.

#### Data Structure: PullRequestDependencyEvent

| Field | Type | Constraints |
|---|---|---|
| `pr_type` | `string` | Required; one of `documentation`, `scaffold`, `code` |
| `merged` | `boolean` | Required |
| `recognized_by_downstream_prs` | `boolean` | Required for `documentation`; optional otherwise |
| `resolves_imports_locally_before_ci` | `boolean` | Required for `code`; optional otherwise |

#### Data Structure: DependencyChainStatus

| Field | Type | Constraints |
|---|---|---|
| `docs_complete` | `boolean` | Required |
| `scaffold_complete` | `boolean` | Required |
| `model_complete` | `boolean` | Required |
| `storage_complete` | `boolean` | Required |
| `cli_complete` | `boolean` | Required |
| `chain_closed` | `boolean` | Required; represents `docs → scaffold → model → storage → CLI` closure |

---

## Cross-Subsystem Protocols

### 1. Dependency Chain Protocol

The TRD explicitly defines the subsystem dependency order:

1. Documentation
2. Scaffold
3. Model
4. Storage
5. CLI

#### Contract

- `scaffold` depends on successful prior documentation merge state.
- `model` depends on scaffold availability.
- `storage` depends on model availability.
- `cli` depends on storage availability.
- The chain is considered closed only when all stages are complete in order.

#### Ordered Dependency Representation

```text
docs -> scaffold -> model -> storage -> cli
```

---

### 2. Merge Recognition Protocol

The TRD states:

- A documentation PR fires the merge gate.
- Downstream PRs recognize that merge.

#### Contract

A downstream subsystem MUST be able to observe that the upstream PR has merged before proceeding as a dependent stage.

#### Minimal Exchange Fields

| Field | Type | Meaning |
|---|---|---|
| `pr_type` | `string` | Upstream PR classification |
| `merged` | `boolean` | Whether merge occurred |
| `recognized_by_downstream_prs` | `boolean` | Whether dependent PRs detected that merge |

---

### 3. Local Workspace Mirror Protocol

The TRD states:

- A scaffold PR with multiple package directories mirrors files to the local test workspace.

#### Contract

For each package directory in the scaffold, a mirror operation copies or reflects repository package contents into the local test workspace.

#### Minimal Exchange Fields

| Field | Type | Meaning |
|---|---|---|
| `package_directories` | `list[string]` | Directories to mirror |
| `source_path` | `string` | Original path |
| `destination_path` | `string` | Mirrored workspace path |
| `recursive` | `boolean` | Whether directory contents are mirrored recursively |

---

### 4. Local Import Resolution Protocol

The TRD states:

- Code PRs that import from previously-merged PRs resolve those imports locally before CI.

#### Contract

Before CI execution, any code artifact in a downstream PR that imports symbols from a previously merged upstream PR MUST resolve those imports in the local workspace.

#### Minimal Exchange Fields

| Field | Type | Meaning |
|---|---|---|
| `module_name` | `string` | Module performing imports |
| `imports_resolvable_locally` | `boolean` | Whether local resolution succeeds |
| `merged` | `boolean` | Whether the upstream dependency is already merged |

---

## Enums and Constants

### PRType

```text
documentation
scaffold
code
```

---

### DocumentName

```text
README
ARCHITECTURE
API_REFERENCE
```

---

### SubsystemName

```text
docs
scaffold
model
storage
cli
```

---

### DependencyChain

```text
docs -> scaffold -> model -> storage -> cli
```

---

### LibraryName

```text
tasklib
```

---

### TRD Metadata Constants

Derived directly from the provided TRD header:

| Constant | Value |
|---|---|
| `TRD_NAME` | `TRD-TASKLIB` |
| `TRD_VERSION` | `1.0` |
| `TRD_STATUS` | `Draft` |
| `TRD_DATE` | `2026-03-26` |
| `LIBRARY_NAME` | `tasklib` |

---

## Validation Rules

### 1. Documentation Validation

A valid documentation interface state MUST satisfy all of the following:

- `readme` is present
- `architecture_overview` is present
- `api_reference` is present

#### Rule Expression

```text
DocumentationSet is valid iff:
readme != null
and architecture_overview != null
and api_reference != null
```

---

### 2. Scaffold Validation

A valid scaffold interface state MUST satisfy:

- `package_directories` contains at least one entry
- multiple package directories are permitted
- mirror behavior to the local test workspace is represented
- each mirror operation has both source and destination paths

#### Rule Expression

```text
PythonPackageScaffold is valid iff:
len(package_directories) >= 1
and mirrored_to_local_test_workspace == true
```

```text
ScaffoldMirrorOperation is valid iff:
source_path is non-empty
and destination_path is non-empty
and recursive is boolean
```

---

### 3. Model Validation

A valid model interface state MUST satisfy:

- the model identifies itself as a task model
- local import resolution is explicitly represented for dependency handling

#### Rule Expression

```text
TaskModel is valid iff:
type == "task"
```

```text
ModelModuleContract is valid iff:
module_name is non-empty
and imports_resolvable_locally is boolean
```

---

### 4. Storage Validation

A valid storage interface state MUST satisfy:

- dependency on model is represented
- local import resolution is explicitly represented

#### Rule Expression

```text
StorageModuleContract is valid iff:
module_name is non-empty
and depends_on_model == true
and imports_resolvable_locally is boolean
```

---

### 5. CLI Validation

A valid CLI interface state MUST satisfy:

- dependency on storage is represented
- local import resolution is explicitly represented

#### Rule Expression

```text
CliModuleContract is valid iff:
module_name is non-empty
and depends_on_storage == true
and imports_resolvable_locally is boolean
```

---

### 6. Merge Recognition Validation

A valid merge recognition event MUST satisfy:

- `pr_type` is one of the allowed enum values
- `merged` is boolean
- if `pr_type == documentation`, `recognized_by_downstream_prs` must be present

#### Rule Expression

```text
PullRequestDependencyEvent is valid iff:
pr_type in {"documentation", "scaffold", "code"}
and merged is boolean
and (
  pr_type != "documentation"
  or recognized_by_downstream_prs is boolean
)
and (
  pr_type != "code"
  or resolves_imports_locally_before_ci is boolean
)
```

---

### 7. Dependency Chain Closure Validation

A valid closed chain MUST satisfy all stage-complete flags and the chain closure flag.

#### Rule Expression

```text
DependencyChainStatus is closed iff:
docs_complete == true
and scaffold_complete == true
and model_complete == true
and storage_complete == true
and cli_complete == true
and chain_closed == true
```

---

## Wire Format Examples

The TRDs do not prescribe a serialization format. For documentation purposes, the following examples use JSON as an illustrative wire format only.

### 1. Documentation Set Example

```json
{
  "readme": {
    "name": "README",
    "path": "README.md",
    "status": "present"
  },
  "architecture_overview": {
    "name": "ARCHITECTURE",
    "path": "ARCHITECTURE.md",
    "status": "present"
  },
  "api_reference": {
    "name": "API_REFERENCE",
    "path": "docs/API.md",
    "status": "present"
  }
}
```

---

### 2. Scaffold Example

```json
{
  "package_directories": [
    "tasklib",
    "tasklib/model",
    "tasklib/storage",
    "tasklib/cli"
  ],
  "mirrored_to_local_test_workspace": true,
  "source_root": ".",
  "workspace_root": "/local/test/workspace"
}
```

---

### 3. Scaffold Mirror Operation Example

```json
{
  "source_path": "tasklib/storage",
  "destination_path": "/local/test/workspace/tasklib/storage",
  "recursive": true,
  "status": "mirrored"
}
```

---

### 4. Model Module Contract Example

```json
{
  "module_name": "tasklib.model",
  "imports_resolvable_locally": true
}
```

---

### 5. Storage Module Contract Example

```json
{
  "module_name": "tasklib.storage",
  "depends_on_model": true,
  "imports_resolvable_locally": true
}
```

---

### 6. CLI Module Contract Example

```json
{
  "module_name": "tasklib.cli",
  "depends_on_storage": true,
  "imports_resolvable_locally": true
}
```

---

### 7. Documentation PR Merge Event Example

```json
{
  "pr_type": "documentation",
  "merged": true,
  "recognized_by_downstream_prs": true
}
```

---

### 8. Code PR Import Resolution Event Example

```json
{
  "pr_type": "code",
  "merged": true,
  "resolves_imports_locally_before_ci": true
}
```

---

### 9. Dependency Chain Status Example

```json
{
  "docs_complete": true,
  "scaffold_complete": true,
  "model_complete": true,
  "storage_complete": true,
  "cli_complete": true,
  "chain_closed": true
}
```

---

## Non-Derivable Interfaces

The following interface details are not defined in the provided TRDs and are therefore intentionally unspecified in this document:

- Task entity fields beyond existence of a task model
- CRUD operation signatures
- CLI commands, flags, arguments, or output schema
- Storage backend type or persistence format
- Error codes or exception schema
- Authentication or authorization mechanisms
- Network endpoints, HTTP routes, or RPC methods
- Version negotiation or backward compatibility policy
- Event bus, queue, or webhook payloads

---

## Source Basis

This document is derived only from:

- `TRD-TASKLIB`
- the provided architecture context excerpt, which does not define additional `tasklib` interface contracts relevant to this library

Where the TRD is silent, this document remains intentionally minimal.