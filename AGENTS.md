# AGENTS.md

Crafted Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack via cryptographic identity and operator-defined policy.

## How to Use This File

This file is the authoritative baseline for every coding session in this repository — read it completely before touching any code. For subsystem-specific detail, see `crafted-docs/` for the full TRDs and `crafted-standards/` for synthesised architecture, interface, and decision documents.

## Document Index

| Document Name | Type | Repo Path | What It Covers |
|---|---|---|---|
| TRD-TASKLIB | DOCX/MD | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Validation TRD for the Crafted Dev Agent pipeline; defines a simple Python task management library (tasklib) to prove the end-to-end dependency chain from docs → scaffold → model → storage → CLI |
| Forge Architecture Context | MD | `crafted-docs/forge_architecture_context.md` | Platform overview of Forge; defines all core subsystems (CAL, CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, VTZ, DTL, TrustLock, MCP, Rewind, Connector SDK) and their relationships, wire formats, and enforcement semantics |

## Critical Rules — Non-Negotiable

1. **Validate CTX-ID first at every enforcement entry point** — no partial processing may occur before CTX-ID validation succeeds.
2. **Reject expired, missing, or invalid CTX-ID tokens unconditionally** — never infer identity from context; missing CTX-ID means UNTRUSTED.
3. **Validate CTX-ID against the TrustLock public key** — software-only validation without TPM-anchored key verification is rejected.
4. **Check VTZ policy before execution of every agent action** — enforcement is structural, not advisory, and cannot be bypassed by application code.
5. **Deny cross-VTZ tool calls unless explicit policy authorization exists** — implicit cross-boundary access is denied by default.
6. **Emit a TrustFlow event for every action outcome (allow, restrict, block)** — emission is synchronous in the enforcement path; async buffering is prohibited.
7. **Fail closed on all trust, identity, policy, and cryptographic failures** — reject the action, log the event, surface to caller; never silently continue.
8. **Never include secrets, keys, tokens, or cleartext payloads in logs or error messages.**
9. **Treat all external input as untrusted** — validate strictly, bounds-check all parsing, fail safely on malformed input.
10. **Assign DTL labels at data ingestion; labels are immutable thereafter** — derived data inherits the highest classification of any source; unlabeled data is CONFIDENTIAL.
11. **Verify DTL labels before any data crosses a trust boundary** — label stripping is a security event that must be audited and policy-controlled.
12. **Generate an audit record before execution of every security-relevant action** — audit records are append-only, never modified or deleted.
13. **Use only FIPS 140-3 approved algorithms for all cryptographic operations** — do not invent cryptography; document all cryptographic design decisions.
14. **Ban `try/except/pass` (or equivalent swallowed exceptions) in all enforcement code paths.**
15. **Ensure every enforcement path has at least one negative test and achieve ≥90% test coverage on enforcement logic.**

## Architecture Overview

### CAL — Conversation Abstraction Layer
- **What it does:** Enforcement choke point for all agent-originated actions — no tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- **What calls it:** Application orchestration layers, agent runtimes, Connector SDK.
- **What it calls:** CTX-ID validation, VTZ enforcement, TrustFlow emission, PEE (Policy Evaluation Engine).
- **Must NEVER:** Allow any action to bypass policy evaluation, execute a tool call without a validated CTX-ID, or silently drop an enforcement decision.

### CPF — Conversation Plane Filter
- **What it does:** Intercepts and filters all conversation-plane traffic entering the CAL enforcement pipeline.
- **What calls it:** Inbound agent communication channels.
- **What it calls:** CAL enforcement pipeline.
- **Must NEVER:** Pass unvalidated or unfiltered input into the enforcement pipeline.

### AIR — Agent Interaction Record
- **What it does:** Structured record of every agent interaction that passes through CAL, providing forensic traceability.
- **What calls it:** CAL components after action processing.
- **What it calls:** TrustFlow for audit emission.
- **Must NEVER:** Omit any enforcement decision or contain secrets in its records.

### CTX-ID — Contextual Identity Token
- **What it does:** Cryptographic identity token binding an agent session to a verified machine identity and VTZ; JWT-like, signed with TrustLock agent key; fields include session, identity, VTZ binding, and expiry.
- **What calls it:** CAL at every enforcement entry point, VTZ at session binding.
- **What it calls:** TrustLock for key verification.
- **Must NEVER:** Be modified after issuance (immutable), be accepted after expiry, or be validated without TrustLock public key verification.

### VTZ — Virtual Trust Zone
- **What it does:** Defines and enforces structural boundaries around agent execution scope; every agent session is bound to exactly one VTZ at CTX-ID issuance.
- **What calls it:** CAL before any action execution, CTX-ID at session binding.
- **What it calls:** Policy store for authorization decisions.
- **Must NEVER:** Allow implicit cross-boundary access, permit policy bypass by application code, or apply policy changes mid-session (changes take effect at next CTX-ID issuance).

### PEE — Policy Evaluation Engine
- **What it does:** Evaluates operator-defined policy against agent actions and produces enforcement verdicts (allow, restrict, block).
- **What calls it:** CAL during action processing.
- **What it calls:** VTZ policy store, DTL label store.
- **Must NEVER:** Return an ambiguous verdict, default to allow on evaluation failure, or execute without a valid policy context.

### TrustFlow / SIS — Audit Stream
- **What it does:** Immutable, append-only audit stream capturing every enforcement decision with event_id, session_id, ctx_id, ts, event_type, payload_hash, and signature.
- **What calls it:** CAL after every enforcement decision, all security-relevant components.
- **What it calls:** Audit storage backend.
- **Must NEVER:** Allow modification or deletion of records, emit events without globally unique CSPRNG event_ids, use non-UTC timestamps, or silently skip emission failures.

### DTL — Data Trust Labels
- **What it does:** Classification labels assigned at data ingestion that govern data handling across trust boundaries; wire format: {label_id, classification, source_id, issued_at, sig}.
- **What calls it:** Data ingestion paths, trust boundary crossings.
- **What it calls:** Label verification at boundary enforcement.
- **Must NEVER:** Allow label mutation after assignment, permit unlabeled data to be treated as non-confidential, or allow label stripping without audit.

### TrustLock — Cryptographic Machine Identity
- **What it does:** TPM-anchored cryptographic identity providing key generation, storage, rotation, and destruction for machine and agent identity verification.
- **What calls it:** CTX-ID for token signing and validation, TrustFlow for event signing.
- **What it calls:** Hardware TPM / secure key storage.
- **Must NEVER:** Expose private key material, fall back to software-only validation, use non-FIPS-approved algorithms, or degrade silently on cryptographic failure.

### MCP — MCP Policy Engine
- **What it does:** Manages and distributes operator-defined policies governing agent behavior across the Forge platform.
- **What calls it:** PEE for policy retrieval, administrative workflows.
- **What it calls:** Policy storage, VTZ configuration.
- **Must NEVER:** Apply policy changes to active sessions, distribute unsigned policies, or allow unauthorized policy modification.

### Rewind — Replay Engine
- **What it does:** Enables forensic replay of agent sessions from the TrustFlow audit stream alone, without requiring external state.
- **What calls it:** Administrative and audit workflows.
- **What it calls:** TrustFlow audit stream.
- **Must NEVER:** Require state beyond the audit stream for replay, modify audit records during replay, or expose secrets during reconstruction.

### Connector SDK
- **What it does:** SDK enabling third-party integrations to connect to the Forge enforcement platform while preserving all enforcement guarantees.
- **What calls it:** External applications and agent frameworks.
- **What it calls:** CAL enforcement pipeline.
- **Must NEVER:** Provide a path that bypasses CAL enforcement, expose internal enforcement internals, or weaken trust guarantees at the integration boundary.

### tasklib — Validation Library (TRD-TASKLIB)
- **What it does:** Deliberately simple Python task management library validating the Crafted Dev Agent build pipeline end-to-end (docs → scaffold → model → storage → CLI).
- **What calls it:** CI/CD pipeline validation, developer testing.
- **What it calls:** Internal subpackages (model, storage, CLI).
- **Must NEVER:** Be treated as production infrastructure — it exists solely to prove the dependency chain closes correctly.

## Interface Contracts

### CTX-ID Contract
- CTX-ID tokens are **immutable** once issued — no field modification after issuance.
- Rotation creates a new token; the old one is invalidated immediately.
- Expired CTX-ID must be rejected — clock skew tolerance is defined per deployment.
- Validate against TrustLock public key — software-only validation is rejected.
- Missing CTX-ID must be treated as UNTRUSTED — never infer identity from context.

### VTZ Enforcement Contract
- Every agent session is bound to exactly one VTZ at CTX-ID issuance.
- Cross-VTZ tool calls require explicit policy authorization — implicit is denied.
- VTZ boundaries are structural, not advisory — enforcement cannot be bypassed by application code.
- VTZ policy changes take effect at next CTX-ID issuance, not mid-session.
- Every VTZ policy denial must produce a `VTZEnforcementDecision` record: `{ctx_id, tool_id, verdict: allow|restrict|block, reason}`.

### TrustFlow Emission Contract
- Every TrustFlow event must include: `event_id`, `session_id`, `ctx_id`, `ts`, `event_type`, `payload_hash`.
- `event_id` must be globally unique (CSPRNG, not sequential).
- `ts` must be UTC Unix timestamp with millisecond precision.
- `payload_hash` must be SHA-256 of the serialized action payload.
- Emission must be **synchronous** in the enforcement path — async buffering is not permitted.
- Failed emission is a WARN-level audit event — never a silent skip.

### DTL Label Contract
- Labels are assigned at **data ingestion** and are immutable thereafter.
- Derived data inherits the **highest classification** of any source.
- Unlabeled data must be treated as **CONFIDENTIAL** until explicitly reclassified.
- Label verification must occur before any data crosses a trust boundary.
- Label stripping is a security event that must be audited and policy-controlled.
- Wire format: `{label_id, classification, source_id, issued_at, sig}`.

### CAL Enforcement Contract
- Every entry point that processes an agent action must call CTX-ID validation **first**.
- CTX-ID validation failure results in **immediate rejection** — no partial processing.
- Every action must be checked against VTZ policy **before** execution.
- Every action outcome (allow, restrict, block) must emit a TrustFlow event.
- TrustFlow emission failure must not silently continue — log and surface the failure.

### Audit Contract
- Every security-relevant action must generate an audit record **before** execution.
- Audit records are **append-only** — no modification or deletion.
- Audit failures are non-fatal to agent operation but must be surfaced immediately.
- Audit records must not contain secrets, keys, tokens, or cleartext sensitive data.
- Replay must be possible from the audit stream alone (no external state required).

## Error Handling Rules

### Fail-Closed Requirement
- All trust, identity, policy, and cryptographic failures **must fail closed**: reject the action, log the event, surface to the caller.
- Never silently continue after an enforcement failure.

### Required Error Fields
- Every error must include: `component`, `operation`, `failure_reason`, `ctx_id` (if available).
- Every error must **exclude**: keys, tokens, secrets, cleartext payloads.

### Banned Patterns
- `try/except/pass` (or language equivalent) is **banned** in all enforcement code paths.
- Silent exception swallowing in any trust, crypto, or policy path is **banned**.
- Logging an error and then proceeding as if it succeeded is **banned**.
- Returning a default "allow" on policy evaluation failure is **banned**.
- Degrading to software-only crypto on hardware failure without explicit audit is **banned**.

### Failure Type Responses
| Failure Type | Response |
|---|---|
| CTX-ID validation failure | Reject immediately, emit TrustFlow block event, return error to caller |
| CTX-ID expired | Reject immediately, require re-issuance |
| CTX-ID missing | Treat as UNTRUSTED, reject, log |
| VTZ policy denial | Block execution, produce VTZEnforcementDecision with verdict=block, emit TrustFlow event |
| Cross-VTZ unauthorized | Deny, log attempted boundary crossing, emit audit event |
| TrustFlow emission failure | WARN-level audit event, surface to caller, do not silently skip |
| Cryptographic verification failure | Fail closed, reject action, log without exposing key material |
| DTL label missing | Treat data as CONFIDENTIAL, enforce accordingly |
| DTL label verification failure at boundary | Block data crossing, audit the event |
| Audit system failure | Non-fatal to agent operation, surface immediately, continue with degraded observability warning |
| Policy evaluation error | Fail closed — deny the action, never default to allow |

## Testing Requirements

### Coverage Rules
- Enforcement path test coverage must be **≥90%**.
- Every enforcement path must have at least one **negative test** (what happens on rejection/failure).
- Every cryptographic operation must have a test with **invalid and expired material**.
- Every TrustFlow emission must be tested for both **success and failure** paths.

### Mandatory Test Categories
- **Unit tests:** All security-critical logic, all parsing, all policy evaluation, all cryptographic operations.
- **Integration tests:** Full enforcement chains from CAL entry through VTZ check through TrustFlow emission.
- **Negative-path tests:** Malformed CTX-ID, expired tokens, invalid signatures, unauthorized cross-VTZ calls, missing DTL labels, corrupted policy.
- **Benchmark tests:** All network, crypto, policy evaluation, and telemetry hot paths.
- **Regression tests:** Every material bug gets a regression test before close.
- **Fuzz tests:** All parser-driven, attacker-controlled, or complex input paths.

### Test Integrity Rules
- Tests must **not** mock the enforcement decision logic — mock the external call but let the enforcement logic run.
- Tests must validate **failure behavior**, not just success behavior.
- Tests must mirror `src/` structure exactly under `tests/`.

### tasklib Validation Tests (TRD-TASKLIB)
- Validate that the documentation PR fires the merge gate and downstream PRs recognize the merge.
- Validate that the scaffold PR mirrors files to the local test workspace.
- Validate that code PRs importing from previously-merged PRs resolve imports locally before CI.
- Validate the full dependency chain closes: docs → scaffold → model → storage → CLI.

## File Naming and Directory Layout

```
src/
  cal/                 # Conversation Abstraction Layer (CPF, AIR, PEE, CAL Verifier Cluster)
  dtl/                 # Data Trust Label components
  trustflow/           # TrustFlow / SIS audit stream components
  vtz/                 # Virtual Trust Zone enforcement
  trustlock/           # Cryptographic machine identity (TPM-anchored)
  mcp/                 # MCP Policy Engine
  rewind/              # Crafted Rewind replay engine

sdk/
  connector/           # Crafted Connector SDK

tests/
  cal/                 # Tests for CAL — mirrors src/cal/ structure exactly
  dtl/                 # Tests for DTL — mirrors src/dtl/ structure exactly
  trustflow/           # Tests for TrustFlow — mirrors src/trustflow/ structure exactly
  vtz/                 # Tests for VTZ — mirrors src/vtz/ structure exactly
  trustlock/           # Tests for TrustLock — mirrors src/trustlock/ structure exactly
  mcp/                 # Tests for MCP — mirrors src/mcp/ structure exactly
  rewind/              # Tests for Rewind — mirrors src/rewind/ structure exactly

crafted-docs/          # Source TRDs and PRDs
crafted-standards/     # Synthesised architecture, interfaces, decisions
docs/                  # Branch-specific context and generated documentation
```

## Security Checklist — Before Every Commit

- [ ] CTX-ID is validated at every enforcement entry point before any processing occurs.
- [ ] TrustFlow event is emitted for every action outcome (allow, restrict, block).
- [ ] VTZ policy is checked before every cross-boundary operation.
- [ ] No silent failure paths exist in trust, crypto, or policy code.
- [ ] No secrets, keys, tokens, or credentials appear in logs, error messages, or generated code.
- [ ] All external input is validated before use — bounds-checked, type-checked, fail-safe on malformed input.
- [ ] Test coverage includes at least one negative path per security boundary.
- [ ] FIPS-approved algorithms are used for all cryptographic operations.
- [ ] DTL labels are verified before any data crosses a trust boundary.
- [ ] Audit records are generated before execution of security-relevant actions.
- [ ] No `try/except/pass` or equivalent silent exception swallowing in enforcement paths.
- [ ] Error messages include component, operation, and failure_reason — never secrets.
- [ ] Dependencies added are justified, reviewed for CVE history, and minimize transitive chains.
- [ ] All cryptographic material paths (generation, storage, rotation, destruction) are defined.
- [ ] No TODO items remain in security-critical or runtime-critical code without a tracked issue.

## Where to Find More Detail

- `crafted-docs/`        — Source TRDs and PRDs (TRD-TASKLIB, Forge Architecture Context, and all future specifications)
- `crafted-standards/`   — Synthesised architecture documents, interface contracts, and decision records
- `docs/`                — Branch-specific context, generated documentation, and operational guides