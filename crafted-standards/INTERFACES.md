# INTERFACES.md

## Interface Contracts

This document defines the wire formats, API contracts, and validation rules derived solely from the provided TRD material.

### Source TRDs
- `TRD-TASKLIB` v1.0
- `forge_architecture_context`

---

## Scope and Derivation Notes

The provided TRDs contain a complete scope statement for a simple Python task management library and partial architectural context for Forge. The task library TRD explicitly defines pipeline validation goals and identifies a dependency chain:

- docs → scaffold → model → storage → CLI

The TRD also states that the documentation set includes:

- README
- ARCHITECTURE overview
- API reference

The scaffold is described as:

- Python package scaffold
- multiple package directories
- mirrored to a local test workspace

No concrete Python class definitions, CLI argument syntax, persistence schema, transport protocol, serialization grammar, or task field schema are included in the provided TRDs. Therefore, this document only specifies interface contracts that are directly supported by the source material and marks unsupported details as unspecified.

---

## Per-Subsystem Data Structures

The following subsystems are derivable from the TRDs.

### 1. Documentation Subsystem

#### 1.1 Documentation Set
Represents the required documentation artifacts named in `TRD-TASKLIB`.

| Field | Type | Constraints |
|---|---|---|
| `readme` | document reference | Required |
| `architecture_overview` | document reference | Required |
| `api_reference` | document reference | Required |

#### 1.2 Documentation PR
Represents the documentation merge event described in the validation goals.

| Field | Type | Constraints |
|---|---|---|
| `type` | string | Must identify a documentation PR |
| `merge_gate_fired` | boolean | Required for validation goal |
| `downstream_prs_recognize_merge` | boolean | Required for validation goal |

Notes:
- Exact PR metadata fields are not defined in the TRDs.
- Exact event payload shape is unspecified.

---

### 2. Scaffold Subsystem

#### 2.1 Python Package Scaffold
Represents the scaffold artifact described in `TRD-TASKLIB`.

| Field | Type | Constraints |
|---|---|---|
| `package_type` | string | Must represent a Python package scaffold |
| `subpackage_directories` | array | Required; must contain multiple package directories |
| `mirrored_to_local_test_workspace` | boolean | Required for validation |

#### 2.2 Subpackage Directory
Represents one package directory within the scaffold.

| Field | Type | Constraints |
|---|---|---|
| `path` | string | Required |
| `files` | array | Optional; file contents and names unspecified in TRD |

Notes:
- Package names are not provided.
- Directory naming conventions are unspecified.

---

### 3. Model Subsystem

The dependency chain explicitly includes `model`, but the TRD excerpt provides no model schema.

#### 3.1 Model Component
| Field | Type | Constraints |
|---|---|---|
| `subsystem` | string | Must equal `model` in dependency-chain context |

Notes:
- No task entity fields are specified.
- No object attributes, identifiers, timestamps, or statuses are defined in the provided TRDs.

---

### 4. Storage Subsystem

The dependency chain explicitly includes `storage`, but the TRD excerpt provides no storage schema.

#### 4.1 Storage Component
| Field | Type | Constraints |
|---|---|---|
| `subsystem` | string | Must equal `storage` in dependency-chain context |

Notes:
- Backend type is unspecified.
- Storage format is unspecified.
- CRUD contract is unspecified.

---

### 5. CLI Subsystem

The dependency chain explicitly includes `CLI`, but the TRD excerpt provides no command grammar.

#### 5.1 CLI Component
| Field | Type | Constraints |
|---|---|---|
| `subsystem` | string | Must equal `cli` in dependency-chain context |

Notes:
- Commands, arguments, flags, exit codes, and stdout/stderr formats are unspecified.

---

### 6. Dependency Chain Contract

This is the most explicit inter-subsystem structure in `TRD-TASKLIB`.

#### 6.1 Dependency Chain
| Field | Type | Constraints |
|---|---|---|
| `stages` | array of strings | Required; ordered as `docs`, `scaffold`, `model`, `storage`, `cli` |
| `fully_closed` | boolean | Required for validation outcome |

#### 6.2 Import Resolution Check
Derived from: “Code PRs that import from previously-merged PRs resolve those imports locally before CI.”

| Field | Type | Constraints |
|---|---|---|
| `imports_from_previously_merged_prs` | boolean | Indicates whether such imports exist |
| `resolved_locally_before_ci` | boolean | Required when such imports exist |

---

### 7. Forge Architecture Context Subsystem References

The provided architecture context defines platform-level named subsystems and relationships, but no payload schemas.

#### 7.1 Platform Overview
| Field | Type | Constraints |
|---|---|---|
| `platform_name` | string | `Forge` |
| `runtime_policy_enforcement` | boolean | True by description |
| `cryptographic_identity` | boolean | True by description |
| `operator_defined_policy` | boolean | True by description |

#### 7.2 CAL — Conversation Abstraction Layer
| Field | Type | Constraints |
|---|---|---|
| `name` | string | `CAL` |
| `full_name` | string | `Conversation Abstraction Layer` |
| `enforcement_choke_point` | boolean | True by description |
| `position_above` | string | `VTZ enforcement plane` |
| `position_below` | string | `application orchestration` |
| `requires_policy_evaluation_for_all_actions` | boolean | True by description |

#### 7.3 CAL Key Components
| Field | Type | Constraints |
|---|---|---|
| `cpf` | string | `CPF` |
| `air` | string | `AIR` |
| `ctx_id` | string | `CTX-ID` |
| `pee` | string | `PEE` |
| `trustflow_sis` | string | `TrustFlow/SIS` |
| `cal_verifier_cluster` | string | `CAL Verifier Cluster` |

#### 7.4 CPF — Conversation Plane Filter
| Field | Type | Constraints |
|---|---|---|
| `name` | string | `CPF` |
| `full_name` | string | `Conversation Plane Filter` |

Notes:
- No CPF fields, methods, protocol messages, or evaluation result schema are present in the supplied text.

---

## Cross-Subsystem Protocols

Only the following protocol-level behaviors are directly supported by the TRDs.

### 1. Documentation Merge Recognition Protocol

Derived from:
- “A documentation PR fires the merge gate”
- “downstream PRs recognize the merge”

#### Contract
1. A documentation PR is merged.
2. The merge gate fires.
3. Downstream PRs detect or recognize that merge state.

#### Required Observable Outcomes
- Merge gate activation
- Downstream merge recognition

#### Undefined
- Event transport
- Event schema
- Polling vs push behavior
- PR identity format

---

### 2. Scaffold Mirroring Protocol

Derived from:
- “A scaffold PR with multiple package directories mirrors files to the local test workspace”

#### Contract
1. A scaffold PR contains multiple package directories.
2. Files are mirrored into a local test workspace.

#### Required Observable Outcomes
- Presence of multiple package directories
- Successful mirroring to local workspace

#### Undefined
- Mirroring trigger
- File copy semantics
- Conflict resolution
- Workspace path format

---

### 3. Local Import Resolution Protocol

Derived from:
- “Code PRs that import from previously-merged PRs resolve those imports locally before CI”

#### Contract
1. A code PR imports symbols or modules from previously merged PRs.
2. Those imports resolve in the local environment.
3. Resolution occurs before CI execution.

#### Required Observable Outcomes
- Prior merged dependency exists
- Local import resolution succeeds pre-CI

#### Undefined
- Import path syntax
- Resolver implementation
- Failure mode reporting format

---

### 4. Dependency Chain Closure Protocol

Derived from:
- “The full dependency chain closes: docs → scaffold → model → storage → CLI”

#### Contract
Execution or merge order must support the following directed dependency sequence:

1. `docs`
2. `scaffold`
3. `model`
4. `storage`
5. `cli`

#### Required Observable Outcomes
- Each stage depends on prior merged work as needed
- Final closure of full chain

#### Undefined
- Whether closure is measured by merge, build, test, import, or release status
- Retry semantics
- Partial-success behavior

---

### 5. CAL Policy Evaluation Protocol

Derived only from the Forge architecture context.

#### Contract
No agent-originated:
- tool call
- data read
- API invocation
- agent handoff

may execute without passing through CAL policy evaluation.

#### Required Observable Outcomes
- CAL is the enforcement choke point
- All listed action classes require policy evaluation before execution

#### Undefined
- Request schema
- Response schema
- Policy decision enum
- Authentication and signature format
- Error codes

---

## Enums and Constants

Only constants and named values explicitly present in the TRDs are included.

### 1. Tasklib Dependency Stage Names
```text
docs
scaffold
model
storage
cli
```

### 2. Documentation Artifact Names
```text
README
ARCHITECTURE overview
API reference
```

### 3. Forge Subsystem Names
```text
Forge
CAL
CPF
AIR
CTX-ID
PEE
TrustFlow/SIS
CAL Verifier Cluster
VTZ enforcement plane
application orchestration
```

### 4. CAL-Protected Action Classes
```text
tool call
data read
API invocation
agent handoff
```

### 5. TRD Metadata Constants

#### TRD-TASKLIB
| Name | Value |
|---|---|
| `version` | `1.0` |
| `status` | `Draft` |
| `author` | `Todd Gould / YouSource.ai` |
| `date` | `2026-03-26` |

---

## Validation Rules

These validation rules are limited to assertions explicitly supported by the TRDs.

### 1. Documentation Validation
- A valid documentation set must include:
  - README
  - ARCHITECTURE overview
  - API reference

### 2. Documentation PR Validation
- A valid documentation PR flow must demonstrate:
  - merge gate fired
  - downstream PRs recognized the merge

### 3. Scaffold Validation
- A valid scaffold PR must include multiple package directories.
- A valid scaffold flow must mirror files to the local test workspace.

### 4. Local Import Validation
- If a code PR imports from previously merged PRs, those imports must resolve locally before CI.

### 5. Dependency Chain Validation
- The full dependency chain must be:
  - docs → scaffold → model → storage → CLI
- Validation succeeds only when the chain is closed end-to-end.

### 6. CAL Enforcement Validation
- No tool call, data read, API invocation, or agent handoff may execute without CAL policy evaluation.

### 7. Positioning Validation for CAL
- CAL must sit:
  - above the VTZ enforcement plane
  - below application orchestration

---

## Wire Format Examples

Because the provided TRDs do not define a canonical wire format, the following examples are illustrative normalized representations using JSON. They are not normative transport specifications beyond the field names directly derivable from the TRDs.

### 1. Documentation Set Example
```json
{
  "readme": "README",
  "architecture_overview": "ARCHITECTURE overview",
  "api_reference": "API reference"
}
```

### 2. Documentation PR Validation Example
```json
{
  "type": "documentation_pr",
  "merge_gate_fired": true,
  "downstream_prs_recognize_merge": true
}
```

### 3. Scaffold Example
```json
{
  "package_type": "python_package_scaffold",
  "subpackage_directories": [
    {
      "path": "package_a",
      "files": []
    },
    {
      "path": "package_b",
      "files": []
    }
  ],
  "mirrored_to_local_test_workspace": true
}
```

### 4. Dependency Chain Example
```json
{
  "stages": ["docs", "scaffold", "model", "storage", "cli"],
  "fully_closed": true
}
```

### 5. Local Import Resolution Example
```json
{
  "imports_from_previously_merged_prs": true,
  "resolved_locally_before_ci": true
}
```

### 6. Forge Platform Context Example
```json
{
  "platform_name": "Forge",
  "runtime_policy_enforcement": true,
  "cryptographic_identity": true,
  "operator_defined_policy": true
}
```

### 7. CAL Context Example
```json
{
  "name": "CAL",
  "full_name": "Conversation Abstraction Layer",
  "enforcement_choke_point": true,
  "position_above": "VTZ enforcement plane",
  "position_below": "application orchestration",
  "requires_policy_evaluation_for_all_actions": true,
  "key_components": {
    "cpf": "CPF",
    "air": "AIR",
    "ctx_id": "CTX-ID",
    "pee": "PEE",
    "trustflow_sis": "TrustFlow/SIS",
    "cal_verifier_cluster": "CAL Verifier Cluster"
  }
}
```

### 8. CAL-Protected Action Policy Requirement Example
```json
{
  "action_classes": [
    "tool call",
    "data read",
    "API invocation",
    "agent handoff"
  ],
  "policy_evaluation_required": true
}
```

---

## Unsupported or Unspecified Interfaces

The following interface details are not defined in the provided TRDs and therefore are intentionally unspecified in this document:

- Task object schema
- Task identifiers
- Task status enum
- Create/read/update/delete request and response bodies
- Storage backend API
- CLI commands and flags
- Exit codes
- Error response schema
- Transport protocol
- Authentication format
- Serialization format beyond illustrative examples
- Event naming and webhook payloads
- Import resolver implementation details
- CAL request/decision/result payload schemas
- CPF behavior beyond name expansion

Any addition of these items would require source TRD support not present in the supplied material.