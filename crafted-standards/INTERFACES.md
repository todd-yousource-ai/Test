# INTERFACES.md

## Interface Contracts

This document defines the interface contracts derivable from the provided TRD content only. Where the TRD is incomplete or truncated, this document records only what is explicitly stated and avoids inventing unspecified interfaces.

---

## Per-Subsystem Data Structures

### 1. Task Management Library (`tasklib`)

The TRD identifies a deliberately simple Python task management library named `tasklib`.

#### 1.1 Library Metadata Structure

Derived from the TRD document header.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `name` | string | Must be `tasklib` | Library/package name |
| `version` | string | TRD value: `1.0` | TRD version |
| `status` | string | TRD value: `Draft` | Specification status |
| `author` | string | TRD value: `Todd Gould / YouSource.ai` | Document author |
| `date` | string | Must be ISO-like date string; TRD value `2026-03-26` | Document date |
| `purpose` | string | Non-empty | Validation purpose statement |

#### 1.2 Documentation Set

The TRD explicitly includes a documentation set.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `readme` | document/file reference | Required | README document |
| `architecture_overview` | document/file reference | Required | Architecture overview document |
| `api_reference` | document/file reference | Required | API reference document |

#### 1.3 Python Package Scaffold

The TRD explicitly includes a Python package scaffold with subpackage directories.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `package_name` | string | Expected to be `tasklib` | Root package name |
| `subpackages` | array of string | Zero or more directory names | Subpackage directories |
| `mirrored_to_local_test_workspace` | boolean | Used for validation workflow | Indicates scaffold files are mirrored locally |

#### 1.4 Validation Dependency Chain

The TRD defines a dependency chain across deliverables.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `chain` | array of string | Ordered; must match documented flow | End-to-end dependency sequence |

Allowed documented sequence:

```text
docs → scaffold → model → storage → CLI
```

#### 1.5 Pull Request / Merge Validation Unit

The TRD describes PR-driven validation behavior but does not define a wire protocol. The minimal structure derivable is:

| Field | Type | Constraints | Description |
|---|---|---|---|
| `pr_type` | string | One of documented chain stages where applicable | Type/category of PR |
| `merged` | boolean | Required | Whether the PR has merged |
| `downstream_recognizes_merge` | boolean | Required for validation scenarios | Whether downstream PRs detect merge |
| `imports_resolve_locally_before_ci` | boolean | Applicable to code PRs | Whether imports resolve in local workspace before CI |

No further PR payload fields are specified in the provided TRD.

---

### 2. Forge Platform Overview

The provided architecture context describes Forge at a platform level.

#### 2.1 Forge Platform Metadata

| Field | Type | Constraints | Description |
|---|---|---|---|
| `platform_name` | string | Must be `Forge` | Platform name |
| `category` | string | Non-empty | Runtime policy enforcement and cryptographic identity platform |
| `target_environment` | string | Non-empty | Enterprise AI agents |
| `enforcement_level` | string | Must reflect TRD wording | Enforcement below application stack |
| `identity_basis` | string | Must reflect TRD wording | Cryptographic identity |
| `policy_source` | string | Must reflect TRD wording | Operator-defined policy |

#### 2.2 CAL — Conversation Abstraction Layer

CAL is the most explicitly defined subsystem in the provided architecture context.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `name` | string | Must be `CAL` | Subsystem short name |
| `expanded_name` | string | Must be `Conversation Abstraction Layer` | Full subsystem name |
| `enforcement_choke_point` | boolean | Must be `true` per TRD | CAL is the enforcement choke point |
| `position_above` | string | Must be `VTZ enforcement plane` | Relative architectural position |
| `position_below` | string | Must be `application orchestration` | Relative architectural position |

#### 2.3 CAL Component Inventory

The architecture context lists CAL key components but does not define fields for their internal schemas.

| Component | Type | Constraints | Description |
|---|---|---|---|
| `CPF` | subsystem reference | Required in CAL component list | Conversation Plane Filter |
| `AIR` | subsystem reference | Required in CAL component list | Name only provided; expansion unspecified |
| `CTX-ID` | subsystem reference | Required in CAL component list | Name only provided; expansion unspecified |
| `PEE` | subsystem reference | Required in CAL component list | Name only provided; expansion unspecified |
| `TrustFlow/SIS` | subsystem reference | Required in CAL component list | Combined naming as provided |
| `CAL Verifier Cluster` | subsystem reference | Required in CAL component list | Verifier cluster component |

#### 2.4 CPF — Conversation Plane Filter

The architecture context provides only the subsystem name and expansion.

| Field | Type | Constraints | Description |
|---|---|---|---|
| `name` | string | Must be `CPF` | Subsystem short name |
| `expanded_name` | string | Must be `Conversation Plane Filter` | Full subsystem name |

No additional CPF wire structures are specified in the provided material.

---

## Cross-Subsystem Protocols

Only cross-subsystem behaviors explicitly stated in the TRDs are included here.

### 1. Tasklib Validation Pipeline Protocol

The TRD defines an ordered dependency and validation flow.

#### 1.1 Dependency Order

```text
docs → scaffold → model → storage → CLI
```

#### 1.2 Merge Recognition Protocol

Documented behavior:

1. A documentation PR fires the merge gate.
2. Downstream PRs recognize the merge.
3. A scaffold PR with multiple package directories mirrors files to the local test workspace.
4. Code PRs importing from previously merged PRs resolve imports locally before CI.
5. The complete chain closes in the documented order.

#### 1.3 Minimal State Transition Model

```text
documentation_merged
  → scaffold_available_locally
  → model_imports_resolve
  → storage_imports_resolve
  → cli_imports_resolve
  → dependency_chain_closed
```

No message framing, transport, API method, or event payload schema is specified in the provided TRD.

---

### 2. CAL Enforcement Protocol

The architecture context specifies CAL as the mandatory enforcement path for agent-originated action.

#### 2.1 Required Evaluation Path

Every action in the following categories must pass through CAL policy evaluation:

- tool call
- data read
- API invocation
- agent handoff

#### 2.2 Protocol Rule

```text
agent-originated action
  → CAL policy evaluation
  → execution decision
```

The provided material does not define:

- request message schema
- response message schema
- decision enum values
- transport
- authentication header format
- verifier exchange format

Therefore, no lower-level wire contract can be derived.

---

## Enums and Constants

### 1. Tasklib Constants

#### 1.1 Library Name

```text
tasklib
```

#### 1.2 TRD Version

```text
1.0
```

#### 1.3 TRD Status

```text
Draft
```

#### 1.4 Validation Chain Stages

```text
docs
scaffold
model
storage
CLI
```

#### 1.5 Documentation Set Names

```text
README
ARCHITECTURE overview
API reference
```

---

### 2. Forge Constants

#### 2.1 Platform Name

```text
Forge
```

#### 2.2 CAL Full Name

```text
Conversation Abstraction Layer
```

#### 2.3 CPF Full Name

```text
Conversation Plane Filter
```

#### 2.4 CAL Component Names

```text
CPF
AIR
CTX-ID
PEE
TrustFlow/SIS
CAL Verifier Cluster
```

#### 2.5 Action Categories Requiring CAL Evaluation

```text
tool call
data read
API invocation
agent handoff
```

#### 2.6 Architectural Position Constants

```text
above: VTZ enforcement plane
below: application orchestration
```

---

## Validation Rules

### 1. Tasklib Validation Rules

#### 1.1 Documentation Completeness

A valid tasklib documentation set must include:

- README
- ARCHITECTURE overview
- API reference

#### 1.2 Scaffold Validation

A valid scaffold stage must:

- provide a Python package scaffold
- include subpackage directories
- mirror files to the local test workspace

#### 1.3 Dependency Resolution Validation

A valid code PR stage must satisfy:

- imports from previously merged PRs resolve locally
- local resolution occurs before CI

#### 1.4 End-to-End Chain Validation

A valid end-to-end pipeline must satisfy the full ordered chain:

```text
docs → scaffold → model → storage → CLI
```

All earlier dependencies must be merged or available before downstream stages are considered valid.

#### 1.5 Merge Gate Validation

A valid documentation PR event must:

- fire the merge gate
- be recognizable by downstream PRs after merge

---

### 2. Forge / CAL Validation Rules

#### 2.1 Mandatory CAL Passage

No agent-originated action in the documented categories may execute without passing through CAL policy evaluation.

#### 2.2 Covered Action Types

The following actions are in-scope for mandatory CAL evaluation:

- tool call
- data read
- API invocation
- agent handoff

#### 2.3 Architectural Placement Rule

CAL must be understood as positioned:

- above the VTZ enforcement plane
- below application orchestration

This is an architectural contract from the provided context, not a transport-level validation rule.

---

## Wire Format Examples

Only minimal examples are provided, and only where a representable structure can be derived from the TRD text. These examples are descriptive artifacts, not evidence of a specified transport protocol.

### 1. Tasklib Metadata Example

```json
{
  "name": "tasklib",
  "version": "1.0",
  "status": "Draft",
  "author": "Todd Gould / YouSource.ai",
  "date": "2026-03-26",
  "purpose": "Validation TRD — proves Crafted Dev Agent pipeline end-to-end"
}
```

### 2. Tasklib Documentation Set Example

```json
{
  "readme": "README",
  "architecture_overview": "ARCHITECTURE overview",
  "api_reference": "API reference"
}
```

### 3. Tasklib Validation Chain Example

```json
{
  "chain": ["docs", "scaffold", "model", "storage", "CLI"]
}
```

### 4. Tasklib PR Validation Example

```json
{
  "pr_type": "scaffold",
  "merged": true,
  "downstream_recognizes_merge": true,
  "imports_resolve_locally_before_ci": true
}
```

### 5. Forge Platform Example

```json
{
  "platform_name": "Forge",
  "category": "runtime policy enforcement and cryptographic identity platform",
  "target_environment": "enterprise AI agents",
  "enforcement_level": "below the application stack",
  "identity_basis": "cryptographic identity",
  "policy_source": "operator-defined policy"
}
```

### 6. CAL Subsystem Example

```json
{
  "name": "CAL",
  "expanded_name": "Conversation Abstraction Layer",
  "enforcement_choke_point": true,
  "position_above": "VTZ enforcement plane",
  "position_below": "application orchestration",
  "components": [
    "CPF",
    "AIR",
    "CTX-ID",
    "PEE",
    "TrustFlow/SIS",
    "CAL Verifier Cluster"
  ]
}
```

### 7. CPF Example

```json
{
  "name": "CPF",
  "expanded_name": "Conversation Plane Filter"
}
```

### 8. CAL Enforcement Flow Example

```json
{
  "action_type": "API invocation",
  "must_pass_through": "CAL policy evaluation"
}
```

---

## Notes on Specification Boundaries

The provided TRD material is incomplete and truncated in several places. Accordingly, this document does **not** define any of the following, because they are not explicitly present in the source material:

- Python class schemas for tasks, models, storage entities, or CLI commands
- Function signatures or module import paths for `tasklib`
- REST, RPC, CLI, queue, or file transport protocols
- Authentication or authorization message formats
- Error codes or exception payloads
- Full subsystem definitions for AIR, CTX-ID, PEE, TrustFlow/SIS, or CAL Verifier Cluster
- Internal CPF protocol behavior beyond its name

If additional TRDs are provided, this file should be expanded strictly from those source documents.