# AGENTS.md

Crafted Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack via cryptographic identity, operator-defined policy, and auditable trust boundaries.

## How to Use This File

This file is the authoritative baseline for every coding session in this repository — read it fully before touching any code. For subsystem-specific detail, see `crafted-docs/` for the full TRDs and PRDs, and `crafted-standards/` for synthesised architecture, interface, and decision documents.

## Document Index

| Document Name | Type | Repo Path | What It Covers |
|---|---|---|---|
| TRD-TASKLIB | DOCX/MD | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Validation TRD for Crafted Dev Agent pipeline — defines a simple Python task management library to prove the full dependency chain (docs → scaffold → model → storage → CLI) closes end-to-end with real merges |
| Forge Architecture Context | MD | `crafted-docs/forge_architecture_context.md` | Platform overview of Forge subsystems: CAL, CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, VTZ, DTL, TrustLock, MCP, CAL Verifier Cluster — injected into every code generation prompt |

## Critical Rules — Non-Negotiable

1. **Never infer trust implicitly** — always assert and verify identity explicitly through CTX-ID validation backed by TrustLock public key; software-only validation is rejected.
2. **Validate CTX-ID at every enforcement entry point FIRST** — CTX-ID validation failure must result in immediate rejection with zero partial processing.
3. **Check VTZ policy BEFORE execution of any agent action** — VTZ boundaries are structural, not advisory; enforcement cannot be bypassed by application code.
4. **Emit a TrustFlow event for every action outcome (allow, restrict, block)** — emission must be synchronous in the enforcement path; async buffering is prohibited.
5. **Fail closed on every trust, identity, policy, or cryptographic failure** — reject the action, log the event, surface to caller; never silently continue.
6. **Never expose secrets, keys, tokens, or cleartext payloads in logs, error messages, or generated code** — all error messages must include component, operation, failure_reason, and ctx_id (if available) only.
7. **Treat all external input as untrusted** — validate strictly, bounds-check all parsing, and fail safely on malformed input.
8. **Assign DTL labels at data ingestion; labels are immutable thereafter** — derived data inherits the highest classification of any source; unlabeled data is CONFIDENTIAL until explicitly reclassified.
9. **Use only FIPS 140-3 validated cryptographic primitives** — do not invent cryptography; document all cryptographic design decisions.
10. **Generate audit records BEFORE execution of every security-relevant action** — audit records are append-only, never modified or deleted, and must never contain secrets or cleartext sensitive data.
11. **Ban `try/except/pass` (or equivalent silent swallowing) in all enforcement code paths** — no silent failure paths anywhere in trust, crypto, or policy code.
12. **Bind every agent session to exactly one VTZ at CTX-ID issuance** — cross-VTZ tool calls require explicit policy authorization; implicit cross-VTZ access is denied.
13. **CTX-ID tokens are immutable once issued** — rotation creates a new token and invalidates the old one immediately; expired CTX-IDs are always rejected.
14. **Verify DTL labels before any data crosses a trust boundary** — label stripping is a security event that must be audited and policy-controlled.
15. **Maintain ≥ 90% test coverage on all enforcement paths** — every enforcement path must have at least one negative test; tests must not mock the enforcement decision logic.

## Architecture Overview

### CAL — Conversation Abstraction Layer
- **What it does:** Enforcement choke point for all agent-originated actions — no tool call, data read, API invocation, or agent handoff executes without passing through a CAL policy evaluation.
- **What calls it:** Application orchestration layers, agent runtimes, MCP engine.
- **What it calls:** CTX-ID validation, VTZ enforcement, TrustFlow emission, PEE, DTL label verification.
- **Must NEVER:** Allow any action to bypass policy evaluation, execute partially on CTX-ID failure, or suppress TrustFlow emission.

### CPF — Conversation Plane Filter
- **What it does:** Filters and intercepts conversation-level traffic at the CAL boundary, routing actions to the appropriate policy evaluation path.
- **What calls it:** CAL entry points.
- **What it calls:** AIR, PEE, VTZ policy lookup.
- **Must NEVER:** Pass through unfiltered actions or allow conversation traffic to skip policy classification.

### AIR — Action Interception and Routing
- **What it does:** Intercepts agent-originated actions and routes them to the correct enforcement pipeline within CAL.
- **What calls it:** CPF.
- **What it calls:** PEE, CTX-ID validation.
- **Must NEVER:** Route actions without prior CTX-ID validation or silently drop intercepted actions.

### CTX-ID — Cryptographic Context Identity
- **What it does:** Provides immutable, cryptographically signed identity tokens binding an agent session to a machine, user, and VTZ at issuance time.
- **What calls it:** CAL (at every enforcement entry point), VTZ enforcement, TrustFlow emission.
- **What it calls:** TrustLock (for key-backed validation).
- **Must NEVER:** Allow modification after issuance, validate without TrustLock public key, or infer identity from ambient context when CTX-ID is missing.

### PEE — Policy Evaluation Engine
- **What it does:** Evaluates operator-defined policy against the current action, CTX-ID, and VTZ context to produce allow/restrict/block verdicts.
- **What calls it:** CAL, AIR, CPF.
- **What it calls:** VTZ policy store, DTL label checks.
- **Must NEVER:** Return a default-allow on evaluation failure, or apply policy changes mid-session (changes take effect at next CTX-ID issuance).

### VTZ — Virtual Trust Zone
- **What it does:** Defines and enforces structural trust boundaries around agent sessions — each session is bound to exactly one VTZ; cross-VTZ access requires explicit policy authorization.
- **What calls it:** CAL, PEE, CTX-ID issuance.
- **What it calls:** DTL label verification, policy store.
- **Must NEVER:** Allow implicit cross-VTZ access, treat boundaries as advisory, or permit application code to bypass enforcement.

### TrustFlow / SIS — Audit Stream
- **What it does:** Emits immutable, cryptographically linked audit events for every action outcome, supporting forensic reconstruction and compliance replay.
- **What calls it:** CAL (synchronously on every action outcome).
- **What it calls:** Audit storage (append-only).
- **Must NEVER:** Buffer events asynchronously in the enforcement path, silently skip emission on failure, or include secrets/keys/tokens in event payloads.

### DTL — Data Trust Labels
- **What it does:** Assigns immutable classification labels to data at ingestion; enforces label inheritance (derived data inherits highest source classification) and verifies labels at trust boundary crossings.
- **What calls it:** VTZ enforcement, CAL, any data ingestion or cross-boundary operation.
- **What it calls:** Label store, audit (for label stripping events).
- **Must NEVER:** Allow label modification after assignment, permit unlabeled data to be treated as public, or strip labels without audited policy authorization.

### TrustLock — Cryptographic Machine Identity
- **What it does:** Provides TPM-anchored cryptographic identity for machines and agents — key generation, storage, rotation, destruction, and recovery.
- **What calls it:** CTX-ID validation, TrustFlow event signing.
- **What it calls:** TPM/HSM hardware, CSPRNG sources.
- **Must NEVER:** Expose private key material, fall back to software-only validation when hardware is expected, or degrade silently on cryptographic failure.

### MCP — MCP Policy Engine
- **What it does:** Manages and distributes operator-defined policies that govern agent behavior across the platform.
- **What calls it:** PEE, administrative workflows.
- **What it calls:** Policy store, VTZ configuration.
- **Must NEVER:** Apply policy changes mid-session, allow unauthenticated policy modification, or distribute policy without audit logging.

### Crafted Rewind — Replay Engine
- **What it does:** Replays agent sessions from the TrustFlow audit stream alone, enabling forensic analysis and compliance review.
- **What calls it:** Administrative/compliance workflows.
- **What it calls:** TrustFlow audit store (read-only).
- **Must NEVER:** Require external state beyond the audit stream for replay, modify audit records, or expose secrets during replay.

### Crafted Connector SDK
- **What it does:** Provides the integration SDK for connecting external systems to the Forge enforcement platform.
- **What calls it:** Third-party integrators, application developers.
- **What it calls:** CAL entry points, CTX-ID issuance.
- **Must NEVER:** Bypass CAL enforcement, issue CTX-IDs without TrustLock validation, or expose internal enforcement interfaces.

### tasklib (Validation Library — TRD-TASKLIB)
- **What it does:** A deliberately simple Python task management library that validates the Crafted Dev Agent build pipeline can close a complete dependency chain (docs → scaffold → model → storage → CLI).
- **What calls it:** CI/CD pipeline, merge gates.
- **What it calls:** Internal subpackages (model, storage, CLI).
- **Must NEVER:** Be treated as a production system — it exists solely to validate the build pipeline end-to-end.

## Interface Contracts

### CTX-ID Wire Format
- JWT-like token, signed with TrustLock agent key.
- CTX-ID tokens are **immutable** once issued — no field modification after issuance.
- Rotation creates a new token; old token is invalidated immediately.
- Expired CTX-ID must be rejected — clock skew tolerance is defined per deployment.
- Validation must be against TrustLock public key — software-only validation is rejected.
- Missing CTX-ID must be treated as **UNTRUSTED** — never infer identity from context.

### TrustFlow Event Schema
```
{
  event_id: <globally unique, CSPRNG-generated>,
  session_id: <string>,
  ctx_id: <string>,
  ts: <UTC Unix timestamp, millisecond precision>,
  event_type: <string>,
  payload_hash: <SHA-256 of serialized action payload>,
  sig: <TrustLock signature>
}
```
- `event_id` must be globally unique via CSPRNG — sequential IDs are prohibited.
- Emission must be synchronous in the enforcement path.
- Failed emission is a WARN-level audit event — never a silent skip.

### DTL Label Wire Format
```
{
  label_id: <string>,
  classification: <string>,
  source_id: <string>,
  issued_at: <timestamp>,
  sig: <signature>
}
```
- Labels are assigned at data ingestion and are immutable.
- Derived data inherits the **highest** classification of any source.
- Unlabeled data is treated as **CONFIDENTIAL** until explicitly reclassified.
- Label verification must occur before any data crosses a trust boundary.

### VTZ Enforcement Decision
```
{
  ctx_id: <string>,
  tool_id: <string>,
  verdict: allow | restrict | block,
  reason: <string>
}
```
- Every agent session is bound to exactly **one** VTZ at CTX-ID issuance.
- Cross-VTZ tool calls require explicit policy authorization — implicit is denied.
- VTZ policy changes take effect at next CTX-ID issuance, not mid-session.
- VTZ policy denial must produce a VTZEnforcementDecision record with `verdict=block`.

### CAL Enforcement Sequence (Mandatory Order)
1. Validate CTX-ID (reject immediately on failure).
2. Check VTZ policy (produce VTZEnforcementDecision).
3. Execute or block action based on verdict.
4. Emit TrustFlow event with outcome.
5. If TrustFlow emission fails: log WARN-level audit event, surface failure — do not silently continue.

## Error Handling Rules

### Fail-Closed Requirement
All failures involving trust, identity, policy, or cryptography **must fail closed**: reject the action, log the event, surface the failure to the caller. There is no exception to this rule.

### Mandatory Error Fields
Every error must include: `component`, `operation`, `failure_reason`, `ctx_id` (if available).

### Banned Patterns
- `try/except/pass` (or any language equivalent that silently swallows exceptions) in enforcement code — **BANNED**.
- Returning default-allow on policy evaluation failure — **BANNED**.
- Logging secrets, keys, tokens, or cleartext payloads in error messages — **BANNED**.
- Silent degradation from cryptographic enforcement to insecure behavior — **BANNED**.
- Async buffering of TrustFlow events in the enforcement path — **BANNED**.

### Failure Type Handling

| Failure Type | Action |
|---|---|
| CTX-ID validation failure | Reject immediately, log event, return error to caller |
| CTX-ID expired | Reject, log, require re-issuance |
| CTX-ID missing | Treat as UNTRUSTED, reject, log |
| VTZ policy denial | Block action, produce VTZEnforcementDecision with `verdict=block`, emit TrustFlow event |
| Cross-VTZ access without explicit authorization | Deny, log, emit TrustFlow event |
| TrustFlow emission failure | Log WARN-level audit event, surface failure — do NOT silently continue |
| Audit record write failure | Non-fatal to agent operation but surface immediately, log escalation |
| Cryptographic operation failure | Fail closed, reject action, log (no key material in log) |
| DTL label missing | Treat data as CONFIDENTIAL, log |
| DTL label verification failure at trust boundary | Block data crossing, log, audit |
| External input validation failure | Reject input, log, return structured error |

## Testing Requirements

### Coverage Rules
- Enforcement path test coverage must be **≥ 90%**.
- Every security-critical logic path must have unit, integration, and negative-path tests.

### Mandatory Negative Tests
- Every enforcement path must have at least one negative test (what happens on rejection).
- Every cryptographic operation must have a test with invalid/expired material.
- Every TrustFlow emission must be tested for both success and failure paths.
- All parsing, policy, trust, and cryptographic logic must be tested against malformed inputs.

### Test Integrity Rules
- Tests **must not** mock the enforcement decision logic — they may mock external calls, but the enforcement logic itself must execute.
- Test for failure behavior, not just success behavior.
- Add regression tests for every material bug.

### Benchmark and Fuzz Requirements
- Benchmark tests must exist for all performance-sensitive paths: network, crypto, policy evaluation, telemetry.
- Fuzzing must be used where inputs are complex, attacker-controlled, or parser-driven.

### tasklib Validation (TRD-TASKLIB Specific)
- Validate that a documentation PR fires the merge gate and downstream PRs recognize the merge.
- Validate that scaffold PRs with multiple package directories mirror files to the local test workspace.
- Validate that code PRs importing from previously-merged PRs resolve imports locally before CI.
- Validate the full dependency chain closes: docs → scaffold → model → storage → CLI.

## File Naming and Directory Layout

```
src/
  cal/                  # Conversation Abstraction Layer (CPF, AIR, PEE, CAL Verifier Cluster)
  dtl/                  # Data Trust Label components
  trustflow/            # TrustFlow / SIS audit stream components
  vtz/                  # Virtual Trust Zone enforcement
  trustlock/            # Cryptographic machine identity (TPM-anchored)
  mcp/                  # MCP Policy Engine
  rewind/               # Crafted Rewind replay engine

sdk/
  connector/            # Crafted Connector SDK

tests/
  cal/                  # Tests for CAL — mirrors src/cal/ structure exactly
  dtl/                  # Tests for DTL — mirrors src/dtl/ structure exactly
  trustflow/            # Tests for TrustFlow — mirrors src/trustflow/ exactly
  vtz/                  # Tests for VTZ — mirrors src/vtz/ exactly
  trustlock/            # Tests for TrustLock — mirrors src/trustlock/ exactly
  mcp/                  # Tests for MCP — mirrors src/mcp/ exactly
  rewind/               # Tests for Rewind — mirrors src/rewind/ exactly

crafted-docs/           # Source TRDs and PRDs
crafted-standards/      # Synthesised architecture, interface, and decision documents
docs/                   # Branch-specific context and generated documentation
```

Python source files use `.py` extension. Go source files use `.go` extension. File naming within each subsystem directory matches the component name (e.g., `src/cal/cpf.py`, `src/trustflow/emitter.py`).

## Security Checklist — Before Every Commit

- [ ] CTX-ID is validated at every enforcement entry point — no exceptions.
- [ ] TrustFlow event is emitted for every action outcome (allow, restrict, block).
- [ ] VTZ policy is checked before any cross-boundary operation.
- [ ] No silent failure paths exist in trust, crypto, or policy code.
- [ ] No secrets, keys, tokens, or cleartext payloads appear in logs or error messages.
- [ ] All external input is validated before use — no trusting of caller-provided data.
- [ ] All cryptographic operations use FIPS-approved algorithms only.
- [ ] DTL labels are verified before data crosses any trust boundary.
- [ ] Audit records are generated before execution of security-relevant actions.
- [ ] Test coverage includes at least one negative path per security boundary.
- [ ] No `try/except/pass` or equivalent silent exception swallowing in enforcement code.
- [ ] No hardcoded secrets, tokens, credentials, or cryptographic material anywhere.
- [ ] Error messages include component, operation, failure_reason, ctx_id — nothing more sensitive.
- [ ] All new dependencies are justified, reviewed for CVE history, and minimal in scope.
- [ ] AI-generated code meets the same review, traceability, and documentation standards as human-written code.

## Where to Find More Detail

- **`crafted-docs/`** — Source TRDs and PRDs (TRD-TASKLIB, Forge Architecture Context, and all future design documents).
- **`crafted-standards/`** — Synthesised architecture documents, interface specifications, and decision records.
- **`docs/`** — Branch-specific context, generated documentation, and operational guides.