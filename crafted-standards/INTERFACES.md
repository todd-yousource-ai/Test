# Interface Contracts

This document defines the interface contracts derivable from the provided TRD material only.

Because the source TRD is a validation TRD with intentionally limited implementation detail, this file records only the explicit and safely implied interfaces present in the provided documents. No undocumented production behavior is invented here.

## Source Basis

Derived from:

- `TRD-TASKLIB`
- `forge_architecture_context`

## Scope of This Document

Covers:

- Task management library subsystem interfaces explicitly described or directly implied by `TRD-TASKLIB`
- Forge architecture subsystem names and their stated responsibilities from `forge_architecture_context`
- Validation-oriented dependency and import contracts called out by the TRD
- Required sections:
  - Per-Subsystem Data Structures
  - Cross-Subsystem Protocols
  - Enums and Constants
  - Validation Rules
  - Wire Format Examples

Does not cover:

- Undocumented method signatures
- Storage schema details not present in the TRD
- CLI argument grammar not present in the TRD
- CAL/CPF/AIR/CTX-ID/PEE/TrustFlow/SIS/Verifier message formats beyond what is explicitly stated

---

## Per-Subsystem Data Structures

## 1. Task Management Library (`tasklib`)

### 1.1 Library Identity

A minimal Python package scaffold is explicitly in scope.

#### Data Structure: `TasklibPackage`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `name` | `string` | Must identify the Python package as `tasklib` | TRD states a "Python task management library (tasklib)" |
| `language` | `string` | Must be `Python` | TRD |
| `purpose` | `string` | Validation-oriented, not production | TRD says "not a production system" |
| `version` | `string` | TRD version is `1.0` | TRD header |
| `status` | `string` | `Draft` in TRD metadata | TRD header |

### 1.2 Documentation Set

The documentation set is explicitly in scope.

#### Data Structure: `DocumentationSet`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `readme_present` | `boolean` | Required | TRD: "A documentation set: README, ARCHITECTURE overview, API reference" |
| `architecture_overview_present` | `boolean` | Required | TRD |
| `api_reference_present` | `boolean` | Required | TRD |

### 1.3 Package Scaffold

The scaffold must include multiple package directories.

#### Data Structure: `PackageScaffold`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `subpackage_directories` | `array[string]` | Must contain multiple package directories | TRD: "Python package scaffold with subpackage dire..." and validation goal mentions "multiple package directories" |
| `mirrored_to_local_test_workspace` | `boolean` | Must be true for validation success | TRD validation goal |

### 1.4 Dependency Chain Stages

The full dependency chain is explicitly named.

#### Data Structure: `DependencyChain`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `stages` | `array[string]` | Ordered chain must be `docs`, `scaffold`, `model`, `storage`, `CLI` | TRD: "docs → scaffold → model → storage → CLI" |
| `closed` | `boolean` | True only when all stages complete in order and integrate successfully | TRD |
| `imports_resolve_locally_before_ci` | `boolean` | Required for code PR validation | TRD |

### 1.5 Pull Request Validation Artifact

The TRD is centered on PR-triggered validation behavior.

#### Data Structure: `ValidationPR`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `pr_type` | `string` | See enum `PRType` | Derived from explicit PR categories in TRD |
| `merge_gate_fired` | `boolean` | Required for documentation PR validation | TRD |
| `downstream_prs_recognize_merge` | `boolean` | Required after upstream merge | TRD |
| `files_mirrored_to_local_workspace` | `boolean` | Required for scaffold PR validation | TRD |
| `local_import_resolution_success` | `boolean` | Required for code PR validation | TRD |
| `ci_dependency_ready` | `boolean` | Implied true only if local imports resolve before CI | Directly implied by TRD |

---

## 2. Forge Platform Overview

The architecture context provides subsystem names and stated responsibilities. Only those are captured here.

### 2.1 Forge Platform

#### Data Structure: `ForgePlatform`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `name` | `string` | Must be `Forge` | Architecture context |
| `platform_role` | `string` | Runtime policy enforcement and cryptographic identity platform | Architecture context |
| `target_domain` | `string` | Enterprise AI agents | Architecture context |

### 2.2 CAL — Conversation Abstraction Layer

#### Data Structure: `CALSubsystem`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `name` | `string` | Must be `CAL` | Architecture context |
| `expanded_name` | `string` | Must be `Conversation Abstraction Layer` | Architecture context |
| `enforcement_choke_point` | `boolean` | True | Architecture context |
| `position_above_vtz` | `boolean` | True | Architecture context: "Sits above the VTZ enforcement plane" |
| `position_below_application_orchestration` | `boolean` | True | Architecture context |
| `requires_policy_evaluation_for_agent_actions` | `boolean` | True | Architecture context |
| `components` | `array[string]` | Must include `CPF`, `AIR`, `CTX-ID`, `PEE`, `TrustFlow/SIS`, `CAL Verifier Cluster` | Architecture context |

### 2.3 CPF — Conversation Plane Filter

Only the subsystem name and expansion are present.

#### Data Structure: `CPFSubsystem`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `name` | `string` | Must be `CPF` | Architecture context |
| `expanded_name` | `string` | Must be `Conversation Plane Filter` | Architecture context |

### 2.4 AIR

Mentioned only as a CAL component.

#### Data Structure: `AIRSubsystemRef`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `name` | `string` | Must be `AIR` | Architecture context |

### 2.5 CTX-ID

Mentioned only as a CAL component.

#### Data Structure: `CTXIDSubsystemRef`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `name` | `string` | Must be `CTX-ID` | Architecture context |

### 2.6 PEE

Mentioned only as a CAL component.

#### Data Structure: `PEESubsystemRef`
| Field | Type | Constraints | Source Basis |
|---||---|---|
| `name` | `string` | Must be `PEE` | Architecture context |

### 2.7 TrustFlow/SIS

Mentioned only as a CAL component grouping.

#### Data Structure: `TrustFlowSISSubsystemRef`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `name` | `string` | Must be `TrustFlow/SIS` | Architecture context |

### 2.8 CAL Verifier Cluster

Mentioned only as a CAL component.

#### Data Structure: `CALVerifierClusterRef`
| Field | Type | Constraints | Source Basis |
|---|---|---|---|
| `name` | `string` | Must be `CAL Verifier Cluster` | Architecture context |

---

## Cross-Subsystem Protocols

## 1. Tasklib Validation Pipeline Protocol

The TRD defines a dependency chain and validation behavior across PR types.

### 1.1 Documentation-to-Downstream Recognition Protocol

#### Purpose
To validate that a documentation PR merge is observable by downstream PRs.

#### Participants
- Documentation PR
- Merge gate
- Downstream PRs

#### Protocol Steps
1. A documentation PR is created or processed.
2. The merge gate fires on that PR.
3. The documentation PR merges.
4. Downstream PRs recognize that the upstream merge occurred.

#### Required Outcomes
- `merge_gate_fired = true`
- `downstream_prs_recognize_merge = true`

### 1.2 Scaffold Mirroring Protocol

#### Purpose
To validate that a scaffold PR containing multiple package directories is mirrored into the local test workspace.

#### Participants
- Scaffold PR
- Package scaffold
- Local test workspace

#### Protocol Steps
1. A scaffold PR includes multiple package directories.
2. Files from those package directories are mirrored to the local test workspace.
3. The local workspace reflects the scaffolded package structure.

#### Required Outcomes
- `subpackage_directories.length >= 2`
- `files_mirrored_to_local_workspace = true`
- `mirrored_to_local_test_workspace = true`

### 1.3 Local Import Resolution Protocol

#### Purpose
To validate that code PRs depending on previously merged PRs can resolve imports locally before CI runs.

#### Participants
- Code PRs
- Previously merged PR outputs
- Local workspace
- CI

#### Protocol Steps
1. An upstream PR merges.
2. A downstream code PR imports symbols or modules from the merged PR.
3. The local workspace contains the merged dependency content.
4. Imports resolve locally before CI starts.

#### Required Outcomes
- `downstream_prs_recognize_merge = true`
- `local_import_resolution_success = true`
- `imports_resolve_locally_before_ci = true`

### 1.4 Full Dependency Chain Closure Protocol

#### Purpose
To validate end-to-end closure of the implementation chain.

#### Ordered Stages
1. `docs`
2. `scaffold`
3. `model`
4. `storage`
5. `CLI`

#### Protocol Rule
Each stage may depend on prior merged output, and the chain is considered closed only if all stages complete in the defined order with dependencies resolved.

#### Required Outcomes
- `stages = ["docs", "scaffold", "model", "storage", "CLI"]`
- `closed = true`

---

## 2. Forge Agent Action Enforcement Protocol

This protocol is limited strictly to the architecture statements provided.

### 2.1 CAL Enforcement Protocol

#### Purpose
To ensure all agent-originated actions pass through CAL policy evaluation.

#### Participants
- Agent-originated action
- CAL
- Policy evaluation mechanism
- VTZ enforcement plane
- Application orchestration layer

#### Protocol Rules
- No tool call executes without passing through CAL policy evaluation.
- No data read executes without passing through CAL policy evaluation.
- No API invocation executes without passing through CAL policy evaluation.
- No agent handoff executes without passing through CAL policy evaluation.
- CAL is positioned above the VTZ enforcement plane.
- CAL is positioned below application orchestration.

#### Required Invariants
- `enforcement_choke_point = true`
- `requires_policy_evaluation_for_agent_actions = true`

---

## Enums and Constants

## 1. Tasklib Enums

### 1.1 `PRType`
Allowed values derived from the TRD:

```text
docs
scaffold
model
storage
cli
code
```

Notes:

- `docs`, `scaffold`, `model`, `storage`, and `cli` are directly supported by the named dependency chain.
- `code` is supported by the TRD phrase "Code PRs".
- `CLI` appears capitalized in the chain; enum normalization here uses lowercase `cli` for value consistency, while preserving the documented stage name separately where needed.

### 1.2 `DependencyStage`
```text
docs
scaffold
model
storage
CLI
```

This preserves the exact stage naming from the TRD.

### 1.3 `DocumentType`
```text
README
ARCHITECTURE_OVERVIEW
API_REFERENCE
```

## 2. Forge Constants

### 2.1 `CALComponent`
```text
CPF
AIR
CTX-ID
PEE
TrustFlow/SIS
CAL Verifier Cluster
```

### 2.2 `BlockedWithoutCALEvaluationAction`
```text
tool_call
data_read
api_invocation
agent_handoff
```

### 2.3 `PlatformName`
```text
Forge
```

### 2.4 `CALName`
```text
CAL
```

### 2.5 `CPFName`
```text
CPF
```

---

## Validation Rules

## 1. Tasklib Validation Rules

### 1.1 General
- The library identifier must be `tasklib`.
- The implementation language must be Python.
- The system is validation-oriented and must not be represented as a production system.

### 1.2 Documentation Completeness
A documentation set is valid only if all of the following are present:
- README
- ARCHITECTURE overview
- API reference

### 1.3 Scaffold Validity
A scaffold is valid only if:
- it contains multiple package directories
- those files are mirrored to the local test workspace

### 1.4 Merge Recognition
A documentation-stage validation is valid only if:
- the merge gate fires
- downstream PRs recognize the merge

### 1.5 Import Resolution
A code-stage validation is valid only if:
- imports from previously merged PRs resolve locally
- local resolution occurs before CI

### 1.6 Dependency Chain Closure
The dependency chain is valid only if:
- stages occur in this order: `docs → scaffold → model → storage → CLI`
- all upstream dependencies are available to downstream work
- the chain closes end to end

## 2. Forge Validation Rules

### 2.1 CAL Enforcement
A Forge agent-action pathway is valid only if every agent-originated:
- tool call
- data read
- API invocation
- agent handoff

passes through CAL policy evaluation.

### 2.2 CAL Placement
The architectural placement is valid only if CAL:
- sits above the VTZ enforcement plane
- sits below application orchestration

### 2.3 CAL Component Presence
A CAL subsystem reference is valid only if it includes the documented components:
- CPF
- AIR
- CTX-ID
- PEE
- TrustFlow/SIS
- CAL Verifier Cluster

---

## Wire Format Examples

The source TRDs do not define a mandated serialization format. The examples below use JSON as a neutral illustrative wire format for the documented contracts only.

## 1. Tasklib Package Descriptor

```json
{
  "name": "tasklib",
  "language": "Python",
  "purpose": "Validation TRD — proves Crafted Dev Agent pipeline end-to-end",
  "version": "1.0",
  "status": "Draft"
}
```

## 2. Documentation Set Descriptor

```json
{
  "readme_present": true,
  "architecture_overview_present": true,
  "api_reference_present": true
}
```

## 3. Scaffold Validation Record

```json
{
  "subpackage_directories": [
    "tasklib/model",
    "tasklib/storage"
  ],
  "mirrored_to_local_test_workspace": true
}
```

## 4. Validation PR Record

```json
{
  "pr_type": "docs",
  "merge_gate_fired": true,
  "downstream_prs_recognize_merge": true,
  "files_mirrored_to_local_workspace": false,
  "local_import_resolution_success": false,
  "ci_dependency_ready": false
}
```

## 5. Code PR Import Resolution Record

```json
{
  "pr_type": "code",
  "merge_gate_fired": false,
  "downstream_prs_recognize_merge": true,
  "files_mirrored_to_local_workspace": true,
  "local_import_resolution_success": true,
  "ci_dependency_ready": true
}
```

## 6. Dependency Chain Record

```json
{
  "stages": ["docs", "scaffold", "model", "storage", "CLI"],
  "closed": true,
  "imports_resolve_locally_before_ci": true
}
```

## 7. Forge Platform Descriptor

```json
{
  "name": "Forge",
  "platform_role": "runtime policy enforcement and cryptographic identity platform",
  "target_domain": "enterprise AI agents"
}
```

## 8. CAL Subsystem Descriptor

```json
{
  "name": "CAL",
  "expanded_name": "Conversation Abstraction Layer",
  "enforcement_choke_point": true,
  "position_above_vtz": true,
  "position_below_application_orchestration": true,
  "requires_policy_evaluation_for_agent_actions": true,
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

## 9. CAL Enforcement Event

```json
{
  "action_type": "tool_call",
  "passes_through_cal_policy_evaluation": true,
  "cal_position": {
    "above_vtz": true,
    "below_application_orchestration": true
  }
}
```

## 10. CPF Reference Descriptor

```json
{
  "name": "CPF",
  "expanded_name": "Conversation Plane Filter"
}
```

---

## Notes on Contract Completeness

The provided TRDs do not specify:

- function or method signatures
- CLI command syntax
- Python class definitions
- storage backends or persistence schemas
- task object fields
- error codes
- transport protocol requirements
- authentication or authorization formats
- CAL component internal message schemas

Accordingly, none of those interfaces are defined here. This file should be extended only when future TRDs provide explicit contract detail.