# Interface Contracts - Validation

## Data Structures

### Task

Represents a single unit of work.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `id` | `string` | Yes | Unique identifier. Generated automatically on creation. |
| `title` | `string` | Yes | Must be non-empty. |
| `status` | `TaskStatus` | Yes | Allowed values: `pending`, `in_progress`, `done`. Default: `pending`. Must be represented as an enumeration, not free text. |
| `created_at` | `number` | Yes | Numeric timestamp. |

#### Task constraints
- `id` MUST be unique.
- `title` MUST be present and MUST be non-empty.
- `status` MUST be one of `pending`, `in_progress`, `done`.
- `created_at` MUST be a numeric timestamp.

---

### CTX-ID

Per-session, per-agent signed token binding identity, VTZ, policy, and permissions.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `agent_id` | `string` | Yes | Immutable once issued. |
| `session_id` | `string` | Yes | Immutable once issued. |
| `vtz_scope` | `string` | Yes | Immutable once issued. Binds session to exactly one VTZ at issuance. |
| `policy_revision` | `string` | Yes | Immutable once issued. |
| `issued_at` | `number` | Yes | Issuance timestamp. Immutable once issued. |
| `sig` | `string` | Yes | Signature. Must validate against TrustLock public key. Immutable once issued. |

#### CTX-ID constraints
- CTX-ID tokens are **IMMUTABLE once issued**.
- Rotation creates a new token; the old token is invalidated immediately.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Expired CTX-ID MUST be rejected.
- CTX-ID MUST be validated against TrustLock public key.
- Identity MUST NOT be inferred from surrounding context when CTX-ID is missing.

---

### TrustFlowEvent

Required event emitted for every action outcome.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `event_id` | `string` | Yes | Globally unique. CSPRNG-generated. Not sequential. |
| `session_id` | `string` | Yes | Must identify the session associated with the action. |
| `ctx_id` | `string` | Yes | CTX-ID associated with the action. |
| `ts` | `number` | Yes | UTC Unix timestamp with millisecond precision. |
| `event_type` | `string` | Yes | Event type identifier. |
| `payload_hash` | `string` | Yes | SHA-256 of the serialized action payload. |

#### TrustFlowEvent constraints
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Failed emission is a WARN-level audit event.
- Failed emission MUST NOT silently continue.

---

### VTZEnforcementDecision

Produced when VTZ policy denies an action.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `verdict` | `VTZVerdict` | Yes | For policy denial, value MUST be `block`. |

#### VTZEnforcementDecision constraints
- VTZ policy denial MUST produce a `VTZEnforcementDecision` record with `verdict=block`.

---

### ValidationResult

Canonical validation outcome for the Validation subsystem.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `valid` | `boolean` | Yes | `true` when validation succeeds, `false` otherwise. |
| `errors` | `array<ValidationError>` | Yes | Empty when `valid=true`. One or more entries when `valid=false`. |

---

### ValidationError

Represents a single validation failure.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `field` | `string` | Yes | Name of the invalid field or validation target. |
| `code` | `string` | Yes | Stable validation error code. |
| `message` | `string` | Yes | Human-readable validation failure description. |

---

### ActionValidationRequest

Validation request for an agent-originated action entering CAL.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `ctx_id` | `CTX-ID \| string \| null` | Yes | MUST be validated first. If missing or `null`, treat as `UNTRUSTED`. |
| `session_id` | `string` | Yes | Must correspond to CTX-ID session when CTX-ID is present. |
| `action_payload` | `object` | Yes | Serialized payload used to compute `payload_hash`. |
| `event_type` | `string` | Yes | Used in TrustFlow emission. |
| `vtz_scope` | `string` | No | If present, MUST be consistent with CTX-ID binding. |

#### ActionValidationRequest constraints
- No tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- Every entry point that processes an agent action MUST call CTX-ID validation FIRST.
- Every action MUST be checked against VTZ policy BEFORE execution.

---

## Enums and Constants

### `TaskStatus`

Allowed values, exactly:

- `pending`
- `in_progress`
- `done`

Constraints:
- Default value at task creation: `pending`
- Must be implemented as an enumeration, not free text

---

### `VTZVerdict`

Allowed values:

- `block`

Constraints:
- On VTZ policy denial, `verdict` MUST be `block`.

---

### Constants and policy requirements

#### CAL
- CAL is the enforcement choke point for all agent-originated action.
- No tool call, data read, API invocation, or agent handoff executes without passing through a CAL policy evaluation.

#### CPF
Three synchronous enforcement tiers, fail closed:
1. Structural validation
2. Semantic classification
3. Behavioral analysis

#### CTX-ID
Required fields, exactly:
- `agent_id`
- `session_id`
- `vtz_scope`
- `policy_revision`
- `issued_at`
- `sig`

#### VTZ
- Each agent session is bound to exactly one VTZ at CTX-ID issuance.
- VTZ defines:
  - allowed tools
  - data classifications
  - network egress
  - peer agents

---

## Validation Rules

### 1. Task validation

#### Required field validation
- `id` MUST be present.
- `title` MUST be present.
- `status` MUST be present unless defaulting is applied at creation.
- `created_at` MUST be present.

#### Field type validation
- `id` MUST be `string`.
- `title` MUST be `string`.
- `status` MUST be `TaskStatus`.
- `created_at` MUST be `number`.

#### Field value validation
- `title` MUST be non-empty.
- `status` MUST be one of `pending`, `in_progress`, `done`.
- `created_at` MUST be numeric.

#### Behavioral validation
- `id` MUST be generated automatically on creation.
- `status` default at creation MUST be `pending`.

---

### 2. CTX-ID validation

#### Ordering requirement
- CTX-ID validation MUST occur FIRST for every entry point that processes an agent action.

#### Presence rules
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Missing CTX-ID MUST NOT permit inferred identity.

#### Integrity and immutability
- CTX-ID tokens are immutable once issued.
- Any field modification after issuance is invalid.
- Rotation MUST create a new token.
- The old token MUST be invalidated immediately.

#### Cryptographic validation
- `sig` MUST validate against TrustLock public key.
- Software-only validation is rejected.

#### Expiry validation
- Expired CTX-ID MUST be rejected.
- Clock skew tolerance is deployment-defined and outside this interface.

#### Binding validation
- `session_id` in the request MUST match the CTX-ID session binding.
- Each session MUST be bound to exactly one VTZ at CTX-ID issuance.

---

### 3. VTZ validation

#### Pre-execution enforcement
- Every action MUST be checked against VTZ policy BEFORE execution.

#### Boundary rules
- Cross-VTZ tool calls require explicit policy authorization.
- Implicit cross-VTZ access is denied.
- VTZ boundaries are structural, not advisory.
- Enforcement cannot be bypassed by application code.

#### Policy denial behavior
- VTZ policy denial MUST produce a `VTZEnforcementDecision` with `verdict=block`.

#### Policy lifecycle
- VTZ policy changes take effect at NEXT CTX-ID issuance, not mid-session.

---

### 4. TrustFlow validation

#### Required emission
- Every action outcome (`allow`, `restrict`, `block`) MUST emit a TrustFlow event.

#### Event field validation
- `event_id` MUST be globally unique.
- `event_id` MUST be CSPRNG-generated and MUST NOT be sequential.
- `session_id` MUST be present.
- `ctx_id` MUST be present.
- `ts` MUST be a UTC Unix timestamp with millisecond precision.
- `event_type` MUST be present.
- `payload_hash` MUST be present.
- `payload_hash` MUST equal the SHA-256 of the serialized action payload.

#### Emission behavior
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Emission failure MUST be logged and surfaced.
- Emission failure is a WARN-level audit event.
- Emission failure MUST NOT silently continue.

---

### 5. CPF validation stages

All tiers run synchronously and fail closed.

#### Tier 1: Structural validation
- Schema validation
- Bounds checking

#### Tier 2: Semantic classification
- Intent classification
- Data sensitivity classification
- Policy match

#### Tier 3: Behavioral analysis
- Anomaly detection
- Attack pattern recognition

---

## Wire Format Examples

### Valid Task

```json
{
  "id": "task_001",
  "title": "Write INTERFACES.md",
  "status": "pending",
  "created_at": 1711920000
}
```

### Invalid Task: empty title

```json
{
  "id": "task_002",
  "title": "",
  "status": "pending",
  "created_at": 1711920001
}
```

Reason:
- `title` is present but empty; must be non-empty.

---

### Invalid Task: invalid status

```json
{
  "id": "task_003",
  "title": "Implement validator",
  "status": "queued",
  "created_at": 1711920002
}
```

Reason:
- `status` must be one of `pending`, `in_progress`, `done`.

---

### Valid CTX-ID

```json
{
  "agent_id": "agent-123",
  "session_id": "session-456",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "rev-9",
  "issued_at": 1711920000123,
  "sig": "base64-signature"
}
```

### Invalid CTX-ID: missing signature

```json
{
  "agent_id": "agent-123",
  "session_id": "session-456",
  "vtz_scope": "vtz-alpha",
  "policy_revision": "rev-9",
  "issued_at": 1711920000123
}
```

Reason:
- `sig` is required.

---

### Valid TrustFlowEvent

```json
{
  "event_id": "0f4c2e91-7d4d-4c67-9d6c-16d07a8d8f22",
  "session_id": "session-456",
  "ctx_id": "ctx-abc",
  "ts": 1711920000456,
  "event_type": "action.allow",
  "payload_hash": "3f0a377ba0a4a460ecb616f6507ce0d8cfa3e704025d4fda3edc5c9e6a8b0f2f"
}
```

### Invalid TrustFlowEvent: sequential event id and missing payload hash

```json
{
  "event_id": "1001",
  "session_id": "session-456",
  "ctx_id": "ctx-abc",
  "ts": 1711920000456,
  "event_type": "action.allow"
}
```

Reasons:
- `payload_hash` is required.
- `event_id` must be globally unique and CSPRNG-generated, not sequential.

---

### Valid VTZEnforcementDecision

```json
{
  "verdict": "block"
}
```

### Invalid VTZEnforcementDecision

```json
{
  "verdict": "allow"
}
```

Reason:
- On VTZ policy denial, `verdict` must be `block`.

---

### Valid ActionValidationRequest

```json
{
  "ctx_id": {
    "agent_id": "agent-123",
    "session_id": "session-456",
    "vtz_scope": "vtz-alpha",
    "policy_revision": "rev-9",
    "issued_at": 1711920000123,
    "sig": "base64-signature"
  },
  "session_id": "session-456",
  "action_payload": {
    "tool": "task.create",
    "title": "New task"
  },
  "event_type": "action.allow",
  "vtz_scope": "vtz-alpha"
}
```

### Invalid ActionValidationRequest: missing CTX-ID

```json
{
  "ctx_id": null,
  "session_id": "session-456",
  "action_payload": {
    "tool": "task.create",
    "title": "New task"
  },
  "event_type": "action.allow"
}
```

Reason:
- Missing CTX-ID must be treated as `UNTRUSTED`.

---

### ValidationResult example

```json
{
  "valid": false,
  "errors": [
    {
      "field": "status",
      "code": "invalid_enum",
      "message": "status must be one of pending, in_progress, done"
    }
  ]
}
```

---

## Integration Points

### CAL integration
- Validation is in the CAL enforcement path.
- No agent-originated action may bypass validation.
- Validation must run before tool call, data read, API invocation, or agent handoff.

### CPF integration
- Validation maps to CPF Tier 1 structural validation and supports Tier 2 and Tier 3 gating.
- All CPF tiers run synchronously and fail closed.

### CTX-ID integration
- Validation must validate CTX-ID first.
- CTX-ID validation result gates all downstream processing.

### VTZ integration
- Validation must verify the session’s VTZ binding from CTX-ID.
- Validation must enforce exactly-one-VTZ session binding.
- Validation must reject unauthorized cross-VTZ actions unless explicitly authorized by policy.

### TrustFlow integration
- Successful and failed enforcement outcomes must emit TrustFlow events.
- Validation must ensure required TrustFlow fields are present and correctly derived.
- TrustFlow emission failure must be logged and surfaced.

### Task model integration
- Validation must enforce `Task` field presence, type correctness, enum constraints, non-empty title, and numeric `created_at`.
- Task creation must apply automatic `id` generation and default `status=pending`.