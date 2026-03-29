# INTERFACES.md

## Source Basis

This document is derived only from the provided TRD material:

- **TRD-TASKLIB**
- **forge_architecture_context**
- Required section headings from **Interface Contracts from standards**

Where the provided TRDs are incomplete or truncated, this document records only what is explicitly stated and avoids inventing unspecified interfaces.

---

# Interface Contracts

## Per-Subsystem Data Structures (field names, types, constraints)

### 1. Task Management Library (`tasklib`)

#### 1.1 Package / Documentation Artifact Set

The TRD explicitly places the following artifacts in scope:

| Artifact | Kind | Constraints |
|---|---|---|
| `README` | Documentation artifact | Must exist as part of documentation set |
| `ARCHITECTURE` overview | Documentation artifact | Must exist as part of documentation set |
| `API reference` | Documentation artifact | Must exist as part of documentation set |
| Python package scaffold | Package artifact | Must include subpackage directories |

No further field-level schema is defined in the provided TRD.

#### 1.2 Dependency Chain Stages

The TRD defines a dependency chain:

```text
docs → scaffold → model → storage → CLI
```

This establishes the following logical subsystem identifiers:

| Subsystem | Type | Constraint |
|---|---|---|
| `docs` | Pipeline stage / subsystem | Upstream of all later stages |
| `scaffold` | Pipeline stage / subsystem | Depends on `docs` |
| `model` | Pipeline stage / subsystem | Depends on `scaffold` |
| `storage` | Pipeline stage / subsystem | Depends on `model` |
| `CLI` | Pipeline stage / subsystem | Depends on `storage` |

No internal data model for these stages is defined in the provided TRD.

---

### 2. Forge Platform

The architecture context defines Forge as:

> a runtime policy enforcement and cryptographic identity platform for enterprise AI agents

This yields the following top-level subsystem entities.

#### 2.1 Forge Platform

| Field | Type | Constraints |
|---|---|---|
| `name` | string | Value: `Forge` |
| `purpose` | string | Runtime policy enforcement and cryptographic identity platform |
| `target_domain` | string | Enterprise AI agents |

#### 2.2 CAL — Conversation Abstraction Layer

Explicitly defined characteristics:

| Field | Type | Constraints |
|---|---|---|
| `name` | string | Value: `CAL` |
| `expanded_name` | string | Value: `Conversation Abstraction Layer` |
| `role` | string | Enforcement choke point for all agent-originated action |
| `position_above` | string | Above the VTZ enforcement plane |
| `position_below` | string | Below application orchestration |

Behavioral constraints captured as interface requirements:

| Field | Type | Constraints |
|---|---|---|
| `gates_tool_call` | boolean | Must be `true` |
| `gates_data_read` | boolean | Must be `true` |
| `gates_api_invocation` | boolean | Must be `true` |
| `gates_agent_handoff` | boolean | Must be `true` |
| `requires_policy_evaluation` | boolean | Must be `true` for all gated actions |

#### 2.3 CAL Key Components

The architecture context names the following CAL components:

| Component | Type | Constraints |
|---|---|---|
| `CPF` | Subcomponent | Part of CAL |
| `AIR` | Subcomponent | Part of CAL |
| `CTX-ID` | Subcomponent | Part of CAL |
| `PEE` | Subcomponent | Part of CAL |
| `TrustFlow/SIS` | Subcomponent | Part of CAL |
| `CAL Verifier Cluster` | Subcomponent | Part of CAL |

No additional field schemas are defined for these components in the provided material.

#### 2.4 CPF — Conversation Plane Filter

The architecture context provides:

| Field | Type | Constraints |
|---|---|---|
| `name` | string | Value: `CPF` |
| `expanded_name` | string | Value: `Conversation Plane Filter` |

No further structure is provided.

---

## Cross-Subsystem Protocols

### 1. Tasklib Pipeline Protocols

The TRD defines validation goals that act as required cross-subsystem behaviors.

#### 1.1 Documentation Merge Propagation Protocol

**Source statement:**  
“A documentation PR fires the merge gate and downstream PRs recognize the merge”

**Contract:**

1. A documentation PR merges.
2. That merge triggers a merge gate event.
3. Downstream PRs must detect or recognize that the upstream documentation merge occurred.

**Protocol participants:**

- `docs` stage
- merge gate mechanism
- downstream PR stages

**Minimum guarantees:**

- Merge of `docs` is observable by downstream stages.
- Downstream dependency resolution includes prior merged state.

#### 1.2 Scaffold Workspace Mirroring Protocol

**Source statement:**  
“A scaffold PR with multiple package directories mirrors files to the local test workspace”

**Contract:**

1. A scaffold PR includes multiple package directories.
2. Files from those package directories are mirrored into a local test workspace.
3. The local workspace must reflect the scaffold PR contents sufficiently for subsequent stages.

**Protocol participants:**

- `scaffold` stage
- package directories
- local test workspace

#### 1.3 Local Import Resolution Protocol

**Source statement:**  
“Code PRs that import from previously-merged PRs resolve those imports locally before CI”

**Contract:**

1. A code PR may import modules introduced by previously merged PRs.
2. Those imports must resolve in the local environment.
3. Resolution must occur before CI execution.

**Protocol participants:**

- code PR
- previously merged PR outputs
- local environment
- CI

#### 1.4 Full Dependency Chain Closure Protocol

**Source statement:**  
“The full dependency chain closes: docs → scaffold → model → storage → CLI”

**Contract:**

Execution or merge ordering must respect the following dependency path:

```text
docs → scaffold → model → storage → CLI
```

Each downstream stage depends on successful upstream completion or merged state.

---

### 2. Forge Enforcement Protocol

The architecture context defines one explicit protocol for agent-originated actions.

#### 2.1 CAL Policy Evaluation Protocol

**Source statement:**  
“No tool call, data read, API invocation, or agent handoff executes without passing through a CAL policy evaluation”

**Contract:**

For every agent-originated action in the following set:

- tool call
- data read
- API invocation
- agent handoff

the action must:

1. pass through CAL, and
2. receive a policy evaluation before execution.

**Protocol invariant:**

```text
execute(action) => prior CAL policy evaluation(action)
```

**Forbidden condition:**

Any direct execution path that bypasses CAL for the above action classes.

#### 2.2 Placement Protocol

**Source statement:**  
“CAL sits above the VTZ enforcement plane, below application orchestration”

**Contract:**

The ordering of layers must satisfy:

```text
application orchestration
    ↓
CAL
    ↓
VTZ enforcement plane
```

No other layer-order semantics are defined in the provided TRDs.

---

## Enums and Constants

### 1. Documented Identifiers

#### 1.1 Tasklib Constants

| Name | Type | Value |
|---|---|---|
| `TRD_TASKLIB_VERSION` | string | `1.0` |
| `TRD_TASKLIB_STATUS` | string | `Draft` |
| `TRD_TASKLIB_DATE` | string | `2026-03-26` |
| `TASKLIB_PACKAGE_NAME` | string | `tasklib` |

#### 1.2 Tasklib Dependency Stage Enum

```text
docs
scaffold
model
storage
CLI
```

Recommended literal set, as directly derived from the TRD:

| Enum Member |
|---|
| `docs` |
| `scaffold` |
| `model` |
| `storage` |
| `CLI` |

#### 1.3 Tasklib Documentation Artifact Enum

| Enum Member |
|---|
| `README` |
| `ARCHITECTURE` |
| `API_REFERENCE` |

`API_REFERENCE` is a normalized label for the TRD phrase “API reference”.

---

### 2. Forge Constants

#### 2.1 Platform and Layer Names

| Name | Type | Value |
|---|---|---|
| `FORGE_PLATFORM_NAME` | string | `Forge` |
| `CAL_NAME` | string | `CAL` |
| `CAL_EXPANDED_NAME` | string | `Conversation Abstraction Layer` |
| `CPF_NAME` | string | `CPF` |
| `CPF_EXPANDED_NAME` | string | `Conversation Plane Filter` |
| `VTZ_LAYER_NAME` | string | `VTZ enforcement plane` |

#### 2.2 Agent-Originated Action Enum

Directly derived from the architecture context:

| Enum Member |
|---|
| `tool_call` |
| `data_read` |
| `api_invocation` |
| `agent_handoff` |

#### 2.3 CAL Component Enum

| Enum Member |
|---|
| `CPF` |
| `AIR` |
| `CTX-ID` |
| `PEE` |
| `TrustFlow/SIS` |
| `CAL Verifier Cluster` |

---

## Validation Rules

### 1. Tasklib Validation Rules

#### 1.1 Documentation Presence

The documentation set must include all of:

- `README`
- `ARCHITECTURE` overview
- `API reference`

#### 1.2 Scaffold Structure

A scaffold PR may contain multiple package directories, and those directories must be mirrored to the local test workspace.

#### 1.3 Upstream Merge Recognition

When a documentation PR merges, downstream PRs must recognize that merged state.

#### 1.4 Local Pre-CI Import Resolution

Imports from previously merged PRs must resolve locally before CI starts.

#### 1.5 Dependency Ordering

The dependency chain must be ordered exactly as documented:

```text
docs → scaffold → model → storage → CLI
```

A stage must not be treated as complete in the chain if its upstream dependency state is unavailable.

---

### 2. Forge Validation Rules

#### 2.1 Mandatory CAL Evaluation

For every agent-originated action of type:

- `tool_call`
- `data_read`
- `api_invocation`
- `agent_handoff`

CAL policy evaluation is mandatory before execution.

#### 2.2 No CAL Bypass

Any execution path for the above action classes that does not pass through CAL is invalid.

#### 2.3 Layer Placement

CAL must be positioned:

- below application orchestration
- above the VTZ enforcement plane

#### 2.4 CAL Component Membership

The CAL subsystem includes the named components:

- `CPF`
- `AIR`
- `CTX-ID`
- `PEE`
- `TrustFlow/SIS`
- `CAL Verifier Cluster`

No omission of these named components is permitted in a representation claiming conformance to the provided architecture context.

---

## Wire Format Examples

The provided TRDs do not define a normative serialization format such as JSON, YAML, protobuf, HTTP, CLI argument grammar, or binary framing. Therefore, the examples below are **illustrative logical representations only**, using JSON for readability. They are not normative unless another source document defines JSON as the wire format.

### 1. Tasklib Dependency Chain Example

```json
{
  "library": "tasklib",
  "version": "1.0",
  "status": "Draft",
  "dependency_chain": [
    "docs",
    "scaffold",
    "model",
    "storage",
    "CLI"
  ]
}
```

### 2. Tasklib Documentation Set Example

```json
{
  "artifacts": [
    "README",
    "ARCHITECTURE",
    "API_REFERENCE"
  ]
}
```

### 3. Tasklib Merge/Resolution Flow Example

```json
{
  "events": [
    {
      "stage": "docs",
      "event": "merged"
    },
    {
      "stage": "scaffold",
      "event": "recognized_upstream_merge"
    },
    {
      "stage": "model",
      "event": "local_imports_resolved_before_ci"
    }
  ]
}
```

### 4. Forge CAL Enforcement Example

```json
{
  "platform": "Forge",
  "subsystem": {
    "name": "CAL",
    "expanded_name": "Conversation Abstraction Layer",
    "position": {
      "below": "application orchestration",
      "above": "VTZ enforcement plane"
    },
    "gates": [
      "tool_call",
      "data_read",
      "api_invocation",
      "agent_handoff"
    ],
    "requires_policy_evaluation": true,
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

### 5. Forge CPF Example

```json
{
  "component": {
    "name": "CPF",
    "expanded_name": "Conversation Plane Filter"
  }
}
```

---

## Non-Specified Interfaces

The following interface details are **not defined** in the provided TRD excerpts and therefore are intentionally omitted from this contract:

- Python class names
- Function signatures
- Module paths
- CLI command syntax
- Storage schema
- HTTP endpoints
- Request/response bodies
- Error codes
- Authentication formats
- Event payload schemas
- Serialization framing rules

If additional TRD material exists for those interfaces, this document should be extended strictly from that source.