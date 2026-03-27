# Interface Contracts - Validation

## Data Structures

### Task

Represents a single unit of work.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `id` | `string` | yes | Unique identifier. Generated automatically on creation. |
| `title` | `string` | yes | Must be non-empty. |
| `status` | `TaskStatus` | yes | Allowed values are `pending`, `in_progress`, `done`. Default is `pending` at creation. Must be represented as an enumeration, not free text. |
| `created_at` | `number` | yes | Numeric timestamp. |

#### Task creation constraints
- `id` MUST be generated automatically on creation.
- `title` MUST be provided and MUST be non-empty.
- `status` defaults to `pending` if omitted at creation.
- `created_at` MUST be recorded at creation as a numeric timestamp.

---

### CTX-ID Token

Per-session, per-agent signed token binding identity, VTZ, policy, and permissions.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `agent_id` | `string` | yes | Immutable once issued. |
| `session_id` | `string` | yes | Immutable once issued. |
| `vtz_scope` | `string` | yes | Session is bound to exactly one VTZ at issuance. Immutable once issued. |
| `policy_revision` | `string` | yes | Immutable once issued. |
| `issued_at` | `number` | yes | Timestamp. Immutable once issued. |
| `sig` | `string` | yes | Signature. Must validate against TrustLock public key. Immutable once issued. |

#### CTX-ID constraints
- Tokens are immutable once issued.
- Rotation creates a new token.
- Old token is invalidated immediately on rotation.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Expired CTX-ID MUST be rejected.
- Validation MUST occur against TrustLock public key.

---

### TrustFlowEvent

Required event emitted for every action outcome.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `event_id` | `string` | yes | Globally unique. CSPRNG-generated, not sequential. |
| `session_id` | `string` | yes | Must correspond to the current session. |
| `ctx_id` | `string` | yes | CTX-ID associated with the action. |
| `ts` | `number` | yes | UTC Unix timestamp with millisecond precision. |
| `event_type` | `string` | yes | Event type discriminator. |
| `payload_hash` | `string` | yes | SHA-256 of the serialized action payload. |

#### TrustFlow emission constraints
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Every action outcome (`allow`, `restrict`, `block`) MUST emit a TrustFlow event.
- Failed emission MUST be surfaced.
- Failed emission is a WARN-level audit event.
- Failed emission MUST NOT be a silent skip.

---

### VTZEnforcementDecision

Produced when VTZ policy is evaluated.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `verdict` | `VTZVerdict` | yes | On VTZ policy denial, MUST be `block`. |
| `session_id` | `string` | yes | Session under evaluation. |
| `ctx_id` | `string` | yes | CTX-ID used for evaluation. |
| `vtz_scope` | `string` | yes | VTZ bound to the session. |
| `policy_revision` | `string` | yes | Policy revision used for evaluation. |
| `reason` | `string` | no | Human-readable denial or restriction reason. |

#### VTZ enforcement constraints
- Every agent session is bound to exactly one VTZ at CTX-ID issuance.
- Every action MUST be checked against VTZ policy before execution.
- Cross-VTZ tool calls require explicit policy authorization.
- Implicit cross-VTZ access is denied.
- VTZ boundaries are structural and cannot be bypassed by application code.
- VTZ policy changes take effect at next CTX-ID issuance, not mid-session.

---

### ValidationResult

Canonical validation outcome for the Validation subsystem.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `valid` | `boolean` | yes | `true` if validation succeeds, else `false`. |
| `errors` | `ValidationError[]` | yes | Empty array when `valid=true`. Non-empty when `valid=false`. |
| `warnings` | `ValidationWarning[]` | no | Optional advisory messages. |
| `subject_type` | `string` | yes | Type being validated, e.g. `Task`, `CTX-ID`, `TrustFlowEvent`, `VTZEnforcementDecision`. |

---

### ValidationError

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable error code. |
| `field` | `string` | no | Field name that failed validation. |
| `message` | `string` | yes | Human-readable error message. |

---

### ValidationWarning

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable warning code. |
| `field` | `string` | no | Related field name. |
| `message` | `string` | yes | Human-readable warning message. |

---

### CPFValidationEnvelope

Validation envelope aligned to CPF Tier 1 structural validation.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `ctx_id` | `CTX-ID Token` | yes | MUST be validated first for any entry point that processes an agent action. |
| `payload_type` | `string` | yes | Identifies the payload schema under validation. |
| `payload` | `object` | yes | Serialized action payload subject to structural validation. |
| `session_id` | `string` | yes | Must match CTX-ID session binding. |
| `ts` | `number` | yes | Request timestamp. |

#### CPF constraints
- Tier 1 performs structural validation including schema and bounds checking.
- Tier 2 performs semantic classification.
- Tier 3 performs behavioral analysis.
- All tiers run synchronously in the enforcement path.
- Validation fails closed.

## Enums and Constants

### `TaskStatus`
Allowed values:
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

Constraint:
- VTZ policy denial MUST produce `verdict=block`.

---

### Trust and identity constants

| Name | Type | Value / Constraint |
|---|---|---|
| `CTX_ID_UNTRUSTED` | `string` | `UNTRUSTED` |
| `HASH_ALGORITHM` | `string` | `SHA-256` |
| `TIMESTAMP_FORMAT_TRUSTFLOW` | `string` | UTC Unix timestamp with millisecond precision |
| `TRUSTFLOW_EVENT_ID_SOURCE` | `string` | CSPRNG |
| `TRUSTFLOW_EVENT_ID_SEQUENCE_ALLOWED` | `boolean` | `false` |

## Validation Rules

### 1. Entry-point validation order
For every entry point that processes an agent action:
1. CTX-ID validation MUST occur first.
2. If CTX-ID validation fails, processing MUST be rejected immediately.
3. No partial processing is permitted after CTX-ID validation failure.
4. VTZ policy evaluation MUST occur before execution.
5. If VTZ policy denies the action, a `VTZEnforcementDecision` MUST be produced with `verdict=block`.
6. Every action outcome MUST emit a `TrustFlowEvent`.

### 2. Task validation rules
- `id` MUST be present for persisted or materialized task objects.
- `id` MUST be unique.
- `id` MUST be generated automatically on creation.
- `title` MUST be present.
- `title` MUST be a string.
- `title` MUST be non-empty.
- `status` MUST be one of `pending`, `in_progress`, `done`.
- `status` MUST be represented as an enumeration, not free text.
- If omitted during creation, `status` defaults to `pending`.
- `created_at` MUST be present.
- `created_at` MUST be numeric.

### 3. CTX-ID validation rules
- CTX-ID MUST be present for any agent-originated action.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- CTX-ID MUST validate against TrustLock public key.
- Software-only validation is rejected.
- CTX-ID fields are immutable after issuance.
- Rotated CTX-ID creates a new token.
- Old CTX-ID is invalid immediately after rotation.
- Expired CTX-ID MUST be rejected.
- Session is bound to exactly one VTZ at CTX-ID issuance.
- VTZ policy changes do not alter existing session behavior mid-session.

### 4. TrustFlow validation rules
- `event_id` MUST be present.
- `event_id` MUST be globally unique.
- `event_id` MUST be CSPRNG-generated.
- Sequential `event_id` values are not permitted.
- `session_id` MUST be present.
- `ctx_id` MUST be present.
- `ts` MUST be present.
- `ts` MUST be a UTC Unix timestamp with millisecond precision.
- `event_type` MUST be present.
- `payload_hash` MUST be present.
- `payload_hash` MUST be the SHA-256 of the serialized action payload.
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Emission failure MUST be logged and surfaced.
- Emission failure MUST be WARN-level audit behavior, not silent continuation.

### 5. VTZ validation rules
- Every action MUST be checked against VTZ policy before execution.
- Every session MUST be bound to exactly one VTZ.
- Cross-VTZ tool calls require explicit policy authorization.
- Implicit cross-VTZ authorization is denied.
- VTZ enforcement cannot be bypassed by application code.
- VTZ denial MUST produce `VTZEnforcementDecision.verdict = block`.

### 6. CPF validation rules
- Tier 1 MUST perform structural validation.
- Tier 1 includes schema validation and bounds checking.
- Tier 2 MUST perform semantic classification.
- Tier 3 MUST perform behavioral analysis.
- All three tiers MUST run synchronously in the enforcement path.
- Validation MUST fail closed.

## Wire Format Examples

### Valid payload: Task

```json
{
  "id": "task_001",
  "title": "Write INTERFACES.md",
  "status": "pending",
  "created_at": 1710000000
}
```

### Invalid payload: Task with empty title

```json
{
  "id": "task_002",
  "title": "",
  "status": "pending",
  "created_at": 1710000000
}
```

Reason:
- `title` is required and must be non-empty.

---

### Invalid payload: Task with invalid status

```json
{
  "id": "task_003",
  "title": "Implement validator",
  "status": "blocked",
  "created_at": 1710000000
}
```

Reason:
- `status` must be one of `pending`, `in_progress`, `done`.

---

### Valid payload: CTX-ID Token

```json
{
  "agent_id": "agent-7",
  "session_id": "session-42",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "2026-03-27.1",
  "issued_at": 1743033600,
  "sig": "base64-signature-material"
}
```

### Invalid payload: CTX-ID Token missing signature

```json
{
  "agent_id": "agent-7",
  "session_id": "session-42",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "2026-03-27.1",
  "issued_at": 1743033600
}
```

Reason:
- `sig` is required.
- CTX-ID must validate against TrustLock public key.

---

### Valid payload: TrustFlowEvent

```json
{
  "event_id": "6f1d7d7e-8e9f-4b52-a8c6-d3f0e1f6a123",
  "session_id": "session-42",
  "ctx_id": "ctx-abc123",
  "ts": 1743033600123,
  "event_type": "block",
  "payload_hash": "3f0a377ba0a4a460ecb616f6507ce0d8cfa1b9c7b1d8eb10e442b7b6f5e4a6ab"
}
```

### Invalid payload: TrustFlowEvent with sequential event id semantics

```json
{
  "event_id": "1001",
  "session_id": "session-42",
  "ctx_id": "ctx-abc123",
  "ts": 1743033600123,
  "event_type": "allow",
  "payload_hash": "3f0a377ba0a4a460ecb616f6507ce0d8cfa1b9c7b1d8eb10e442b7b6f5e4a6ab"
}
```

Reason:
- `event_id` must be globally unique and CSPRNG-generated, not sequential.

---

### Valid payload: VTZEnforcementDecision

```json
{
  "verdict": "block",
  "session_id": "session-42",
  "ctx_id": "ctx-abc123",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "2026-03-27.1",
  "reason": "Cross-VTZ tool call denied"
}
```

### Invalid payload: VTZ denial recorded as allow

```json
{
  "verdict": "allow",
  "session_id": "session-42",
  "ctx_id": "ctx-abc123",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "2026-03-27.1",
  "reason": "Policy denied action"
}
```

Reason:
- VTZ policy denial must produce `verdict=block`.

---

### Valid payload: CPFValidationEnvelope

```json
{
  "ctx_id": {
    "agent_id": "agent-7",
    "session_id": "session-42",
    "vtz_scope": "vtz-alpha",
    "policy_revision": "2026-03-27.1",
    "issued_at": 1743033600,
    "sig": "base64-signature-material"
  },
  "payload_type": "Task",
  "payload": {
    "id": "task_004",
    "title": "Run structural validation",
    "status": "in_progress",
    "created_at": 1743033600
  },
  "session_id": "session-42",
  "ts": 1743033600123
}
```

### Invalid payload: CPFValidationEnvelope with session mismatch

```json
{
  "ctx_id": {
    "agent_id": "agent-7",
    "session_id": "session-42",
    "vtz_scope": "vtz-alpha",
    "policy_revision": "2026-03-27.1",
    "issued_at": 1743033600,
    "sig": "base64-signature-material"
  },
  "payload_type": "Task",
  "payload": {
    "id": "task_004",
    "title": "Run structural validation",
    "status": "in_progress",
    "created_at": 1743033600
  },
  "session_id": "session-99",
  "ts": 1743033600123
}
```

Reason:
- Envelope `session_id` must match `ctx_id.session_id`.

## Integration Points

### CAL — Conversation Abstraction Layer
Validation integrates with CAL as the enforcement choke point for all agent-originated action.
- No tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- Validation must execute in the CAL enforcement path.

### CPF — Conversation Plane Filter
Validation maps directly to CPF tiers:
- Tier 1: structural validation, including schema and bounds checking.
- Tier 2: semantic classification.
- Tier 3: behavioral analysis.
- All tiers run synchronously.
- Fail closed behavior is required.

### CTX-ID
Validation must:
- validate CTX-ID first,
- reject missing or expired tokens,
- enforce immutability,
- require TrustLock public key verification,
- treat missing CTX-ID as `UNTRUSTED`.

### VTZ — Virtual Trust Zone
Validation must:
- enforce exactly one VTZ per session,
- validate policy before execution,
- deny implicit cross-VTZ actions,
- produce `VTZEnforcementDecision` records for denials.

### TrustFlow / SIS
Validation must ensure:
- every action outcome emits a `TrustFlowEvent`,
- the event includes `event_id`, `session_id`, `ctx_id`, `ts`, `event_type`, `payload_hash`,
- synchronous emission in enforcement path,
- surfaced WARN-level behavior on emission failure.

### Task model validation
Validation must support the tasklib dependency chain by enforcing:
- task identity generation,
- title non-empty requirement,
- enumerated status values,
- numeric creation timestamp.