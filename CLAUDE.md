# CLAUDE.md

Crafted Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack via cryptographic identity and operator-defined policy.

## How to Use This File

This file is the authoritative baseline for every coding session in this repository — read it fully before touching any code. For subsystem-specific detail, see `crafted-docs/` for the full TRDs and PRDs and `crafted-standards/` for synthesised architecture, interface, and decision documents.

## Document Index

| Document Name | Type | Repo Path | What It Covers |
|---|---|---|---|
| TRD-TASKLIB | DOCX/MD | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Validation TRD for the Crafted Dev Agent pipeline — defines a simple Python task management library (tasklib) to prove the end-to-end dependency chain from docs → scaffold → model → storage → CLI with real merge gates |
| Forge Architecture Context | MD | `crafted-docs/forge_architecture_context.md` | Platform overview of Forge — defines all core subsystems (CAL, CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, VTZ, DTL, TrustLock, MCP, Rewind), their responsibilities, protocol wire formats, and enforcement relationships |

## Critical Rules — Non-Negotiable

1. Validate CTX-ID at every enforcement entry point FIRST — CTX-ID validation failure results in immediate rejection with zero partial processing.
2. Never infer trust implicitly — always assert and verify explicitly using TrustLock-anchored cryptographic identity.
3. Check VTZ policy BEFORE execution of every agent action — implicit cross-VTZ access is denied by default.
4. Emit a TrustFlow event for every action outcome (allow, restrict, block) — TrustFlow emission is synchronous in the enforcement path, not async-buffered.
5. Fail closed on all trust, identity, policy, and cryptographic failures — reject the action, log the event, surface to caller, never silently continue.
6. Never include secrets, keys, tokens, credentials, or cleartext sensitive payloads in logs, error messages, or generated code.
7. Treat all external input as untrusted — validate strictly with bounds-checked parsing that fails safely.
8. Assign DTL labels at data ingestion as immutable — derived data inherits the highest classification of any source, and unlabeled data is treated as CONFIDENTIAL.
9. Use only FIPS 140-3 approved cryptographic algorithms — do not invent cryptography, do not degrade silently to insecure behavior on cryptographic failure.
10. Generate an audit record BEFORE execution of every security-relevant action — audit records are append-only with no modification or deletion.
11. Bind every agent session to exactly one VTZ at CTX-ID issuance — VTZ boundaries are structural and cannot be bypassed by application code.
12. CTX-ID tokens are immutable once issued — rotation creates a new token and immediately invalidates the old one; expired CTX-IDs are rejected unconditionally.
13. TrustFlow emission failure is a WARN-level audit event — it must not silently continue; log and surface the failure.
14. Do not mock enforcement decision logic in tests — mock external calls if needed but the enforcement logic itself must execute.
15. Every dependency chain must close fully and traceably — from documentation through scaffold to working code, with real merges at each step as validated by the tasklib TRD pattern.

## Architecture Overview

### CAL — Conversation Abstraction Layer
- **Does:** Serves as the enforcement choke point for all agent-originated actions — no tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- **Called by:** Application orchestration layer, agent runtime.
- **Calls:** VTZ enforcement, CTX-ID validation, TrustFlow emission, PEE.
- **Must NEVER:** Allow any action to bypass policy evaluation or execute with an unvalidated CTX-ID.

### CPF — Conversation Plane Filter
- **Does:** Filters and intercepts conversation-plane traffic entering the CAL enforcement path.
- **Called by:** Inbound agent communication channels.
- **Calls:** CAL pipeline entry.
- **Must NEVER:** Pass unfiltered or uninspected traffic into the enforcement pipeline.

### AIR — Agent Identity Resolution
- **Does:** Resolves the authenticated identity of the acting agent within the enforcement path.
- **Called by:** CAL during action processing.
- **Calls:** CTX-ID validation, TrustLock key verification.
- **Must NEVER:** Infer agent identity from context or ambient signals — always verify cryptographically.

### CTX-ID — Contextual Identity Token
- **Does:** Provides immutable, cryptographically signed session identity tokens binding agent to VTZ, issued and validated against TrustLock public keys.
- **Called by:** CAL, AIR, VTZ enforcement, TrustFlow emission.
- **Calls:** TrustLock for key validation.
- **Must NEVER:** Allow modification after issuance, accept expired tokens, or perform software-only validation without TrustLock anchor.

### PEE — Policy Evaluation Engine
- **Does:** Evaluates operator-defined policy against the current action, CTX-ID, and VTZ context to produce allow/restrict/block verdicts.
- **Called by:** CAL.
- **Calls:** VTZ policy store, DTL label verification.
- **Must NEVER:** Default to allow on policy lookup failure — must fail closed with a block verdict.

### VTZ — Virtual Trust Zone
- **Does:** Defines and enforces structural trust boundaries around agent sessions — each session is bound to exactly one VTZ at CTX-ID issuance.
- **Called by:** PEE, CAL, CTX-ID issuance.
- **Calls:** Policy store, DTL boundary checks.
- **Must NEVER:** Allow cross-VTZ access without explicit policy authorization or permit mid-session VTZ changes.

### DTL — Data Trust Labels
- **Does:** Assigns immutable classification labels at data ingestion, enforces label inheritance on derived data, and verifies labels before any trust boundary crossing.
- **Called by:** VTZ enforcement, PEE, data ingestion pipelines.
- **Calls:** Audit subsystem for label-stripping events.
- **Must NEVER:** Allow unlabeled data to be treated as anything other than CONFIDENTIAL, or permit label stripping without audited policy authorization.

### TrustFlow / SIS — Audit Event Stream
- **Does:** Emits structured, signed audit events for every enforcement decision synchronously in the enforcement path.
- **Called by:** CAL after every action outcome.
- **Calls:** Audit storage, Rewind replay engine.
- **Must NEVER:** Buffer asynchronously, silently skip emission failures, or include secrets/keys/tokens in event payloads.

### TrustLock — Cryptographic Machine Identity
- **Does:** Provides TPM-anchored cryptographic identity for agents and machines — generates, stores, rotates, and validates keys.
- **Called by:** CTX-ID issuance/validation, AIR, TrustFlow signing.
- **Calls:** TPM/hardware security module interfaces.
- **Must NEVER:** Expose private key material, fall back to software-only key storage when hardware is available, or degrade silently on cryptographic failure.

### MCP — MCP Policy Engine
- **Does:** Manages operator-defined policy definitions, distribution, and lifecycle for consumption by PEE and VTZ.
- **Called by:** PEE, administrative interfaces.
- **Calls:** Policy storage, audit subsystem.
- **Must NEVER:** Apply policy changes mid-session — changes take effect at next CTX-ID issuance.

### Rewind — Crafted Rewind Replay Engine
- **Does:** Enables forensic replay of agent sessions from the TrustFlow audit stream alone, with no external state required.
- **Called by:** Administrative and audit interfaces.
- **Calls:** TrustFlow audit storage.
- **Must NEVER:** Modify or delete audit records, or require external state beyond the audit stream for replay.

### Connector SDK
- **Does:** Provides the SDK for integrating external tools and services into the Crafted enforcement plane.
- **Called by:** External tool integrations.
- **Calls:** CAL enforcement entry points.
- **Must NEVER:** Bypass CAL policy evaluation or emit unauthenticated actions.

### tasklib — Validation Task Library (TRD-TASKLIB)
- **Does:** Validates that the Crafted Dev Agent build pipeline closes a complete dependency chain from documentation through scaffold to working code with real merge gates (docs → scaffold → model → storage → CLI).
- **Called by:** CI/CD pipeline validation.
- **Calls:** Internal package imports across subpackages.
- **Must NEVER:** Be treated as a production system — it exists solely for pipeline validation.

## Interface Contracts

### CTX-ID Wire Format
- JWT-like token, signed with TrustLock agent key.
- Immutable after issuance — rotation creates a new token and invalidates the old one immediately.
- Validate against TrustLock public key — reject software-only validation.
- Missing CTX-ID means UNTRUSTED — never infer identity from context.
- Expired CTX-ID is rejected unconditionally; clock skew tolerance is defined per deployment.

### TrustFlow Event Schema
```
{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}
```
- `event_id`: globally unique via CSPRNG (not sequential).
- `ts`: UTC Unix timestamp with millisecond precision.
- `payload_hash`: SHA-256 of the serialized action payload.
- Emission is synchronous in the enforcement path.
- Failed emission is a WARN-level audit event — never a silent skip.

### DTL Label Wire Format
```
{label_id, classification, source_id, issued_at, sig}
```
- Assigned at data ingestion — immutable thereafter.
- Derived data inherits the HIGHEST classification of any source.
- Unlabeled data is CONFIDENTIAL until explicitly reclassified.
- Verify labels before any data crosses a trust boundary.
- Label stripping is a security event — audit and policy-control it.

### VTZ Enforcement Decision
```
{ctx_id, tool_id, verdict: allow|restrict|block, reason}
```
- Every action checked against VTZ policy before execution.
- Denial produces a VTZEnforcementDecision record with `verdict=block`.
- Cross-VTZ tool calls require explicit policy authorization.
- VTZ policy changes take effect at next CTX-ID issuance, not mid-session.

### CAL Enforcement Sequence
1. Receive agent action.
2. Validate CTX-ID (reject immediately on failure).
3. Evaluate VTZ policy via PEE (block on denial).
4. Execute action (only if allowed).
5. Emit TrustFlow event with outcome.
6. Surface TrustFlow emission failure if it occurs.

### Audit Record Contract
- Generated BEFORE execution of the security-relevant action.
- Append-only — no modification or deletion.
- Must NOT contain secrets, keys, tokens, or cleartext sensitive data.
- Replay must be possible from the audit stream alone.
- Audit failures are non-fatal to agent operation but must be surfaced immediately.

## Error Handling Rules

- **All trust, identity, policy, and cryptographic failures MUST fail closed.** Fail closed means: reject the action, log the event, surface to the caller. Never silently continue.
- **Banned pattern: `try/except/pass` (or equivalent) in any enforcement path.** Swallowing exceptions in enforcement code is a reviewable rejection.
- **Banned pattern: silent fallthrough on validation failure.** Every validation check must have an explicit rejection branch.
- **Banned pattern: logging secrets, keys, tokens, or cleartext payloads in error messages.**
- **All errors MUST include:** component name, operation attempted, failure reason, and CTX-ID (if available).
- **All errors MUST NOT include:** keys, tokens, secrets, or cleartext payloads.
- **TrustFlow emission failure:** WARN-level audit event, not silent — log and surface.
- **Audit subsystem failure:** Non-fatal to agent operation but MUST be surfaced immediately — do not silently degrade.
- **CTX-ID validation failure:** Immediate rejection, no partial processing, no fallback.
- **VTZ policy lookup failure:** Fail closed with block verdict — never default to allow.
- **DTL label verification failure at trust boundary:** Block the data transfer, log the event.
- **Cryptographic operation failure:** Fail closed — never degrade to insecure behavior.

## Testing Requirements

- **90% minimum test coverage** for all enforcement paths — this is a hard gate, not a target.
- **Every enforcement path MUST have at least one negative test** — test what happens on rejection, not just success.
- **Every cryptographic operation MUST have a test with invalid and expired material.**
- **Every TrustFlow emission path MUST be tested for both success and failure.**
- **Do not mock enforcement decision logic.** Mock external calls if necessary, but the enforcement logic itself must execute in the test.
- **All parsing, policy, trust, and cryptographic logic MUST be tested against malformed inputs.**
- **Regression tests are mandatory** for every material bug fix.
- **Benchmark tests MUST exist** for performance-sensitive paths — network, crypto, policy evaluation, and telemetry.
- **Fuzzing SHOULD be used** where inputs are complex, attacker-controlled, or parser-driven.
- **Tests mirror `src/` structure exactly** under `tests/<subsystem>/`.
- **tasklib validation tests** must verify the full dependency chain closes: docs → scaffold → model → storage → CLI, with real merge gate verification.

## File Naming and Directory Layout

```
src/
  cal/              # Conversation Abstraction Layer (CPF, AIR, PEE, CAL Verifier)
  dtl/              # Data Trust Label components
  trustflow/        # TrustFlow / SIS audit event stream
  vtz/              # Virtual Trust Zone enforcement
  trustlock/        # Cryptographic machine identity (TPM-anchored)
  mcp/              # MCP Policy Engine
  rewind/           # Crafted Rewind replay engine

sdk/
  connector/        # Crafted Connector SDK

tests/
  cal/              # Tests for CAL — mirrors src/cal/
  dtl/              # Tests for DTL — mirrors src/dtl/
  trustflow/        # Tests for TrustFlow — mirrors src/trustflow/
  vtz/              # Tests for VTZ — mirrors src/vtz/
  trustlock/        # Tests for TrustLock — mirrors src/trustlock/
  mcp/              # Tests for MCP — mirrors src/mcp/
  rewind/           # Tests for Rewind — mirrors src/rewind/

crafted-docs/       # Source TRDs and PRDs
crafted-standards/  # Synthesised architecture, interfaces, decisions
docs/               # Branch-specific context
```

- CAL components: `src/cal/<component>.py` (or `.go`)
- DTL components: `src/dtl/<component>.py`
- TrustFlow components: `src/trustflow/<component>.py`
- VTZ components: `src/vtz/<component>.py`
- TrustLock components: `src/trustlock/<component>.py`
- MCP components: `src/mcp/<component>.py`
- Rewind components: `src/rewind/<component>.py`
- Connector SDK: `sdk/connector/<component>.py`

## Security Checklist — Before Every Commit

- [ ] CTX-ID validated at every enforcement entry point — no action proceeds without it.
- [ ] TrustFlow event emitted for every action outcome (allow, restrict, block).
- [ ] VTZ policy checked before any cross-boundary operation.
- [ ] No silent failure paths in any trust, crypto, or policy code.
- [ ] No secrets, keys, tokens, or credentials in logs, error messages, or generated code.
- [ ] All external input validated before use — treated as untrusted.
- [ ] All parsing is bounds-checked and fails safely.
- [ ] FIPS 140-3 approved algorithms used for all cryptographic operations.
- [ ] DTL labels verified before data crosses any trust boundary.
- [ ] Audit records generated before execution of security-relevant actions.
- [ ] Audit records contain no secrets, keys, tokens, or cleartext sensitive data.
- [ ] Error messages include component, operation, failure reason, and CTX-ID — never secrets.
- [ ] No `try/except/pass` or equivalent swallowed exceptions in enforcement paths.
- [ ] Test coverage includes at least one negative path per security boundary.
- [ ] No new dependency added without justification for licensing, maintenance health, CVE history, and transitive risk.

## Where to Find More Detail

- `crafted-docs/` — Source TRDs and PRDs (TRD-TASKLIB, Forge Architecture Context, and all future design documents)
- `crafted-standards/` — Synthesised architecture documents, interface contracts, and decision records
- `docs/` — Branch-specific context and working documentation