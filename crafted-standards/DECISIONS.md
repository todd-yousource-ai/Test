

# DECISIONS.md

---

## ADR-001: Use a Deliberately Simple Library to Validate the Build Pipeline
**Status:** Accepted
**Context:** The Crafted Dev Agent pipeline needs end-to-end validation that a complete dependency chain — from documentation through scaffold to working code — can close with real merges at each step. A complex production system would introduce unnecessary variables and make it difficult to isolate pipeline failures from application logic failures.
**Decision:** Define `tasklib`, a deliberately simple Python task management library, whose sole purpose is to prove the pipeline can process a full dependency chain: docs → scaffold → model → storage → CLI.
**Consequences:** The library is not intended for production use. All design choices optimize for pipeline validation, not feature richness. Future production systems will inherit proven pipeline mechanics but not `tasklib` code.
**Rejected alternatives:** Using an existing open-source project as the validation target was rejected because it would introduce external dependencies and versioning concerns unrelated to pipeline validation. Building a production-grade system first was rejected because pipeline correctness must be established before trusting it with real deliverables.

---

## ADR-002: Linear Dependency Chain for Pipeline Stages
**Status:** Accepted
**Context:** The pipeline must demonstrate that each stage recognizes the merge of its predecessor before proceeding. Parallel or loosely-ordered stages would not adequately prove merge-gate propagation.
**Decision:** Enforce a strict linear dependency chain: documentation PR → scaffold PR → model PR → storage PR → CLI PR. Each stage depends on the successful merge of the prior stage.
**Consequences:** Stages cannot be reordered or parallelized during validation. A failure at any stage blocks all downstream stages, which is the desired behavior for proving gate correctness. This serialization increases total wall-clock time but guarantees causal ordering.
**Rejected alternatives:** A DAG-based dependency graph with parallel branches was considered but rejected because it would complicate the initial validation without adding confidence in the core merge-gate mechanism.

---

## ADR-003: Documentation PR as the First Merge Gate Trigger
**Status:** Accepted
**Context:** The pipeline must prove that a documentation-only PR can fire the merge gate and that downstream PRs recognize that merge event. Documentation is the earliest artifact in the chain and has no code dependencies.
**Decision:** The first PR in the chain is a documentation set (README, ARCHITECTURE overview, API reference). Its merge triggers the gate that unblocks the scaffold PR.
**Consequences:** Documentation becomes a first-class pipeline artifact, not a side effect. The merge-gate infrastructure must treat documentation PRs identically to code PRs. Documentation must be committed to the repository (not external wikis or hosting) so the merge event is observable.
**Rejected alternatives:** Starting with a code scaffold and treating documentation as a parallel or post-hoc artifact was rejected because it would not validate that non-code PRs correctly trigger the merge gate.

---

## ADR-004: Scaffold PR Must Mirror Multiple Package Directories to Local Workspace
**Status:** Accepted
**Context:** The scaffold stage creates the Python package structure with subpackage directories. The pipeline must prove that multi-directory file creation works correctly and that the local test workspace reflects the full package layout.
**Decision:** The scaffold PR creates multiple subpackage directories (model, storage, CLI at minimum) and the pipeline mirrors these files to the local test workspace before downstream code PRs begin.
**Consequences:** The scaffold must define all subpackage directories upfront. Downstream code PRs assume the directory structure exists. Any mismatch between the scaffold and expected import paths will surface as an immediate failure, which is the desired validation behavior.
**Rejected alternatives:** Generating directories on-demand during each code PR was rejected because it would not validate that the scaffold stage correctly provisions the full workspace in a single atomic operation.

---

## ADR-005: Local Import Resolution Before CI for Code PRs
**Status:** Accepted
**Context:** Code PRs that import from previously-merged PRs (e.g., the CLI PR importing from the model and storage packages) must resolve those imports locally before CI runs. This validates that the pipeline correctly materializes dependencies from merged PRs into the working tree.
**Decision:** Code PRs must resolve imports from previously-merged packages in the local test workspace prior to CI execution. The pipeline is responsible for ensuring that merged artifacts are available locally, not just in the remote repository.
**Consequences:** The pipeline must include a workspace synchronization step that pulls merged artifacts into the local environment. CI failures due to missing imports indicate a pipeline defect, not a code defect. This constrains the CI environment to operate on a fully-hydrated workspace.
**Rejected alternatives:** Relying solely on CI to install previously-merged packages from a package registry was rejected because it would not validate local workspace integrity and would introduce registry infrastructure as an unnecessary dependency for initial validation.

---

## ADR-006: Python as the Implementation Language
**Status:** Accepted
**Context:** The validation library needs a language with straightforward package/subpackage semantics, widely-understood import mechanics, and minimal build toolchain complexity so that pipeline behavior — not language tooling — is what is being validated.
**Decision:** Implement `tasklib` in Python with standard Python package conventions (`__init__.py`, subpackage directories, standard imports).
**Consequences:** The pipeline must support Python project conventions (e.g., `pyproject.toml` or `setup.py`, `__init__.py` files). Pipeline tooling for other languages is not validated by this exercise.
**Rejected alternatives:** Compiled languages (Go, Rust) were rejected because their build/link steps would add complexity unrelated to pipeline merge-gate validation. JavaScript/TypeScript was considered but rejected in favor of Python's simpler and more explicit package structure.

---

## ADR-007: Forge Subsystem — CAL as the Universal Enforcement Choke Point
**Status:** Accepted
**Context:** Enterprise AI agents perform diverse actions (tool calls, data reads, API invocations, agent handoffs). Without a single enforcement point, policy evaluation would be scattered across application code, creating gaps and inconsistencies.
**Decision:** The Conversation Abstraction Layer (CAL) is the mandatory choke point for all agent-originated actions. No tool call, data read, API invocation, or agent handoff executes without passing through a CAL policy evaluation. CAL sits above the VTZ enforcement plane and below application orchestration.
**Consequences:** All agent actions must be routed through CAL; there is no bypass path. Application orchestration layers cannot directly invoke tools or APIs. This creates a hard dependency on CAL availability for all agent operations. CAL must be low-latency to avoid becoming a performance bottleneck.
**Rejected alternatives:** Distributed policy enforcement at each tool/API boundary was rejected because it cannot guarantee consistent policy application and creates an audit gap. Application-layer middleware was rejected because it operates above the trust boundary and can be circumvented by the agent or orchestration framework.

---

## ADR-008: Forge Subsystem — CPF as the Conversation Plane Filter
**Status:** Accepted
**Context:** Within the CAL enforcement architecture, there must be a specific component responsible for filtering at the conversation plane — inspecting and enforcing policy on the content and intent of agent communications before they translate into actions.
**Decision:** The Conversation Plane Filter (CPF) is a key component within CAL responsible for filtering agent conversations at the conversation plane level.
**Consequences:** CPF must have visibility into the full conversation context to make filtering decisions. It becomes a dependency for CAL's policy evaluation pipeline. CPF logic must be separable from other CAL components (AIR, CTX-ID, PEE, TrustFlow/SIS) to allow independent evolution and testing.
**Rejected alternatives:** Combining conversation filtering with action-level enforcement in a single monolithic component was rejected because it would conflate two distinct concerns (content inspection vs. action authorization) and reduce modularity.

---

## ADR-009: Forge Subsystem — Cryptographic Identity as the Foundation for Agent Trust
**Status:** Accepted
**Context:** Enterprise environments require strong guarantees about which agent is performing an action and under what authority. Software-level identity (API keys, tokens) can be spoofed or replayed if not anchored to a cryptographic root of trust.
**Decision:** Forge uses cryptographic identity as the foundation for agent trust. Agent identity is established and verified cryptographically, and all policy enforcement references this identity. Key components include CTX-ID (contextual identity) and the CAL Verifier Cluster.
**Consequences:** Every agent must possess a cryptographic identity before it can interact with the platform. Identity issuance, rotation, and revocation become critical operational concerns. Policy definitions are bound to cryptographic identities, not ambient credentials. This requires key management infrastructure.
**Rejected alternatives:** Bearer token–based identity was rejected because it lacks non-repudiation and is vulnerable to replay attacks. Relying on network-layer identity (e.g., mTLS alone) was rejected because it identifies machines, not agents, and does not support multi-agent environments on shared infrastructure.

---

## ADR-010: Forge Subsystem — Runtime Enforcement Below the Application Stack
**Status:** Accepted
**Context:** Policy enforcement that operates within or above the application stack can be bypassed by application bugs, misconfigurations, or adversarial agents that manipulate the orchestration layer.
**Decision:** Forge enforces agent execution at runtime, below the application stack, via the VTZ enforcement plane. CAL and its components operate at a layer that the application and agent cannot circumvent.
**Consequences:** The enforcement layer must be deployed and configured independently of the application. Application developers cannot weaken or bypass policy through application code. This introduces infrastructure complexity and a hard requirement that the enforcement plane is provisioned before agents are activated.
**Rejected alternatives:** Application-level middleware enforcement was rejected because it is within the agent's trust boundary and can be manipulated. Host OS–level enforcement was considered too coarse-grained for per-agent, per-action policy decisions.

---

## ADR-011: Forge Subsystem — Operator-Defined Policy
**Status:** Accepted
**Context:** Different enterprises have different compliance requirements, risk tolerances, and operational constraints. A one-size-fits-all policy model would either be too permissive for regulated industries or too restrictive for agile environments.
**Decision:** Policy is operator-defined. Enterprise operators author and deploy policies that govern agent behavior, and these policies are enforced by CAL and the VTZ plane. The platform provides the enforcement mechanism; the operator provides the rules.
**Consequences:** The platform must provide a policy authoring and deployment interface. Policy must be versioned, auditable, and testable. The platform cannot assume any specific policy content — it must be general-purpose in its enforcement capabilities. Operators bear responsibility for policy correctness.
**Rejected alternatives:** Hardcoded platform policies were rejected because they cannot accommodate diverse enterprise requirements. Fully agent-self-governed policies were rejected because they violate the principle that the enforcer must be independent of the enforced.