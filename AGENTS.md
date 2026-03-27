# AGENTS.md

Crafted Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack via cryptographic identity, operator-defined policy, and auditable trust boundaries.

## How to Use This File

This file is the authoritative baseline for every coding session in this repository — read it completely before touching any code. For subsystem-specific detail, see `crafted-docs/` for the full TRDs and PRDs, and `crafted-standards/` for synthesised architecture, interface contracts, and decision records.

## Document Index

| Document Name | Type | Repo Path | What It Covers |
|---|---|---|---|
| TRD-TASKLIB | DOCX/MD | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Validation TRD for Crafted Dev Agent pipeline — defines a simple Python task management library to prove the end-to-end dependency chain (docs → scaffold → model → storage → CLI) |
| Forge Architecture Context | MD | `crafted-docs/forge_architecture_context.md` | Platform overview, core subsystem definitions (CAL, CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, VTZ, DTL, TrustLock, MCP, Rewind), protocol wire formats, and enforcement architecture |

## Critical Rules — Non-Negotiable

1. Validate CTX-ID at every enforcement entry point BEFORE any processing occurs — CTX-ID validation failure results in immediate rejection with zero partial processing.
2. Never infer trust implicitly — always assert and verify identity explicitly via TrustLock-anchored cryptographic material.
3. Emit a TrustFlow event for every action outcome (allow, restrict, block) synchronously in the enforcement path — async buffering is forbidden.
4. Check VTZ policy BEFORE execution of every agent action — implicit cross-VTZ access is denied by default.
5. Fail closed on all trust, identity, policy, and cryptographic failures — reject the action, log the event, surface to the caller, never silently continue.
6. Never include secrets, keys, tokens, credentials, or cleartext sensitive payloads in logs, error messages, or generated code.
7. Treat all external input as untrusted — validate strictly, bounds-check all parsing, and fail safely on malformed input.
8. Assign DTL labels at data ingestion and treat them as immutable — derived data inherits the highest classification of any source, and unlabeled data is CONFIDENTIAL until explicitly reclassified.
9. CTX-ID tokens are immutable once issued — rotation creates a new token and immediately invalidates the old one.
10. VTZ boundaries are structural enforcement, not advisory — application code cannot bypass VTZ enforcement under any circumstance.
11. Generate audit records BEFORE execution of every security-relevant action — audit records are append-only with no modification or deletion.
12. Use only FIPS 140-3 approved cryptographic algorithms — never invent cryptography, never degrade silently into insecure behavior.
13. Ban `try/except/pass` (or any equivalent silent exception swallowing) in all enforcement, trust, identity, policy, and cryptographic code paths.
14. Do not mock enforcement decisions in tests — mock external calls if needed but the enforcement logic itself must execute.
15. Every TrustFlow event must include `event_id` (CSPRNG-generated, globally unique), `session_id`, `ctx_id`, `ts` (UTC Unix ms), `event_type`, `payload_hash` (SHA-256), and `sig`.

## Architecture Overview

### CAL — Conversation Abstraction Layer
- **Does:** Serves as the enforcement choke point for all agent-originated actions — no tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- **Called by:** Application orchestration layers, agent runtimes.
- **Calls:** VTZ enforcement, CTX-ID validation, TrustFlow emission, PEE (Policy Enforcement Engine).
- **Must NEVER:** Allow any action to bypass policy evaluation, execute partially on validation failure, or emit actions without a corresponding TrustFlow event.

### CPF — Conversation Plane Filter
- **Does:** Filters and intercepts conversation-level traffic entering the CAL enforcement plane.
- **Called by:** Inbound agent communication channels.
- **Calls:** CAL for policy evaluation.
- **Must NEVER:** Pass unvalidated or unfiltered traffic through to CAL without inspection.

### CTX-ID — Contextual Identity
- **Does:** Provides cryptographic session identity for every agent interaction — JWT-like token signed with TrustLock agent key containing session, identity, VTZ binding, and temporal claims.
- **Called by:** CAL at every enforcement entry point.
- **Calls:** TrustLock for key validation.
- **Must NEVER:** Allow modification after issuance, accept expired tokens, or infer identity from context when CTX-ID is missing.

### VTZ — Virtual Trust Zones
- **Does:** Defines and enforces structural trust boundaries around agent sessions — each session is bound to exactly one VTZ at CTX-ID issuance.
- **Called by:** CAL before any action execution, CTX-ID during issuance.
- **Calls:** Policy store for boundary definitions.
- **Must NEVER:** Allow implicit cross-VTZ access, permit mid-session VTZ policy changes, or treat boundaries as advisory.

### TrustFlow / SIS — Audit Stream
- **Does:** Captures every enforcement decision as an immutable, signed, append-only audit event stream enabling forensic reconstruction and replay.
- **Called by:** CAL after every action outcome.
- **Calls:** Audit storage backend.
- **Must NEVER:** Drop events silently, allow modification of emitted records, or include secrets/keys/tokens in event payloads.

### DTL — Data Trust Labels
- **Does:** Assigns immutable classification labels to data at ingestion, enforces label inheritance on derived data, and verifies labels before data crosses any trust boundary.
- **Called by:** Data ingestion pipelines, CAL before cross-boundary data movement.
- **Calls:** Label store, audit stream for label-stripping events.
- **Must NEVER:** Allow label modification after assignment, permit unlabeled data to be treated as non-confidential, or strip labels without auditing.

### TrustLock — Cryptographic Machine Identity
- **Does:** Provides TPM-anchored cryptographic identity for agents and machines — manages key generation, storage, rotation, destruction, and validation.
- **Called by:** CTX-ID for token signing and validation.
- **Calls:** TPM/HSM interfaces, key storage.
- **Must NEVER:** Accept software-only validation when hardware anchoring is required, expose private key material, or degrade silently on cryptographic failure.

### PEE — Policy Enforcement Engine
- **Does:** Evaluates operator-defined policy rules against agent actions and produces enforcement decisions (allow, restrict, block).
- **Called by:** CAL during action evaluation.
- **Calls:** Policy store, VTZ boundary definitions.
- **Must NEVER:** Default to allow on policy lookup failure, suggest policy without enforcing it, or bypass VTZ constraints.

### MCP — MCP Policy Engine
- **Does:** Manages policy definition, distribution, and lifecycle for the platform.
- **Called by:** Administrative workflows, PEE for policy retrieval.
- **Calls:** Policy store, audit stream for policy change events.
- **Must NEVER:** Apply policy changes mid-session (changes take effect at next CTX-ID issuance), allow unauthenticated policy modification, or skip audit logging on policy changes.

### Rewind — Replay Engine
- **Does:** Reconstructs and replays agent sessions from the TrustFlow audit stream alone for forensic analysis and compliance verification.
- **Called by:** Administrative and compliance workflows.
- **Calls:** TrustFlow audit stream (read-only).
- **Must NEVER:** Require external state beyond the audit stream for replay, modify audit records, or expose secrets during replay.

### Connector SDK
- **Does:** Provides the integration SDK for connecting external systems and tools to the Crafted enforcement plane.
- **Called by:** Third-party integrations, tool providers.
- **Calls:** CAL for policy-gated tool invocation.
- **Must NEVER:** Bypass CAL enforcement, expose internal enforcement interfaces directly, or allow unauthenticated tool registration.

### tasklib (Validation Library)
- **Does:** A deliberately simple Python task management library that validates the Crafted Dev Agent build pipeline can close a complete dependency chain (docs → scaffold → model → storage → CLI).
- **Called by:** CI/CD pipeline validation, integration tests.
- **Calls:** Internal subpackages (model, storage, CLI).
- **Must NEVER:** Be treated as production infrastructure — it exists solely to prove the pipeline.

## Interface Contracts

### CTX-ID Wire Format
```
JWT-like token, signed with TrustLock agent key
Fields: session_id, ctx_id, vtz_binding, issued_at, expires_at, claims
```
- Tokens are immutable once issued.
- Rotation creates a new token; old token is invalidated immediately.
- Expired tokens must be rejected — clock skew tolerance is deployment-defined.
- Validate against TrustLock public key — software-only validation is rejected.
- Missing CTX-ID means UNTRUSTED — never infer identity.

### TrustFlow Event Schema
```
{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}
```
- `event_id`: globally unique, generated via CSPRNG (not sequential).
- `ts`: UTC Unix timestamp, millisecond precision.
- `payload_hash`: SHA-256 of serialized action payload.
- Emission is synchronous in the enforcement path.
- Failed emission is a WARN-level audit event — never a silent skip.

### VTZ Enforcement Decision
```
{ctx_id, tool_id, verdict: allow|restrict|block, reason}
```
- Every denial must produce a `VTZEnforcementDecision` record with `verdict=block`.
- Cross-VTZ tool calls require explicit policy authorization.
- Policy changes take effect at next CTX-ID issuance, not mid-session.

### DTL Label Wire Format
```
{label_id, classification, source_id, issued_at, sig}
```
- Labels assigned at ingestion are immutable.
- Derived data inherits the highest classification of any source.
- Label verification occurs before any trust boundary crossing.
- Label stripping is a security event — audited and policy-controlled.

### Audit Record Contract
- Generated BEFORE execution of security-relevant actions.
- Append-only — no modification or deletion permitted.
- Must NOT contain secrets, keys, tokens, or cleartext sensitive data.
- Audit failures are non-fatal to agent operation but must be surfaced immediately.
- Full session replay must be possible from the audit stream alone.

### Error Response Contract
- All errors must include: `component`, `operation`, `failure_reason`, `ctx_id` (if available).
- Error messages must NOT include: keys, tokens, secrets, or cleartext payloads.

## Error Handling Rules

### Fail-Closed Requirement
All failures involving trust, identity, policy, or cryptography must fail closed: reject the action, log the event, surface the failure to the caller. There is no exception to this rule.

### Per-Failure-Type Behavior
| Failure Type | Action |
|---|---|
| CTX-ID validation failure | Immediate rejection, no partial processing, log with component/operation/reason |
| CTX-ID missing | Treat as UNTRUSTED, reject, log |
| CTX-ID expired | Reject, log, include clock skew context |
| VTZ policy denial | Block action, emit `VTZEnforcementDecision` with `verdict=block`, emit TrustFlow event |
| VTZ cross-zone unauthorized | Deny, log, emit enforcement decision |
| TrustFlow emission failure | WARN-level audit event, surface failure — do NOT silently continue |
| DTL label missing | Treat data as CONFIDENTIAL, reject cross-boundary movement until labeled |
| DTL label verification failure | Block data movement, log, audit |
| Cryptographic operation failure | Fail closed, log (without key material), reject action |
| TrustLock key validation failure | Reject CTX-ID, fail closed |
| Policy lookup failure | Default to DENY, log, surface |
| Audit write failure | Non-fatal to agent operation, surface immediately, WARN-level event |
| External input validation failure | Reject input, log with sanitized context |

### Banned Patterns
- `try/except/pass` or any equivalent silent exception swallowing in enforcement code.
- Logging secrets, keys, tokens, or cleartext sensitive payloads in any error path.
- Returning partial results on validation failure.
- Defaulting to allow on any policy, trust, or identity failure.
- Catching broad exception types (e.g., bare `except Exception`) in enforcement paths without re-raising or explicit handling.
- Using sequential IDs for `event_id` or any security-critical identifier.

## Testing Requirements

### Coverage Rules
- Enforcement path test coverage must be >= 90%.
- Every enforcement path must have at least one negative test (what happens on rejection).
- Every cryptographic operation must have a test with invalid and expired material.
- Every TrustFlow emission must be tested for both success and failure paths.
- Every DTL label operation must be tested for missing, invalid, and cross-boundary scenarios.

### Mandatory Test Categories
- **Unit tests:** All security-critical logic, all parsing, all policy evaluation.
- **Integration tests:** Full enforcement chains (CTX-ID → VTZ → CAL → TrustFlow).
- **Negative-path tests:** Malformed inputs, expired tokens, invalid signatures, missing labels, cross-VTZ violations.
- **Regression tests:** Every material bug gets a regression test before the fix is merged.
- **Benchmark tests:** All network, crypto, policy evaluation, and telemetry hot paths.
- **Fuzz tests:** All parsers handling complex, attacker-controlled, or external input.

### Testing Constraints
- Do NOT mock the enforcement decision logic — mock external calls if needed but enforcement logic must execute.
- Tests must verify fail-closed behavior explicitly — assert that rejection occurred, not just that no exception was thrown.
- Tests must verify that TrustFlow events are emitted with correct schema on both allow and block paths.
- Tests for the tasklib validation library must prove the full dependency chain closes: docs → scaffold → model → storage → CLI.

### Test Directory Structure
Tests mirror `src/` structure exactly:
```
tests/cal/           - CAL enforcement tests
tests/dtl/           - DTL label tests
tests/trustflow/     - TrustFlow emission tests
tests/vtz/           - VTZ enforcement tests
tests/trustlock/     - TrustLock crypto tests
tests/mcp/           - MCP Policy Engine tests
tests/rewind/        - Rewind replay tests
tests/connector/     - Connector SDK tests
tests/tasklib/       - Pipeline validation tests
```

## File Naming and Directory Layout

```
src/
├── cal/              # Conversation Abstraction Layer — enforcement choke point
├── dtl/              # Data Trust Labels — classification and enforcement
├── trustflow/        # TrustFlow audit stream — event emission and storage
├── vtz/              # Virtual Trust Zone — boundary enforcement
├── trustlock/        # Cryptographic machine identity — TPM-anchored keys
├── mcp/              # MCP Policy Engine — policy lifecycle and distribution
├── rewind/           # Rewind replay engine — forensic reconstruction
sdk/
├── connector/        # Connector SDK — third-party integration
tests/
├── cal/
├── dtl/
├── trustflow/
├── vtz/
├── trustlock/
├── mcp/
├── rewind/
├── connector/
├── tasklib/
crafted-docs/         # Source TRDs and PRDs
crafted-standards/    # Synthesised architecture, interfaces, decisions
docs/                 # Branch-specific context
```

Each subsystem directory contains its components as individual files (e.g., `src/cal/cpf.py`, `src/cal/air.py`, `src/cal/ctx_id.py`, `src/cal/pee.py`). File names must be lowercase, snake_case, and descriptive of the component they implement.

## Security Checklist — Before Every Commit

- [ ] CTX-ID is validated at every enforcement entry point before any processing.
- [ ] TrustFlow event is emitted for every action outcome (allow, restrict, block).
- [ ] VTZ policy is checked before all cross-boundary operations.
- [ ] No silent failure paths exist in trust, identity, policy, or cryptographic code.
- [ ] No secrets, keys, tokens, or credentials appear in logs, error messages, or generated code.
- [ ] All external input is validated before use — no unchecked deserialization.
- [ ] All parsing is bounds-checked and fails safely on malformed input.
- [ ] DTL labels are verified before any data crosses a trust boundary.
- [ ] All cryptographic operations use FIPS 140-3 approved algorithms only.
- [ ] Fail-closed behavior is implemented for all trust/identity/policy/crypto failures.
- [ ] No `try/except/pass` or equivalent silent exception swallowing in enforcement paths.
- [ ] Error messages include component, operation, and failure reason — never secrets.
- [ ] Audit records are generated before execution of security-relevant actions.
- [ ] Test coverage includes at least one negative path per security boundary.
- [ ] No new dependencies added without justification for licensing, maintenance, CVE history, and transitive risk.

## Where to Find More Detail

- `crafted-docs/`        — source TRDs and PRDs (TRD-TASKLIB, Forge Architecture Context, and all future requirement documents)
- `crafted-standards/`   — synthesised architecture documents, interface specifications, and decision records
- `docs/`                — branch-specific context, build instructions, and operational documentation