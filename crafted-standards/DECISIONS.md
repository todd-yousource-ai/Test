

# DECISIONS.md

---

## Table of Contents

1. [Tasklib Subsystem Decisions](#tasklib-subsystem-decisions)
2. [Forge Platform Subsystem Decisions](#forge-platform-subsystem-decisions)

---

# Tasklib Subsystem Decisions

## DEC-TL-001: Use Tasklib as a Pipeline Validation Vehicle, Not a Production System

**Status:** Accepted

**Context:** The Crafted Dev Agent build pipeline needed end-to-end validation that the full dependency chain — from documentation through scaffold to working code — could close with real merges at each step. A real production system would introduce unnecessary complexity and risk for this validation purpose.

**Decision:** Define a deliberately simple Python task management library (`tasklib`) whose sole purpose is to prove the pipeline can close a complete dependency chain: docs → scaffold → model → storage → CLI. It is explicitly not a production system.

**Consequences:** The library must remain minimal; feature creep is rejected by design. All architectural choices in tasklib are subordinate to pipeline validation goals. Tasklib cannot be referenced as a production dependency by other subsystems. Future pipeline changes can be validated against this known-good baseline.

**Rejected alternatives:** Using an existing open-source library (would not exercise documentation-first pipeline stages); building a production-grade task system (unnecessary complexity for a validation objective); using unit tests alone without a real library (would not validate merge gates and cross-PR dependency resolution).

---

## DEC-TL-002: Documentation-First Dependency Chain

**Status:** Accepted

**Context:** The pipeline must prove that a documentation PR fires the merge gate and that downstream PRs recognize the merge. This requires documentation to be the first stage in the dependency chain rather than an afterthought.

**Decision:** The full dependency chain is ordered as: documentation → scaffold → model → storage → CLI. Documentation (README, ARCHITECTURE overview, API reference) is the first deliverable and first merged artifact. All subsequent stages depend on the documentation PR having merged successfully.

**Consequences:** No scaffold or code PR can proceed until the documentation PR has merged. The merge gate must be able to detect documentation PR merge status. Documentation changes that affect downstream contracts require re-validation of the full chain. This enforces a design-before-code discipline.

**Rejected alternatives:** Code-first with retroactive documentation (would not validate the docs merge gate); parallel documentation and code PRs (would not prove sequential dependency resolution).

---

## DEC-TL-003: Multi-Package Scaffold with Subpackage Directories

**Status:** Accepted

**Context:** The scaffold PR must validate that the pipeline can handle multiple package directories and mirror files to the local test workspace correctly. A single flat package would not exercise this capability.

**Decision:** The Python package scaffold uses subpackage directories (model, storage, CLI as separate subpackages). The scaffold PR must demonstrate that multiple package directories are correctly mirrored to the local test workspace.

**Consequences:** Each subpackage becomes an independently addressable unit in the dependency chain. Import resolution across subpackages must work locally before CI. The scaffold structure constrains how code PRs organize their files. Directory mirroring logic in the pipeline must handle nested package structures.

**Rejected alternatives:** Single flat module (would not validate multi-directory mirroring); monolithic single-file implementation (would not test cross-package imports); namespace packages without `__init__.py` (adds implicit import complexity irrelevant to validation goals).

---

## DEC-TL-004: Local Import Resolution Before CI

**Status:** Accepted

**Context:** Code PRs that import from previously-merged PRs must resolve those imports locally before CI runs. Without this, developers would depend entirely on CI for feedback, slowing the validation loop and masking pipeline integration issues.

**Decision:** Code PRs that depend on artifacts from earlier stages (e.g., CLI importing from model, storage importing from model) must resolve those imports in the local test workspace before being submitted to CI. The pipeline must ensure previously-merged artifacts are available locally.

**Consequences:** The local workspace must maintain state across PR merges — previously merged packages must remain available. The pipeline must implement a workspace synchronization mechanism. CI failures due to missing local imports indicate a pipeline defect, not a code defect. This adds a pre-CI validation step to the developer workflow.

**Rejected alternatives:** CI-only import resolution (hides pipeline bugs until CI, slow feedback); vendoring all dependencies into each PR (duplicates code, defeats dependency chain validation); mock imports (would not prove real dependency resolution).

---

# Forge Platform Subsystem Decisions

## DEC-FG-001: Runtime Policy Enforcement Below the Application Stack

**Status:** Accepted

**Context:** Enterprise AI agents require policy enforcement that cannot be bypassed by application-level code. Enforcement at the application layer is vulnerable to misconfiguration, agent prompt injection, and developer error. A lower-level enforcement plane is needed to provide cryptographic guarantees.

**Decision:** Forge enforces agent execution policy at runtime, below the application stack, via cryptographic identity and operator-defined policy. No agent action executes without passing through the enforcement plane regardless of what the application layer requests.

**Consequences:** All agent-originated actions must transit the enforcement layer — there is no bypass path. Application developers cannot override or circumvent policy. The enforcement layer must operate with minimal latency to avoid degrading agent performance. The platform must maintain cryptographic key material and identity infrastructure. Debugging requires visibility into both the application layer and the enforcement plane.

**Rejected alternatives:** Application-level middleware enforcement (bypassable, no cryptographic guarantees); network-level enforcement only (cannot inspect semantic agent actions); post-hoc audit without runtime blocking (permits policy violations to execute before detection).

---

## DEC-FG-002: CAL as the Single Enforcement Choke Point

**Status:** Accepted

**Context:** With multiple types of agent-originated actions (tool calls, data reads, API invocations, agent handoffs), there is a risk of enforcement fragmentation if each action type has its own policy evaluation path. A single choke point simplifies reasoning about security invariants.

**Decision:** The Conversation Abstraction Layer (CAL) is the single enforcement choke point for all agent-originated actions. No tool call, data read, API invocation, or agent handoff executes without passing through a CAL policy evaluation. CAL sits above the VTZ enforcement plane and below application orchestration.

**Consequences:** All new action types must be routed through CAL — adding a new agent capability requires CAL integration. CAL becomes a potential single point of failure and must be designed for high availability. Performance of the entire agent system is bounded by CAL throughput. Security audits can focus on a single enforcement surface. CAL's component set (CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, CAL Verifier Cluster) must be co-designed to handle all action categories.

**Rejected alternatives:** Per-action-type enforcement layers (fragmented security surface, harder to audit, risk of inconsistent policy application); enforcement at the LLM provider boundary only (misses internal agent-to-agent handoffs and local tool calls); distributed policy evaluation without a choke point (cannot guarantee total mediation).

---

## DEC-FG-003: CPF as the Conversation Plane Filter

**Status:** Accepted

**Context:** Within the CAL enforcement choke point, there needs to be a dedicated component responsible for filtering and inspecting the conversation plane — the stream of messages, tool calls, and context flowing through agent interactions. This filtering must happen before policy evaluation to normalize and classify the action.

**Decision:** The Conversation Plane Filter (CPF) is a dedicated component within CAL responsible for intercepting and filtering all conversation-plane traffic before it reaches policy evaluation. It is the first point of contact within the enforcement path.

**Consequences:** CPF must understand the structure of all supported conversation formats and tool-call schemas. Changes to LLM provider APIs or agent frameworks require CPF updates. CPF introduces a processing step before policy evaluation, contributing to overall latency. CPF must be stateless or minimally stateful to support horizontal scaling.

**Rejected alternatives:** Inline policy evaluation without pre-filtering (mixes concerns, harder to extend for new formats); application-layer filtering before CAL (bypassable, violates the below-application-stack enforcement model); post-policy filtering (too late — policy must evaluate normalized, classified actions).

---

## DEC-FG-004: Cryptographic Identity as the Foundation for Agent Trust

**Status:** Accepted

**Context:** Enterprise deployments require that agent identity be unforgeable and verifiable. Token-based or credential-based identity systems are vulnerable to theft, replay, and impersonation. Operators need assurance that the agent executing an action is the agent that was authorized.

**Decision:** Forge uses cryptographic identity (CTX-ID and the CAL Verifier Cluster) as the foundation for establishing and verifying agent trust. Every agent action is bound to a cryptographic identity that is verified at enforcement time. TrustFlow/SIS provides the trust scoring and identity services.

**Consequences:** The platform must manage key lifecycle (generation, rotation, revocation) for all agents. Cryptographic operations add latency to every enforcement evaluation. Compromise of identity key material is a critical security event requiring incident response procedures. All components in the enforcement path must have access to verification infrastructure. Interoperability with external identity providers requires bridging to the cryptographic identity model.

**Rejected alternatives:** Bearer token identity (replayable, no cryptographic binding to action); OAuth/OIDC alone (designed for user identity, not runtime agent action binding); no identity verification with post-hoc attribution (permits unauthorized actions to execute).

---

## DEC-FG-005: Operator-Defined Policy as the Governance Model

**Status:** Accepted

**Context:** Different enterprises have different compliance requirements, risk tolerances, and operational constraints for their AI agents. A hardcoded policy model cannot accommodate this diversity. Operators — not the platform vendor and not the agents themselves — must define what is permitted.

**Decision:** Policy is operator-defined: enterprise operators author and manage the policy rules that govern agent behavior. The PEE (Policy Evaluation Engine) within CAL evaluates these operator-defined policies at runtime against every agent action.

**Consequences:** The platform must provide a policy authoring and management interface. Policy syntax and semantics must be well-defined and documented. Operators bear responsibility for policy correctness — the platform enforces but does not judge policy quality. Policy changes take effect at runtime without requiring agent redeployment. The PEE must be performant enough to evaluate potentially complex policy rules on every action.

**Rejected alternatives:** Vendor-defined default policies only (insufficient for enterprise diversity); agent-self-governance (agents cannot be trusted to enforce their own constraints); compile-time policy embedding (requires redeployment for policy changes, incompatible with operational agility).