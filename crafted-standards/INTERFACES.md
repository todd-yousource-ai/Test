# Interface Contracts - Validation

## Data Structures

### Task

Represents a single unit of work.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `id` | `string` | yes | Unique identifier. Generated automatically on creation. |
| `title` | `string` | yes | Must be non-empty. |
| `status` | `TaskStatus` | yes | Allowed values: `pending`, `in_progress`, `done`. Default on creation: `pending`. |
| `created_at` | `number` | yes | Numeric timestamp. |

#### Task constraints
- `id` MUST be unique.
- `title` MUST be present and MUST NOT be empty.
- `status` MUST be an enumeration value, not a free-form string.
- `created_at` MUST be numeric.

---

### CTXIDToken

Per-session, per-agent signed token binding identity, VTZ, policy, and permissions.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `agent_id` | `string` | yes | Immutable once issued. |
| `session_id` | `string` | yes | Immutable once issued. |
| `vtz_scope` | `string` | yes | Immutable once issued. Binds session to exactly one VTZ. |
| `policy_revision` | `string` | yes | Immutable once issued. |
| `issued_at` | `number` | yes | Timestamp. Immutable once issued. |
| `sig` | `string` | yes | Signature. Must validate against TrustLock public key. Immutable once issued. |

#### CTXIDToken constraints
- CTX-ID tokens are IMMUTABLE once issued.
- Rotation creates a new token; the old one is invalidated immediately.
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Expired CTX-ID MUST be rejected.
- Validation MUST occur against TrustLock public key.
- No field modification is allowed after issuance.

---

### VTZEnforcementDecision

Decision record produced when VTZ policy is evaluated.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `verdict` | `VTZVerdict` | yes | On VTZ policy denial, value MUST be `block`. |

#### VTZEnforcementDecision constraints
- Produced before execution when action is checked against VTZ policy.
- VTZ policy denial MUST produce a record with `verdict=block`.

---

### TrustFlowEvent

Audit/enforcement event emitted for every action outcome.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `event_id` | `string` | yes | Must be globally unique. CSPRNG-generated, not sequential. |
| `session_id` | `string` | yes | Session identifier. |
| `ctx_id` | `string` | yes | CTX-ID reference for the action. |
| `ts` | `number` | yes | UTC Unix timestamp with millisecond precision. |
| `event_type` | `string` | yes | Event type identifier. |
| `payload_hash` | `string` | yes | SHA-256 of the serialized action payload. |

#### TrustFlowEvent constraints
- MUST be emitted for every action outcome: `allow`, `restrict`, `block`.
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- Failed emission is a WARN-level audit event.
- Failure MUST NOT silently continue.

---

### ValidationResult

Canonical validation response for the Validation subsystem.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `valid` | `boolean` | yes | `true` only if all applicable validation rules pass. |
| `errors` | `ValidationError[]` | yes | Empty array when `valid=true`. |
| `warnings` | `ValidationWarning[]` | yes | Empty array if none. |
| `decision` | `VTZEnforcementDecision` | no | Present when VTZ policy evaluation occurs. |
| `trustflow_event` | `TrustFlowEvent` | no | Present when emission succeeds. |

#### ValidationResult constraints
- If `valid=true`, `errors` MUST be empty.
- If CTX-ID validation fails, processing MUST be rejected immediately.
- No partial processing is allowed after CTX-ID validation failure.

---

### ValidationError

Represents a validation failure.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable error code. |
| `message` | `string` | yes | Human-readable description. |
| `field` | `string` | no | Field name associated with the error. |
| `severity` | `ValidationSeverity` | yes | Severity classification. |

---

### ValidationWarning

Represents a non-fatal validation or audit issue.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `code` | `string` | yes | Stable machine-readable warning code. |
| `message` | `string` | yes | Human-readable description. |
| `field` | `string` | no | Field name associated with the warning. |
| `severity` | `ValidationSeverity` | yes | Severity classification. |

---

### AgentActionEnvelope

Validation input envelope for any agent-originated action.

| Field | Type | Required | Constraints |
|---|---|---:|---|
| `ctx_id` | `CTXIDToken` | yes | MUST be validated first. Missing CTX-ID is `UNTRUSTED`. |
| `session_id` | `string` | yes | Must match session bound in CTX-ID. |
| `action_payload` | `object` | yes | Serialized payload used to compute `payload_hash`. |
| `event_type` | `string` | yes | Used in emitted `TrustFlowEvent`. |

#### AgentActionEnvelope constraints
- Every entry point that processes an agent action MUST call CTX-ID validation FIRST.
- Every action MUST be checked against VTZ policy BEFORE execution.
- No tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.

---

## Enums and Constants

### TaskStatus

Allowed values exactly:

- `pending`
- `in_progress`
- `done`

---

### VTZVerdict

Allowed values:

- `allow`
- `restrict`
- `block`

Constraint:
- On VTZ policy denial, value MUST be `block`.

---

### ValidationSeverity

Allowed values:

- `error`
- `warning`

---

### Validation Constants

#### Identity and trust constants
- `UNTRUSTED` — classification used when CTX-ID is missing.

#### Hashing
- `SHA-256` — required algorithm for `payload_hash`.

#### Time format
- `ts` in `TrustFlowEvent` MUST be a UTC Unix timestamp with millisecond precision.
- `issued_at` in `CTXIDToken` MUST be a timestamp.
- `created_at` in `Task` MUST be a numeric timestamp.

---

## Validation Rules

### 1. Task validation

#### 1.1 Required fields
A `Task` payload MUST include:
- `id`
- `title`
- `status`
- `created_at`

#### 1.2 Field rules
- `id` MUST be unique.
- `id` MUST be generated automatically on creation.
- `title` MUST be a string.
- `title` MUST be non-empty.
- `status` MUST be one of:
  - `pending`
  - `in_progress`
  - `done`
- `status` MUST be defined as an enumeration, not as free-form input.
- If not explicitly provided at creation, `status` defaults to `pending`.
- `created_at` MUST be numeric.

---

### 2. CTX-ID validation

Validation order is mandatory.

#### 2.1 First-step validation
- Every entry point that processes an agent action MUST call CTX-ID validation FIRST.

#### 2.2 Rejection behavior
- CTX-ID validation failure MUST result in immediate rejection.
- No partial processing is permitted after CTX-ID validation failure.

#### 2.3 Presence rules
- Missing CTX-ID MUST be treated as `UNTRUSTED`.
- Identity MUST never be inferred from surrounding context.

#### 2.4 Token rules
- CTX-ID tokens are immutable once issued.
- Rotation creates a new token.
- The old token is invalidated immediately.
- Expired CTX-ID MUST be rejected.
- Validation MUST be performed against TrustLock public key.
- Software-only validation is rejected.

#### 2.5 Session/VTZ binding
- Each agent session is bound to exactly one VTZ at CTX-ID issuance.
- `vtz_scope` binds identity to VTZ.
- VTZ policy changes take effect at next CTX-ID issuance, not mid-session.

---

### 3. VTZ policy validation

- Every action MUST be checked against VTZ policy BEFORE execution.
- Cross-VTZ tool calls require explicit policy authorization.
- Implicit cross-VTZ access is denied.
- VTZ boundaries are structural, not advisory.
- Enforcement cannot be bypassed by application code.
- VTZ policy denial MUST produce a `VTZEnforcementDecision` with:
  - `verdict`: `block`

---

### 4. TrustFlow validation and emission

- Every action outcome MUST emit a `TrustFlowEvent`.
- Outcomes include:
  - `allow`
  - `restrict`
  - `block`
- Emission MUST be synchronous in the enforcement path.
- Async buffering is not permitted.
- `event_id` MUST be globally unique.
- `event_id` MUST be CSPRNG-generated and MUST NOT be sequential.
- `ts` MUST be UTC Unix timestamp with millisecond precision.
- `payload_hash` MUST be SHA-256 of the serialized action payload.
- TrustFlow emission failure MUST NOT silently continue.
- Failed emission is a WARN-level audit event and MUST be surfaced.

---

### 5. CAL and CPF enforcement validation

#### 5.1 CAL
- No tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.

#### 5.2 CPF
All three tiers run synchronously in the enforcement path and fail closed.

Tier requirements:
1. Tier 1: structural validation
   - schema
   - bounds checking
2. Tier 2: semantic classification
   - intent
   - data sensitivity
   - policy match
3. Tier 3: behavioral analysis
   - anomaly detection
   - attack pattern recognition

Fail-closed requirement:
- If any required CPF validation fails, the action MUST be rejected.

---

## Wire Format Examples

## Valid payloads

### Valid Task

```json
{
  "id": "task_01",
  "title": "Write INTERFACES.md",
  "status": "pending",
  "created_at": 1712345678
}
```

### Valid Task with non-default status

```json
{
  "id": "task_02",
  "title": "Implement validation checks",
  "status": "in_progress",
  "created_at": 1712345678
}
```

### Valid CTXIDToken

```json
{
  "agent_id": "agent_123",
  "session_id": "session_456",
  "vtz_scope": "vtz_alpha",
  "policy_revision": "2026-03-01",
  "issued_at": 1712345678123,
  "sig": "base64-signature"
}
```

### Valid TrustFlowEvent

```json
{
  "event_id": "a4f2b7b2-7c57-4f47-bf96-1bb9c4ef2f01",
  "session_id": "session_456",
  "ctx_id": "ctx_789",
  "ts": 1712345678123,
  "event_type": "task.create",
  "payload_hash": "8f14e45fceea167a5a36dedd4bea2543d0f9e8dbf6a1f4d3c7b2e5d6a7b8c9d0"
}
```

### Valid AgentActionEnvelope

```json
{
  "ctx_id": {
    "agent_id": "agent_123",
    "session_id": "session_456",
    "vtz_scope": "vtz_alpha",
    "policy_revision": "2026-03-01",
    "issued_at": 1712345678123,
    "sig": "base64-signature"
  },
  "session_id": "session_456",
  "event_type": "task.create",
  "action_payload": {
    "id": "task_03",
    "title": "Create task",
    "status": "pending",
    "created_at": 1712345678
  }
}
```

### Valid ValidationResult

```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "decision": {
    "verdict": "allow"
  },
  "trustflow_event": {
    "event_id": "a4f2b7b2-7c57-4f47-bf96-1bb9c4ef2f01",
    "session_id": "session_456",
    "ctx_id": "ctx_789",
    "ts": 1712345678123,
    "event_type": "task.create",
    "payload_hash": "8f14e45fceea167a5a36dedd4bea2543d0f9e8dbf6a1f4d3c7b2e5d6a7b8c9d0"
  }
}
```

## Invalid payloads

### Invalid Task: empty title

```json
{
  "id": "task_04",
  "title": "",
  "status": "pending",
  "created_at": 1712345678
}
```

Reason:
- `title` must be non-empty.

### Invalid Task: unsupported status

```json
{
  "id": "task_05",
  "title": "Bad status example",
  "status": "blocked",
  "created_at": 1712345678
}
```

Reason:
- `status` must be one of `pending`, `in_progress`, `done`.

### Invalid Task: non-numeric timestamp

```json
{
  "id": "task_06",
  "title": "Bad timestamp",
  "status": "done",
  "created_at": "1712345678"
}
```

Reason:
- `created_at` must be numeric.

### Invalid CTXIDToken: missing signature

```json
{
  "agent_id": "agent_123",
  "session_id": "session_456",
  "vtz_scope": "vtz_alpha",
  "policy_revision": "2026-03-01",
  "issued_at": 1712345678123
}
```

Reason:
- `sig` is required.

### Invalid AgentActionEnvelope: missing CTX-ID

```json
{
  "session_id": "session_456",
  "event_type": "task.create",
  "action_payload": {
    "id": "task_03",
    "title": "Create task",
    "status": "pending",
    "created_at": 1712345678
  }
}
```

Reason:
- Missing CTX-ID must be treated as `UNTRUSTED`.
- Request must be rejected.

### Invalid VTZEnforcementDecision for denial

```json
{
  "verdict": "allow"
}
```

Reason:
- On VTZ policy denial, `verdict` must be `block`.

### Invalid TrustFlowEvent: sequential event id and wrong timestamp precision

```json
{
  "event_id": "1001",
  "session_id": "session_456",
  "ctx_id": "ctx_789",
  "ts": 1712345678,
  "event_type": "task.create",
  "payload_hash": "not-a-sha-256"
}
```

Reason:
- `event_id` must be globally unique and CSPRNG-generated, not sequential.
- `ts` must be UTC Unix timestamp with millisecond precision.
- `payload_hash` must be SHA-256 of the serialized action payload.

---

## Integration Points

### CAL — Conversation Abstraction Layer
Validation subsystem integration requirements:
- Acts as enforcement choke point for all agent-originated action.
- Sits above the VTZ enforcement plane and below application orchestration.
- No action may bypass CAL validation.

### CPF — Conversation Plane Filter
Validation subsystem MUST support synchronous fail-closed validation across:
- Tier 1 structural validation
- Tier 2 semantic classification
- Tier 3 behavioral analysis

### CTX-ID
Validation subsystem MUST:
- Validate CTX-ID first
- Reject expired, missing, invalid, or modified CTX-ID
- Enforce immutability and rotation behavior
- Bind action processing to `agent_id`, `session_id`, `vtz_scope`, `policy_revision`, `issued_at`, `sig`

### VTZ — Virtual Trust Zone
Validation subsystem MUST:
- Enforce exactly-one-VTZ binding per session
- Evaluate policy before execution
- Deny implicit cross-VTZ calls
- Produce `VTZEnforcementDecision` on denial with `verdict=block`

### TrustFlow
Validation subsystem MUST:
- Emit one synchronous `TrustFlowEvent` for every action outcome
- Include exactly these required fields:
  - `event_id`
  - `session_id`
  - `ctx_id`
  - `ts`
  - `event_type`
  - `payload_hash`

### Task library model validation
Validation subsystem MUST validate `Task` payloads for:
- required fields
- enum-constrained `status`
- non-empty `title`
- numeric `created_at`
- unique auto-generated `id`