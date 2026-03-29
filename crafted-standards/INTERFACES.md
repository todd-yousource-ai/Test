# INTERFACES.md

## Interface Contracts

This document defines the interface contracts derivable from the provided TRD material only.

Source basis:
- `TRD-TASKLIB`
- `forge_architecture_context`

Because the supplied TRD content is partial and explicitly identifies `tasklib` as a deliberately simple validation library rather than a production system, only interfaces directly supported by the text are specified here. No unstated endpoints, payloads, RPC methods, persistence schemas, or transport bindings are invented.

---

## Per-Subsystem Data Structures

### 1. Task Management Library (`tasklib`)

The TRD establishes `tasklib` as a Python task management library with a dependency chain:

- docs
- scaffold
- model
- storage
- CLI

The TRD excerpt does **not** define concrete task fields, storage record layouts, CLI argument schemas, or serialized object formats.

Accordingly, the only supported subsystem-level structures are the build/dependency-chain concepts and documentation artifacts named in the TRD.

#### 1.1 Dependency Chain Unit

Represents a stage in the validation dependency chain.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `name` | string | MUST be one of the defined stage names | Stage identifier |
| `depends_on` | array<string> | Each entry MUST name another defined stage | Declares upstream dependency stages |

#### Defined stage names

- `docs`
- `scaffold`
- `model`
- `storage`
- `CLI`

#### Canonical chain

| Stage | depends_on |
|---|---|
| `docs` | `[]` |
| `scaffold` | `["docs"]` |
| `model` | `["scaffold"]` |
| `storage` | `["model"]` |
| `CLI` | `["storage"]` |

---

### 2. Documentation Set

The TRD explicitly includes a documentation set.

#### 2.1 Documentation Artifact

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `name` | string | MUST be one of the documented artifact names | Artifact identifier |

#### Defined documentation artifact names

- `README`
- `ARCHITECTURE overview`
- `API reference`

No document body schema, frontmatter contract, or versioning metadata is defined in the provided TRD text.

---

### 3. Python Package Scaffold

The TRD specifies a Python package scaffold with multiple package directories and mirroring behavior to a local test workspace.

#### 3.1 Package Directory Descriptor

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `path` | string | MUST be a valid package directory path in the repository context | Exact path format unspecified in TRD |
| `mirrored_to_local_test_workspace` | boolean | Indicates whether mirroring occurred | Mirroring is a validation concern named by the TRD |

No required directory names, file manifests, import roots, or namespace package rules are defined in the supplied text.

---

### 4. Merge/PR Validation Concepts

The TRD defines behavior around documentation PRs, scaffold PRs, and code PRs in the Crafted Dev Agent pipeline.

#### 4.1 Pull Request Validation Unit

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `pr_type` | string | MUST be one of the known PR types | Identifies role in pipeline |
| `merged` | boolean | Indicates merge status | Used by downstream recognition logic |
| `downstream_recognizes_merge` | boolean | Applicable where downstream dependency exists | Derived from validation goals |
| `imports_resolve_locally_before_ci` | boolean | Applicable to code PRs importing from previously merged PRs | Explicitly stated in validation goals |

#### Defined PR types

- `documentation`
- `scaffold`
- `code`

The TRD does not define PR identifiers, webhook schemas, CI event payloads, branch naming conventions, or status check formats.

---

### 5. Forge Architecture Context

The injected architecture context describes platform subsystems and relationships. Only the explicitly named structures are captured.

#### 5.1 Platform Descriptor

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `name` | string | MUST be `Forge` | Platform name |
| `description` | string | Free text | Runtime policy enforcement and cryptographic identity platform for enterprise AI agents |

#### 5.2 CAL Subsystem Descriptor

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `name` | string | MUST be `CAL` | Conversation Abstraction Layer |
| `expanded_name` | string | MUST be `Conversation Abstraction Layer` | Long form |
| `role` | array<string> | Values MUST be supported by source text | Describes subsystem responsibilities |
| `positioning` | array<string> | Values MUST be supported by source text | Placement in architecture |
| `components` | array<string> | Values MUST be supported by source text | Named key components |

##### Supported `role` values
- `Enforcement choke point for all agent-originated action`

##### Supported `positioning` values
- `Sits above the VTZ enforcement plane`
- `Sits below application orchestration`

##### Supported `components` values
- `CPF`
- `AIR`
- `CTX-ID`
- `PEE`
- `TrustFlow/SIS`
- `CAL Verifier Cluster`

#### 5.3 CPF Subsystem Descriptor

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `name` | string | MUST be `CPF` | Conversation Plane Filter |
| `expanded_name` | string | MUST be `Conversation Plane Filter` | Long form |

No additional CPF fields are defined in the provided material; the description is incomplete.

---

## Cross-Subsystem Protocols

Only the following cross-subsystem contracts are directly established by the provided TRDs.

### 1. Crafted Dev Agent Validation Chain

The `tasklib` TRD defines an ordered dependency chain that must close fully:

`docs → scaffold → model → storage → CLI`

#### Protocol rules

1. A documentation PR merge is an upstream event.
2. The merge gate MUST fire on a documentation PR.
3. Downstream PRs MUST recognize that merge.
4. A scaffold PR MAY contain multiple package directories.
5. Files from the scaffold PR MUST mirror to the local test workspace.
6. Code PRs importing from previously merged PRs MUST resolve those imports locally before CI.
7. The dependency chain is considered closed only when all stages from `docs` through `CLI` complete in dependency order.

#### Abstract protocol state machine

| State | Trigger | Next State |
|---|---|---|
| `docs_pending` | documentation PR merged | `docs_merged` |
| `docs_merged` | scaffold PR prepared/merged with mirrored package directories | `scaffold_merged` |
| `scaffold_merged` | model implementation merged | `model_merged` |
| `model_merged` | storage implementation merged | `storage_merged` |
| `storage_merged` | CLI implementation merged | `cli_merged` |

The TRD does not define transport, event bus schema, webhook body, or CI provider protocol.

---

### 2. Local Import Resolution Contract

The TRD explicitly requires local resolution of imports from previously merged PRs before CI.

#### Protocol statement

For any code PR in the dependency chain:
- if the PR imports code originating from a previously merged PR,
- those imports MUST resolve in the local workspace before CI execution.

#### Implied participants

- previously merged PR content
- local test workspace
- code PR under validation
- CI boundary

No module resolution algorithm, path precedence rules, or environment variable contract is specified in the supplied text.

---

### 3. CAL Enforcement Path

From the architecture context, CAL is the mandatory enforcement point for agent-originated action.

#### Protocol statement

No:
- tool call
- data read
- API invocation
- agent handoff

may execute without passing through CAL policy evaluation.

This is a normative architectural rule from the provided context. However, no request/response message schema, policy evaluation payload, or error contract is defined in the supplied material.

---

### 4. Architectural Positioning Protocol

CAL is positioned:
- above the VTZ enforcement plane
- below application orchestration

This is a placement/interface relationship, not a wire-level payload definition. No call signatures between CAL and VTZ or between CAL and orchestration are provided.

---

## Enums and Constants

### 1. Tasklib Dependency Stages

```text
docs
scaffold
model
storage
CLI
```

### 2. Documentation Artifact Names

```text
README
ARCHITECTURE overview
API reference
```

### 3. PR Types

```text
documentation
scaffold
code
```

### 4. Forge Platform Constants

#### Platform name
```text
Forge
```

#### Subsystem names
```text
CAL
CPF
AIR
CTX-ID
PEE
TrustFlow/SIS
CAL Verifier Cluster
VTZ
```

### 5. CAL Prohibited-Without-Evaluation Action Types

```text
tool call
data read
API invocation
agent handoff
```

### 6. Version and Status Constants Explicitly Present

#### TRD-TASKLIB
```text
version = 1.0
status = Draft
date = 2026-03-26
author = Todd Gould / YouSource.ai
```

---

## Validation Rules

### 1. Source-of-Truth Rule

All interface definitions in this document are constrained to the provided TRD content only.

Therefore:
- undefined fields MUST NOT be assumed,
- undefined transports MUST NOT be assumed,
- undefined persistence schemas MUST NOT be assumed,
- undefined CLI syntax MUST NOT be assumed,
- undefined API endpoints MUST NOT be assumed.

---

### 2. Tasklib Chain Validation Rules

1. The dependency chain MUST be treated as ordered:
   - `docs`
   - `scaffold`
   - `model`
   - `storage`
   - `CLI`

2. `scaffold` MUST NOT be considered valid unless it reflects multiple package directories when such directories are present in the PR.

3. Files from the scaffold PR MUST mirror to the local test workspace.

4. Code PRs depending on previously merged PR outputs MUST resolve imports locally before CI.

5. The end-to-end validation succeeds only when the full chain closes:
   - `docs → scaffold → model → storage → CLI`

---

### 3. Documentation Validation Rules

The documentation set MUST include the explicitly named artifacts:
- `README`
- `ARCHITECTURE overview`
- `API reference`

No additional required document structure is defined by the supplied text.

---

### 4. CAL Enforcement Validation Rules

1. CAL MUST act as the enforcement choke point for all agent-originated action.
2. A tool call MUST NOT execute without CAL policy evaluation.
3. A data read MUST NOT execute without CAL policy evaluation.
4. An API invocation MUST NOT execute without CAL policy evaluation.
5. An agent handoff MUST NOT execute without CAL policy evaluation.

---

### 5. Architectural Completeness Rules

For Forge architecture context:
- CAL component lists MAY include only the explicitly named components from the source text.
- CPF MUST be recognized by its expanded name `Conversation Plane Filter`.
- No further CPF behavioral contract is validly derivable from the provided excerpt.

---

## Wire Format Examples

Because the supplied TRD content does not define an explicit wire protocol, the following examples are **illustrative canonical serializations** of the explicitly defined contracts only. They do **not** imply a mandated transport unless and until a TRD defines one.

### 1. Tasklib Dependency Chain Example

```json
{
  "library": "tasklib",
  "validation_chain": [
    {
      "name": "docs",
      "depends_on": []
    },
    {
      "name": "scaffold",
      "depends_on": ["docs"]
    },
    {
      "name": "model",
      "depends_on": ["scaffold"]
    },
    {
      "name": "storage",
      "depends_on": ["model"]
    },
    {
      "name": "CLI",
      "depends_on": ["storage"]
    }
  ]
}
```

---

### 2. Documentation Set Example

```json
{
  "documentation_set": [
    { "name": "README" },
    { "name": "ARCHITECTURE overview" },
    { "name": "API reference" }
  ]
}
```

---

### 3. PR Validation Example

```json
{
  "pull_requests": [
    {
      "pr_type": "documentation",
      "merged": true,
      "downstream_recognizes_merge": true
    },
    {
      "pr_type": "scaffold",
      "merged": true
    },
    {
      "pr_type": "code",
      "merged": false,
      "imports_resolve_locally_before_ci": true
    }
  ]
}
```

---

### 4. Package Scaffold Mirroring Example

```json
{
  "package_directories": [
    {
      "path": "package_dir_a",
      "mirrored_to_local_test_workspace": true
    },
    {
      "path": "package_dir_b",
      "mirrored_to_local_test_workspace": true
    }
  ]
}
```

Note: Directory names above are placeholders because no canonical package paths are provided in the TRD excerpt.

---

### 5. Forge CAL Subsystem Example

```json
{
  "platform": {
    "name": "Forge",
    "description": "runtime policy enforcement and cryptographic identity platform for enterprise AI agents"
  },
  "subsystem": {
    "name": "CAL",
    "expanded_name": "Conversation Abstraction Layer",
    "role": [
      "Enforcement choke point for all agent-originated action"
    ],
    "positioning": [
      "Sits above the VTZ enforcement plane",
      "Sits below application orchestration"
    ],
    "components": [
      "CPF",
      "AIR",
      "CTX-ID",
      "PEE",
      "TrustFlow/SIS",
      "CAL Verifier Cluster"
    ]
  }
}
```

---

### 6. CAL Enforcement Rule Example

```json
{
  "agent_originated_action_policy": {
    "requires_cal_evaluation_for": [
      "tool call",
      "data read",
      "API invocation",
      "agent handoff"
    ]
  }
}
```

---

## Non-Derivable Interfaces

The following interfaces are **not** specified in the provided TRD excerpts and therefore are intentionally omitted as normative contracts:

- concrete `Task` object schema
- task IDs, titles, status values, timestamps, or priority fields
- storage backend schema or file format
- CLI commands, flags, stdin/stdout contracts, exit codes
- Python module names or package import paths
- REST, RPC, GraphQL, gRPC, webhook, or message-bus endpoints
- CI event payload structures
- CAL request/response payloads
- policy decision object schemas
- CPF behavioral interfaces beyond naming

If those details exist in fuller TRDs, this document should be extended only from those source documents.