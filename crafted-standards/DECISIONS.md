# DECISIONS.md

---

## ADR-001: Use a Deliberately Simple Library to Validate the Build Pipeline
**Status:** Accepted
**Context:** The Crafted Dev Agent build pipeline needs end-to-end validation proving that documentation PRs fire merge gates, scaffold PRs mirror files correctly, code PRs resolve imports from previously-merged PRs, and the full dependency chain closes from docs through working code. A complex production system would conflate pipeline validation failures with domain-logic failures.
**Decision:** Define a minimal Python task management library (`tasklib`) whose sole purpose is to exercise every stage of the dependency chain — docs → scaffold → model → storage → CLI — without production ambitions.
**Consequences:** The library must remain intentionally simple; feature richness is explicitly not a goal. Any complexity added must serve a pipeline-validation purpose. The library is not intended for production use.
**Rejected alternatives:** Using an existing open-source project (too many uncontrolled variables); using a production Forge subsystem as the test target (failures would be ambiguous — pipeline bug vs. domain bug); a purely synthetic no-op package (would not exercise real import resolution or subpackage interactions).

---

## ADR-002: Five-Stage Linear Dependency Chain (Docs → Scaffold → Model → Storage → CLI)
**Status:** Accepted
**Context:** The pipeline must prove that each stage's merge is visible to the next stage downstream. A branching or parallel dependency graph would weaken the proof that sequential merge-gate propagation works.
**Decision:** Enforce a strict linear dependency chain: documentation PR merges first, scaffold PR depends on docs, model code depends on scaffold, storage depends on model, and CLI depends on storage.
**Consequences:** No stage may be built or merged out of order. CI must fail if a stage's upstream dependency has not yet merged. This serializes the build but maximizes confidence in merge-gate correctness.
**Rejected alternatives:** A diamond dependency graph (harder to diagnose failures in the gate); a single monolithic PR (would not test inter-PR dependency resolution at all).

---

## ADR-003: Documentation Set as the First Merge-Gate Trigger
**Status:** Accepted
**Context:** The pipeline must prove that a documentation-only PR can fire the merge gate and that downstream PRs recognize that merge event.
**Decision:** The first PR in the chain is a documentation set comprising a README, an ARCHITECTURE overview, and an API reference. Its merge must be the trigger that unblocks the scaffold PR.
**Consequences:** Documentation is not decorative — it is a first-class build artifact whose presence is a prerequisite for subsequent stages. The merge gate must be configured to treat doc PRs identically to code PRs.
**Rejected alternatives:** Starting with the scaffold PR and adding docs later (would not validate that docs-only merges propagate through the gate); embedding docs inside the scaffold PR (would collapse two validation stages into one).

---

## ADR-004: Scaffold PR Must Create Multiple Subpackage Directories
**Status:** Accepted
**Context:** The pipeline must prove that a scaffold PR can mirror multiple package directories into the local test workspace and that later code PRs can import from those directories.
**Decision:** The scaffold PR creates the full Python package structure with subpackage directories (at minimum: model, storage, CLI entry point) as empty or `__init__.py`-only packages.
**Consequences:** Subsequent code PRs must place their modules inside the directories established by the scaffold. The scaffold defines the canonical package layout; deviations require re-scaffolding.
**Rejected alternatives:** A flat single-directory layout (would not test subpackage mirroring); generating directories on-demand in each code PR (would not test that the scaffold merge is visible to downstream PRs).

---

## ADR-005: Code PRs Must Resolve Imports from Previously-Merged PRs Locally Before CI
**Status:** Accepted
**Context:** A key validation goal is proving that code generated in one PR can import symbols defined in a previously-merged PR, and that this resolution happens in the local test workspace before CI runs remotely.
**Decision:** Each code PR must demonstrate local import resolution against the workspace state left by all previously-merged PRs. CI may re-verify, but local resolution is the primary proof point.
**Consequences:** The workspace must accumulate merged artifacts in a way that preserves Python import paths. Editable installs or `sys.path` manipulation must be deterministic and documented. A code PR that passes CI but fails local import resolution is considered a pipeline defect.
**Rejected alternatives:** Relying solely on CI for import verification (would not prove local workspace fidelity); vendoring dependencies into each PR (would sidestep the merge-gate proof entirely).

---

## ADR-006: Python as the Implementation Language
**Status:** Accepted
**Context:** The validation library needs a language with straightforward package/subpackage semantics, widespread CI tooling, and minimal build ceremony so that pipeline behavior — not language toolchain behavior — is what is being tested.
**Decision:** Implement `tasklib` in Python with standard `__init__.py`-based packaging.
**Consequences:** All tooling assumptions (import resolution, package discovery, test runners) are Python-specific. The pipeline validation results are transferable in principle but not in tooling detail to other languages.
**Rejected alternatives:** TypeScript/Node (module resolution rules are more complex and would obscure pipeline-specific failures); Rust (compile times and cargo workspace semantics add confounding variables); Go (flat package model would not test subpackage mirroring).

---

## ADR-007: Forge Runtime Enforcement via Conversation Abstraction Layer (CAL) as the Universal Choke Point
**Status:** Accepted
**Context:** Enterprise AI agents can originate tool calls, data reads, API invocations, and agent handoffs. Without a single enforcement point, policy must be duplicated across every integration surface, creating gaps.
**Decision:** All agent-originated actions must pass through the CAL policy evaluation layer. No tool call, data read, API invocation, or agent handoff executes without a CAL evaluation. CAL sits above the VTZ enforcement plane and below application orchestration.
**Consequences:** Every new integration surface (tool, API, data source, agent-to-agent handoff) must register with CAL. Bypass of CAL is treated as a security violation. Latency is added to every agent action, requiring the CAL evaluation path to be highly optimized.
**Rejected alternatives:** Per-tool policy enforcement (creates policy fragmentation and audit gaps); enforcement at the application orchestration layer (too easy to bypass; not below the application stack); enforcement only at the network/API gateway level (cannot inspect semantic intent of agent actions).

---

## ADR-008: Cryptographic Identity as the Foundation for Agent Trust
**Status:** Accepted
**Context:** Enterprise environments require non-repudiable proof of which agent performed which action under which policy. Session tokens or API keys alone are insufficient because they can be shared, replayed, or do not bind to a specific policy evaluation context.
**Decision:** Forge uses cryptographic identity (CTX-ID and related constructs within CAL) to bind every agent action to a verifiable identity. Policy evaluation references this identity; audit logs are cryptographically attributable.
**Consequences:** Key management, certificate lifecycle, and identity provisioning become operational prerequisites. Agents without valid cryptographic identity cannot execute any action. The system must handle identity revocation, rotation, and compromise scenarios.
**Rejected alternatives:** OAuth/OIDC tokens alone (do not provide action-level binding or cryptographic non-repudiation); shared service accounts (destroy attribution); application-layer identity assertions (can be forged by a compromised application).

---

## ADR-009: Policy Enforcement Below the Application Stack
**Status:** Accepted
**Context:** If policy enforcement lives inside the application layer, a bug or compromise in the application can bypass policy. Enterprise customers require assurance that policy cannot be circumvented by application-level code.
**Decision:** Forge enforces policy at runtime below the application stack, via the VTZ enforcement plane and CAL. Application orchestration code cannot skip or override policy evaluation.
**Consequences:** The enforcement layer must be deployed and managed independently of application code. Application developers cannot add policy exceptions without operator approval. Debugging requires visibility into both the application layer and the sub-application enforcement layer.
**Rejected alternatives:** Middleware-based enforcement within the application framework (bypassable by application code); compile-time policy checks only (cannot enforce runtime context like data sensitivity or real-time trust scores); pure network-layer enforcement (cannot evaluate semantic policy).

---

## ADR-010: CAL Components — CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, Verifier Cluster
**Status:** Accepted
**Context:** The CAL choke point requires multiple specialized functions: filtering conversation-plane traffic, managing action-identity resolution, maintaining contextual identity, evaluating policy expressions, computing trust flow, and verifying claims. These could be monolithic or decomposed.
**Decision:** Decompose CAL into discrete components: CPF (Conversation Plane Filter), AIR (Action-Identity Resolution), CTX-ID (Contextual Identity), PEE (Policy Expression Evaluation), TrustFlow/SIS (trust scoring), and the CAL Verifier Cluster. Each component has a defined responsibility boundary.
**Consequences:** Components can be developed, tested, and scaled independently. Inter-component contracts must be precisely defined. Failure in one component must not silently degrade policy enforcement — it must fail closed. Operational complexity increases relative to a monolithic design.
**Rejected alternatives:** A monolithic CAL implementation (simpler initially but harder to scale, test, and evolve); a microservices-per-action architecture (too fine-grained, excessive network overhead for a latency-sensitive enforcement path).