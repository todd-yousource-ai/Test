# CLAUDE.md

Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack through explicit trust assertion, CTX-ID validation, VTZ policy enforcement, DTL labeling, and synchronous TrustFlow audit emission. This repository currently implements `tasklib`, a validation library that proves the Crafted Dev Agent build pipeline closes a complete dependency chain from documentation through scaffold to working code.

## Critical Rules - Read Before Writing Any Code

1. Validate `ctx_id` at every CAL enforcement entry point BEFORE any other processing occurs; validation failure means immediate rejection with zero partial processing.
2. Reject immediately on CTX-ID validation failure and perform no partial processing; never silently continue.
3. Check every action against VTZ policy before execution and emit a `VTZEnforcementDecision` with `verdict=block` on denial.
4. Emit a TrustFlow event synchronously in the enforcement path for every action outcome (allow, restrict, block) using fields: `event_id`, `session_id`, `ctx_id`, `ts`, `event_type`, `payload_hash`, and `sig`. Async buffering is forbidden.
5. Never silently continue when TrustFlow emission fails; log and surface the failure as a WARN-level audit event.
6. Treat missing CTX-ID as `UNTRUSTED` and never infer identity from session context, tool context, or caller metadata. Expired CTX-ID must be rejected.
7. CTX-ID tokens are immutable once issued; no field modification is permitted after issuance.
8. All failures involving trust, identity, policy, or cryptography must fail closed — reject the action, log the event, surface to caller, never silently continue.
9. Never log, embed in error messages, or include in generated code any secrets, keys, tokens, credentials, or cleartext payloads.
10. VTZ boundaries are structural, not advisory — application code cannot bypass enforcement; cross-VTZ tool calls require explicit policy authorization.
11. DTL labels are immutable after assignment at data ingestion; derived data inherits the HIGHEST classification of any source; unlabeled data is CONFIDENTIAL until explicitly reclassified.
12. All external input is untrusted and must be validated strictly with bounds-checked parsing that fails safely.
13. `try/except/pass` is BANNED in any enforcement path — every exception must be caught, logged with structured context, and surfaced.
14. Audit records must be generated BEFORE execution, are append-only, and must never contain secrets or cleartext sensitive data.
15. `tasklib` must have zero dependencies outside the Python standard library — no third-party packages.
16. Keep `tasklib` intentionally minimal — no logging, configuration, persistence, authentication, or extra features not specified in `TRD-TASKLIB`.
17. Preserve the required `tasklib` dependency chain: docs → scaffold → model → storage → CLI, with no circular imports.
18. `tasklib` implementation files must not exceed 3 per PR and 6 acceptance criteria per PR; split before generating code if either limit would be exceeded.

## tasklib Domain Rules

1. Implement `TaskStatus` as an enumeration with exactly three members: `pending`, `in_progress`, and `done`. Never use free-form status strings.
2. Implement `Task` as a self-contained dataclass carrying these fields: `identifier` (str), `title` (str), `status` (TaskStatus), and `created_at` (numeric timestamp).
3. `title` is required and must be non-empty at task creation time; raise `ValueError` if empty or missing.
4. Default new `Task` instances to `status=TaskStatus.pending` and record `created_at` as a numeric timestamp (seconds since epoch).

## Architecture Overview

| Subsystem | Path | Enforces | Must NOT do |
|---|---|---|---|
| **CAL** (Conversation Abstraction Layer) | `src/cal/` | Agent action processing; calls CTX-ID validation first on every entry point | Must not process any action before identity validation and VTZ policy checks complete |
| **CPF** (Conversation Plane Filter) | Within `src/cal/` | Three-tier inspection: Tier 1 structural validation, Tier 2 semantic classification | Must not skip tiers, reorder inspection sequence, or bypass bounds checks or policy linkage |
| **VTZ** (Virtual Trust Zone) | `src/vtz/` | Binds each agent session to exactly one VTZ; enforces structural boundaries on tool calls | Must not permit implicit cross-VTZ tool calls |
| **TrustLock** | `src/trustlock/` | TPM-anchored cryptographic machine identity; CTX-ID issuance and signature validation against TrustLock public key | Must not perform software-only trust substitution; must not allow CTX-ID field modification after issuance |
| **DTL** (Data Trust Labels) | `src/dtl/` | Data Trust Label issuance and verification; immutable labels assigned at ingestion | Must not allow label mutation after assignment; must not allow derived data to carry a lower classification than any source |
| **TrustFlow** | `src/trustflow/` | Synchronous audit event emission for every enforcement decision | Must not buffer events asynchronously; must not omit required fields (`event_id`, `session_id`, `ctx_id`, `ts`, `event_type`, `payload_hash`, `sig`) |
| **tasklib** | `src/tasklib/` | Validation library proving the build pipeline dependency chain (docs → scaffold → model → storage → CLI) | Must not import third-party packages; must not add features beyond TRD-TASKLIB specification |