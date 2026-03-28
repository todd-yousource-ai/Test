# CLAUDE.md

Crafted Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack via cryptographic identity, operator-defined policy, and auditable trust decisions.

## How to Use This File

This file is the authoritative baseline for all code generation, review, and architectural decisions in this repository — read it in full before touching any code. For subsystem-specific detail see `crafted-docs/` for the full TRDs and `crafted-standards/` for synthesised architecture, interface, and decision records.

## Document Index

| Document Name | Type | Repo Path | What It Covers |
|---|---|---|---|
| TRD-TASKLIB | DOCX / MD | `crafted-docs/TRD-TASKLIB.docx` / `crafted-docs/TRD-TASKLIB.md` | Validation TRD for the Crafted Dev Agent build pipeline — defines a simple Python task management library to prove the full dependency chain (docs → scaffold → model → storage → CLI) closes with real merges |
| Forge Architecture Context | MD | `crafted-docs/forge_architecture_context.md` | Platform overview of Forge, all core subsystems (CAL, CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, VTZ, DTL, TrustLock, MCP, Rewind), protocol wire formats, and subsystem relationships |

## Critical Rules — Non-Negotiable

1. Validate CTX-ID against the TrustLock public key at every enforcement entry point before any other processing occurs — software-only validation is rejected.
2. Reject any request with a missing or expired CTX-ID as UNTRUSTED — never infer identity from context, environment, or headers.
3. Check VTZ policy before execution of every agent action — implicit cross-VTZ access is denied by default.
4. Emit a TrustFlow event synchronously in the enforcement path for every action outcome (allow, restrict, block) — async buffering is not permitted.
5. Fail closed on all trust, identity, policy, and cryptographic failures — reject the action, log the event, surface to caller; never silently continue.
6. Never log, emit, or include secrets, keys, tokens, credentials, or cleartext sensitive payloads in error messages, audit records, or generated code.
7. Treat all external input as untrusted — validate strictly, bounds-check all parsing, and fail safely on malformed data.
8. Assign DTL labels at data ingestion; labels are immutable thereafter and derived data inherits the highest classification of any source.
9. Treat unlabeled data as CONFIDENTIAL until explicitly reclassified by policy-controlled action.
10. Generate an append-only audit record before execution of every security-relevant action — audit records must never be modified or deleted.
11. Use only FIPS 140-3 approved cryptographic primitives — do not invent cryptography or use unapproved algorithms.
12. Ban `try/except/pass` (or equivalent silent exception swallowing) in all enforcement, trust, policy, and cryptographic code paths.
13. Ensure every TrustFlow event includes: `event_id` (CSPRNG-generated), `session_id`, `ctx_id`, `ts` (UTC Unix ms), `event_type`, `payload_hash` (SHA-256), and `sig`.
14. Bind every agent session to exactly one VTZ at CTX-ID issuance — VTZ policy changes take effect at next CTX-ID issuance, not mid-session.
15. Maintain full traceability from every enforcement code path to a requirement, TRD, design decision, or bug fix — untraceable code must not be merged.

## Architecture Overview

### CAL — Conversation Abstraction Layer
- **Does:** Enforcement choke point for all agent-originated actions (tool calls, data reads, API invocations, agent handoffs). No action executes without passing through CAL policy evaluation.
- **Called by:** Application orchestration layers, agent runtimes.
- **Calls:** CPF, PEE, CTX-ID validator, VTZ enforcement, TrustFlow emitter.
- **Must NEVER:** Allow an action to bypass policy evaluation or execute without a validated CTX-ID.

### CPF — Conversation Plane Filter
- **Does:** First-pass filtering on the conversation plane — intercepts and classifies agent actions before policy evaluation.
- **Called by:** CAL pipeline.
- **Calls:** AIR, PEE.
- **Must NEVER:** Make enforcement decisions autonomously — it classifies and routes, it does not decide.

### CTX-ID — Contextual Identity Token
- **Does:** Immutable cryptographic identity token binding an agent session to a verified identity, a VTZ, and a TrustLock key.
- **Called by:** Every enforcement entry point (CAL, VTZ, PEE).
- **Calls:** TrustLock for key validation.
- **Must NEVER:** Be modified after issuance, reused after expiration, or validated without TrustLock public key verification.

### VTZ — Virtual Trust Zone
- **Does:** Structural boundary enforcement around agent sessions — each session is bound to exactly one VTZ defining permitted tools, data, and cross-zone access.
- **Called by:** CAL, PEE.
- **Calls:** DTL for label verification at boundary crossings, TrustFlow for decision logging.
- **Must NEVER:** Allow cross-VTZ access without explicit policy authorization or be bypassed by application code.

### PEE — Policy Enforcement Engine
- **Does:** Evaluates operator-defined policy against the current CTX-ID, VTZ, action, and DTL labels to produce a `VTZEnforcementDecision` (allow | restrict | block).
- **Called by:** CAL.
- **Calls:** VTZ policy store, DTL label store, TrustFlow emitter.
- **Must NEVER:** Return a permissive default on evaluation failure — all policy errors fail closed with verdict `block`.

### TrustFlow / SIS — Security Information Stream
- **Does:** Immutable, append-only audit stream capturing every enforcement decision, security event, and action outcome with cryptographic integrity.
- **Called by:** CAL, PEE, VTZ, DTL, TrustLock — every subsystem that makes or observes a trust-relevant decision.
- **Calls:** Audit storage backend.
- **Must NEVER:** Drop events silently, allow record modification, or include secrets/keys/tokens in event payloads.

### DTL — Data Trust Labels
- **Does:** Classification labels assigned at data ingestion that govern how data may flow across trust boundaries. Labels are immutable and inherited by derived data.
- **Called by:** VTZ boundary checks, PEE policy evaluation, data ingestion pipelines.
- **Calls:** TrustFlow for label-stripping audit events.
- **Must NEVER:** Allow label removal without a policy-controlled, audited security event, or permit unlabeled data to cross a trust boundary as anything other than CONFIDENTIAL.

### TrustLock — Cryptographic Machine Identity
- **Does:** TPM-anchored cryptographic identity providing key generation, storage, rotation, destruction, and CTX-ID signing.
- **Called by:** CTX-ID issuance and validation, TrustFlow event signing.
- **Calls:** Platform TPM/HSM interfaces.
- **Must NEVER:** Export private keys, fall back to software-only key storage in production, or degrade silently on cryptographic failure.

### MCP — MCP Policy Engine
- **Does:** Manages operator-defined policy lifecycle — creation, versioning, distribution, and activation of enforcement policies consumed by PEE.
- **Called by:** Administrative interfaces, PEE (for policy retrieval).
- **Calls:** Policy storage, TrustFlow for policy-change audit.
- **Must NEVER:** Apply policy changes mid-session — changes take effect at next CTX-ID issuance.

### Rewind — Crafted Rewind Replay Engine
- **Does:** Deterministic replay of agent sessions from the TrustFlow audit stream for forensic analysis, debugging, and compliance.
- **Called by:** Administrative and compliance tooling.
- **Calls:** TrustFlow audit stream (read-only).
- **Must NEVER:** Modify audit records, execute replayed actions against live systems, or replay without a valid CTX-ID context.

### AIR — Agent Interaction Router
- **Does:** Routes classified agent interactions to the appropriate enforcement and execution paths within CAL.
- **Called by:** CPF.
- **Calls:** PEE, VTZ.
- **Must NEVER:** Route an action without prior CPF classification or skip VTZ boundary checks.

### Connector SDK
- **Does:** Provides the integration surface for third-party tools and services to interoperate with Forge enforcement.
- **Called by:** External tool integrations.
- **Calls:** CAL (all actions re-enter the enforcement pipeline).
- **Must NEVER:** Provide a bypass path around CAL enforcement or allow unauthenticated tool registration.

### tasklib (Validation Library)
- **Does:** Deliberately simple Python task management library validating the Crafted Dev Agent build pipeline end-to-end (docs → scaffold → model → storage → CLI).
- **Called by:** CI/CD pipeline validation.
- **Calls:** Internal subpackages only (model, storage, CLI).
- **Must NEVER:** Be treated as production infrastructure — it exists solely to prove the dependency chain closes.

## Interface Contracts

### CTX-ID Wire Format
```
JWT-like token, signed with TrustLock agent key
Fields: ctx_id, session_id, vtz_id, issued_at, expires_at, trustlock_key_id, sig
```
- Tokens are IMMUTABLE after issuance.
- Rotation creates a new token; the old one is invalidated immediately.
- Expired tokens MUST be rejected — clock skew tolerance is deployment-defined.
- Missing CTX-ID = UNTRUSTED. No exceptions.

### TrustFlow Event Schema
```
{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}
```
- `event_id`: globally unique via CSPRNG (not sequential).
- `ts`: UTC Unix timestamp, millisecond precision.
- `payload_hash`: SHA-256 of serialized action payload.
- Emission is synchronous in the enforcement path.
- Failed emission is a WARN-level audit event — never a silent skip.

### VTZ Enforcement Decision
```
{ctx_id, tool_id, verdict: allow|restrict|block, reason}
```
- Every policy denial MUST produce this record with `verdict=block`.
- Cross-VTZ tool calls require explicit policy authorization.
- VTZ boundaries are structural — application code cannot bypass them.

### DTL Label Wire Format
```
{label_id, classification, source_id, issued_at, sig}
```
- Assigned at data ingestion — immutable thereafter.
- Derived data inherits the HIGHEST classification of any source.
- Label verification MUST occur before any data crosses a trust boundary.
- Label stripping is a security event — audited and policy-controlled.

### CAL Enforcement Sequence (per action)
1. Validate CTX-ID against TrustLock public key → reject on failure.
2. Check VTZ policy via PEE → produce VTZEnforcementDecision.
3. On `block`: reject action, emit TrustFlow event with verdict.
4. On `allow`/`restrict`: execute action, emit TrustFlow event with outcome.
5. TrustFlow emission failure → log WARN, surface failure — never silently continue.

## Error Handling Rules

### Fail-Closed Mandate
- All trust, identity, policy, and cryptographic failures MUST fail closed: reject the action, log the event, surface to the caller.
- "Fail closed" means the system denies access/action — it does not mean crash.

### Required Error Fields
Every error MUST include: `component`, `operation`, `failure_reason`, `ctx_id` (if available).

### Banned Patterns
- `try/except/pass` or equivalent silent exception swallowing in any enforcement, trust, policy, or cryptographic code path.
- Returning a permissive/default-allow result on policy evaluation failure.
- Logging secrets, keys, tokens, or cleartext payloads in error messages.
- Inferring identity or trust from context when explicit verification fails.
- Swallowing TrustFlow emission failures without logging.

### Error Classification
| Failure Type | Required Behavior |
|---|---|
| CTX-ID missing or expired | Reject as UNTRUSTED, emit TrustFlow event, return error |
| CTX-ID signature invalid | Reject, log with `failure_reason`, fail closed |
| VTZ policy evaluation failure | Default to `block`, emit VTZEnforcementDecision, log |
| Cross-VTZ access without policy | Deny, emit TrustFlow event with `verdict=block` |
| TrustFlow emission failure | Log WARN-level audit event, surface failure — do not halt agent |
| Cryptographic operation failure | Fail closed, log without exposing key material |
| DTL label missing | Treat data as CONFIDENTIAL, log, enforce highest restriction |
| Audit write failure | Non-fatal to agent operation, surface immediately to monitoring |

## Testing Requirements

### Coverage Rules
- Enforcement path test coverage MUST be ≥ 90%.
- Every enforcement path MUST have at least one negative test (rejection case).
- Every cryptographic operation MUST have a test with invalid and expired material.
- Every TrustFlow emission MUST be tested for both success and failure paths.

### Mandatory Test Categories
- **Unit tests:** All security-critical logic, all policy evaluation paths, all CTX-ID validation logic.
- **Integration tests:** Full CAL enforcement sequence, VTZ boundary crossings, DTL label inheritance chains.
- **Negative-path tests:** Malformed CTX-ID, expired tokens, invalid signatures, missing DTL labels, cross-VTZ access without policy.
- **Fuzz tests:** All parsers handling external/attacker-controlled input (CTX-ID parsing, DTL label parsing, policy document parsing).
- **Benchmark tests:** All network, crypto, policy evaluation, and TrustFlow emission hot paths.
- **Regression tests:** One regression test for every material bug fix.

### Test Integrity Rules
- Tests MUST NOT mock the enforcement decision logic — they may mock external calls but the policy/enforcement logic itself must execute.
- Tests must verify failure behavior, not just success behavior.
- All tests must run deterministically — no flaky tests in enforcement paths.

### tasklib Validation Tests
- Verify the full dependency chain closes: docs → scaffold → model → storage → CLI.
- Verify that code PRs importing from previously-merged PRs resolve imports locally before CI.
- Verify that documentation PRs fire the merge gate and downstream PRs recognize the merge.

## File Naming and Directory Layout

```
src/
├── cal/              # Conversation Abstraction Layer (CPF, AIR, PEE, CAL Verifier)
├── dtl/              # Data Trust Label assignment, inheritance, verification
├── trustflow/        # TrustFlow / SIS audit stream emission, storage, query
├── vtz/              # Virtual Trust Zone boundary enforcement
├── trustlock/        # Cryptographic machine identity (TPM-anchored keys, signing)
├── mcp/              # MCP Policy Engine (policy lifecycle, versioning, distribution)
├── rewind/           # Crafted Rewind replay engine (forensic replay from audit stream)
sdk/
├── connector/        # Crafted Connector SDK (third-party tool integration)
tests/
├── cal/              # Mirrors src/cal/ — unit, integration, negative-path tests
├── dtl/              # Mirrors src/dtl/
├── trustflow/        # Mirrors src/trustflow/
├── vtz/              # Mirrors src/vtz/
├── trustlock/        # Mirrors src/trustlock/
├── mcp/              # Mirrors src/mcp/
├── rewind/           # Mirrors src/rewind/
├── connector/        # Mirrors sdk/connector/
├── benchmarks/       # Performance benchmarks for crypto, policy, network, TrustFlow
├── fuzz/             # Fuzz targets for parsers and external input handlers
crafted-docs/         # Source TRDs and PRDs
crafted-standards/    # Synthesised architecture, interfaces, decisions
docs/                 # Branch-specific context and generated documentation
```

### Test File Naming
- Test files mirror the source file they test: `src/cal/cpf.py` → `tests/cal/test_cpf.py`.
- Benchmark files: `tests/benchmarks/bench_<subsystem>_<component>.py`.
- Fuzz targets: `tests/fuzz/fuzz_<subsystem>_<component>.py`.

## Security Checklist — Before Every Commit

- [ ] CTX-ID is validated at every enforcement entry point before any processing.
- [ ] TrustFlow event is emitted for every action outcome (allow, restrict, block).
- [ ] VTZ policy is checked before any cross-boundary operation.
- [ ] No silent failure paths exist in trust, identity, policy, or cryptographic code.
- [ ] No secrets, keys, tokens, or credentials appear in logs, error messages, or generated code.
- [ ] All external input is validated before use — bounds-checked, type-checked, fail-safe.
- [ ] DTL labels are verified before any data crosses a trust boundary.
- [ ] All cryptographic operations use FIPS 140-3 approved algorithms only.
- [ ] Test coverage includes at least one negative path per security boundary.
- [ ] No `try/except/pass` or equivalent silent swallowing in enforcement paths.
- [ ] Audit records are generated before execution of security-relevant actions.
- [ ] Error messages include `component`, `operation`, `failure_reason`, `ctx_id` — nothing else sensitive.
- [ ] No dead code, unused dependencies, or experimental leftovers in the diff.
- [ ] Code is traceable to a requirement, TRD, design decision, or bug fix.

## Where to Find More Detail

- `crafted-docs/` — Source TRDs and PRDs (TRD-TASKLIB, Forge Architecture Context, and all future TRDs)
- `crafted-standards/` — Synthesised architecture documents, interface specifications, and decision records
- `docs/` — Branch-specific context, generated documentation, and operational guides