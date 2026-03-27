# Interface Contracts - Validation

## Data Structures

### Task

Represents a single unit of work.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `id` | `string` | yes | Unique identifier. Generated automatically on creation. |
| `title` | `string` | yes | Must be non-empty. |
| `status` | `TaskStatus` | yes | Allowed values are `pending`, `in_progress`, `done`. Default is `pending` at creation. Must be represented as an enumeration, not a free-form string domain. |
| `created_at` | `number` | yes | Numeric timestamp. |

#### Task creation constraints
- `id` MUST be generated automatically on creation.
- `title` MUST be present and MUST be non-empty.
- `status` defaults to `pending` if omitted at creation.
- `created_at` MUST be recorded at creation time as a numeric timestamp.

---

### CTX-ID

Per-session, per-agent signed token binding identity, VTZ, policy, and permissions.

Fields are defined exactly as follows:

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `agent_id` | `string` | yes | Immutable once issued. |
| `session_id` | `string` | yes | Immutable once issued. |
| `vtz_scope` | `string` | yes | Binds the session to exactly one VTZ at issuance. Immutable once issued. |
| `policy_revision` | `string` \| `number` | yes | Immutable once issued. Exact source type not further constrained in the provided standards; value is part of the signed token. |
| `issued_at` | `number` | yes | Timestamp. Immutable once issued. |
| `sig` | `string` | yes | Signature. Must validate against TrustLock public key. Immutable once issued. |

#### CTX-ID constraints
- CTX-ID tokens are **IMMUTABLE once issued**.
- Rotation creates a new token; the old one is invalidated immediately.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Expired CTX-ID MUST be rejected.
- CTX-ID MUST be validated against TrustLock public key.
- Every entry point that processes an agent action MUST call CTX-ID validation first.

---

### TrustFlowEvent

Required event emitted for every action outcome.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `event_id` | `string` | yes | Globally unique. CSPRNG-generated, not sequential. |
| `session_id` | `string` | yes | Must identify the session associated with the action. |
| `ctx_id` | `string` | yes | CTX-ID reference for the action. |
| `ts` | `number` | yes | UTC Unix timestamp with millisecond precision. |
| `event_type` | `string` | yes | Event kind. Exact allowed values not defined in provided standards. |
| `payload_hash` | `string` | yes | SHA-256 of the serialized action payload. |

#### TrustFlowEvent constraints
- Every action outcome (`allow`, `restrict`, `block`) MUST emit a TrustFlow event.
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Failed emission is a WARN-level audit event.
- Failure MUST NOT silently continue; it must be logged and surfaced.

---

### VTZEnforcementDecision

Produced when VTZ policy is evaluated.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `verdict` | `VTZVerdict` | yes | On VTZ policy denial, MUST be `block`. |

#### VTZEnforcementDecision constraints
- Every action MUST be checked against VTZ policy before execution.
- VTZ policy denial MUST produce a `VTZEnforcementDecision` record with `verdict=block`.

---

### ValidationResult

Canonical validation response structure for the Validation subsystem.

This structure is derived from the required validation behavior in the standards and is the recommended wire contract for validation outcomes.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `valid` | `boolean` | yes | `true` only when all applicable validation rules pass. |
| `errors` | `ValidationError[]` | yes | Empty array when `valid=true`. |
| `warnings` | `ValidationWarning[]` | yes | Empty array if none. |
| `decision` | `VTZEnforcementDecision` | no | Required when VTZ policy is evaluated. On denial, `verdict` MUST be `block`. |
| `trustflow_event` | `TrustFlowEvent` | no | Present when emission succeeds synchronously. |
| `ctx_id_status` | `CTXIDStatus` | no | Present for CTX-ID validation flows. |

---

### ValidationError

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable error code. |
| `message` | `string` | yes | Human-readable description. |
| `field` | `string` | no | Field name associated with the error, if applicable. |
| `constraint` | `string` | no | Violated rule description. |

---

### ValidationWarning

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable warning code. |
| `message` | `string` | yes | Human-readable description. |

---

### CPFInspectionResult

Represents the three-tier CPF evaluation outcome.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `tier_1_structural` | `CPFCheckResult` | yes | Tier 1 structural validation: schema, bounds checking. |
| `tier_2_semantic` | `CPFCheckResult` | yes | Tier 2 semantic classification: intent, data sensitivity, policy match. |
| `tier_3_behavioral` | `CPFCheckResult` | yes | Tier 3 behavioral analysis: anomaly detection, attack pattern recognition. |
| `passed` | `boolean` | yes | `true` only if all tiers pass. Fail closed. |

---

### CPFCheckResult

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `passed` | `boolean` | yes | Result of the tier check. |
| `reasons` | `string[]` | yes | Empty array when `passed=true`. |

---

## Enums and Constants

### `TaskStatus`

Allowed values:

- `pending`
- `in_progress`
- `done`

Constraints:
- Must be implemented as an enumeration.
- Must not be treated as a free-form status string set.

---

### `VTZVerdict`

Allowed values required by provided standards:

- `block`

Notes:
- The standards explicitly require `verdict=block` on VTZ policy denial.
- Other verdict values are not defined in the provided source and must not be inferred as contractual.

---

### `CTXIDStatus`

Allowed values:

- `valid`
- `invalid`
- `expired`
- `missing`
- `untrusted`

Constraints:
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Expired CTX-ID MUST be rejected.

---

### TrustFlow timing constant

| Name | Value | Meaning |
|---|---|---|
| `ts` precision | `millisecond` | UTC Unix timestamp with millisecond precision |

---

### CPF processing constant

| Name | Value | Meaning |
|---|---|---|
| enforcement mode | `fail closed` | All CPF tiers run synchronously in the enforcement path; failures reject processing. |

---

## Validation Rules

### 1. Task validation

#### Required fields
- `id` MUST be present on a materialized `Task`.
- `title` MUST be present.
- `status` MUST be present on a materialized `Task`.
- `created_at` MUST be present.

#### Field rules
- `id` MUST be unique and generated automatically on creation.
- `title` MUST be a string and MUST be non-empty.
- `status` MUST be one of:
  - `pending`
  - `in_progress`
  - `done`
- `status` defaults to `pending` at creation if omitted.
- `created_at` MUST be a numeric timestamp.

---

### 2. CTX-ID validation

Validation order and behavior are mandatory.

#### Entry-point rule
- Every entry point that processes an agent action MUST call CTX-ID validation FIRST.

#### Rejection rule
- CTX-ID validation failure MUST result in immediate rejection.
- No partial processing is permitted after CTX-ID validation failure.

#### Token rules
- CTX-ID MUST be present for trusted processing.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Expired CTX-ID MUST be rejected.
- CTX-ID MUST validate against TrustLock public key.
- CTX-ID fields are immutable once issued.
- Rotation MUST create a new token and invalidate the old token immediately.

---

### 3. VTZ validation

- Every agent session is bound to exactly one VTZ at CTX-ID issuance.
- Every action MUST be checked against VTZ policy BEFORE execution.
- Cross-VTZ tool calls require explicit policy authorization.
- Implicit authorization is denied.
- VTZ boundaries are structural, not advisory.
- VTZ policy changes take effect at next CTX-ID issuance, not mid-session.
- VTZ policy denial MUST produce a `VTZEnforcementDecision` with:
  - `verdict`: `block`

---

### 4. TrustFlow validation

- Every action outcome MUST emit a TrustFlow event.
- Outcomes include:
  - `allow`
  - `restrict`
  - `block`
- Every `TrustFlowEvent` MUST include:
  - `event_id`
  - `session_id`
  - `ctx_id`
  - `ts`
  - `event_type`
  - `payload_hash`
- `event_id` MUST be globally unique and CSPRNG-generated.
- `ts` MUST be a UTC Unix timestamp with millisecond precision.
- `payload_hash` MUST be SHA-256 of the serialized action payload.
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Emission failure MUST be logged and surfaced.
- Emission failure is a WARN-level audit event.
- Emission failure MUST NOT silently continue.

---

### 5. CPF validation

- CPF is a three-tier inspection and classification engine within CAL.
- Tier 1 MUST perform structural validation, including:
  - schema validation
  - bounds checking
- Tier 2 MUST perform semantic classification, including:
  - intent
  - data sensitivity
  - policy match
- Tier 3 MUST perform behavioral analysis, including:
  - anomaly detection
  - attack pattern recognition
- All three tiers MUST run synchronously in the enforcement path.
- CPF MUST fail closed.

---

### 6. CAL enforcement validation

- No tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- CAL is the enforcement choke point for all agent-originated action.
- CAL sits above the VTZ enforcement plane and below application orchestration.

---

## Wire Format Examples

### Valid Task

```json
{
  "id": "task_01JXYZ8A1M7K9P2Q4R6S8T0U1V",
  "title": "Write INTERFACES.md",
  "status": "pending",
  "created_at": 1712345678
}
```

### Invalid Task: empty title

```json
{
  "id": "task_01JXYZ8A1M7K9P2Q4R6S8T0U1V",
  "title": "",
  "status": "pending",
  "created_at": 1712345678
}
```

Reason:
- `title` must be non-empty.

---

### Invalid Task: bad status

```json
{
  "id": "task_01JXYZ8A1M7K9P2Q4R6S8T0U1V",
  "title": "Implement storage",
  "status": "blocked",
  "created_at": 1712345678
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
  "policy_revision": "2026-03-01",
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
  "policy_revision": "2026-03-01",
  "issued_at": 1712345678123
}
```

Reason:
- `sig` is required.
- CTX-ID must validate against TrustLock public key.

---

### Valid TrustFlowEvent

```json
{
  "event_id": "evt_4f1d6a0f4d6f4b5e8a8f5f8f7e6d3c2b",
  "session_id": "session-456",
  "ctx_id": "ctx_abc123",
  "ts": 1712345678123,
  "event_type": "block",
  "payload_hash": "3f0a377ba0a4a460ecb616f6507ce0d8cfa3e704025d4b17d4cd6a1d8f8d235b"
}
```

### Invalid TrustFlowEvent: sequential ID and missing payload hash

```json
{
  "event_id": "1001",
  "session_id": "session-456",
  "ctx_id": "ctx_abc123",
  "ts": 1712345678,
  "event_type": "allow"
}
```

Reasons:
- `event_id` must be globally unique and CSPRNG-generated, not sequential.
- `payload_hash` is required.
- `ts` must be UTC Unix timestamp with millisecond precision.

---

### Valid VTZEnforcementDecision on denial

```json
{
  "verdict": "block"
}
```

### Invalid VTZEnforcementDecision on denial

```json
{
  "verdict": "deny"
}
```

Reason:
- VTZ policy denial must produce `verdict=block`.

---

### Valid ValidationResult: blocked by VTZ

```json
{
  "valid": false,
  "errors": [
    {
      "code": "VTZ_POLICY_DENIED",
      "message": "Action denied by VTZ policy."
    }
  ],
  "warnings": [],
  "decision": {
    "verdict": "block"
  },
  "trustflow_event": {
    "event_id": "evt_4f1d6a0f4d6f4b5e8a8f5f8f7e6d3c2b",
    "session_id": "session-456",
    "ctx_id": "ctx_abc123",
    "ts": 1712345678123,
    "event_type": "block",
    "payload_hash": "3f0a377ba0a4a460ecb616f6507ce0d8cfa3e704025d4b17d4cd6a1d8f8d235b"
  },
  "ctx_id_status": "valid"
}
```

### Invalid ValidationResult: claims valid with errors

```json
{
  "valid": true,
  "errors": [
    {
      "code": "TITLE_EMPTY",
      "message": "title must be non-empty",
      "field": "title"
    }
  ],
  "warnings": []
}
```

Reason:
- `valid=true` is inconsistent with non-empty `errors`.

---

## Integration Points

### CAL

Validation subsystem integration requirements:

- Every entry point that processes an agent action MUST call CTX-ID validation first.
- No tool call, data read, API invocation, or agent handoff may execute before CAL policy evaluation.
- CPF inspection MUST run synchronously within the enforcement path.
- VTZ policy evaluation MUST occur before execution.
- TrustFlow emission MUST occur for every action outcome.

#### Expected sequence
1. Receive action payload.
2. Validate `CTX-ID`.
3. Reject immediately on CTX-ID failure.
4. Run CPF:
   - Tier 1 structural
   - Tier 2 semantic
   - Tier 3 behavioral
5. Evaluate VTZ policy.
6. If denied, produce `VTZEnforcementDecision` with `verdict=block`.
7. Emit `TrustFlowEvent` synchronously.
8. Surface any emission failure as WARN-level audit event.
9. Only then allow downstream execution when permitted.

---

### Task model

Validation subsystem MUST validate task payloads against:

- `id` auto-generated uniqueness requirement
- non-empty `title`
- enumerated `status`
- numeric `created_at`

---

### CTX-ID / TrustLock

Validation subsystem MUST support:

- required CTX-ID presence checks
- immutable field handling after issuance
- expiry rejection
- TrustLock public key signature validation
- rotation semantics where old token is invalidated immediately

---

### VTZ enforcement plane

Validation subsystem MUST enforce:

- exactly one VTZ binding per agent session at CTX-ID issuance
- explicit authorization for cross-VTZ tool calls
- deny-by-default for implicit cross-VTZ access
- policy changes effective only at next CTX-ID issuance

---

### TrustFlow

Validation subsystem MUST produce or validate events with exact required fields:

- `event_id`
- `session_id`
- `ctx_id`
- `ts`
- `event_type`
- `payload_hash`

Emission requirements:

- synchronous in enforcement path
- no async buffering
- no silent failure

---

### CPF

Validation subsystem MUST expose validation hooks for all three CPF tiers:

- structural validation
- semantic classification
- behavioral analysis

All tiers MUST execute synchronously and fail closed.