# CLAUDE.md

Crafted Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack via cryptographic identity (TrustLock/CTX-ID) and operator-defined policy (VTZ), with an end-to-end validated build pipeline proven through the tasklib dependency chain.

## How to Use This File

This file is the authoritative baseline for every LLM coding session in this repository — read it completely before touching any code. For subsystem-specific detail, see `crafted-docs/` for the full TRDs and PRDs, and `crafted-standards/` for synthesised architecture, interface, and decision records.

## Document Index

| Document Name | Type | Repo Path | What It Covers |
|---|---|---|---|
| TRD-TASKLIB | DOCX/MD | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Validation TRD for the Crafted Dev Agent build pipeline; defines a Python task management library (tasklib) that proves the full dependency chain (docs → scaffold → model → storage → CLI) with real merges at each step |
| Forge Architecture Context | MD | `crafted-docs/forge_architecture_context.md` | Platform overview of Forge runtime enforcement; defines core subsystems (CAL, CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, VTZ, DTL, TrustLock, MCP, Rewind, Connector SDK) and their relationships, wire formats, and enforcement invariants |

## Critical Rules — Non-Negotiable

1. Validate CTX-ID at every enforcement entry point FIRST — before any processing occurs.
2. Reject any request with a missing, expired, or invalid CTX-ID immediately; never infer identity from context.
3. Check VTZ policy BEFORE execution of every agent action; implicit cross-VTZ access is always denied.
4. Emit a TrustFlow event for every action outcome (allow, restrict, block) synchronously in the enforcement path — async buffering is forbidden.
5. Fail closed on all trust, identity, policy, and cryptographic failures — reject the action, log the event, surface to caller.
6. Never log, emit in error messages, or include in generated code any secrets, keys, tokens, credentials, or cleartext sensitive payloads.
7. Treat all external input as untrusted; validate strictly, bounds-check all parsing, and fail safely on malformed input.
8. Assign DTL labels at data ingestion; labels are immutable, derived data inherits the highest classification of any source, and unlabeled data is treated as CONFIDENTIAL.
9. CTX-ID tokens are immutable once issued — rotation creates a new token and immediately invalidates the old one.
10. VTZ boundaries are structural and enforced — application code cannot bypass them; policy changes take effect at next CTX-ID issuance, not mid-session.
11. Use only FIPS 140-3 approved cryptographic primitives; never invent cryptography or degrade silently to insecure behavior.
12. Generate an audit record BEFORE execution of every security-relevant action; audit records are append-only and must support full replay without external state.
13. Never swallow exceptions in enforcement paths — `try/except/pass` is banned in all trust, identity, policy, and cryptographic code.
14. Every TrustFlow event must include: `event_id` (CSPRNG-generated), `session_id`, `ctx_id`, `ts` (UTC Unix ms), `event_type`, `payload_hash` (SHA-256), `sig`.
15. The tasklib validation pipeline must close the full dependency chain (docs → scaffold → model → storage → CLI) with real merges — no step may be skipped or simulated.

## Architecture Overview

### CAL — Conversation Abstraction Layer
- **What it does:** Enforcement choke point for all agent-originated actions; no tool call, data read, API invocation, or agent handoff executes without passing CAL policy evaluation.
- **What calls it:** Application orchestration layers, agent runtimes, MCP Policy Engine.
- **What it calls:** CTX-ID validation, VTZ enforcement, TrustFlow emission, DTL label verification.
- **Must NEVER:** Allow any action to bypass policy evaluation, execute partially on CTX-ID failure, or silently drop enforcement decisions.

### CPF — Conversation Plane Filter
- **What it does:** Intercepts and filters agent conversation traffic at the transport layer before it reaches CAL evaluation.
- **What calls it:** Inbound agent communication channels.
- **What it calls:** CAL enforcement pipeline.
- **Must NEVER:** Pass unvalidated or unfiltered traffic to CAL, modify message content without audit, or silently discard messages.

### CTX-ID — Contextual Identity Token
- **What it does:** Cryptographic session identity token (JWT-like, signed with TrustLock agent key) binding an agent session to a verified identity and a single VTZ.
- **What calls it:** CAL at every enforcement entry point; any component that needs identity assertion.
- **What it calls:** TrustLock for key validation and signature verification.
- **Must NEVER:** Be modified after issuance, be validated with software-only keys (requires TrustLock public key), or be implicitly trusted when missing or expired.

### VTZ — Virtual Trust Zones
- **What it does:** Structural policy enforcement boundaries; each agent session is bound to exactly one VTZ at CTX-ID issuance.
- **What calls it:** CAL/PEE before every action execution; CTX-ID issuance logic.
- **What it calls:** Policy store for rule evaluation; emits VTZEnforcementDecision records.
- **Must NEVER:** Allow implicit cross-VTZ access, apply policy changes mid-session, or be treated as advisory.

### TrustFlow / SIS — Security Information Stream
- **What it does:** Immutable audit event stream recording every action outcome with cryptographic integrity.
- **What calls it:** CAL after every enforcement decision; any security-relevant component.
- **What it calls:** Audit storage; Rewind replay engine.
- **Must NEVER:** Buffer events asynchronously in the enforcement path, silently skip failed emissions, or include secrets/keys/tokens in event payloads.

### DTL — Data Trust Labels
- **What it does:** Classifies data at ingestion with immutable labels; enforces label inheritance and verification at trust boundaries.
- **What calls it:** Data ingestion pipelines; CAL before cross-boundary data operations.
- **What it calls:** Label store; audit stream for label-stripping events.
- **Must NEVER:** Allow label modification after assignment, permit unlabeled data to be treated as non-confidential, or strip labels without auditing.

### TrustLock — Cryptographic Machine Identity
- **What it does:** TPM-anchored cryptographic identity for machines and agents; provides key generation, storage, rotation, destruction, and signature verification.
- **What calls it:** CTX-ID issuance and validation; any component requiring cryptographic identity assertion.
- **What it calls:** TPM/hardware security modules; approved CSPRNG sources.
- **Must NEVER:** Expose private key material, use non-FIPS-approved algorithms, or fall back to software-only key storage when hardware is available.

### PEE — Policy Evaluation Engine
- **What it does:** Evaluates operator-defined policy rules against agent actions within CAL.
- **What calls it:** CAL enforcement pipeline.
- **What it calls:** VTZ policy store; DTL label verification; emits TrustFlow events.
- **Must NEVER:** Suggest policy (must enforce), allow unevaluated actions to proceed, or cache stale policy across CTX-ID boundaries.

### MCP — MCP Policy Engine
- **What it does:** Policy engine for MCP (Model Context Protocol) tool call governance.
- **What calls it:** CAL for MCP-specific tool invocations.
- **What it calls:** VTZ enforcement; TrustFlow emission.
- **Must NEVER:** Allow ungoverned tool calls, bypass VTZ boundaries, or execute without CTX-ID validation.

### Rewind — Crafted Rewind Replay Engine
- **What it does:** Deterministic replay of agent sessions from the TrustFlow audit stream alone.
- **What calls it:** Forensic analysis tools; compliance workflows.
- **What it calls:** TrustFlow event store (read-only).
- **Must NEVER:** Require external state beyond the audit stream for replay, modify audit records, or replay with elevated privileges.

### Connector SDK — Crafted Connector SDK
- **What it does:** SDK for integrating third-party tools and services into the Crafted enforcement plane.
- **What calls it:** Third-party integrations; agent tool frameworks.
- **What it calls:** CAL enforcement; CTX-ID validation; VTZ policy.
- **Must NEVER:** Bypass CAL enforcement, issue its own CTX-IDs, or expose internal enforcement APIs to external consumers.

### tasklib — Validation Task Management Library
- **What it does:** Deliberately simple Python task library that validates the Crafted Dev Agent build pipeline end-to-end (docs → scaffold → model → storage → CLI).
- **What calls it:** CI/CD pipeline; merge gate validation.
- **What it calls:** Internal subpackages (model, storage, CLI).
- **Must NEVER:** Be treated as a production system; its sole purpose is pipeline validation with real merge dependencies.

## Interface Contracts

### CTX-ID Wire Format
```
JWT-like token, signed with TrustLock agent key
Fields: {ctx_id, session_id, vtz_id, issued_at, expires_at, agent_identity, sig}
```
- Immutable after issuance. Rotation = new token + immediate old-token invalidation.
- Validate against TrustLock public key — reject software-only validation.
- Missing CTX-ID = UNTRUSTED. Expired CTX-ID = REJECTED. No exceptions.

### TrustFlow Event Schema
```
{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}
```
- `event_id`: globally unique via CSPRNG (never sequential).
- `ts`: UTC Unix timestamp, millisecond precision.
- `payload_hash`: SHA-256 of serialized action payload.
- Emission is synchronous in the enforcement path.

### VTZ Enforcement Decision
```
{ctx_id, tool_id, verdict: allow|restrict|block, reason}
```
- Every denied action produces a VTZEnforcementDecision with `verdict=block`.
- Cross-VTZ tool calls require explicit policy authorization.

### DTL Label Wire Format
```
{label_id, classification, source_id, issued_at, sig}
```
- Assigned at ingestion. Immutable. Derived data inherits highest source classification.
- Verify labels before any cross-trust-boundary data movement.

### Audit Record Contract
- Generated BEFORE execution of the security-relevant action.
- Append-only — no modification or deletion.
- Must NOT contain secrets, keys, tokens, or cleartext sensitive data.
- Must support full session replay from audit stream alone.

### Error Response Contract
All errors MUST include: `component`, `operation`, `failure_reason`, `ctx_id` (if available).
All errors MUST NOT include: keys, tokens, secrets, or cleartext payloads.

## Error Handling Rules

1. **All trust, identity, policy, and cryptographic failures fail CLOSED.** Reject the action, log the event, surface to the caller. Never silently continue.
2. **`try/except/pass` is BANNED in all enforcement code.** Every exception in an enforcement path must be caught, logged with structured context, and result in action rejection.
3. **TrustFlow emission failure** is a WARN-level audit event — not a silent skip. Log the failure, surface it, but do not block the enforcement decision itself.
4. **Audit record write failure** is non-fatal to agent operation but must be surfaced immediately to operators.
5. **CTX-ID validation failure** results in immediate rejection — no partial processing of the request.
6. **VTZ policy denial** produces a VTZEnforcementDecision record and a TrustFlow block event. The action does not execute.
7. **DTL label verification failure** at a trust boundary blocks the data movement and generates a security audit event.
8. **Cryptographic failure** (invalid signature, expired key, algorithm mismatch) always fails closed. No fallback to weaker algorithms or unverified state.
9. **Parsing failure** on any external input fails safely — reject the input, log the failure context (without the raw payload if sensitive), and return a structured error.
10. **No silent failure paths anywhere.** If a failure occurs and no log/event is emitted, the code is non-conformant.

### Banned Patterns
- `try: ... except: pass` in any enforcement path
- Swallowing exceptions without logging in trust/crypto/policy code
- Falling back to insecure defaults on cryptographic failure
- Inferring identity when CTX-ID is missing
- Logging secrets, keys, tokens, or credentials at any log level
- Async buffering of TrustFlow events in enforcement paths

## Testing Requirements

1. **Enforcement path coverage must be >= 90%.** This is a hard gate, not a goal.
2. **Every enforcement path must have at least one negative test** — what happens on rejection, invalid input, expired credentials, denied policy.
3. **Every cryptographic operation must be tested with invalid and expired material** — wrong key, tampered signature, expired token, algorithm mismatch.
4. **Every TrustFlow emission point must be tested for both success and failure paths.**
5. **Tests must NOT mock the enforcement decision logic.** External calls may be mocked, but the policy evaluation, CTX-ID validation, and VTZ enforcement logic must execute for real.
6. **All parsing, policy, trust, and cryptographic logic must be tested against malformed inputs.**
7. **Regression tests are mandatory for every material bug fix.**
8. **Benchmark tests must exist for all performance-sensitive paths** — network, crypto, policy evaluation, telemetry emission.
9. **Fuzzing must be used where inputs are complex, attacker-controlled, or parser-driven.**
10. **tasklib validation tests must prove the full dependency chain closes:** docs PR → scaffold PR → model PR → storage PR → CLI PR, each recognizing the prior merge.

## File Naming and Directory Layout

```
src/
  cal/                 # Conversation Abstraction Layer (CPF, AIR, PEE, CAL Verifier Cluster)
  dtl/                 # Data Trust Labels — classification, inheritance, verification
  trustflow/           # TrustFlow / SIS audit event stream
  vtz/                 # Virtual Trust Zone enforcement
  trustlock/           # Cryptographic machine identity (TPM-anchored)
  mcp/                 # MCP Policy Engine
  rewind/              # Crafted Rewind replay engine

sdk/
  connector/           # Crafted Connector SDK

tests/
  cal/                 # Mirrors src/cal/ exactly
  dtl/                 # Mirrors src/dtl/ exactly
  trustflow/           # Mirrors src/trustflow/ exactly
  vtz/                 # Mirrors src/vtz/ exactly
  trustlock/           # Mirrors src/trustlock/ exactly
  mcp/                 # Mirrors src/mcp/ exactly
  rewind/              # Mirrors src/rewind/ exactly
  connector/           # Mirrors sdk/connector/ exactly

crafted-docs/          # Source TRDs and PRDs
crafted-standards/     # Synthesised architecture, interfaces, decisions
docs/                  # Branch-specific context and generated documentation
```

Test files mirror the `src/` structure exactly — `src/cal/cpf.py` → `tests/cal/test_cpf.py`.

## Security Checklist — Before Every Commit

- [ ] CTX-ID is validated at every enforcement entry point before any processing
- [ ] TrustFlow event is emitted for every action outcome (allow, restrict, block)
- [ ] VTZ policy is checked before any cross-boundary operation
- [ ] No silent failure paths exist in trust, identity, policy, or cryptographic code
- [ ] No secrets, keys, tokens, or credentials appear in logs, error messages, or generated code
- [ ] All external input is validated before use; parsing is bounds-checked
- [ ] DTL labels are verified before data crosses any trust boundary
- [ ] All cryptographic operations use FIPS 140-3 approved algorithms only
- [ ] Audit records are generated before execution of security-relevant actions
- [ ] Error responses include component, operation, failure_reason, ctx_id — but never secrets
- [ ] Test coverage includes at least one negative path per security boundary
- [ ] No `try/except/pass` exists in any enforcement path
- [ ] Dependencies added are justified, reviewed for CVE history, and minimize transitive chains
- [ ] No TODO items remain in security-critical or runtime-critical code without a tracked issue

## Where to Find More Detail

- `crafted-docs/` — Source TRDs and PRDs (TRD-TASKLIB, Forge Architecture Context, and all future specification documents)
- `crafted-standards/` — Synthesised architecture documents, interface specifications, and decision records
- `docs/` — Branch-specific context, generated API documentation, and operational guides