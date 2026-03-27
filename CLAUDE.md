# CLAUDE.md

Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack through cryptographic identity, operator-defined policy, and auditable runtime controls.

## Critical Rules - Read Before Writing Any Code

### Identity & Enforcement

1. Validate `ctx_id` at every CAL enforcement entry point before any action processing — validation failure means immediate rejection with zero partial processing.
2. Treat missing `ctx_id` as `UNTRUSTED` — never infer identity from session context, caller context, or application state.
3. `CTX-ID` tokens are IMMUTABLE once issued — modification after issuance is a security violation; rotation creates a new token and invalidates the old one immediately.
4. Bind every agent session to exactly one VTZ at `CTX-ID` issuance — deny implicit cross-VTZ calls by default.
5. Check every action against VTZ policy BEFORE execution — never execute first. Use `VTZEnforcementDecision.verdict` values exactly as `allow|restrict|block`; never invent or weaken these values.
6. Fail closed on every trust, identity, policy, and cryptographic failure — reject the action, log the event, surface to caller.

### Audit & Data Trust

7. Emit a synchronous TrustFlow event for every action outcome (`allow`, `restrict`, `block`) — async buffering is forbidden in enforcement paths.
8. Never silently continue when TrustFlow emission fails — log and surface the failure immediately.
9. Audit records are APPEND-ONLY — no modification, no deletion; audit failures are non-fatal but MUST be surfaced immediately.
10. DTL labels are assigned at DATA INGESTION and are immutable — unlabeled data MUST be treated as CONFIDENTIAL until explicitly reclassified. Never allow label stripping without audit.

### Code Quality & Security

11. `try/except/pass` is BANNED in any enforcement code path — no swallowed exceptions, no silent continues, anywhere.
12. Never log or return secrets, keys, tokens, credentials, or cleartext sensitive payloads.
13. Treat all external input as untrusted — validate strictly, bounds-check all parsing, fail safely on malformed data.
14. Tests MUST NOT mock the enforcement decision logic — external calls may be mocked but enforcement logic must execute.
15. No more than 3 implementation files per PR and no more than 6 acceptance criteria per PR — split before exceeding.

### tasklib-Specific Rules

16. No dependency outside the Python standard library is permitted for `tasklib`.
17. Do not add persistence, authentication, multi-user behavior, configuration systems, logging, or speculative abstractions beyond the TRD.
18. Preserve the TRD-TASKLIB dependency chain exactly: `docs → scaffold → model → storage → CLI`.
19. Implement `TaskStatus` as an enumeration with exactly three members: `pending`, `in_progress`, and `done` — never use free-form status strings.
20. For the current task (model tests), test behavior of `Task` and `TaskStatus` directly — do not couple tests to storage or CLI concerns.

## Architecture Overview


src/
  cal/           — Conversation Abstraction Layer enforcement entry points.
                   MUST validate ctx_id first.
                   MUST NOT execute actions before identity and policy checks.
                   MUST NOT make policy decisions — delegates to VTZ.
  cal/cpf/       — Conversation Plane Filter. Three-tier inspection:
                   (1) structural validation, (2) semantic classification.
                   MUST NOT skip tiers. MUST NOT bypass CAL enforcement order.
  dtl/           — Data Trust Labels. Assigns and enforces classification
                   labels at ingestion. MUST NOT allow label stripping without audit.
  trustflow/     — TrustFlow audit stream. Emits immutable, signed audit events.
                   MUST NOT buffer asynchronously in enforcement paths.
  vtz/           — Virtual Trust Zone enforcement. Evaluates policy and returns
                   verdict (allow|restrict|block) via VTZEnforcementDecision.verdict.
                   MUST NOT be bypassed by application code.
                   MUST NOT allow implicit cross-VTZ tool calls.
  trustlock/     — Cryptographic machine identity (TPM-anchored). Issues and
                   validates CTX-ID via TrustLock public key. MUST verify token
                   authenticity and expiry. MUST NOT accept software-only validation.
  mcp/           — MCP Policy Engine. Defines and distributes operator policy.
                   MUST NOT execute actions — policy definition and distribution only.


## tasklib Architecture


tasklib/
  models.py      — Task dataclass and TaskStatus enumeration (current focus).
  storage.py     — In-memory task storage (future PR, depends on models).
  cli.py         — Command-line interface (future PR, depends on storage).


### Task Model Contract

- `TaskStatus` enum: members are `pending`, `in_progress`, `done` — no other values.
- `Task` dataclass fields:
  - `id`: `str` — unique task identifier.
  - `title`: `str` — human-readable task title; must not be empty.
  - `description`: `str` — task description; defaults to empty string.
  - `status`: `TaskStatus` — defaults to `TaskStatus.pending`.
- `Task` is a pure data object with no side effects, no I/O, no persistence logic.

### Current Task: Model Tests

- Test `TaskStatus` enumeration members and their values.
- Test `Task` default construction and field defaults.
- Test `Task` construction with explicit arguments.
- Test that `Task.status` accepts only `TaskStatus` values.
- Test equality and identity semantics of `Task` instances.
- Do not test storage or CLI behavior in model tests.