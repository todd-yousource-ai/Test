

# DECISIONS.md

---

## ADR-001: Use a Deliberately Simple Library for Pipeline Validation

**Status:** Accepted

**Context:** The Crafted Dev Agent build pipeline needed end-to-end validation proving that the full dependency chain — from documentation through scaffold to working code — could close with real merges at each step. A complex production system would introduce unnecessary risk and confound validation of the pipeline itself.

**Decision:** Define a deliberately simple Python task management library (`tasklib`) whose sole purpose is to validate the agent pipeline. The library is not intended for production use.

**Consequences:** The library's feature set is intentionally minimal; any complexity beyond what is needed to exercise the pipeline is out of scope. Future production systems should not reuse `tasklib` as a foundation. All design choices within `tasklib` serve pipeline validation, not end-user functionality.

**Rejected alternatives:** Using an existing open-source library (rejected because it would not exercise the specific merge-gate and dependency-chain behaviors needed); building a production-grade system first (rejected because pipeline validation must precede production workloads).

---

## ADR-002: Linear Dependency Chain — Docs → Scaffold → Model → Storage → CLI

**Status:** Accepted

**Context:** The pipeline must prove that each stage's output is consumed correctly by the next stage — that merge gates fire, downstream PRs recognize upstream merges, and imports resolve locally before CI.

**Decision:** Enforce a strict linear dependency chain: documentation PR → scaffold PR → model PR → storage PR → CLI PR. Each stage depends on the successful merge of the previous stage.

**Consequences:** PRs cannot be merged out of order. A failure at any stage blocks all downstream stages. This validates the merge-gate propagation but means the pipeline cannot parallelize work across these stages.

**Rejected alternatives:** A DAG-based dependency graph with parallel branches (rejected because the validation goal is to prove sequential merge-gate propagation first); a monolithic single-PR approach (rejected because it would not exercise cross-PR dependency resolution).

---

## ADR-003: Documentation PR as the First Merge Gate Trigger

**Status:** Accepted

**Context:** The pipeline must validate that a documentation-only PR can fire the merge gate and that downstream PRs detect the merge event.

**Decision:** The first PR in the chain is a documentation set (README, ARCHITECTURE overview, API reference). Its merge triggers the gate that unblocks the scaffold PR.

**Consequences:** Documentation is a first-class artifact in the pipeline, not an afterthought. The merge-gate mechanism must handle PRs with no executable code. Documentation must be authored before any code scaffold exists.

**Rejected alternatives:** Starting with the scaffold PR and treating docs as a parallel or trailing artifact (rejected because it would not validate docs-only merge-gate behavior).

---

## ADR-004: Scaffold PR Creates Multiple Package Directories with File Mirroring

**Status:** Accepted

**Context:** The pipeline must prove that a scaffold PR containing multiple subpackage directories correctly mirrors files to the local test workspace.

**Decision:** The scaffold PR creates the full Python package structure with subpackage directories for model, storage, and CLI. Files are mirrored to the local test workspace upon merge.

**Consequences:** The scaffold defines the package layout that all subsequent code PRs must conform to. Changing the package structure after scaffold merge requires a new PR and re-validation. The mirroring mechanism must handle directory creation, not just file placement.

**Rejected alternatives:** Generating package structure on-the-fly during code PRs (rejected because it would not validate scaffold mirroring as a distinct pipeline stage); a flat single-directory layout (rejected because it would not exercise subpackage resolution).

---

## ADR-005: Code PRs Must Resolve Imports from Previously-Merged PRs Locally Before CI

**Status:** Accepted

**Context:** In a multi-stage pipeline, later code PRs import symbols defined in earlier PRs (e.g., CLI imports from model and storage). These imports must resolve in the local development workspace, not just in CI.

**Decision:** Code PRs that depend on previously-merged PRs must resolve those imports locally before CI runs. The local test workspace receives merged artifacts via the file-mirroring mechanism established by the scaffold PR.

**Consequences:** The local workspace must be kept in sync with merged state. Developers (or agents) cannot rely solely on CI to catch import errors. The mirroring mechanism is a prerequisite for local development, not just deployment.

**Rejected alternatives:** Allowing CI-only validation of cross-PR imports (rejected because it would not prove the local development loop works); vendoring dependencies within each PR (rejected because it would not validate real cross-package imports).

---

## ADR-006: Python as the Implementation Language for tasklib

**Status:** Accepted

**Context:** The validation library needs a language with straightforward package/import semantics to clearly exercise the dependency-chain validation goals.

**Decision:** Implement `tasklib` in Python, using standard Python packaging conventions (subpackages with `__init__.py`, standard imports).

**Consequences:** All pipeline tooling must support Python package structures. Import resolution validation is Python-specific. The pipeline validation results apply directly to Python-based agent workloads but would need re-validation for other languages.

**Rejected alternatives:** TypeScript/Node (rejected because Python's import and package model is more directly relevant to the target agent workloads); polyglot implementation (rejected as unnecessary complexity for a validation exercise).

---

## ADR-007: Forge Uses Runtime Policy Enforcement Below the Application Stack

**Status:** Accepted

**Context:** Enterprise AI agents require policy enforcement that cannot be bypassed by application-level code. Enforcement at the application layer is insufficient because agents or their orchestrators could circumvent it.

**Decision:** Forge enforces agent execution policy at runtime, below the application stack, via cryptographic identity and operator-defined policy. No tool call, data read, API invocation, or agent handoff executes without passing through policy evaluation.

**Consequences:** All agent actions are mediated by the enforcement layer regardless of the application framework used. This introduces latency on every action but guarantees policy compliance. Application developers cannot opt out of enforcement. The platform must be performant enough to sit in the critical path of every agent operation.

**Rejected alternatives:** Application-level middleware enforcement (rejected because it can be bypassed); audit-only / post-hoc enforcement (rejected because it allows policy violations to occur before detection); static pre-deployment policy checks only (rejected because runtime context is required for meaningful policy decisions).

---

## ADR-008: CAL as the Single Enforcement Choke Point

**Status:** Accepted

**Context:** With multiple agent action types (tool calls, data reads, API invocations, agent handoffs), enforcement must be unified to prevent gaps.

**Decision:** The Conversation Abstraction Layer (CAL) is the single enforcement choke point for all agent-originated actions. It sits above the VTZ enforcement plane and below application orchestration. Key components include the CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, and CAL Verifier Cluster.

**Consequences:** Every new action type must be routed through CAL; there is no "fast path" that bypasses it. CAL becomes a critical availability dependency — if CAL is down, agents cannot act. All policy logic is centralized, simplifying auditing but creating a single point of design complexity.

**Rejected alternatives:** Distributed per-tool enforcement (rejected because it creates gaps and inconsistency); enforcement at the LLM API gateway only (rejected because it misses tool calls and inter-agent handoffs that don't traverse the gateway).

---

## ADR-009: Cryptographic Identity as the Foundation for Agent Trust

**Status:** Accepted

**Context:** Policy enforcement requires reliable identification of agents, operators, and contexts. Identifier schemes based on names or API keys are spoofable and do not provide non-repudiation.

**Decision:** Forge uses cryptographic identity (CTX-ID and related constructs) as the foundation for agent trust. Agent identity, operator identity, and conversation context are all cryptographically bound.

**Consequences:** All agents must be provisioned with cryptographic credentials before they can operate. Key management becomes an operational requirement. Policy decisions can be cryptographically verified after the fact, enabling audit trails with non-repudiation. Credential rotation and revocation must be supported.

**Rejected alternatives:** API-key-based identity (rejected due to lack of non-repudiation and ease of leakage); OAuth/OIDC tokens alone (rejected because they do not bind to conversation context); no identity layer with network-perimeter trust only (rejected because agents operate across trust boundaries).

---

## ADR-010: CPF (Conversation Plane Filter) as the Policy Evaluation Entry Point

**Status:** Accepted

**Context:** Within the CAL subsystem, there must be a defined entry point where raw agent action requests are received and initial policy filtering occurs before deeper evaluation.

**Decision:** The Conversation Plane Filter (CPF) serves as the policy evaluation entry point within CAL, performing initial filtering and routing of agent action requests to the appropriate policy evaluation components.

**Consequences:** CPF must be highly available and low-latency since it is the first component in the enforcement path. Policy rules must be expressible in a form that CPF can evaluate efficiently. CPF's filtering logic must be kept in sync with the overall policy model.

**Rejected alternatives:** Direct routing to the full policy evaluation engine for every request (rejected due to performance concerns — CPF provides an efficient first-pass filter); client-side pre-filtering (rejected because it is untrusted).

---

## ADR-011: Validation Scope Includes Documentation as a Deliverable Artifact

**Status:** Accepted

**Context:** The `tasklib` validation exercise needs to prove that the pipeline handles non-code artifacts. Documentation (README, ARCHITECTURE, API reference) is the most common non-code deliverable.

**Decision:** The `tasklib` scope explicitly includes a documentation set — README, ARCHITECTURE overview, and API reference — as first-class deliverable artifacts that flow through the same pipeline as code.

**Consequences:** The pipeline's PR, merge-gate, and mirroring mechanisms must handle markdown/text files, not just Python source. Documentation quality is gated by the same merge process as code. Documentation updates follow the same dependency-chain rules.

**Rejected alternatives:** Treating documentation as out-of-band (rejected because it would leave a gap in pipeline validation); auto-generating all documentation from code (rejected because the validation goal requires a docs-first PR with no code to generate from).