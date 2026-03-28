# DECISIONS.md

## Use a deliberately simple Python task management library to validate the end-to-end pipeline
**Status:** Accepted  
**Context:** The TRD states that `tasklib` is not intended to be a production system. Its stated purpose is to validate that the Crafted Dev Agent build pipeline can close a complete dependency chain from documentation through scaffold to working code, with real merges at each step.  
**Decision:** Build `tasklib` as a deliberately simple Python task management library whose primary success criterion is end-to-end pipeline validation rather than production readiness.  
**Consequences:** The system is constrained toward simplicity and demonstrability over completeness, scale, or production hardening. Design choices should favor clear dependency sequencing and merge validation.  
**Rejected alternatives:**  
- Building a production-grade task system: rejected because the TRD explicitly defines the library as a validation artifact, not a production system.  
- Using a more complex domain model: rejected because complexity would not improve validation of the pipeline’s dependency-chain behavior.

## Validate the full dependency chain in the order docs → scaffold → model → storage → CLI
**Status:** Accepted  
**Context:** The TRD explicitly defines the validation goal that the full dependency chain must close in the sequence `docs → scaffold → model → storage → CLI`.  
**Decision:** Structure delivery and subsystem dependencies to follow the ordered chain of documentation, scaffold, model, storage, and CLI.  
**Consequences:** Later subsystems depend on earlier merged work. Work must be decomposed so each stage can merge independently and be consumed by downstream stages. This constrains implementation order and package boundaries.  
**Rejected alternatives:**  
- Implementing subsystems in parallel without ordered dependencies: rejected because it would not validate downstream recognition of prior merges.  
- Combining multiple stages into one change: rejected because it would weaken proof of dependency-chain closure.

## Treat documentation as a first-class subsystem that triggers downstream merge behavior
**Status:** Accepted  
**Context:** One validation goal requires that a documentation PR fires the merge gate and that downstream PRs recognize the merge. The in-scope documentation set includes README, architecture overview, and API reference.  
**Decision:** Define documentation as an explicit subsystem and require a documentation deliverable set consisting of README, ARCHITECTURE overview, and API reference.  
**Consequences:** Documentation is not ancillary; it is part of the validated dependency chain. The pipeline must support docs-originated merges as dependency inputs to later work.  
**Rejected alternatives:**  
- Deferring documentation until after code: rejected because the TRD requires docs to participate in the dependency chain.  
- Limiting docs to only a README: rejected because the TRD explicitly includes README, ARCHITECTURE overview, and API reference.

## Use a Python package scaffold with multiple subpackage directories
**Status:** Accepted  
**Context:** The TRD includes a Python package scaffold with subpackage directories in scope, and a validation goal requires that a scaffold PR with multiple package directories mirrors files to the local test workspace.  
**Decision:** Structure `tasklib` as a Python package scaffold containing multiple subpackage directories.  
**Consequences:** Package layout must be explicit enough to validate multi-directory scaffold mirroring. Downstream model, storage, and CLI code must be organized within this scaffold.  
**Rejected alternatives:**  
- A single-module or flat package layout: rejected because it would not validate multi-package-directory scaffold behavior.  
- Deferring subpackage structure until implementation: rejected because scaffold structure itself is part of the validation target.

## Require local import resolution from previously merged PRs before CI
**Status:** Accepted  
**Context:** The TRD specifies that code PRs importing from previously merged PRs must resolve those imports locally before CI. This validates real dependency consumption across sequential merges.  
**Decision:** Design the development and integration flow so downstream code can import artifacts from earlier merged PRs in the local test workspace prior to CI execution.  
**Consequences:** Package naming, module boundaries, and merge sequencing must support local importability. This constrains how code is scaffolded and mirrored into the workspace.  
**Rejected alternatives:**  
- Relying on CI-only resolution of dependencies: rejected because the TRD explicitly requires local resolution before CI.  
- Mocking earlier modules instead of consuming merged outputs: rejected because it would not validate actual merge-based dependency behavior.

## Mirror scaffolded files into the local test workspace
**Status:** Accepted  
**Context:** A stated validation goal is that a scaffold PR with multiple package directories mirrors files to the local test workspace.  
**Decision:** Treat file mirroring from scaffold outputs into the local test workspace as a required behavior of the scaffold stage.  
**Consequences:** The scaffold cannot be purely conceptual; it must produce concrete file structures consumable by subsequent stages locally. This constrains tooling and packaging expectations around workspace synchronization.  
**Rejected alternatives:**  
- Generating scaffold metadata without materialized files: rejected because the TRD requires mirrored files.  
- Depending on remote-only artifact availability: rejected because validation is explicitly local-workspace based.

## Scope the library to documentation, scaffold, and implementation layers sufficient for pipeline validation
**Status:** Accepted  
**Context:** The TRD scope includes a documentation set and Python package scaffold, and the validation chain extends through model, storage, and CLI. The purpose is proving the pipeline end-to-end.  
**Decision:** Limit subsystem scope to the minimum set necessary to validate the chain: documentation, package scaffold, model layer, storage layer, and CLI layer.  
**Consequences:** Additional concerns not stated in the TRD should not be introduced as core subsystems. The design remains intentionally narrow and validation-oriented.  
**Rejected alternatives:**  
- Expanding scope to include production concerns such as authentication, networking, or deployment: rejected because they are not in the TRD scope or validation goals.  
- Reducing scope to only code generation: rejected because documentation and scaffold are explicitly required parts of the chain.

## Position CAL as the enforcement choke point for all agent-originated actions in Forge
**Status:** Accepted  
**Context:** The provided Forge architecture context states that CAL (Conversation Abstraction Layer) is the enforcement choke point for all agent-originated action, and that no tool call, data read, API invocation, or agent handoff executes without passing through CAL policy evaluation.  
**Decision:** Define CAL as the mandatory policy-evaluation layer for all agent-originated actions in the Forge platform.  
**Consequences:** Any subsystem performing tool calls, data access, API invocation, or agent handoff must integrate through CAL. This centralizes enforcement and constrains bypass paths.  
**Rejected alternatives:**  
- Allowing direct execution paths outside CAL: rejected because the architecture context explicitly forbids execution without CAL evaluation.  
- Splitting enforcement responsibility across multiple optional layers: rejected because CAL is defined as the choke point.

## Place CAL above the VTZ enforcement plane and below application orchestration
**Status:** Accepted  
**Context:** The Forge architecture context explicitly states that CAL sits above the VTZ enforcement plane and below application orchestration.  
**Decision:** Adopt the architectural layering in which CAL is positioned between application orchestration and the VTZ enforcement plane.  
**Consequences:** Integrations must respect this layering. Application-level orchestration cannot bypass CAL, and CAL itself depends on lower-layer enforcement capabilities in VTZ.  
**Rejected alternatives:**  
- Positioning CAL at the application layer: rejected because the context places it below application orchestration.  
- Positioning CAL below VTZ: rejected because the context places it above the VTZ enforcement plane.

## Define CAL around the specified core components
**Status:** Accepted  
**Context:** The Forge architecture context identifies CAL key components as CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, and the CAL Verifier Cluster.  
**Decision:** Treat CPF, AIR, CTX-ID, PEE, TrustFlow/SIS, and the CAL Verifier Cluster as the constituent components of CAL.  
**Consequences:** CAL design and implementation must preserve these component boundaries and names unless a future TRD supersedes them.  
**Rejected alternatives:**  
- Defining CAL without these named components: rejected because they are explicitly listed in the provided architecture context.  
- Introducing alternative CAL core components from unstated sources: rejected because decisions must be derived entirely from the provided TRDs.

## Define CPF as a core CAL component
**Status:** Accepted  
**Context:** The Forge architecture context lists CPF (Conversation Plane Filter) as a core subsystem under CAL, though no further detail is provided in the excerpt.  
**Decision:** Recognize CPF as a defined CAL component and preserve it as part of the Forge subsystem model.  
**Consequences:** CPF exists as a named architectural element even though its detailed responsibilities are not specified in the provided material. Further elaboration requires additional TRD input.  
**Rejected alternatives:**  
- Omitting CPF due to lack of detail: rejected because it is explicitly named in the provided architecture context.  
- Inferring undocumented CPF behavior: rejected because decisions must be derived only from the provided TRDs.