

# DECISIONS.md

---

## ADR-001: Use a Deliberately Simple Task Library as Pipeline Validation Vehicle

**Status:** Accepted

**Context:** The Crafted Dev Agent build pipeline needed an end-to-end proof that the full dependency chain — from documentation through scaffold to working code — could close with real merges at each step. A production-grade system would introduce unnecessary complexity and obscure pipeline validation failures behind domain-specific bugs.

**Decision:** Define `tasklib` as a deliberately simple Python task management library whose sole purpose is to validate the build pipeline. It is explicitly not a production system. Its design is driven entirely by what exercises the pipeline's merge gates and dependency resolution.

**Consequences:** The library's feature set is minimal and constrained to what proves the pipeline works. Any architectural decisions within tasklib are subordinated to pipeline validation goals. Future production libraries should not inherit tasklib's intentionally simplistic patterns.

**Rejected alternatives:** Using an existing open-source library (rejected because it would not exercise scaffold generation and full dependency chain closure). Building a production-grade system first (rejected because it conflates pipeline validation with domain complexity).

---

## ADR-002: Five-Stage Linear Dependency Chain (Docs → Scaffold → Model → Storage → CLI)

**Status:** Accepted

**Context:** The pipeline must prove that each stage's merge is recognized by downstream stages, that import resolution works against previously-merged code, and that CI gates fire correctly at each transition.

**Decision:** The tasklib dependency chain is strictly linear with five stages: documentation → scaffold → model → storage → CLI. Each stage produces a PR that depends on all prior stages having merged successfully.

**Consequences:** No stage can be built or merged out of order. This constrains parallelism but guarantees that every merge-gate transition is exercised exactly once. The model layer must exist before storage, and storage before CLI.

**Rejected alternatives:** A diamond dependency graph (rejected because it adds complexity without additional pipeline validation coverage). A two-stage chain (rejected because it would not prove multi-hop dependency resolution).

---

## ADR-003: Documentation PR as the First Merge Gate Trigger

**Status:** Accepted

**Context:** The pipeline must prove that a documentation-only PR can fire the merge gate and that downstream PRs recognize that merge event. Many CI systems treat documentation PRs as no-ops.

**Decision:** The first stage in the dependency chain is a documentation PR containing a README, ARCHITECTURE overview, and API reference. This PR must pass through the full merge gate — it is not exempted or fast-tracked.

**Consequences:** The merge gate must be configured to treat documentation PRs as first-class artifacts. Downstream scaffold generation cannot begin until the docs PR has merged. This validates that non-code artifacts participate in the dependency chain.

**Rejected alternatives:** Starting the chain with the scaffold PR (rejected because it would leave documentation merge-gate behavior unvalidated). Treating docs as a side-channel artifact outside the dependency chain (rejected because it defeats the validation goal).

---

## ADR-004: Scaffold PR Mirrors Multiple Package Directories to Local Test Workspace

**Status:** Accepted

**Context:** The pipeline must prove that scaffold generation correctly creates subpackage directory structures and that these structures are faithfully mirrored to the local test workspace where subsequent code PRs will resolve imports.

**Decision:** The scaffold PR creates a Python package scaffold with multiple subpackage directories. The pipeline infrastructure mirrors these directories to the local test workspace upon merge.

**Consequences:** The local test workspace must support multi-directory package layouts. Import resolution in later stages (model, storage, CLI) depends on correct mirroring. Any failure in directory mirroring will surface as import errors in the model stage, providing a clear diagnostic signal.

**Rejected alternatives:** A single flat module with no subpackages (rejected because it would not exercise directory mirroring). Generating scaffold inline during code PRs (rejected because it conflates scaffold validation with code generation validation).

---

## ADR-005: Code PRs Must Resolve Imports from Previously-Merged PRs Locally Before CI

**Status:** Accepted

**Context:** Code generation stages (model, storage, CLI) import symbols from packages introduced by earlier PRs. If import resolution is deferred to CI, failures arrive late and are difficult to diagnose.

**Decision:** Code PRs must resolve all imports from previously-merged PRs in the local test workspace before being submitted to CI. The pipeline validates import resolution as a pre-CI gate.

**Consequences:** The local workspace must contain all merged artifacts at the time a new code PR is generated. The agent pipeline must sequence workspace updates before code generation. This adds a synchronization requirement but catches dependency errors earlier.

**Rejected alternatives:** Relying solely on CI to catch import errors (rejected because it defeats the goal of proving local dependency chain closure). Vendoring dependencies into each PR (rejected because it does not exercise cross-PR import resolution).

---

## ADR-006: Forge Platform Enforces Policy via Conversation Abstraction Layer (CAL) as Single Choke Point

**Status:** Accepted

**Context:** Enterprise AI agents can originate tool calls, data reads, API invocations, and agent handoffs. Without a single enforcement point, policy must be duplicated across every integration surface, creating gaps.

**Decision:** All agent-originated actions must pass through the Conversation Abstraction Layer (CAL) for policy evaluation. No tool call, data read, API invocation, or agent handoff executes without CAL clearance. CAL sits above the VTZ enforcement plane and below application orchestration.

**Consequences:** Every integration surface must route through CAL — there is no bypass path. This creates a single point of enforcement but also a potential bottleneck and single point of failure. All policy logic concentrates in CAL's components (CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, CAL Verifier Cluster). Application-layer orchestrators are explicitly forbidden from making independent policy decisions.

**Rejected alternatives:** Distributed per-tool policy enforcement (rejected because it creates policy gaps and inconsistency). Application-layer policy middleware (rejected because it can be bypassed by agents that interact below the application stack).

---

## ADR-007: Conversation Plane Filter (CPF) as CAL's Primary Enforcement Mechanism

**Status:** Accepted

**Context:** Within CAL, a specific component must perform the actual filtering and policy evaluation on the conversation plane. Separating the filtering concern from identity, context, and trust evaluation enables independent evolution of each.

**Decision:** The Conversation Plane Filter (CPF) is the primary enforcement mechanism within CAL. It operates as the innermost gate through which all conversation-plane traffic must pass.

**Consequences:** CPF must be highly performant since it is in the hot path of every agent action. Other CAL components (AIR, CTX-ID, PEE, TrustFlow/SIS) feed data into CPF but do not independently block or allow actions. CPF's policy evaluation logic must be deterministic and auditable.

**Rejected alternatives:** Merging filtering into the trust evaluation layer (rejected because it couples performance-sensitive filtering with computationally heavier trust calculations). Implementing filtering at the VTZ plane (rejected because it is too low-level to express conversation-plane semantics).

---

## ADR-008: Cryptographic Identity as the Foundation for Agent Authentication

**Status:** Accepted

**Context:** Enterprise AI agents must be authenticated before policy can be applied. Token-based or session-based identity schemes are vulnerable to replay, delegation, and impersonation attacks in multi-agent environments.

**Decision:** Forge uses cryptographic identity (CTX-ID and related components) as the foundation for agent authentication. Agent identity is bound cryptographically, not by bearer tokens or session cookies.

**Consequences:** All agents must possess and manage cryptographic credentials. Identity verification is computationally more expensive than token lookup but provides stronger guarantees. The platform must handle key lifecycle management, rotation, and revocation. Agents without valid cryptographic identity cannot interact with any Forge-protected resource.

**Rejected alternatives:** OAuth/bearer token identity (rejected because tokens can be replayed and do not bind to agent context). Mutual TLS only (rejected because it authenticates transport endpoints, not agent-level identity within a conversation).

---

## ADR-009: Runtime Enforcement Below the Application Stack

**Status:** Accepted

**Context:** Policy enforcement implemented at the application layer can be circumvented by agents that operate at lower abstraction levels or by misconfigured application code. Enforcement must be positioned where it cannot be bypassed.

**Decision:** Forge enforces agent execution policy at runtime, below the application stack, via the VTZ enforcement plane. Application code cannot opt out of or circumvent policy evaluation.

**Consequences:** The enforcement plane must be integrated at a level that intercepts all agent actions regardless of the application framework in use. This imposes deployment and integration constraints — Forge cannot be adopted as a simple library import. Performance overhead at the sub-application layer must be carefully managed.

**Rejected alternatives:** Application-layer middleware (rejected because applications can be misconfigured or bypassed). Static analysis / pre-deployment policy checking only (rejected because it cannot enforce runtime-dynamic policies such as context-dependent access control).

---

## ADR-010: Operator-Defined Policy as the Governance Model

**Status:** Accepted

**Context:** AI agent behavior policies vary dramatically across enterprises, industries, and regulatory environments. Hardcoded policies would be too rigid; fully agent-defined policies would be insecure.

**Decision:** Policies are defined by operators (enterprise administrators), not by agents or application developers. Operators configure what actions are permitted, under what conditions, for which agent identities.

**Consequences:** The platform must provide a policy authoring and management interface for operators. Agents and application developers cannot override operator policies. Policy expressiveness must be sufficient for enterprise use cases (RBAC, ABAC, context-sensitive rules) without requiring operators to write code.

**Rejected alternatives:** Agent-defined policies (rejected because agents should not govern their own permissions). Developer-embedded policies (rejected because they cannot be updated independently of application deployments). Hardcoded default policies (rejected because they cannot accommodate enterprise diversity).