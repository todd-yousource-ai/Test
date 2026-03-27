# AGENTS.md

Forge is a runtime policy enforcement and cryptographic identity platform for enterprise AI agents that enforces agent execution below the application stack through CTX-ID, VTZ policy, DTL labels, TrustFlow audit emission, and TrustLock-backed cryptographic identity. This repository contains `tasklib`, a deliberately minimal Python task management library whose sole purpose is to validate the Crafted Dev Agent build pipeline end-to-end.

## Critical Rules — Read Before Writing Any Code

1. Validate `ctx_id` at every CAL enforcement entry point before any agent action processing begins. Validation failure means immediate rejection with zero partial processing.
2. Treat missing `ctx_id` as `UNTRUSTED`. Never infer identity from ambient context. Missing CTX-ID means UNTRUSTED, no exceptions.
3. Validate CTX-ID against the TrustLock public key; software-only validation is rejected.
4. Bind every agent session to exactly one VTZ at CTX-ID issuance. Deny implicit cross-VTZ tool calls; cross-VTZ tool calls require explicit policy authorization.
5. Check every action against VTZ policy BEFORE execution and emit a `VTZEnforcementDecision` with `verdict=block` on denial.
6. Emit a synchronous TrustFlow event for every action outcome: `allow`, `restrict`, or `block`. Async buffering is forbidden in the enforcement path.
7. Never silently skip TrustFlow emission failures; log and surface them as WARN-level audit events.
8. Audit records are APPEND-ONLY — no modification or deletion. Every security-relevant action must generate an audit record BEFORE execution.
9. Assign DTL labels at data ingestion; labels are immutable after assignment. Derived data inherits the HIGHEST classification of any source. Unlabeled data must be treated as `CONFIDENTIAL`.
10. Fail closed on all trust, identity, policy, and cryptographic failures: reject the action, log the event, surface the failure to the caller. Never silently continue.
11. Never hardcode secrets, tokens, credentials, or cryptographic material anywhere in the codebase.
12. Never log secrets, keys, tokens, credentials, or cleartext sensitive payloads in logs, error messages, or generated code.
13. All external input must be treated as untrusted and validated strictly. All parsing must be bounds-checked and fail safely.
14. `try/except/pass` is BANNED in any enforcement code path.
15. In this repository, implement only the minimal `tasklib` scaffold defined by `TRD-TASKLIB`. Never add persistence, authentication, non-stdlib dependencies, logging, configuration, or extra features.
16. `tasklib` must have zero dependencies outside the Python standard library — no exceptions.
17. Keep the dependency chain acyclic and aligned to: `docs → scaffold → model → storage → CLI`.
18. For `tasklib`, `Task.status` must be an enumeration with exactly three values: `pending`, `in_progress`, and `done`. New tasks must default to `pending`.
19. Create no more than 3 implementation files per PR and no more than 6 acceptance criteria per PR for tasklib work.

## Architecture Overview

| Subsystem | Path | Enforces | Must NOT |
|---|---|---|---|
| **CAL** (Conversation Abstraction Layer) | `src/cal/` | Agent action processing; validates `ctx_id` first, then VTZ policy, then emits TrustFlow event | Never process an action without CTX-ID validation completing first |
| **CPF** (Conversation Plane Filter) | `src/cal/cpf/` | Three-tier inspection: Tier 1 structural validation (schema, bounds), Tier 2 semantic classification (intent, sensitivity, policy match) | Never skip structural validation to jump to semantic classification |
| **TrustLock** | `src/trustlock/` | Cryptographic machine identity (TPM-anchored); CTX-ID issuance and validation against TrustLock public key | Never accept software-only validation; never modify a CTX-ID after issuance |
| **VTZ** (Virtual Trust Zone) | `src/vtz/` | Operator-defined policy enforcement; evaluates policy before execution | Never allow implicit cross-VTZ operations; never execute before policy check |
| **DTL** (Data Trust Labels) | `src/dtl/` | Data classification labels; verifies labels before trust-boundary crossing | Never mutate labels after ingestion; never allow unlabeled data to pass as non-confidential |
| **TrustFlow** | `src/trustflow/` | Append-only audit stream; synchronously emits every action outcome | Never buffer asynchronously in the enforcement path; never delete or modify audit records |

## tasklib Scaffold

`tasklib` is a zero-dependency Python library for validating the Crafted Dev Agent pipeline. It lives in `src/tasklib/`.

### Package Structure


src/tasklib/
  __init__.py       # public API surface
  task.py           # Task model with status enum
  store.py          # in-memory task storage (no persistence)


### Key Contracts

- `Task.task_id`: `str` — unique identifier.
- `Task.title`: `str` — non-empty, validated at creation.
- `Task.status`: `TaskStatus` enum — exactly `pending`, `in_progress`, `done`. Defaults to `pending`.
- `TaskStore.add(task: Task) -> Task` — must reject duplicate `task_id`.
- `TaskStore.get(task_id: str) -> Task` — must raise `KeyError` on missing ID.
- `TaskStore.list() -> list[Task]` — returns all tasks; never `None`.
- No persistence, no authentication, no logging, no configuration beyond what `TRD-TASKLIB` specifies.

### Build & Test

bash
python -m pytest tests/


All tests must pass with zero warnings before merge. Tests must use only `pytest` and the Python standard library.