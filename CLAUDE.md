# CLAUDE.md

Crafted Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack via cryptographic identity and operator-defined policy.

## How to Use This File

This file is the authoritative baseline for every coding session in this repository — read it completely before touching any code. For subsystem-specific detail, see `crafted-docs/` for the full TRDs and PRDs, and `crafted-standards/` for synthesised architecture, interface, and decision documents.

## Document Index

| Document Name | Type | Repo Path | What It Covers |
|---|---|---|---|
| TRD-TASKLIB | DOCX/MD | `crafted-docs/TRD-TASKLIB.md` / `crafted-docs/TRD-TASKLIB.docx` | Validation TRD for the Crafted Dev Agent build pipeline — defines a simple Python task management library to prove the full dependency chain (docs → scaffold → model → storage → CLI) closes with real merges |
| Forge Architecture Context | MD | `crafted-docs/forge_architecture_context.md` | Platform overview and core subsystem definitions — CAL, CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, VTZ, DTL, TrustLock, MCP, CAL Verifier Cluster; injected into every code generation prompt |

## Critical Rules — Non-Negotiable

1. Validate CTX-ID at every enforcement entry point FIRST — reject immediately on failure with zero partial processing.
2. Never infer trust implicitly; always assert and verify trust explicitly via cryptographic proof.
3. Emit a TrustFlow event for every action outcome (allow, restrict, block) synchronously in the enforcement path — async buffering is forbidden.
4. Fail closed on all trust, identity, policy, and cryptographic failures — reject the action, log the event, surface to the caller, never silently continue.
5. Never include secrets, keys, tokens, credentials, or cleartext sensitive payloads in logs, error messages, or generated code.
6. Validate all external input as untrusted with strict bounds-checking; fail safely on malformed input.
7. Check VTZ policy BEFORE every execution — cross-VTZ tool calls require explicit policy authorization; implicit access is denied.
8. Treat CTX-ID tokens as immutable after issuance — rotation creates a new token and immediately invalidates the old one.
9. Assign DTL labels at data ingestion as immutable; derived data inherits the highest classification of any source; unlabeled data is CONFIDENTIAL until explicitly reclassified.
10. Generate an audit record BEFORE executing every security-relevant action — audit records are append-only, never modified or deleted.
11. Use only FIPS 140-3 approved cryptographic algorithms; never invent cryptography or degrade silently into insecure behavior.
12. Ban `try/except/pass` (or any equivalent swallowed exception) in all enforcement, trust, identity, policy, and cryptographic code paths.
13. Enforce VTZ boundaries structurally — application code cannot bypass VTZ enforcement; policy changes take effect at next CTX-ID issuance, not mid-session.
14. Verify DTL labels before any data crosses a trust boundary; label stripping is a security event that must be audited and policy-controlled.
15. Every TrustFlow event must include `event_id` (CSPRNG-generated, globally unique), `session_id`, `ctx_id`, `ts` (UTC Unix ms), `event_type`, `payload_hash` (SHA-256), and `sig`.

## Architecture Overview

### CAL — Conversation Abstraction Layer
- **Does:** Serves as the enforcement choke point for all agent-originated actions — no tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.
- **Called by:** Application orchestration layers, agent runtimes.
- **Calls:** CPF, PEE, CTX-ID validation, VTZ enforcement, TrustFlow emission, DTL verification.
- **Must NEVER:** Allow an action to proceed without CTX-ID validation and VTZ policy check completing first.

### CPF — Conversation Plane Filter
- **Does:** Intercepts and filters all conversation-plane traffic entering the enforcement pipeline.
- **Called by:** CAL as the first-stage filter.
- **Calls:** AIR for action interpretation, PEE for policy evaluation.
- **Must NEVER:** Pass unvalidated or unfiltered traffic downstream.

### CTX-ID — Contextual Identity
- **Does:** Provides cryptographic session identity tokens (JWT-like, signed with TrustLock agent key) binding an agent session to a VTZ, operator identity, and policy set.
- **Called by:** CAL at every enforcement entry point; VTZ at session binding.
- **Calls:** TrustLock for key validation and signature verification.
- **Must NEVER:** Accept an expired, modified, or unsigned CTX-ID; never infer identity from context when CTX-ID is missing.

### VTZ — Virtual Trust Zones
- **Does:** Enforces structural trust boundaries around agent sessions — each session is bound to exactly one VTZ at CTX-ID issuance.
- **Called by:** CAL before every cross-boundary or tool-call operation.
- **Calls:** Policy store for authorization decisions; emits VTZEnforcementDecision records.
- **Must NEVER:** Allow cross-VTZ access without explicit policy authorization; never treat boundaries as advisory.

### TrustFlow / SIS — Security Information Stream
- **Does:** Emits immutable, structured audit events for every enforcement decision, synchronously in the enforcement path.
- **Called by:** CAL after every action outcome; PEE after every policy decision.
- **Calls:** Audit persistence layer.
- **Must NEVER:** Buffer events asynchronously, skip emission silently, or include secrets/keys/tokens in event payloads.

### DTL — Data Trust Labels
- **Does:** Classifies data at ingestion with immutable labels; enforces label verification at trust boundaries; propagates highest classification to derived data.
- **Called by:** CAL before data crosses any trust boundary; ingestion pipelines at data entry.
- **Calls:** Policy store for reclassification authorization; TrustFlow for label-stripping audit events.
- **Must NEVER:** Allow unlabeled data to be treated as anything other than CONFIDENTIAL; allow label modification after assignment without audited reclassification.

### TrustLock — Cryptographic Machine Identity
- **Does:** Provides TPM-anchored cryptographic identity for agents and machines; generates, stores, rotates, and destroys key material.
- **Called by:** CTX-ID for token signing and validation; CAL Verifier Cluster for signature verification.
- **Calls:** Hardware TPM or approved HSM interfaces; CSPRNG sources.
- **Must NEVER:** Accept software-only validation when TrustLock hardware validation is required; expose private key material.

### PEE — Policy Evaluation Engine
- **Does:** Evaluates operator-defined policies against agent actions to produce allow/restrict/block verdicts.
- **Called by:** CAL and CPF for every action requiring policy evaluation.
- **Calls:** VTZ for zone-scoped policy; TrustFlow for decision audit emission.
- **Must NEVER:** Default to allow when policy is missing or evaluation fails — default is deny.

### MCP — MCP Policy Engine
- **Does:** Manages policy lifecycle — authoring, distribution, versioning, and enforcement of operator-defined policies.
- **Called by:** PEE for policy retrieval; administrative workflows for policy management.
- **Calls:** Policy storage; TrustFlow for policy-change audit events.
- **Must NEVER:** Apply policy changes mid-session; allow policy modification without audit.

### AIR — Action Interpretation and Routing
- **Does:** Interprets and classifies agent-originated actions for routing to appropriate enforcement paths.
- **Called by:** CPF after initial filtering.
- **Calls:** PEE for policy evaluation; VTZ for boundary checks.
- **Must NEVER:** Route an action that has not been interpreted and classified.

### Crafted Rewind — Replay Engine
- **Does:** Enables forensic replay of agent sessions from the TrustFlow audit stream alone, with no external state required.
- **Called by:** Administrative and forensic workflows.
- **Calls:** TrustFlow audit stream for event retrieval.
- **Must NEVER:** Require external state beyond the audit stream for complete replay.

### Crafted Connector SDK
- **Does:** Provides the integration SDK for connecting external tools and services to the Crafted enforcement plane.
- **Called by:** External integrations and third-party tool adapters.
- **Calls:** CAL for enforcement; CTX-ID for identity propagation.
- **Must NEVER:** Bypass CAL enforcement or allow unauthenticated tool connections.

### tasklib — Validation Library (TRD-TASKLIB)
- **Does:** Deliberately simple Python task management library validating the Crafted Dev Agent build pipeline end-to-end (docs → scaffold → model → storage → CLI).
- **Called by:** Dev Agent pipeline validation tests.
- **Calls:** Internal subpackages only (model, storage, CLI).
- **Must NEVER:** Be treated as a production system — it exists solely to prove the dependency chain closes.

## Interface Contracts

### CTX-ID Wire Format
```
JWT-like token, signed with TrustLock agent key
Fields: immutable after issuance
Validation: against TrustLock public key (software-only validation rejected)
Expiry: enforced strictly; clock skew tolerance defined per deployment
Missing CTX-ID: treated as UNTRUSTED — never infer identity
```

### TrustFlow Event Schema
```
{
  event_id:      string  // globally unique, CSPRNG-generated (not sequential)
  session_id:    string
  ctx_id:        string
  ts:            int64   // UTC Unix timestamp, millisecond precision
  event_type:    string
  payload_hash:  string  // SHA-256 of serialized action payload
  sig:           string  // cryptographic signature
}
```

### DTL Label Wire Format
```
{
  label_id:       string
  classification: string  // e.g., CONFIDENTIAL, INTERNAL, PUBLIC
  source_id:      string
  issued_at:      int64
  sig:            string
}
```

### VTZ Enforcement Decision
```
{
  ctx_id:   string
  tool_id:  string
  verdict:  "allow" | "restrict" | "block"
  reason:   string
}
```

### CAL Enforcement Sequence (mandatory order)
1. Validate CTX-ID (reject immediately on failure).
2. Check VTZ policy (emit VTZEnforcementDecision with `verdict=block` on denial).
3. Execute action (only on allow/restrict).
4. Emit TrustFlow event for the outcome.
5. If TrustFlow emission fails: log at WARN level, surface the failure — do not silently continue.

### Audit Record Requirements
- Generated BEFORE execution of the security-relevant action.
- Append-only — no modification or deletion permitted.
- Must NOT contain secrets, keys, tokens, or cleartext sensitive data.
- Audit failures are non-fatal to agent operation but must be surfaced immediately.
- Full session replay must be possible from the audit stream alone.

## Error Handling Rules

### Fail-Closed Mandate
All trust, identity, policy, and cryptographic failures MUST fail closed: reject the action, log the event, surface to the caller. There is no exception to this rule.

### Required Error Structure
Every error must include:
- `component` — the subsystem that failed
- `operation` — the action being attempted
- `failure_reason` — what went wrong
- `ctx_id` — if available at time of failure

### Banned Patterns
- `try/except/pass` or any equivalent silent exception swallowing in enforcement code — **BANNED**.
- Logging an error and continuing execution in trust/crypto/policy paths — **BANNED**.
- Including keys, tokens, secrets, or cleartext payloads in error messages — **BANNED**.
- Returning a default "allow" on policy evaluation failure — **BANNED**.
- Degrading silently from cryptographic enforcement to insecure behavior — **BANNED**.

### Failure Type Responses
| Failure Type | Response |
|---|---|
| CTX-ID validation failure | Immediate rejection, no partial processing, TrustFlow event emitted |
| CTX-ID missing | Treat as UNTRUSTED, reject, audit |
| CTX-ID expired | Reject — no grace period beyond deployment-defined clock skew |
| VTZ policy denial | Block action, emit VTZEnforcementDecision with `verdict=block` and reason |
| Cross-VTZ without explicit auth | Deny — implicit is never permitted |
| DTL label missing | Treat data as CONFIDENTIAL, enforce accordingly |
| DTL label verification failure | Block data from crossing trust boundary, audit |
| TrustFlow emission failure | WARN-level audit event, surface failure — do not silently skip |
| TrustLock key validation failure | Reject operation, audit, fail closed |
| Policy evaluation error | Default deny, audit, surface to operator |
| Cryptographic operation failure | Fail closed, audit, never fall back to insecure alternative |
| Audit system failure | Non-fatal to operation but surface immediately to operator |

## Testing Requirements

### Coverage Rules
- Enforcement path test coverage MUST be >= 90%.
- Every enforcement path MUST have at least one negative test (rejection/denial behavior).
- Every cryptographic operation MUST have a test with invalid and expired material.
- Every TrustFlow emission MUST be tested for both success and failure paths.
- Every parsing, policy, trust, and cryptographic path MUST be tested against malformed inputs.

### Test Integrity Rules
- Tests MUST NOT mock the enforcement decision logic — external calls may be mocked but the enforcement logic itself must execute.
- Add a regression test for every material bug fix.
- Benchmark tests MUST exist for all performance-sensitive paths (network, crypto, policy evaluation, telemetry).
- Fuzzing SHOULD be used where inputs are complex, attacker-controlled, or parser-driven.
- Test for failure behavior, not just success behavior.

### Test Directory Structure
Tests mirror `src/` structure exactly:
```
tests/cal/           - CAL enforcement tests
tests/dtl/           - DTL label tests
tests/trustflow/     - TrustFlow emission tests
tests/vtz/           - VTZ enforcement tests
tests/trustlock/     - TrustLock crypto tests
tests/mcp/           - MCP policy engine tests
tests/rewind/        - Rewind replay tests
tests/connector/     - Connector SDK tests
```

### tasklib Validation Tests (TRD-TASKLIB)
- Verify the full dependency chain closes: docs → scaffold → model → storage → CLI.
- Verify documentation PR fires the merge gate and downstream PRs recognize the merge.
- Verify scaffold PR mirrors files correctly to the local test workspace.
- Verify code PRs importing from previously-merged PRs resolve imports locally before CI.

## File Naming and Directory Layout

```
src/
├── cal/              # Conversation Abstraction Layer — enforcement choke point
│   ├── cpf.py        # Conversation Plane Filter
│   ├── air.py        # Action Interpretation and Routing
│   ├── ctx_id.py     # Contextual Identity token handling
│   ├── pee.py        # Policy Evaluation Engine
│   └── verifier.py   # CAL Verifier Cluster
├── dtl/              # Data Trust Labels — classification and enforcement
├── trustflow/        # TrustFlow / SIS — audit event stream
├── vtz/              # Virtual Trust Zone — structural trust boundaries
├── trustlock/        # Cryptographic machine identity (TPM-anchored)
├── mcp/              # MCP Policy Engine — policy lifecycle
├── rewind/           # Crafted Rewind — forensic replay engine
sdk/
└── connector/        # Crafted Connector SDK — external tool integration
tests/
├── cal/
├── dtl/
├── trustflow/
├── vtz/
├── trustlock/
├── mcp/
├── rewind/
└── connector/
crafted-docs/         # Source TRDs and PRDs
crafted-standards/    # Synthesised architecture, interfaces, decisions
docs/                 # Branch-specific context
```

## Security Checklist — Before Every Commit

- [ ] CTX-ID is validated at every enforcement entry point before any processing occurs.
- [ ] TrustFlow event is emitted for every action outcome (allow, restrict, block).
- [ ] VTZ policy is checked before every cross-boundary operation and tool call.
- [ ] No silent failure paths exist in trust, identity, policy, or cryptographic code.
- [ ] No secrets, keys, tokens, or credentials appear in logs, error messages, or generated code.
- [ ] All external input is validated as untrusted before use, with strict bounds-checking.
- [ ] Test coverage includes at least one negative-path test per security boundary.
- [ ] Only FIPS 140-3 approved algorithms are used for all cryptographic operations.
- [ ] DTL labels are verified before data crosses any trust boundary.
- [ ] Audit records are generated before security-relevant actions execute.
- [ ] No `try/except/pass` or equivalent swallowed exceptions exist in enforcement code.
- [ ] Error messages include component, operation, failure_reason, and ctx_id — but never secrets.
- [ ] All dependencies are justified, reviewed for CVE history, and minimized.
- [ ] No hardcoded secrets, tokens, credentials, or cryptographic material exist anywhere.
- [ ] Randomness comes exclusively from approved cryptographic sources (CSPRNG).

## Where to Find More Detail

- `crafted-docs/`        — source TRDs and PRDs (TRD-TASKLIB, Forge Architecture Context, and all future specification documents)
- `crafted-standards/`   — synthesised architecture documents, interface specifications, and decision records
- `docs/`                — branch-specific context and working documentation