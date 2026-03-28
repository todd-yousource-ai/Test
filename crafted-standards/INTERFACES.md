# INTERFACES.md

This document defines the wire formats and interface contracts derivable from the provided TRD material only.

## Interface Contracts

### Source Basis

This file is derived from:

- `TRD-TASKLIB`
- `forge_architecture_context`

Because the provided TRD content is partial and explicitly scoped as validation documentation, only interfaces directly supported by that text are specified here. Where the TRD names subsystems but does not define fields or protocol behavior, those interfaces are listed as declared but unspecified.

---

## Per-Subsystem Data Structures

### 1. Task Management Library (`tasklib`)

The TRD establishes `tasklib` as a deliberately simple Python task management library and identifies the following documentation/API areas as in scope:

- README
- ARCHITECTURE overview
- API reference

It also defines a dependency chain:

- docs
- scaffold
- model
- storage
- CLI

From this, the following subsystem-level structures are supported.

#### 1.1 Documentation Artifact

Represents a documentation unit in the `docs` stage.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `name` | string | yes | Must identify one of the in-scope documentation artifacts named by the TRD |
| `kind` | string | yes | Must be a supported documentation kind |
| `status` | string | no | If present, constrained by documented lifecycle enums where available |

##### Allowed `name` values

- `README`
- `ARCHITECTURE`
- `API_REFERENCE`

##### Allowed `kind` values

- `readme`
- `architecture_overview`
- `api_reference`

#### 1.2 Package Scaffold

Represents scaffolded Python package structure.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `package_name` | string | yes | For this TRD, package is `tasklib` |
| `subpackage_directories` | array<string> | no | TRD states scaffold includes subpackage directories; specific names not provided |
| `mirrored_to_local_test_workspace` | boolean | no | Used to express the validation goal that scaffold PR mirrors files locally |

#### 1.3 Pull Request Validation Stage

Represents a stage in the end-to-end dependency chain.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `stage` | string | yes | Must be one of the dependency-chain stages listed in the TRD |
| `merged` | boolean | yes | Indicates whether the stage PR is merged |
| `downstream_recognized_merge` | boolean | no | Applicable to dependency validation stages |
| `imports_resolve_locally_before_ci` | boolean | no | Applicable to code stages that import prior merged work |

##### Allowed `stage` values

- `docs`
- `scaffold`
- `model`
- `storage`
- `cli`

#### 1.4 Dependency Chain Record

Represents the documented pipeline closure condition.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `stages` | array<string> | yes | Ordered chain must follow TRD sequence |
| `closed` | boolean | yes | True only when full chain is complete |

##### Required order

1. `docs`
2. `scaffold`
3. `model`
4. `storage`
5. `cli`

---

### 2. Forge Platform Overview

The architecture context defines Forge as:

> a runtime policy enforcement and cryptographic identity platform for enterprise AI agents

This provides platform-level subsystem declarations, but not concrete field schemas.

#### 2.1 Forge Platform Descriptor

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `platform_name` | string | yes | Must be `Forge` |
| `purpose` | string | yes | Runtime policy enforcement and cryptographic identity platform |
| `domain` | string | yes | Enterprise AI agents |

#### 2.2 Core Subsystem Declaration

Represents a named subsystem defined by the architecture context.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `name` | string | yes | Must match a subsystem named in provided context |
| `description` | string | no | Free-text description from TRD/context |
| `position` | string | no | Relative stack position if explicitly provided |
| `key_components` | array<string> | no | Only where explicitly enumerated |

##### Declared subsystem names

- `CAL`
- `CPF`

---

### 3. CAL — Conversation Abstraction Layer

The architecture context explicitly defines CAL behavior and relationships.

#### 3.1 CAL Subsystem Contract

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `name` | string | yes | Must be `CAL` |
| `expansion` | string | yes | Must be `Conversation Abstraction Layer` |
| `role` | array<string> | yes | Must contain explicitly documented CAL roles |
| `position_above` | string | no | Must be `VTZ enforcement plane` if provided |
| `position_below` | string | no | Must be `application orchestration` if provided |
| `key_components` | array<string> | no | Limited to enumerated components in source text |

##### Required `role` members

- `Enforcement choke point for all agent-originated action`
- `No tool call, data read, API invocation, or agent handoff executes without passing through a CAL policy evaluation`

##### Allowed `key_components`

- `CPF`
- `AIR`
- `CTX-ID`
- `PEE`
- `TrustFlow/SIS`
- `CAL Verifier Cluster`

---

### 4. CPF — Conversation Plane Filter

The architecture context names CPF and expands the acronym, but provides no further interface details.

#### 4.1 CPF Subsystem Contract

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `name` | string | yes | Must be `CPF` |
| `expansion` | string | yes | Must be `Conversation Plane Filter` |
| `description` | string | no | No additional contract specified in provided material |

---

## Cross-Subsystem Protocols

Only protocols explicitly inferable from the TRD text are included.

### 1. Tasklib Dependency Chain Protocol

Defines the required stage dependency ordering for the validation pipeline.

#### Protocol Summary

A downstream stage depends on prior stage merge completion in this exact order:

`docs → scaffold → model → storage → cli`

#### Contract Rules

1. A documentation PR merge must occur before downstream PRs can recognize that merge.
2. A scaffold PR must mirror files, including multiple package directories, to the local test workspace.
3. Code PRs importing from previously merged PRs must resolve those imports locally before CI.
4. The chain is considered closed only when all stages complete in order.

#### Minimal protocol message shape

```json
{
  "stages": [
    {"stage": "docs", "merged": true},
    {"stage": "scaffold", "merged": true},
    {"stage": "model", "merged": true, "imports_resolve_locally_before_ci": true},
    {"stage": "storage", "merged": true, "imports_resolve_locally_before_ci": true},
    {"stage": "cli", "merged": true, "imports_resolve_locally_before_ci": true}
  ],
  "closed": true
}
```

---

### 2. CAL Enforcement Passage Protocol

The architecture context defines a mandatory pass-through requirement for CAL.

#### Protocol Summary

The following action classes must not execute without CAL policy evaluation:

- tool call
- data read
- API invocation
- agent handoff

#### Contract Rules

1. Every agent-originated action must pass through CAL.
2. CAL functions as the enforcement choke point.
3. CAL sits above the VTZ enforcement plane and below application orchestration.
4. No wire-level request or response schema is specified in the provided material.

#### Abstract action gate shape

```json
{
  "subsystem": "CAL",
  "action_type": "tool_call",
  "policy_evaluated": true
}
```

---

### 3. CAL Component Reference Protocol

The context establishes that CAL includes or references named key components.

#### Referenced components

- `CPF`
- `AIR`
- `CTX-ID`
- `PEE`
- `TrustFlow/SIS`
- `CAL Verifier Cluster`

No message sequencing, transport, or payload schemas are defined for communication among these components in the provided source material.

---

## Enums and Constants

### 1. TRD Document Metadata Constants

From `TRD-TASKLIB`:

| Name | Value |
|---|---|
| `TRD_TASKLIB_VERSION` | `1.0` |
| `TRD_TASKLIB_STATUS` | `Draft` |
| `TRD_TASKLIB_AUTHOR` | `Todd Gould / YouSource.ai` |
| `TRD_TASKLIB_DATE` | `2026-03-26` |

---

### 2. Tasklib Stage Enum

```text
docs
scaffold
model
storage
cli
```

---

### 3. Documentation Artifact Name Enum

```text
README
ARCHITECTURE
API_REFERENCE
```

---

### 4. Documentation Artifact Kind Enum

```text
readme
architecture_overview
api_reference
```

---

### 5. Forge Subsystem Name Enum

```text
CAL
CPF
```

---

### 6. CAL Component Enum

```text
CPF
AIR
CTX-ID
PEE
TrustFlow/SIS
CAL Verifier Cluster
```

---

### 7. CAL Action Type Enum

Only action categories explicitly named in the context are included.

```text
tool_call
data_read
api_invocation
agent_handoff
```

---

### 8. Positional Constants

```text
VTZ enforcement plane
application orchestration
```

---

## Validation Rules

### 1. Tasklib Validation Rules

#### 1.1 Package identity

- `package_name` for the scoped library must be `tasklib`.

#### 1.2 Dependency chain order

- If `stages` is provided for the tasklib validation chain, it must appear in this order:
  1. `docs`
  2. `scaffold`
  3. `model`
  4. `storage`
  5. `cli`

#### 1.3 Chain closure

- `closed` may be `true` only if all dependency chain stages are present and complete.

#### 1.4 Merge dependency recognition

- A documentation PR must be merged before downstream PRs can recognize that merge.

#### 1.5 Local workspace mirroring

- A scaffold PR must support mirroring files to the local test workspace.
- The TRD states this includes multiple package directories.
- Specific directory names are not defined in the provided material.

#### 1.6 Local import resolution before CI

- For code PRs importing from previously merged PRs, imports must resolve locally before CI.
- The TRD does not define a specific resolver interface or file layout contract.

---

### 2. Documentation Artifact Validation Rules

- `name` must be one of:
  - `README`
  - `ARCHITECTURE`
  - `API_REFERENCE`
- `kind` must be one of:
  - `readme`
  - `architecture_overview`
  - `api_reference`

---

### 3. Forge Platform Validation Rules

#### 3.1 CAL mandatory passage

Any agent-originated action in the explicitly named categories must not execute unless CAL policy evaluation has occurred.

#### 3.2 CAL positional relationship

If positional fields are represented:

- `position_above` must be `VTZ enforcement plane`
- `position_below` must be `application orchestration`

#### 3.3 CAL component membership

If `key_components` is provided for CAL, values must be chosen from:

- `CPF`
- `AIR`
- `CTX-ID`
- `PEE`
- `TrustFlow/SIS`
- `CAL Verifier Cluster`

#### 3.4 CPF contract completeness

- Only the name and expansion of CPF are specified by the provided context.
- No additional validation constraints can be derived.

---

### 4. Undefined or Unspecified Interfaces

The following are named or implied by the provided materials but do not have sufficient TRD detail to define full contracts:

- `model` subsystem payload schema
- `storage` subsystem payload schema
- `CLI` command/request/response schema
- specific Python class or function signatures for `tasklib`
- CAL internal message formats
- CPF internal message formats
- `AIR` interface
- `CTX-ID` interface
- `PEE` interface
- `TrustFlow/SIS` interface
- `CAL Verifier Cluster` interface
- `VTZ enforcement plane` interface

These must not be invented beyond the declarations above.

---

## Wire Format Examples

Only example payloads grounded in the provided TRD text are included.

### 1. Documentation Artifact Example

```json
{
  "name": "README",
  "kind": "readme",
  "status": "Draft"
}
```

---

### 2. Package Scaffold Example

```json
{
  "package_name": "tasklib",
  "subpackage_directories": [],
  "mirrored_to_local_test_workspace": true
}
```

Note: the TRD confirms subpackage directories exist but does not provide their names.

---

### 3. PR Validation Stage Example

```json
{
  "stage": "scaffold",
  "merged": true,
  "downstream_recognized_merge": true
}
```

---

### 4. Full Dependency Chain Example

```json
{
  "stages": [
    {
      "stage": "docs",
      "merged": true,
      "downstream_recognized_merge": true
    },
    {
      "stage": "scaffold",
      "merged": true
    },
    {
      "stage": "model",
      "merged": true,
      "imports_resolve_locally_before_ci": true
    },
    {
      "stage": "storage",
      "merged": true,
      "imports_resolve_locally_before_ci": true
    },
    {
      "stage": "cli",
      "merged": true,
      "imports_resolve_locally_before_ci": true
    }
  ],
  "closed": true
}
```

---

### 5. Forge Platform Descriptor Example

```json
{
  "platform_name": "Forge",
  "purpose": "runtime policy enforcement and cryptographic identity platform",
  "domain": "enterprise AI agents"
}
```

---

### 6. CAL Subsystem Example

```json
{
  "name": "CAL",
  "expansion": "Conversation Abstraction Layer",
  "role": [
    "Enforcement choke point for all agent-originated action",
    "No tool call, data read, API invocation, or agent handoff executes without passing through a CAL policy evaluation"
  ],
  "position_above": "VTZ enforcement plane",
  "position_below": "application orchestration",
  "key_components": [
    "CPF",
    "AIR",
    "CTX-ID",
    "PEE",
    "TrustFlow/SIS",
    "CAL Verifier Cluster"
  ]
}
```

---

### 7. CPF Subsystem Example

```json
{
  "name": "CPF",
  "expansion": "Conversation Plane Filter"
}
```

---

### 8. CAL Enforcement Gate Example

```json
{
  "subsystem": "CAL",
  "action_type": "api_invocation",
  "policy_evaluated": true
}
```

---

## Notes

- This document intentionally avoids inventing interfaces not present in the supplied TRD excerpts.
- The `TRD-TASKLIB` excerpt is truncated; therefore only the explicitly visible tasklib contracts are included.
- The architecture context is descriptive, not a complete protocol specification. Accordingly, only declared names, roles, and mandatory constraints are formalized here.