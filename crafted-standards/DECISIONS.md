

# DECISIONS.md

---

## ADR-001: Use a Deliberately Simple Task Library for Pipeline Validation

**Status:** Accepted

**Context:** The Crafted Dev Agent build pipeline needed end-to-end validation proving that the full dependency chain — from documentation through scaffold to working code — could close with real merges at each step. A production-grade system would introduce unnecessary complexity and risk, obscuring whether pipeline failures stem from the system under build or the pipeline itself.

**Decision:** Define a deliberately simple Python task management library (`tasklib`) whose sole purpose is to validate the build pipeline. The library is not intended for production use.

**Consequences:** The library's complexity is capped at the minimum needed to exercise every pipeline stage. Future production systems must have their own TRDs and cannot inherit assumptions from tasklib. Any feature creep in tasklib undermines its validation purpose.

**Rejected alternatives:** Using a real production subsystem (e.g., a Forge component) as the first pipeline validation target — rejected because a failure would be ambiguous (pipeline bug vs. design bug), and production TRDs were not yet stable enough to serve as a fixed validation baseline.

---

## ADR-002: Five-Stage Linear Dependency Chain (Docs → Scaffold → Model → Storage → CLI)

**Status:** Accepted

**Context:** The pipeline must prove that each stage's merge triggers downstream stages correctly, that import resolution works against previously-merged artifacts, and that the merge gate fires at each transition. A linear chain is the simplest topology that exercises every inter-stage dependency.

**Decision:** The tasklib dependency chain is strictly linear: documentation → scaffold → model → storage → CLI. Each stage depends on the successful merge of the preceding stage.

**Consequences:** No stage may be built out of order. The pipeline must support blocking on upstream merge completion before opening a downstream PR. Parallelism across stages within tasklib is explicitly excluded. This constrains the validation to serial execution but guarantees that every merge-gate transition is exercised.

**Rejected alternatives:** A diamond or DAG dependency graph — rejected because the first validation pass should prove the simplest case; complex topologies can be validated in a follow-up iteration once the linear chain is proven.

---

## ADR-003: Documentation PR as the First Merge-Gate Trigger

**Status:** Accepted

**Context:** The pipeline must prove that a documentation-only PR can fire the merge gate and that downstream PRs recognize that merge event. Documentation is the first artifact in the dependency chain and has zero code dependencies, making it the ideal candidate for the initial trigger.

**Decision:** The first PR in the tasklib chain is a documentation set (README, ARCHITECTURE overview, API reference). Its merge must be observable by downstream scaffold and code PRs as a satisfied dependency.

**Consequences:** The merge-gate mechanism must treat documentation PRs identically to code PRs in terms of event emission. CI must not skip or short-circuit documentation-only PRs. The documentation artifacts must land in a well-known path that downstream stages can reference.

**Rejected alternatives:** Starting with a code scaffold PR and deferring documentation — rejected because it would leave the docs → code transition untested and would not validate that non-code artifacts participate fully in the merge gate.

---

## ADR-004: Scaffold PR Must Mirror Multiple Package Directories to Local Test Workspace

**Status:** Accepted

**Context:** The scaffold stage creates the Python package structure with subpackage directories. The pipeline must prove that multi-directory file creation works and that the local test workspace accurately reflects the repository state post-merge, since subsequent code PRs must resolve imports against this structure.

**Decision:** The scaffold PR creates multiple subpackage directories (at minimum: model, storage, CLI entry point) and the pipeline mirrors all of them to the local test workspace upon merge.

**Consequences:** The workspace mirroring mechanism must handle directory creation, not just file updates. Import resolution in later stages depends on the scaffold's directory layout being exactly as specified. Any deviation in mirroring breaks the entire downstream chain.

**Rejected alternatives:** A single flat package with no subpackages — rejected because it would not exercise the multi-directory mirroring capability, which is a critical pipeline behavior to validate.

---

## ADR-005: Code PRs Must Resolve Imports from Previously-Merged PRs Locally Before CI

**Status:** Accepted

**Context:** When a code PR (e.g., storage) imports from a previously-merged PR (e.g., model), the import must resolve in the local workspace before CI runs. This validates that the pipeline's workspace state management correctly accumulates artifacts across merges.

**Decision:** Import resolution is validated locally (in the developer/agent workspace) prior to CI submission. The pipeline must ensure that all previously-merged artifacts are present in the local workspace at the time a downstream PR is prepared.

**Consequences:** The pipeline cannot rely solely on CI to catch import errors — local pre-flight checks are mandatory. The workspace must maintain a cumulative view of all merged artifacts, not just the current PR's diff. This means the workspace management layer must implement incremental state accumulation.

**Rejected alternatives:** Relying entirely on CI-side resolution (e.g., installing previously-merged packages from a registry) — rejected because it would not validate the local workspace state management, which is a core pipeline capability under test.

---

## ADR-006: Python as the Implementation Language for tasklib

**Status:** Accepted

**Context:** The validation library needs a language with straightforward package/import semantics, broad tooling support, and minimal build ceremony so that pipeline behavior — not language complexity — is what is being tested.

**Decision:** tasklib is implemented in Python with standard package conventions (`__init__.py`, subpackages, setuptools or equivalent).

**Consequences:** The pipeline's scaffold templates, import resolution logic, and CI configuration are all Python-specific for this validation. Validating the pipeline for other languages requires separate TRDs and validation libraries.

**Rejected alternatives:** TypeScript/Node.js — rejected due to more complex module resolution semantics (CommonJS vs. ESM) that would introduce ambiguity in diagnosing pipeline failures. Rust — rejected due to compilation overhead and more complex package management that would slow iteration on pipeline debugging.

---

## ADR-007: CAL as the Single Enforcement Choke Point for All Agent-Originated Actions

**Status:** Accepted

**Context:** In the Forge platform, enterprise AI agents perform tool calls, data reads, API invocations, and agent handoffs. Without a single enforcement point, policy evaluation would be scattered across the application stack, leading to inconsistent enforcement and bypass vulnerabilities.

**Decision:** The Conversation Abstraction Layer (CAL) is the mandatory enforcement choke point for all agent-originated actions. No tool call, data read, API invocation, or agent handoff executes without passing through a CAL policy evaluation.

**Consequences:** Every agent action pathway must route through CAL — there is no "fast path" that bypasses policy. This introduces latency on every action but guarantees complete policy coverage. All subsystems (CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, CAL Verifier Cluster) are subordinate to or coordinated through CAL. Application-layer orchestration sits above CAL and cannot circumvent it.

**Rejected alternatives:** Distributed policy enforcement at each tool/API boundary — rejected because it would create enforcement gaps, version skew between policy evaluators, and make audit trails incoherent. A post-hoc audit-only approach — rejected because enterprise compliance requires preventive enforcement, not just detection.

---

## ADR-008: CAL Positioned Below Application Orchestration, Above VTZ Enforcement Plane

**Status:** Accepted

**Context:** The enforcement layer must intercept actions after the application/orchestration layer has decided what to do, but before the low-level execution plane (VTZ) carries out the action. Placing it too high means it can be bypassed by orchestration internals; placing it too low means it lacks semantic context about the action.

**Decision:** CAL sits above the VTZ (Virtual Trust Zone) enforcement plane and below application orchestration. This gives it access to semantic action context (what the agent intends) while ensuring that VTZ-level execution cannot proceed without CAL approval.

**Consequences:** The VTZ must refuse to execute any action not bearing a valid CAL authorization token/signal. Application orchestrators must be designed to emit action requests downward through CAL, not directly to execution primitives. This creates a strict layering invariant that all integration code must respect.

**Rejected alternatives:** Embedding enforcement inside the orchestration layer — rejected because different orchestration frameworks would require different enforcement implementations, fragmenting the security boundary. Enforcement solely at the VTZ level — rejected because VTZ lacks the semantic context to evaluate business-level policy.

---

## ADR-009: Cryptographic Identity as the Foundation for Agent Policy Enforcement

**Status:** Accepted

**Context:** Agents operating in enterprise environments need unforgeable identities to bind policy decisions to specific actors. Software-level identity (API keys, session tokens) can be replayed, shared, or spoofed without detection.

**Decision:** Forge uses cryptographic identity (CTX-ID and related mechanisms) as the basis for binding agents to their policy context. Every agent action carries a cryptographic proof of identity that CAL validates before policy evaluation.

**Consequences:** All agents must be provisioned with cryptographic credentials before they can operate. Key management, rotation, and revocation become operational requirements. Policy evaluation has a hard dependency on cryptographic verification, meaning verification failures are action-blocking, not advisory.

**Rejected alternatives:** Shared API keys per agent class — rejected because they cannot distinguish individual agent instances and are trivially replayable. OAuth/OIDC tokens alone — rejected because they are designed for user-to-service flows and lack the agent-specific binding semantics Forge requires (though they may be used as one input to identity derivation).

---

## ADR-010: Runtime Enforcement Below the Application Stack

**Status:** Accepted

**Context:** Policy enforcement that operates only at the application layer can be bypassed by agents that interact directly with underlying infrastructure, SDKs, or runtime APIs. Enterprise compliance requires that enforcement cannot be circumvented regardless of how an agent is implemented.

**Decision:** Forge enforces agent execution policy at runtime, below the application stack, so that enforcement is not dependent on application-layer cooperation.

**Consequences:** The enforcement mechanism must integrate at a level that application code cannot trivially bypass (e.g., intercepting system calls, network traffic, or runtime API invocations). This increases deployment complexity and may require privileged access on host systems. It also means Forge has a hard dependency on the runtime environment's cooperation (container runtime, OS, hypervisor).

**Rejected alternatives:** Pure application-layer middleware enforcement — rejected because it can be bypassed by agents that do not use the expected middleware stack. Static analysis / pre-deployment policy checking only — rejected because it cannot account for runtime-dynamic behavior.

---

## ADR-011: Operator-Defined Policy as the Governance Model

**Status:** Accepted

**Context:** Different