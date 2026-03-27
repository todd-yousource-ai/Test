# Interface Contracts - Validation

## Data Structures

### Task

Represents a single unit of work.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `id` | `string` | yes | Unique identifier. Generated automatically on creation. |
| `title` | `string` | yes | Must be non-empty. |
| `status` | `TaskStatus` | yes | Allowed values: `pending`, `in_progress`, `done`. Default on creation: `pending`. Must be represented as an enumeration, not free text. |
| `created_at` | `number` | yes | Numeric timestamp. |

#### Task constraints
- `id` MUST be unique.
- `title` MUST be present and MUST be non-empty.
- `status` MUST be one of `pending`, `in_progress`, `done`.
- `created_at` MUST be a numeric timestamp.

---

### CTX-ID Token

Per-session, per-agent signed token binding identity, VTZ, policy, and permissions.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `agent_id` | `string` | yes | Immutable once issued. |
| `session_id` | `string` | yes | Immutable once issued. |
| `vtz_scope` | `string` | yes | Identifies the bound VTZ scope. Immutable once issued. |
| `policy_revision` | `string` | yes | Immutable once issued. |
| `issued_at` | `number` | yes | Timestamp. Immutable once issued. |
| `sig` | `string` | yes | Signature. Must validate against TrustLock public key. Immutable once issued. |

#### CTX-ID constraints
- Token is IMMUTABLE once issued.
- Rotation creates a new token.
- Old token is invalidated immediately on rotation.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Expired CTX-ID MUST be rejected.
- Validation MUST occur against TrustLock public key.
- Software-only validation is rejected.

---

### TrustFlowEvent

Event emitted for every action outcome.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `event_id` | `string` | yes | Globally unique. CSPRNG-generated. Must not be sequential. |
| `session_id` | `string` | yes | Session identifier. |
| `ctx_id` | `string` | yes | CTX-ID token identifier or serialized token reference. |
| `ts` | `number` | yes | UTC Unix timestamp with millisecond precision. |
| `event_type` | `string` | yes | Event type discriminator. |
| `payload_hash` | `string` | yes | SHA-256 of the serialized action payload. |

#### TrustFlowEvent constraints
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Failed emission is a WARN-level audit event.
- Failed emission MUST NOT be silently skipped.

---

### VTZEnforcementDecision

Decision record produced when VTZ policy is evaluated.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `verdict` | `VTZVerdict` | yes | On VTZ policy denial, MUST be `block`. |

#### VTZEnforcementDecision constraints
- MUST be produced before execution when VTZ policy is evaluated.
- VTZ policy denial MUST produce a `VTZEnforcementDecision` record with `verdict=block`.

---

### ValidationResult

Canonical validation response for the Validation subsystem.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `valid` | `boolean` | yes | `true` if validation succeeded; `false` otherwise. |
| `errors` | `ValidationError[]` | yes | Empty array when `valid=true`. Non-empty when `valid=false`. |
| `warnings` | `ValidationWarning[]` | no | Optional advisory diagnostics. |
| `subject_type` | `string` | yes | Type being validated. Recommended values in this subsystem: `Task`, `CTX-ID`, `TrustFlowEvent`, `VTZEnforcementDecision`. |

---

### ValidationError

Validation failure detail.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable error code. |
| `field` | `string` | no | Field name that failed validation. |
| `message` | `string` | yes | Human-readable validation message. |

---

### ValidationWarning

Validation warning detail.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable warning code. |
| `field` | `string` | no | Field name associated with the warning. |
| `message` | `string` | yes | Human-readable warning message. |

---

### CAL Validation Input

Represents an action entering the validation/enforcement path.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `ctx_id` | `CTX-ID Token \| string` | yes | MUST be validated FIRST at every entry point that processes an agent action. Missing CTX-ID is `UNTRUSTED`. |
| `action_payload` | `object` | yes | Serialized payload used to compute `payload_hash`. |
| `session_id` | `string` | yes | Must correspond to CTX-ID session binding. |
| `vtz_scope` | `string` | yes | Must match the VTZ bound at CTX-ID issuance. |

#### CAL Validation Input constraints
- No tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- Every action MUST be checked against VTZ policy BEFORE execution.

---

### CPF Validation Stages

Three-tier inspection and classification result structure.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `tier1_structural` | `boolean` | yes | Structural validation result: schema, bounds checking. |
| `tier2_semantic` | `boolean` | yes | Semantic classification result: intent, data sensitivity, policy match. |
| `tier3_behavioral` | `boolean` | yes | Behavioral analysis result: anomaly detection, attack pattern recognition. |
| `final_verdict` | `ValidationVerdict` | yes | All tiers run synchronously in the enforcement path; fail closed. |

#### CPF Validation Stages constraints
- Tier 1: structural validation.
- Tier 2: semantic classification.
- Tier 3: behavioral analysis.
- All tiers run synchronously in the enforcement path.
- System MUST fail closed.

## Enums and Constants

### `TaskStatus`

Allowed values, exactly:

- `pending`
- `in_progress`
- `done`

Default:
- `pending`

---

### `VTZVerdict`

Allowed values:

- `allow`
- `restrict`
- `block`

Required constraint:
- VTZ policy denial MUST produce `block`.

---

### `ValidationVerdict`

Allowed values:

- `allow`
- `restrict`
- `block`

---

### Constants and Required Literal Values

| Name | Value | Notes |
|---|---|---|
| Missing CTX-ID classification | `UNTRUSTED` | Must be used when CTX-ID is absent. |
| WARN audit level | `WARN` | Required severity for failed TrustFlow emission. |
| Hash algorithm | `SHA-256` | For `payload_hash`. |
| Time format for TrustFlow `ts` | `UTC Unix timestamp with millisecond precision` | Required exactly. |
| Event ID generation | `CSPRNG` | Must not be sequential. |

## Validation Rules

### 1. Task validation

#### Required fields
- `id`
- `title`
- `status`
- `created_at`

#### Field rules
- `id` MUST be unique.
- `id` MUST be generated automatically on creation.
- `title` MUST be a string.
- `title` MUST be non-empty.
- `status` MUST be an enumeration value.
- `status` MUST NOT be free text.
- `status` MUST be one of:
  - `pending`
  - `in_progress`
  - `done`
- If omitted during creation, `status` defaults to `pending`.
- `created_at` MUST be a number.

---

### 2. CTX-ID validation

- Every entry point that processes an agent action MUST call CTX-ID validation FIRST.
- CTX-ID validation failure MUST result in immediate rejection.
- No partial processing is permitted after CTX-ID validation failure.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- CTX-ID tokens are IMMUTABLE once issued.
- Rotation creates a new token.
- The old token is invalidated immediately.
- Expired CTX-ID MUST be rejected.
- Validation MUST use TrustLock public key.
- Software-only validation is rejected.
- Each agent session is bound to EXACTLY ONE VTZ at CTX-ID issuance.

#### CTX-ID field validation
- `agent_id`: required, string
- `session_id`: required, string
- `vtz_scope`: required, string
- `policy_revision`: required, string
- `issued_at`: required, number
- `sig`: required, string

---

### 3. VTZ validation

- Every action MUST be checked against VTZ policy BEFORE execution.
- Cross-VTZ tool calls require explicit policy authorization.
- Implicit cross-VTZ access is denied.
- VTZ boundaries are structural, not advisory.
- Enforcement cannot be bypassed by application code.
- VTZ policy changes take effect at NEXT CTX-ID issuance, not mid-session.
- VTZ policy denial MUST produce a `VTZEnforcementDecision` with `verdict=block`.

---

### 4. TrustFlow validation

- Every action outcome (`allow`, `restrict`, `block`) MUST emit a TrustFlow event.
- TrustFlow emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Every TrustFlow event MUST include:
  - `event_id`
  - `session_id`
  - `ctx_id`
  - `ts`
  - `event_type`
  - `payload_hash`
- `event_id` MUST be globally unique.
- `event_id` MUST be generated using CSPRNG.
- `event_id` MUST NOT be sequential.
- `ts` MUST be a UTC Unix timestamp with millisecond precision.
- `payload_hash` MUST be SHA-256 of the serialized action payload.
- TrustFlow emission failure MUST NOT silently continue.
- TrustFlow emission failure MUST be logged and surfaced.
- Failed emission is a `WARN`-level audit event.

---

### 5. CPF validation

- CPF is a three-tier inspection and classification engine within CAL.
- Tier 1 MUST perform structural validation:
  - schema
  - bounds checking
- Tier 2 MUST perform semantic classification:
  - intent
  - data sensitivity
  - policy match
- Tier 3 MUST perform behavioral analysis:
  - anomaly detection
  - attack pattern recognition
- All tiers run synchronously in the enforcement path.
- Validation MUST fail closed.

---

### 6. CAL enforcement ordering

Required processing order for any agent-originated action:

1. Validate `ctx_id` FIRST.
2. Reject immediately on CTX-ID validation failure.
3. Evaluate VTZ policy BEFORE execution.
4. Produce `VTZEnforcementDecision` when applicable.
5. Emit TrustFlow event for the outcome.
6. If TrustFlow emission fails, log and surface the failure; do not silently continue.

## Wire Format Examples

### Valid Task

```json
{
  "id": "task_01HZX3V1J7Y8M2Q4K9P6R5S1T",
  "title": "Write INTERFACES.md",
  "status": "pending",
  "created_at": 1717171717.123
}
```

### Invalid Task: empty title

```json
{
  "id": "task_01HZX3V1J7Y8M2Q4K9P6R5S1T",
  "title": "",
  "status": "pending",
  "created_at": 1717171717.123
}
```

Reason:
- `title` must be non-empty.

---

### Invalid Task: unsupported status

```json
{
  "id": "task_01HZX3V1J7Y8M2Q4K9P6R5S1T",
  "title": "Write tests",
  "status": "queued",
  "created_at": 1717171717.123
}
```

Reason:
- `status` must be one of `pending`, `in_progress`, `done`.

---

### Valid CTX-ID Token

```json
{
  "agent_id": "agent-123",
  "session_id": "session-456",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "2025-03-01",
  "issued_at": 1717171717123,
  "sig": "base64-signature"
}
```

### Invalid CTX-ID Token: missing signature

```json
{
  "agent_id": "agent-123",
  "session_id": "session-456",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "2025-03-01",
  "issued_at": 1717171717123
}
```

Reason:
- `sig` is required.

---

### Valid TrustFlowEvent

```json
{
  "event_id": "evt_csprng_7f3c2a91f4bb4e6b8c1d9a20f0d67e11",
  "session_id": "session-456",
  "ctx_id": "ctx_abc123",
  "ts": 1717171717123,
  "event_type": "block",
  "payload_hash": "3f0a377ba0a4a460ecb616f6507ce0d8cfa3e704025d4fda3ed0c5ca05468728"
}
```

### Invalid TrustFlowEvent: sequential event id and bad hash

```json
{
  "event_id": "10001",
  "session_id": "session-456",
  "ctx_id": "ctx_abc123",
  "ts": 1717171717,
  "event_type": "allow",
  "payload_hash": "not-a-sha256"
}
```

Reasons:
- `event_id` must be globally unique and CSPRNG-generated, not sequential.
- `ts` must be UTC Unix timestamp with millisecond precision.
- `payload_hash` must be SHA-256 of the serialized action payload.

---

### Valid VTZEnforcementDecision

```json
{
  "verdict": "block"
}
```

### Invalid VTZEnforcementDecision: deny without block

```json
{
  "verdict": "restrict"
}
```

Reason:
- VTZ policy denial must produce `verdict=block`.

---

### Valid ValidationResult

```json
{
  "valid": false,
  "subject_type": "Task",
  "errors": [
    {
      "code": "TASK_TITLE_EMPTY",
      "field": "title",
      "message": "title must be non-empty"
    }
  ],
  "warnings": []
}
```

## Integration Points

### CAL — Conversation Abstraction Layer

Validation subsystem integration requirements:
- No tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- CAL is the enforcement choke point for all agent-originated action.
- Validation must support CAL-first processing semantics.

#### Required integration behavior
- Accept CAL action input containing `ctx_id`, `action_payload`, `session_id`, and `vtz_scope`.
- Perform CTX-ID validation FIRST.
- Stop processing immediately on CTX-ID validation failure.
- Pass validated action to VTZ policy evaluation before execution.
- Ensure outcome emits TrustFlow event.

---

### CPF — Conversation Plane Filter

Validation subsystem MUST support CPF’s three synchronous tiers:

1. `tier1_structural`
   - schema validation
   - bounds checking

2. `tier2_semantic`
   - intent classification
   - data sensitivity classification
   - policy match evaluation

3. `tier3_behavioral`
   - anomaly detection
   - attack pattern recognition

Integration constraint:
- All three tiers execute synchronously in the enforcement path.
- Fail closed on any validation failure.

---

### CTX-ID

Validation subsystem MUST:
- Validate presence of CTX-ID.
- Validate CTX-ID fields and signature.
- Enforce immutability semantics.
- Reject expired CTX-ID.
- Treat missing CTX-ID as `UNTRUSTED`.
- Bind session processing to exactly one VTZ from CTX-ID issuance.

---

### VTZ — Virtual Trust Zone

Validation subsystem MUST:
- Validate that each agent session is bound to exactly one VTZ.
- Validate action authorization against VTZ policy before execution.
- Deny implicit cross-VTZ operations.
- Require explicit policy authorization for cross-VTZ tool calls.
- Produce `VTZEnforcementDecision` with `verdict=block` on denial.

---

### TrustFlow

Validation subsystem MUST:
- Generate or validate `TrustFlowEvent`.
- Ensure required fields are present:
  - `event_id`
  - `session_id`
  - `ctx_id`
  - `ts`
  - `event_type`
  - `payload_hash`
- Validate `event_id` uniqueness and CSPRNG origin requirements.
- Validate `payload_hash` as SHA-256 of serialized action payload.
- Require synchronous emission in the enforcement path.
- Log and surface emission failures as `WARN`-level audit events.