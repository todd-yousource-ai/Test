# AGENTS.md

Crafted Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack via cryptographic identity, operator-defined policy, and auditable trust decisions.

## How to Use This File

This file is the authoritative baseline for every LLM coding session in this repository — read it completely before touching any code. For subsystem-specific detail see `crafted-docs/` for the full TRDs and `crafted-standards/` for synthesised architecture, interface, and decision records.

## Document Index

| Document Name | Type | Repo Path | What It Covers |
|---|---|---|---|
| TRD-TASKLIB | DOCX/MD | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Validation TRD for the Crafted Dev Agent pipeline — defines a simple Python task management library (tasklib) to prove the end-to-end dependency chain from docs → scaffold → model → storage → CLI |
| forge_architecture_context | MD | `crafted-docs/forge_architecture_context.md` | Platform overview and core subsystem definitions for Forge: CAL, CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, VTZ, DTL, TrustLock, MCP, Rewind, and CAL Verifier Cluster |

## Critical Rules — Non-Negotiable

1. Validate CTX-ID at every enforcement entry point FIRST — rejection on failure is immediate with zero partial processing.
2. Never infer trust implicitly — always assert and verify identity explicitly against TrustLock public key material.
3. Fail closed on every trust, identity, policy, and cryptographic failure — reject the action, log the event, surface to caller.
4. Emit a TrustFlow event for every action outcome (allow, restrict, block) synchronously in the enforcement path — async buffering is forbidden.
5. Check VTZ policy BEFORE execution of any agent action — implicit cross-VTZ access is denied by default.
6. Never include secrets, keys, tokens, credentials, or cleartext sensitive payloads in logs, error messages, or generated code.
7. Treat all external input as untrusted — validate strictly, bounds-check all parsing, fail safely on malformed input.
8. Assign DTL labels at data ingestion; labels are immutable thereafter, derived data inherits the highest classification of any source, and unlabeled data is treated as CONFIDENTIAL.
9. Generate an audit record BEFORE execution of every security-relevant action — audit records are append-only and must support full replay without external state.
10. Use only FIPS 140-3 approved cryptographic primitives — never invent cryptography, never degrade silently into insecure behavior.
11. CTX-ID tokens are immutable once issued — rotation creates a new token and immediately invalidates the old one.
12. VTZ policy changes take effect at next CTX-ID issuance, never mid-session.
13. Ban `try/except/pass` (or any swallowed-exception pattern) in all enforcement, trust, policy, and cryptographic code paths.
14. Every TrustFlow event must include: `event_id` (CSPRNG-generated), `session_id`, `ctx_id`, `ts` (UTC Unix ms), `event_type`, `payload_hash` (SHA-256), `sig`.
15. Every dependency must be justified, reviewed for licensing/CVE/maintenance health, and rejected if it materially degrades performance or security posture.

## Architecture Overview

### CAL — Conversation Abstraction Layer
- **Does:** Serves as the enforcement choke point for all agent-originated actions — no tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- **Called by:** Application orchestration layers, agent runtimes.
- **Calls:** CPF, PEE, VTZ enforcement, TrustFlow emission, CTX-ID validation.
- **Must NEVER:** Allow an action to proceed without CTX-ID validation and VTZ policy check completing first.

### CPF — Conversation Plane Filter
- **Does:** Filters and classifies agent conversation traffic at the enforcement plane, routing actions to the appropriate policy evaluation path.
- **Called by:** CAL.
- **Calls:** AIR, PEE.
- **Must NEVER:** Pass unclassified or unvalidated conversation data downstream.

### AIR — Action Interception and Routing
- **Does:** Intercepts agent-initiated actions and routes them to the correct enforcement pipeline.
- **Called by:** CPF.
- **Calls:** PEE, VTZ.
- **Must NEVER:** Route an action without first confirming the originating CTX-ID is valid.

### CTX-ID — Cryptographic Context Identity
- **Does:** Issues and validates JWT-like cryptographic identity tokens bound to a specific agent session, machine identity, and VTZ. Fields: session, agent, machine identity, VTZ binding, issuance/expiry timestamps.
- **Called by:** CAL (validation at every entry point), TrustFlow (included in every event).
- **Calls:** TrustLock (for key material and signature verification).
- **Must NEVER:** Allow modification of token fields after issuance, accept expired tokens, or infer identity from ambient context when CTX-ID is missing.

### PEE — Policy Evaluation Engine
- **Does:** Evaluates operator-defined policy against the current action, CTX-ID, VTZ, and DTL labels to produce an enforcement decision (allow, restrict, block).
- **Called by:** CAL, CPF, AIR.
- **Calls:** VTZ (boundary checks), DTL (label verification).
- **Must NEVER:** Default to allow when policy is missing or evaluation fails.

### VTZ — Virtual Trust Zone
- **Does:** Defines and enforces structural trust boundaries for agent sessions — each session is bound to exactly one VTZ at CTX-ID issuance.
- **Called by:** PEE, CAL.
- **Calls:** DTL (for cross-boundary label verification).
- **Must NEVER:** Allow cross-VTZ tool calls without explicit policy authorization or permit application code to bypass enforcement boundaries.

### DTL — Data Trust Labels
- **Does:** Assigns immutable classification labels to data at ingestion, enforces label inheritance on derived data, and verifies labels before any data crosses a trust boundary.
- **Called by:** VTZ, PEE, CAL.
- **Calls:** TrustFlow (label-stripping events are audited).
- **Must NEVER:** Allow label modification after assignment, permit unlabeled data to be treated as public, or strip labels without generating an audit event.

### TrustFlow / SIS — Audit Stream
- **Does:** Emits cryptographically signed, append-only audit events for every enforcement decision synchronously in the enforcement path.
- **Called by:** CAL (on every action outcome), all enforcement subsystems.
- **Calls:** CTX-ID (for event attribution), TrustLock (for event signing).
- **Must NEVER:** Buffer events asynchronously, silently skip failed emissions, or include secrets/keys/tokens in event payloads.

### TrustLock — Cryptographic Machine Identity
- **Does:** Provides TPM-anchored cryptographic identity, key generation, signing, and verification for CTX-ID and TrustFlow operations.
- **Called by:** CTX-ID (issuance and validation), TrustFlow (event signing).
- **Calls:** Platform TPM/HSM interfaces.
- **Must NEVER:** Perform software-only identity validation when hardware anchoring is available, or expose private key material outside the secure boundary.

### MCP — MCP Policy Engine
- **Does:** Manages operator-defined policy definitions, distribution, and versioning for the enforcement plane.
- **Called by:** PEE (policy lookup).
- **Calls:** VTZ (policy-to-zone binding).
- **Must NEVER:** Apply policy changes to active sessions — changes take effect at next CTX-ID issuance only.

### Rewind — Replay Engine
- **Does:** Reconstructs past agent sessions from the TrustFlow audit stream for forensic analysis, debugging, and compliance.
- **Called by:** Operators, compliance tooling.
- **Calls:** TrustFlow (reads audit stream).
- **Must NEVER:** Modify audit records or require external state beyond the audit stream for complete replay.

### CAL Verifier Cluster
- **Does:** Distributed verification of CAL enforcement decisions for high-availability and tamper-resistance.
- **Called by:** CAL.
- **Calls:** CTX-ID, TrustFlow.
- **Must NEVER:** Accept unverified enforcement decisions or operate without quorum when configured for distributed mode.

### tasklib — Validation Library (TRD-TASKLIB)
- **Does:** A deliberately simple Python task management library that validates the Crafted Dev Agent build pipeline end-to-end (docs → scaffold → model → storage → CLI).
- **Called by:** CI/CD pipeline for validation purposes.
- **Calls:** Nothing external — self-contained validation artifact.
- **Must NEVER:** Be treated as a production system or used for runtime enforcement.

## Interface Contracts

### CTX-ID Wire Format
```
JWT-like token, signed with TrustLock agent key
Fields: session_id, agent_id, machine_id, vtz_id, issued_at, expires_at, sig
```
- Immutable after issuance.
- Validated against TrustLock public key — software-only validation is rejected.
- Missing CTX-ID = UNTRUSTED. No exceptions.
- Expired CTX-ID = REJECTED. Clock skew tolerance is deployment-defined.

### TrustFlow Event Schema
```
{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}
```
- `event_id`: globally unique, generated via CSPRNG (not sequential).
- `ts`: UTC Unix timestamp, millisecond precision.
- `payload_hash`: SHA-256 of the serialized action payload.
- Emission is synchronous in the enforcement path.
- Failed emission: WARN-level audit event, never a silent skip.

### VTZ Enforcement Decision
```
{ctx_id, tool_id, verdict: allow|restrict|block, reason}
```
- Every denied action produces a `VTZEnforcementDecision` record with `verdict=block`.
- One session = one VTZ. Cross-VTZ requires explicit policy authorization.
- Policy changes apply at next CTX-ID issuance, not mid-session.

### DTL Label Wire Format
```
{label_id, classification, source_id, issued_at, sig}
```
- Assigned at data ingestion, immutable thereafter.
- Derived data inherits the HIGHEST classification of any source input.
- Unlabeled data = CONFIDENTIAL until explicitly reclassified.
- Label verification required before any trust boundary crossing.
- Label stripping = audited security event.

### Error Response Contract
Every error must include: `component`, `operation`, `failure_reason`, `ctx_id` (if available).
Every error must NEVER include: keys, tokens, secrets, cleartext payloads.

## Error Handling Rules

1. **All trust/identity/policy/cryptographic failures fail CLOSED** — reject the action, log the event, surface the error to the caller. Never silently continue.
2. **Banned patterns:**
   - `try/except/pass` or any equivalent swallowed-exception pattern in enforcement code.
   - Silent fallback to insecure defaults.
   - Logging secrets, keys, tokens, or cleartext sensitive data in error messages.
   - Returning partial results after a policy denial.
3. **CTX-ID validation failure:** Immediate rejection. No partial processing of the action.
4. **VTZ policy denial:** Produce a `VTZEnforcementDecision` with `verdict=block`, emit TrustFlow event, return denial to caller.
5. **TrustFlow emission failure:** Log at WARN level, surface the failure — do NOT silently skip. Agent operation continues but the failure is visible.
6. **Audit write failure:** Non-fatal to agent operation but MUST be surfaced immediately to operators.
7. **Cryptographic failure (invalid key, signature mismatch, expired material):** Fail closed. Never degrade into unencrypted or unsigned operation.
8. **DTL label missing or invalid at trust boundary:** Block the data transfer, generate audit event.
9. **Unknown/unclassified input:** Treat as untrusted. Apply maximum restriction until explicitly classified.

## Testing Requirements

1. **Enforcement path coverage must be ≥ 90%.**
2. Every enforcement path MUST have at least one negative test — verify correct behavior on rejection, denial, invalid input, and expired credentials.
3. Every cryptographic operation MUST have a test with invalid and expired material.
4. Every TrustFlow emission path MUST be tested for both success and failure.
5. Tests MUST NOT mock the enforcement decision logic — mock external calls if needed, but the policy evaluation logic must execute.
6. All parsing, policy, trust, and cryptographic logic must be tested against malformed, oversized, and adversarial inputs.
7. Benchmark tests must exist for all network, crypto, policy evaluation, and telemetry hot paths.
8. Add a regression test for every material bug fix.
9. Fuzzing must be used where inputs are complex, attacker-controlled, or parser-driven.
10. For tasklib (TRD-TASKLIB): validate the full dependency chain closes — docs → scaffold → model → storage → CLI — with real merges at each step, including import resolution from previously-merged PRs.

## File Naming and Directory Layout

```
src/
  cal/              # Conversation Abstraction Layer (CPF, AIR, PEE, CAL Verifier)
  dtl/              # Data Trust Label components
  trustflow/        # TrustFlow / SIS audit stream components
  vtz/              # Virtual Trust Zone enforcement
  trustlock/        # Cryptographic machine identity (TPM-anchored)
  mcp/              # MCP Policy Engine
  rewind/           # Crafted Rewind replay engine

sdk/
  connector/        # Crafted Connector SDK

tests/
  cal/              # Mirrors src/cal/ structure exactly
  dtl/              # Mirrors src/dtl/
  trustflow/        # Mirrors src/trustflow/
  vtz/              # Mirrors src/vtz/
  trustlock/        # Mirrors src/trustlock/
  mcp/              # Mirrors src/mcp/
  rewind/           # Mirrors src/rewind/

crafted-docs/       # Source TRDs and PRDs
crafted-standards/  # Synthesised architecture, interfaces, decisions
docs/               # Branch-specific context and generated documentation
```

Test files mirror `src/` structure exactly. A component at `src/cal/cpf.py` has tests at `tests/cal/test_cpf.py`.

## Security Checklist — Before Every Commit

- [ ] CTX-ID validated at every enforcement entry point — no action proceeds without it.
- [ ] TrustFlow event emitted for every action outcome (allow, restrict, block).
- [ ] VTZ policy checked before any cross-boundary operation.
- [ ] No silent failure paths in trust, identity, policy, or cryptographic code.
- [ ] No secrets, keys, tokens, or credentials in logs, error messages, or generated code.
- [ ] All external input validated before use — bounds-checked, type-checked, fail-safe on malformed data.
- [ ] No hardcoded secrets, tokens, credentials, or cryptographic material anywhere.
- [ ] FIPS 140-3 approved algorithms used for all cryptographic operations.
- [ ] DTL labels verified before any data crosses a trust boundary.
- [ ] Audit record generated before execution of every security-relevant action.
- [ ] Error responses include component/operation/failure_reason/ctx_id but never keys/tokens/secrets.
- [ ] No `try/except/pass` or swallowed exceptions in enforcement paths.
- [ ] Test coverage includes at least one negative path per security boundary.
- [ ] Dependencies justified, reviewed for CVE history and license, minimal transitive chains.
- [ ] Cryptographic key material: generation, storage, rotation, and destruction paths are defined and documented.

## Where to Find More Detail

- `crafted-docs/`        — Source TRDs and PRDs (TRD-TASKLIB, forge_architecture_context, and future documents)
- `crafted-standards/`   — Synthesised architecture, interface contracts, and decision records
- `docs/`                — Branch-specific context and generated documentation