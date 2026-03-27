

# DECISIONS.md

---

## ADR-001: Use a Deliberately Simple Task Library as Pipeline Validation Vehicle

**Status:** Accepted

**Context:** The Crafted Dev Agent build pipeline needs end-to-end validation proving that the full dependency chain — from documentation through scaffold to working code — can close with real merges at each step. A production-grade system would introduce unnecessary complexity and risk for this validation purpose.

**Decision:** Define `tasklib` as a deliberately simple Python task management library whose sole purpose is to exercise and validate the build pipeline. It is explicitly not a production system.

**Consequences:** The library's design is driven by pipeline validation goals rather than feature richness. Any architectural choices in tasklib serve pipeline coverage, not end-user utility. Future production systems cannot assume tasklib patterns are production-ready.

**Rejected alternatives:** Using an existing open-source project (too many uncontrolled variables); building a production-grade system first (delays pipeline validation and conflates two concerns).

---

## ADR-002: Linear Dependency Chain for Pipeline Validation

**Status:** Accepted

**Context:** The pipeline must prove that downstream PRs recognize upstream merges, imports resolve locally before CI, and merge gates fire correctly across the full chain.

**Decision:** The full dependency chain follows a strict linear order: `docs → scaffold → model → storage → CLI`. Each stage depends on the successful merge of the preceding stage.

**Consequences:** PRs cannot be merged out of order. The pipeline must detect and enforce ordering. Parallelization of these specific stages is not permitted. This constrains the validation run to be sequential but guarantees each link in the chain is exercised.

**Rejected alternatives:** A DAG-based dependency graph with parallel branches (adds complexity without additional validation signal for the initial proof); a single monolithic PR (defeats the purpose of validating cross-PR dependency resolution).

---

## ADR-003: Documentation PR as the First Merge Gate Trigger

**Status:** Accepted

**Context:** The pipeline must validate that a documentation-only PR can fire the merge gate and that downstream PRs recognize this merge event.

**Decision:** The first PR in the chain is a documentation set comprising a README, an ARCHITECTURE overview, and an API reference. This PR fires the merge gate and establishes the baseline that all subsequent PRs depend upon.

**Consequences:** Documentation is a first-class artifact in the pipeline, not a side-effect. The merge gate must support non-code PRs. Downstream scaffold and code PRs must be able to query whether the docs PR has merged.

**Rejected alternatives:** Starting with the scaffold PR (skips validation that non-code PRs trigger the gate); bundling docs into the scaffold PR (collapses two distinct validation steps into one).

---

## ADR-004: Python Package Scaffold with Subpackage Directories

**Status:** Accepted

**Context:** The scaffold PR must validate that the pipeline can create multiple package directories and mirror files to the local test workspace correctly.

**Decision:** The scaffold PR creates a Python package structure with explicit subpackage directories (model, storage, CLI as separate subpackages within the tasklib namespace).

**Consequences:** Each subsequent code PR targets a specific subpackage, enabling fine-grained validation of import resolution across packages. The scaffold must include `__init__.py` files and any package metadata required for local imports to work before CI. The directory layout is fixed once the scaffold PR merges.

**Rejected alternatives:** A flat module layout (would not exercise cross-subpackage import resolution); a single package with no subpackages (insufficient validation of directory mirroring).

---

## ADR-005: Local Import Resolution Before CI

**Status:** Accepted

**Context:** Code PRs that import from previously-merged PRs must resolve those imports in the local test workspace before CI runs. This validates that the workspace correctly reflects the merged state of upstream dependencies.

**Decision:** The pipeline must ensure that when a code PR (e.g., storage) imports from a previously-merged PR (e.g., model), those imports resolve locally. The local workspace is the source of truth for import resolution, not a remote registry or CI artifact cache.

**Consequences:** The workspace synchronization mechanism must pull merged code into the local environment before running any import-dependent steps. Developers and agents cannot rely on CI to catch import errors — they must be caught locally. This implies a workspace update step is mandatory before code PR validation.

**Rejected alternatives:** Relying solely on CI for import validation (defeats the purpose of proving local resolution); using mock/stub imports (would not validate real dependency closure).

---

## ADR-006: Forge Architecture — CAL as the Universal Enforcement Choke Point

**Status:** Accepted

**Context:** Enterprise AI agents perform tool calls, data reads, API invocations, and agent handoffs. All of these actions require policy enforcement to ensure compliance with operator-defined rules and cryptographic identity verification.

**Decision:** The Conversation Abstraction Layer (CAL) is the single enforcement choke point for all agent-originated actions. No tool call, data read, API invocation, or agent handoff executes without passing through a CAL policy evaluation. CAL sits above the VTZ enforcement plane and below application orchestration.

**Consequences:** Every new action type must be routed through CAL — there is no bypass path. This creates a hard architectural constraint: any subsystem that introduces a new agent capability must integrate with CAL. Performance and latency of CAL become system-critical. CAL's availability is a single point of failure for all agent execution.

**Rejected alternatives:** Distributed enforcement at each tool/API boundary (inconsistent policy application, impossible to audit centrally); enforcement only at the application orchestration layer (too high in the stack, can be bypassed by lower-level calls).

---

## ADR-007: Forge Architecture — CPF as the Conversation Plane Filter

**Status:** Accepted

**Context:** Within the CAL enforcement architecture, a specific component is needed to filter and evaluate conversation-plane traffic — the stream of messages, tool calls, and context flowing through agent interactions.

**Decision:** The Conversation Plane Filter (CPF) is a dedicated component within CAL responsible for filtering conversation-plane traffic against operator-defined policy before any action is permitted to execute.

**Consequences:** All conversation-plane traffic is subject to CPF evaluation. Policy definitions must be expressible in a form CPF can evaluate at runtime. CPF must operate at conversation speed without introducing unacceptable latency. CPF becomes the natural extension point for new policy types.

**Rejected alternatives:** Embedding filtering logic directly in application code (not enforceable, not auditable); post-hoc filtering after action execution (violates the principle of pre-execution enforcement).

---

## ADR-008: Forge Architecture — Runtime Enforcement Below the Application Stack

**Status:** Accepted

**Context:** Policy enforcement for AI agents can be implemented at various levels: application code, middleware, runtime platform, or infrastructure. The level chosen determines the strength of the guarantee.

**Decision:** Forge enforces agent execution policy at runtime, below the application stack, via cryptographic identity and operator-defined policy. Enforcement occurs at the platform level, not within application logic.

**Consequences:** Applications cannot bypass enforcement by modifying their own code. Cryptographic identity is required for every agent — agents without valid identity cannot execute. Operator-defined policy is external to agent code and managed at the platform level. This creates a strong separation of concerns but requires platform-level integration for all deployments.

**Rejected alternatives:** Application-level middleware enforcement (can be disabled or bypassed by the application); infrastructure-level enforcement only (too coarse-grained for conversation-level policy); trust-based enforcement without cryptographic identity (insufficient for enterprise compliance requirements).

---

## ADR-009: Forge CAL — Key Component Composition

**Status:** Accepted

**Context:** CAL must support multiple enforcement concerns: policy evaluation, identity verification, context tracking, trust scoring, and audit. A monolithic implementation would be difficult to extend and test.

**Decision:** CAL is composed of discrete, named components: CPF (Conversation Plane Filter), AIR (Agent Identity Resolution), CTX-ID (Context Identity), PEE (Policy Evaluation Engine), TrustFlow/SIS (Trust Scoring / Security Intelligence Service), and CAL Verifier Cluster. Each component has a defined responsibility within the enforcement pipeline.

**Consequences:** Components can be developed, tested, and evolved independently. The enforcement pipeline has a defined order of operations. Inter-component contracts must be explicitly defined. Adding new enforcement concerns means adding new components rather than modifying existing ones. Operational complexity increases with component count.

**Rejected alternatives:** A single monolithic enforcement engine (poor separation of concerns, difficult to test and extend); a plugin architecture with dynamic loading (too much runtime unpredictability for a security-critical path).