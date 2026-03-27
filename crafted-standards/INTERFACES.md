# Interface Contracts - Validation

## Data Structures

### Task

Represents a single unit of work.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `id` | `string` | yes | Unique identifier. Generated automatically on creation. |
| `title` | `string` | yes | Must be non-empty. |
| `status` | `TaskStatus` | yes | Allowed values: `pending`, `in_progress`, `done`. Default at creation: `pending`. Must be represented as an enumeration, not free text. |
| `created_at` | `number` | yes | Numeric timestamp. |

#### Task constraints
- `id` MUST be unique.
- `id` MUST be generated automatically on creation.
- `title` MUST be present.
- `title` MUST be non-empty.
- `status` MUST be one of `pending`, `in_progress`, `done`.
- `status` default value on creation MUST be `pending`.
- `created_at` MUST be a numeric timestamp.

---

### CTX-ID Token

Per-session, per-agent signed token binding identity, VTZ, policy, and permissions.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `agent_id` | `string` | yes | Part of immutable CTX-ID token. |
| `session_id` | `string` | yes | Part of immutable CTX-ID token. |
| `vtz_scope` | `string` | yes | Binds the token to exactly one VTZ scope. |
| `policy_revision` | `string` \| `number` | yes | Included exactly as named in source. Immutable once issued. |
| `issued_at` | `number` | yes | Timestamp of issuance. |
| `sig` | `string` | yes | Signature. Must validate against TrustLock public key. |

#### CTX-ID constraints
- CTX-ID tokens are **IMMUTABLE once issued**.
- Rotation creates a new CTX-ID.
- Old token is invalidated immediately on rotation.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Expired CTX-ID MUST be rejected.
- CTX-ID MUST be validated against TrustLock public key.
- Software-only validation is rejected.
- Each agent session is bound to exactly one VTZ at CTX-ID issuance.

---

### TrustFlowEvent

Audit/enforcement event emitted for every action outcome.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `event_id` | `string` | yes | Must be globally unique. CSPRNG, not sequential. |
| `session_id` | `string` | yes | Session identifier associated with the event. |
| `ctx_id` | `string` | yes | CTX-ID token reference or serialized identifier. |
| `ts` | `number` | yes | UTC Unix timestamp with millisecond precision. |
| `event_type` | `string` | yes | Event type discriminator. |
| `payload_hash` | `string` | yes | SHA-256 of the serialized action payload. |

#### TrustFlowEvent constraints
- Every TrustFlow event MUST include all listed fields.
- `event_id` MUST be globally unique.
- `event_id` MUST be CSPRNG-generated.
- `event_id` MUST NOT be sequential.
- `ts` MUST be UTC Unix timestamp with millisecond precision.
- `payload_hash` MUST be SHA-256 of the serialized action payload.
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Failed emission is a `WARN`-level audit event.
- Failed emission MUST NOT be a silent skip.

---

### VTZEnforcementDecision

Decision record produced when VTZ policy denies an action.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `verdict` | `string` | yes | For policy denial, value MUST be `block`. |

#### VTZEnforcementDecision constraints
- VTZ policy denial MUST produce a `VTZEnforcementDecision` record.
- On denial, `verdict` MUST equal `block`.

---

### ValidationResult

Canonical validation outcome for the Validation subsystem.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `valid` | `boolean` | yes | `true` if validation passed; otherwise `false`. |
| `errors` | `array<ValidationError>` | yes | Empty array when `valid=true`. Non-empty when `valid=false`. |
| `warnings` | `array<ValidationWarning>` | yes | May be empty. Includes surfaced TrustFlow emission failures as warnings. |

---

### ValidationError

Validation failure record.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable error code. |
| `message` | `string` | yes | Human-readable description of failure. |
| `field` | `string` | no | Field name associated with the error when applicable. |

---

### ValidationWarning

Validation warning record.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable warning code. |
| `message` | `string` | yes | Human-readable description of warning. |
| `field` | `string` | no | Field name associated with the warning when applicable. |

---

### CPFValidationReport

Result of synchronous three-tier Conversation Plane Filter inspection.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `tier1_structural` | `CPFValidationTierResult` | yes | Structural validation: schema, bounds checking. |
| `tier2_semantic` | `CPFValidationTierResult` | yes | Semantic classification: intent, data sensitivity, policy match. |
| `tier3_behavioral` | `CPFValidationTierResult` | yes | Behavioral analysis: anomaly detection, attack pattern recognition. |
| `passed` | `boolean` | yes | `true` only if all tiers pass. Fail closed. |

---

### CPFValidationTierResult

Tier-level result within CPF validation.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `passed` | `boolean` | yes | Indicates whether the tier passed. |
| `reason` | `string` | no | Required when `passed=false` to describe failure. |

---

## Enums and Constants

### TaskStatus

Allowed values for `Task.status`:

- `pending`
- `in_progress`
- `done`

### VTZ Enforcement Verdict

Allowed/required values from contract:

- `block`

### Trust/Identity Constants

- `UNTRUSTED` — required treatment for missing CTX-ID
- `WARN` — audit severity for failed TrustFlow emission

### CPF Tiers

- `tier1_structural`
- `tier2_semantic`
- `tier3_behavioral`

---

## Validation Rules

### 1. Task validation

#### Required fields
A `Task` payload MUST include:
- `id`
- `title`
- `status`
- `created_at`

#### Field validation
- `id` MUST be a `string`.
- `id` MUST be unique.
- `id` MUST be auto-generated on creation.
- `title` MUST be a `string`.
- `title` MUST be non-empty.
- `status` MUST be a valid `TaskStatus` enum value.
- `status` MUST NOT be arbitrary free text.
- `created_at` MUST be a `number`.

#### Creation defaults
- If a new task is created without `status`, the effective default MUST be `pending`.

---

### 2. CTX-ID validation

Every entry point that processes an agent action MUST call CTX-ID validation FIRST.

#### Required fields
A CTX-ID token MUST include:
- `agent_id`
- `session_id`
- `vtz_scope`
- `policy_revision`
- `issued_at`
- `sig`

#### Validation behavior
- CTX-ID validation failure MUST result in immediate rejection.
- No partial processing is permitted after CTX-ID validation failure.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Identity MUST NEVER be inferred from context when CTX-ID is missing.
- CTX-ID MUST be validated against TrustLock public key.
- Software-only validation is rejected.
- CTX-ID tokens are immutable once issued.
- Field modification after issuance is invalid.
- Rotation MUST create a new token.
- The old token MUST be invalidated immediately.
- Expired CTX-ID MUST be rejected.
- Clock skew tolerance is deployment-defined and not specified in this contract.

---

### 3. VTZ validation

Every action MUST be checked against VTZ policy BEFORE execution.

#### Validation behavior
- Every agent session MUST be bound to EXACTLY ONE VTZ at CTX-ID issuance.
- Cross-VTZ tool calls require explicit policy authorization.
- Implicit cross-VTZ access is denied.
- VTZ boundaries are structural, not advisory.
- Enforcement cannot be bypassed by application code.
- VTZ policy denial MUST produce a `VTZEnforcementDecision` record with `verdict=block`.
- VTZ policy changes take effect at NEXT CTX-ID issuance, not mid-session.

---

### 4. TrustFlow event validation

Every action outcome (`allow`, `restrict`, `block`) MUST emit a TrustFlow event.

#### Required fields
A `TrustFlowEvent` MUST include:
- `event_id`
- `session_id`
- `ctx_id`
- `ts`
- `event_type`
- `payload_hash`

#### Field validation
- `event_id` MUST be globally unique.
- `event_id` MUST be CSPRNG-generated.
- `event_id` MUST NOT be sequential.
- `ts` MUST be UTC Unix timestamp with millisecond precision.
- `payload_hash` MUST be SHA-256 of the serialized action payload.

#### Emission behavior
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- TrustFlow emission failure MUST NOT silently continue.
- Failure MUST be logged.
- Failure MUST be surfaced.
- Failed emission is a `WARN`-level audit event.

---

### 5. CPF validation

CPF is a three-tier inspection and classification engine within CAL.

#### Tier requirements
- Tier 1: structural validation (`schema`, `bounds checking`)
- Tier 2: semantic classification (`intent`, `data sensitivity`, `policy match`)
- Tier 3: behavioral analysis (`anomaly detection`, `attack pattern recognition`)

#### Execution behavior
- All tiers run synchronously in the enforcement path.
- CPF MUST fail closed.
- A failure in any tier causes overall validation failure.

---

### 6. CAL enforcement ordering

Validation subsystem implementations MUST preserve this enforcement sequence:

1. CTX-ID validation FIRST
2. VTZ policy check BEFORE execution
3. CPF synchronous tiered validation in enforcement path
4. Action execution only if validation passes
5. TrustFlow event emission for every action outcome

---

## Wire Format Examples

### Valid Task payload

```json
{
  "id": "task_01JABCDEF123456789",
  "title": "Write INTERFACES.md",
  "status": "pending",
  "created_at": 1712345678.123
}
```

### Invalid Task payload: empty title

```json
{
  "id": "task_01JABCDEF123456789",
  "title": "",
  "status": "pending",
  "created_at": 1712345678.123
}
```

Reason:
- `title` is present but empty; must be non-empty.

---

### Invalid Task payload: status not in enum

```json
{
  "id": "task_01JABCDEF123456789",
  "title": "Write tests",
  "status": "queued",
  "created_at": 1712345678.123
}
```

Reason:
- `status` must be one of `pending`, `in_progress`, `done`.

---

### Valid CTX-ID payload

```json
{
  "agent_id": "agent-123",
  "session_id": "session-456",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "2026-03-27",
  "issued_at": 1712345678123,
  "sig": "base64-signature"
}
```

### Invalid CTX-ID payload: missing signature

```json
{
  "agent_id": "agent-123",
  "session_id": "session-456",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "2026-03-27",
  "issued_at": 1712345678123
}
```

Reason:
- Missing `sig`.
- CTX-ID validation must reject immediately.

---

### Valid TrustFlowEvent payload

```json
{
  "event_id": "c2b1c8df-7a0c-4c88-b9d7-1f79d7f9c4af",
  "session_id": "session-456",
  "ctx_id": "ctx_01JABCDEF123456789",
  "ts": 1712345678123,
  "event_type": "block",
  "payload_hash": "3f0a377ba0a4a460ecb616f6507ce0d8cfa1b16d8b58b1a0a6d6b3d88c3b9f9e"
}
```

### Invalid TrustFlowEvent payload: sequential event id and non-millisecond timestamp

```json
{
  "event_id": "1001",
  "session_id": "session-456",
  "ctx_id": "ctx_01JABCDEF123456789",
  "ts": 1712345678,
  "event_type": "allow",
  "payload_hash": "not-a-sha256"
}
```

Reason:
- `event_id` must be globally unique and CSPRNG-generated, not sequential.
- `ts` must be UTC Unix timestamp with millisecond precision.
- `payload_hash` must be SHA-256 of the serialized action payload.

---

### Valid VTZEnforcementDecision payload

```json
{
  "verdict": "block"
}
```

### Invalid VTZEnforcementDecision payload

```json
{
  "verdict": "deny"
}
```

Reason:
- On VTZ policy denial, `verdict` must equal `block`.

---

### Valid CPFValidationReport payload

```json
{
  "tier1_structural": {
    "passed": true
  },
  "tier2_semantic": {
    "passed": true
  },
  "tier3_behavioral": {
    "passed": true
  },
  "passed": true
}
```

### Invalid CPFValidationReport payload: fail-open mismatch

```json
{
  "tier1_structural": {
    "passed": false,
    "reason": "schema validation failed"
  },
  "tier2_semantic": {
    "passed": true
  },
  "tier3_behavioral": {
    "passed": true
  },
  "passed": true
}
```

Reason:
- CPF must fail closed.
- If any tier fails, top-level `passed` must be `false`.

---

### Valid ValidationResult payload

```json
{
  "valid": false,
  "errors": [
    {
      "code": "INVALID_TASK_STATUS",
      "message": "status must be one of pending, in_progress, done",
      "field": "status"
    }
  ],
  "warnings": []
}
```

---

## Integration Points

### CAL — Conversation Abstraction Layer
Validation subsystem participates in CAL as the enforcement choke point for agent-originated action.

Integration requirements:
- No tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- Validation must operate above the VTZ enforcement plane and below application orchestration.
- Relevant CAL-adjacent components:
  - `CPF`
  - `AIR`
  - `CTX-ID`
  - `PEE`
  - `TrustFlow/SIS`
  - `CAL Verifier Cluster`

### CPF — Conversation Plane Filter
Validation subsystem MUST support CPF’s synchronous three-tier inspection model:
- `tier1_structural`
- `tier2_semantic`
- `tier3_behavioral`

### CTX-ID
Validation subsystem MUST:
- Validate CTX-ID first at every action-processing entry point
- Reject immediately on failure
- Treat missing CTX-ID as `UNTRUSTED`
- Enforce immutability and rotation semantics

### VTZ — Virtual Trust Zone
Validation subsystem MUST:
- Ensure each session is bound to exactly one VTZ
- Perform VTZ policy check before execution
- Produce `VTZEnforcementDecision` with `verdict=block` on denial
- Require explicit authorization for cross-VTZ tool calls

### TrustFlow/SIS
Validation subsystem MUST:
- Emit a `TrustFlowEvent` for every outcome: `allow`, `restrict`, `block`
- Emit synchronously in the enforcement path
- Log and surface emission failure as `WARN`
- Never silently continue on emission failure