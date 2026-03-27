# DECISIONS.md

## Validation subsystem is the sole authority for protocol conformance checks
**Status:** Accepted  
**Context:** The architecture defines multiple signed wire artifacts and decision records used across subsystem boundaries: CTX-ID, TrustFlow events, DTL labels, and VTZ enforcement decisions. Without a single validation authority, producers and consumers could each implement partial or divergent checks, creating inconsistent acceptance criteria and security gaps.  
**Decision:** Implement the Validation subsystem as the single canonical component that verifies structural, semantic, and signature conformance for all protocol-defined artifacts before they are trusted, persisted, routed, or acted upon.  
**Consequences:** All components must route inbound protocol objects through Validation before use. Validation logic becomes the source of truth for protocol acceptance and rejection behavior. Downstream systems may perform defensive checks, but those checks must not redefine validity. Protocol evolution must update Validation first.  
**Rejected alternatives:** Embedding validation independently in each producer/consumer was rejected because it creates drift and inconsistent security posture. Trusting upstream components to self-validate was rejected because signed artifacts can still be malformed, stale, or semantically invalid. Limiting Validation to schema-only checks was rejected because signatures and protocol semantics are security-critical.

## Validate CTX-ID strictly against its JWT-like signed wire format
**Status:** Accepted  
**Context:** CTX-ID is a signed, JWT-like wire artifact and is foundational to session and context propagation. Mis-parsing or weak validation would allow malformed or spoofed context to influence trust decisions and event correlation.  
**Decision:** Enforce strict parsing and validation of CTX-ID according to its JWT-like wire format, including required field presence, canonical structure, signature verification with the TrustLock agent key, and semantic checks on contained values before accepting the context as valid.  
**Consequences:** Only correctly formed and correctly signed CTX-IDs are admitted. Components must treat invalid, unverifiable, or semantically inconsistent CTX-IDs as rejected rather than partially usable. Any implementation must preserve exact wire-level semantics and signature verification behavior.  
**Rejected alternatives:** Treating CTX-ID as an opaque token and only checking presence was rejected because it permits malformed or forged context to propagate. Supporting permissive parsing for backward compatibility was rejected because ambiguity in a signed format undermines interoperability and security. Deferring signature checks until first use was rejected because invalid context could already influence system behavior.

## Validate TrustFlow events against the canonical event schema before ingestion
**Status:** Accepted  
**Context:** TrustFlow events are defined by the schema `{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}` and are used for traceability and downstream trust workflows. Event ingestion must ensure both structural completeness and cryptographic integrity.  
**Decision:** Require every TrustFlow event to conform exactly to the canonical schema, validate all required fields, verify that `ctx_id` is itself valid or resolvable to a valid CTX-ID, and verify the event signature before the event is accepted for ingestion or processing.  
**Consequences:** Event producers must emit the complete schema with no omitted required fields. Consumers must not process unsigned, partially formed, or structurally non-conformant events. Correlation logic may assume validated identifiers and timestamps.  
**Rejected alternatives:** Accepting events with optional omission of schema fields was rejected because downstream correlation depends on a complete event envelope. Allowing schema validation without signature verification was rejected because tampered events would appear structurally valid. Validating only at storage time was rejected because invalid events could contaminate live workflows before persistence.

## Validate DTL labels as signed classification artifacts
**Status:** Accepted  
**Context:** DTL labels use the wire format `{label_id, classification, source_id, issued_at, sig}` and drive classification-aware behavior. Because labels represent trust-bearing assertions, they require stronger guarantees than simple data-shape validation.  
**Decision:** Enforce validation of DTL labels as signed artifacts by checking required fields, allowed classification semantics, source identity presence, issuance metadata, and signature validity before any label is used for policy, routing, or display.  
**Consequences:** Unsigned or semantically invalid labels cannot influence any decision path. Classification values must be interpreted from a constrained, validated set rather than free-form input. Label provenance becomes mandatory for downstream use.  
**Rejected alternatives:** Treating labels as advisory metadata without signature checks was rejected because untrusted labels could manipulate policy outcomes. Allowing arbitrary classification strings was rejected because it would fragment policy interpretation. Accepting labels with missing provenance fields was rejected because unverifiable source attribution weakens trust decisions.

## Validate VTZ enforcement decisions as canonical verdict records
**Status:** Accepted  
**Context:** VTZ enforcement decisions are defined as `{ctx_id, tool_id, verdict: allow|restrict|block, reason}` and directly constrain tool execution. Since these records affect enforcement, Validation must ensure both format correctness and a closed verdict set.  
**Decision:** Validate every VTZ enforcement decision against the canonical structure, require a valid `ctx_id`, require a `tool_id`, constrain `verdict` to exactly `allow`, `restrict`, or `block`, and require a non-empty `reason` before the decision is accepted for enforcement or audit.  
**Consequences:** Enforcement components may rely on a normalized and finite verdict vocabulary. Invalid or ambiguous decisions are rejected rather than interpreted leniently. Audit records remain consistent across implementations.  
**Rejected alternatives:** Allowing extensible free-form verdict values was rejected because enforcement logic must remain deterministic and interoperable. Making `reason` optional was rejected because operator and audit traceability would be degraded. Validating `ctx_id` only syntactically was rejected because enforcement must bind to trusted context, not merely well-formed identifiers.

## Reject invalid artifacts fail-closed rather than degrade gracefully
**Status:** Accepted  
**Context:** The Validation subsystem sits on the trust boundary for signed protocol artifacts. In security-sensitive workflows, permissive fallback behavior turns validation failures into exploitable ambiguity.  
**Decision:** Reject any artifact that fails parsing, required-field checks, semantic validation, or signature verification, and do not substitute defaults, partial acceptance, or best-effort interpretation for protocol-defined inputs.  
**Consequences:** Callers must handle explicit validation failures and cannot assume malformed input will be normalized. Operational processes must account for rejection paths and observability around invalid inputs. Security posture is prioritized over permissive interoperability.  
**Rejected alternatives:** Graceful degradation with partial field acceptance was rejected because it creates undefined behavior for signed protocols. Auto-repair or normalization of malformed artifacts was rejected because modifying signed or canonical inputs can invalidate provenance and mask producer defects. Quarantining but still processing suspect artifacts was rejected because downstream systems may mistakenly treat them as trusted.

## Separate structural validation, semantic validation, and signature verification as distinct phases
**Status:** Accepted  
**Context:** The subsystem must validate multiple artifact types with different wire formats but shared needs for shape checking, semantic interpretation, and cryptographic verification. A phased approach improves determinism and diagnostics.  
**Decision:** Implement validation in explicit phases: structural parsing and required-field checks first, semantic and domain-rule validation second, and signature verification against the appropriate trust material as a distinct step with explicit outcome reporting.  
**Consequences:** Validation behavior becomes predictable and easier to reason about across artifact types. Error reporting can distinguish malformed data from invalid semantics and failed signatures. Implementations are constrained to preserve phase boundaries rather than mixing concerns ad hoc.  
**Rejected alternatives:** A single monolithic validation routine per artifact type was rejected because it obscures failure causes and encourages duplication. Performing signature verification before structure checks was rejected because the wire artifact must first be parsed deterministically. Deferring semantic checks to downstream consumers was rejected because accepted artifacts must already meet protocol expectations.

## Use protocol-defined canonical field sets and do not admit undeclared compatibility shapes
**Status:** Accepted  
**Context:** The TRDs provide explicit wire formats and schemas for Validation to enforce. Allowing alternate field names, extra compatibility envelopes, or multiple accepted shapes would weaken interoperability and complicate signing assumptions.  
**Decision:** Accept only the protocol-defined canonical field sets and shapes for CTX-ID, TrustFlow events, DTL labels, and VTZ enforcement decisions, and reject undeclared aliases, wrapper formats, or shape variations unless the protocol reference is formally revised.  
**Consequences:** Producers must emit canonical wire representations. Consumers and validators share a stable contract with low ambiguity. Protocol upgrades require explicit schema revision rather than implicit compatibility hacks.  
**Rejected alternatives:** Supporting alias fields or version-by-convention parsing was rejected because it introduces ambiguity in signed payload interpretation. Allowing extra compatibility wrappers was rejected because it complicates canonicalization and cross-system interoperability. Best-effort field mapping was rejected because it hides producer non-conformance and makes validation outcomes non-deterministic.

## Validation results must be explicit and artifact-type specific
**Status:** Accepted  
**Context:** Because the subsystem validates multiple protocol artifacts with security and enforcement impact, callers need deterministic outcomes that indicate both acceptability and failure reason categories. Generic pass/fail behavior is insufficient for integration and auditing.  
**Decision:** Return explicit validation outcomes per artifact type that distinguish success from rejection and identify whether failure occurred in structure, semantics, or signature verification, without permitting callers to override a rejection into acceptance.  
**Consequences:** Integrators can build clear error handling and observability around validation failures. Auditability improves because rejection causes are categorized consistently. The Validation subsystem constrains downstream callers to treat failure as terminal for trust-bearing use.  
**Rejected alternatives:** Returning only boolean validity was rejected because it obscures operational diagnosis and integration behavior. Exposing low-level parser exceptions directly as the API contract was rejected because it is unstable and implementation-coupled. Allowing caller-specified validation leniency was rejected because validity criteria must remain centralized and uniform.