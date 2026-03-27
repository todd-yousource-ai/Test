# DECISIONS.md

## Use protocol-defined wire formats unchanged at validation boundaries
**Status:** Accepted

**Context:** The Validation subsystem must interoperate with other subsystems and external validators using the protocol references defined in the TRDs. These references already specify canonical wire formats for CTX-ID, TrustFlow events, DTL labels, and VTZ enforcement decisions. Any subsystem-local variation would create ambiguity in signature verification, schema validation, and downstream enforcement behavior.

**Decision:** Implement the Validation subsystem to consume, validate, and emit the protocol-defined wire formats without modification:
- CTX-ID as a JWT-like signed token using the TrustLock agent key
- TrustFlow events as `{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}`
- DTL labels as `{label_id, classification, source_id, issued_at, sig}`
- VTZ enforcement decisions as `{ctx_id, tool_id, verdict: allow|restrict|block, reason}`

Treat these formats as canonical contracts at all subsystem boundaries. Permit only additive internal representations that map losslessly to the canonical forms.

**Consequences:** Validation logic is constrained to strict schema and signature handling for the exact protocol fields. Internal models must preserve round-trip fidelity to the wire contracts. The subsystem cannot rename fields, alter encodings, wrap messages in custom envelopes, or introduce derived fields into externally visible payloads unless separately standardized.

**Rejected alternatives:**  
- Defining validation-specific wrapper schemas around protocol messages: rejected because wrappers introduce translation ambiguity and complicate signature scope.  
- Normalizing all message types into a single internal generic envelope for external exchange: rejected because it obscures protocol semantics and weakens compatibility with other subsystems.  
- Allowing per-integration schema variants: rejected because variant handling would fragment verification logic and undermine deterministic validation outcomes.

## Verify signatures against the authoritative signing identity for each artifact type
**Status:** Accepted

**Context:** The Validation subsystem is responsible for establishing authenticity before any semantic checks are trusted. The protocol references explicitly tie CTX-ID to a TrustLock agent key and include signatures in TrustFlow events and DTL labels. Without artifact-type-specific signature verification rules, the subsystem could accept forged or misattributed inputs.

**Decision:** Require signature verification before accepting any CTX-ID, TrustFlow event, or DTL label as valid. Verify each artifact against its authoritative signing identity and declared format:
- CTX-ID must verify using the TrustLock agent key
- TrustFlow event signatures must verify against the expected event signer identity for the producing component
- DTL label signatures must verify against the issuing source identity represented by `source_id`

Fail closed on missing, invalid, unverifiable, or mismatched signatures.

**Consequences:** Unsigned or unverifiable artifacts cannot participate in validation decisions. Validation pipelines must have access to trusted key material or trust anchors needed for verification. Semantic validation, correlation, and enforcement must not proceed on artifacts that fail authenticity checks.

**Rejected alternatives:**  
- Performing schema validation before signature validation and allowing provisional processing: rejected because it risks acting on forged content.  
- Accepting artifacts from trusted transport channels without verifying payload signatures: rejected because transport trust does not replace object-level authenticity.  
- Using a single shared verification key for all artifact types: rejected because it collapses trust domains and prevents issuer accountability.

## Correlate validation state by `ctx_id` as the primary cross-artifact identifier
**Status:** Accepted

**Context:** The protocol references include `ctx_id` in TrustFlow events and VTZ enforcement decisions, and CTX-ID itself is the originating context token. The Validation subsystem must associate artifacts across event streams, labels, and enforcement outcomes in a deterministic way. A single primary correlation key is necessary to avoid inconsistent joins.

**Decision:** Use `ctx_id` as the primary correlation identifier across CTX-ID-derived validation state, TrustFlow events, and VTZ enforcement decisions. Maintain validation records and lookup paths keyed by `ctx_id`, with `session_id`, `event_id`, `label_id`, and `tool_id` treated as secondary identifiers for scoping and deduplication.

**Consequences:** Data stores, caches, and APIs in the Validation subsystem must be optimized for `ctx_id` lookup. Cross-artifact validation flows must anchor on `ctx_id` rather than infer linkage from session-only or event-only metadata. Inputs lacking a usable `ctx_id` cannot be fully correlated and must be treated as incomplete or invalid for context-bound decisions.

**Rejected alternatives:**  
- Using `session_id` as the primary correlation key: rejected because not all protocol artifacts are session-scoped and session boundaries may not uniquely identify context.  
- Correlating by `event_id`: rejected because events are per-occurrence identifiers, not context identifiers.  
- Building correlation heuristically from multiple optional fields: rejected because heuristic joins are nondeterministic and unsafe for enforcement-related validation.

## Validate TrustFlow events against strict schema and integrity requirements
**Status:** Accepted

**Context:** TrustFlow events are the primary evidence stream for validation decisions. The TRD defines a fixed schema including identifiers, timestamp, event type, payload hash, and signature. To preserve auditability and deterministic downstream behavior, Validation must reject malformed or incomplete events rather than attempt best-effort interpretation.

**Decision:** Enforce strict validation of TrustFlow events against the schema `{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}`. Require all fields to be present, structurally valid, and semantically consistent. Verify that `payload_hash` is present and used as the integrity reference for the associated event payload. Reject events with missing fields, malformed identifiers, invalid timestamps, or signature failures.

**Consequences:** Event ingestion must include schema parsing, required-field checks, timestamp validation, and integrity verification tied to `payload_hash`. Producers must emit complete protocol-conformant events; partial events are not acceptable. Consumers can rely on accepted events having a uniform minimum quality bar.

**Rejected alternatives:**  
- Allowing sparse events with optional missing fields during degraded operation: rejected because missing fields break audit and correlation guarantees.  
- Treating `payload_hash` as advisory metadata only: rejected because integrity evidence must be mandatory for trustworthy validation.  
- Auto-repairing malformed events during ingestion: rejected because inferred corrections would compromise evidentiary integrity.

## Treat DTL labels as signed classification assertions, not inferred facts
**Status:** Accepted

**Context:** The DTL wire format explicitly defines labels as signed artifacts containing `label_id`, `classification`, `source_id`, `issued_at`, and `sig`. The Validation subsystem must preserve the distinction between an issuer’s signed classification assertion and internally derived interpretations of that assertion. Conflating the two would damage provenance and auditability.

**Decision:** Accept DTL labels only as signed classification assertions from the identified source. Preserve the original `classification`, `source_id`, and `issued_at` values as authoritative label content. Perform any internal normalization or policy mapping as derived metadata separate from the original label artifact.

**Consequences:** Validation storage and APIs must retain original label values alongside any derived interpretations. Policy logic must not overwrite or mutate the source-issued classification in the canonical record. Audit trails must be able to reconstruct exactly what the issuer asserted and when.

**Rejected alternatives:**  
- Rewriting classifications into a subsystem-local taxonomy in place: rejected because it destroys source provenance and makes signature-backed assertions unverifiable in their original form.  
- Accepting unsigned labels from trusted sources: rejected because label provenance must be object-verifiable, not transport-assumed.  
- Treating labels as mere hints for heuristic scoring: rejected because the protocol defines them as signed assertions with explicit provenance.

## Emit VTZ enforcement decisions only from validated context
**Status:** Accepted

**Context:** VTZ enforcement decisions directly affect whether tools are allowed, restricted, or blocked. The protocol defines the decision shape as `{ctx_id, tool_id, verdict: allow|restrict|block, reason}`. Because these decisions are security-sensitive, the Validation subsystem must ensure they are derived only from authenticated and correlated inputs.

**Decision:** Generate VTZ enforcement decisions only after successful validation of the associated context and evidence. Emit decisions strictly in the protocol shape `{ctx_id, tool_id, verdict, reason}`, where `verdict` is limited to `allow`, `restrict`, or `block`. Require `ctx_id` and `tool_id` to resolve unambiguously before emission, and include a machine-usable `reason` tied to validation outcome.

**Consequences:** Enforcement output is constrained to three verdict states and cannot include custom verdict extensions without a protocol change. The subsystem must not emit speculative or partial decisions when context correlation is incomplete. Decision producers must maintain traceability from the emitted `reason` back to the validation result.

**Rejected alternatives:**  
- Emitting provisional decisions before validation completes: rejected because premature enforcement creates inconsistent and potentially unsafe tool behavior.  
- Introducing additional verdicts such as `warn`, `defer`, or `unknown`: rejected because they violate the protocol contract and complicate enforcement consumers.  
- Emitting tool decisions based only on local policy without validated context inputs: rejected because enforcement must be grounded in authenticated evidence.

## Fail closed on validation errors affecting authenticity, integrity, or correlation
**Status:** Accepted

**Context:** The Validation subsystem feeds security-relevant enforcement and audit flows. Errors involving signatures, payload integrity, schema conformance, or context correlation create uncertainty about whether an artifact is authentic and applicable. In this domain, permissive handling would produce unsafe false accepts.

**Decision:** Fail closed whenever validation errors affect authenticity, integrity, required schema conformance, or `ctx_id`-based correlation. On such failures, reject the artifact or emit a restrictive outcome rather than allowing processing to continue as valid. Only non-security-impacting operational issues may be retried or deferred without changing the closed-by-default stance.

**Consequences:** The subsystem will prefer rejection or restrictive enforcement over availability when trust cannot be established. Error handling, retries, and observability must be designed to distinguish transient operational failures from trust failures. Integrators must expect strict rejection semantics for malformed or untrusted inputs.

**Rejected alternatives:**  
- Failing open to preserve workflow continuity: rejected because validation outputs influence enforcement and cannot safely assume trust under uncertainty.  
- Downgrading all failures to warnings and continuing processing: rejected because warnings are insufficient when authenticity or correlation is in doubt.  
- Applying component-specific fail-open exceptions: rejected because exceptions would create inconsistent trust semantics and hidden attack paths.

## Preserve immutable audit evidence for all accepted and rejected artifacts
**Status:** Accepted

**Context:** Validation decisions must be explainable and defensible, especially when they lead to VTZ enforcement outcomes. Because the protocol artifacts are signed and structured, the subsystem has sufficient evidence to retain exact inputs and validation results. Immutable audit evidence is required to support traceability, incident review, and non-repudiation.

**Decision:** Persist immutable audit evidence for every processed protocol artifact, including both accepted and rejected cases. At minimum, retain the original artifact representation, validation outcome, failure reasons if any, and the correlation identifiers used (`ctx_id`, plus applicable `event_id`, `session_id`, `label_id`, or `tool_id`). Ensure stored audit records preserve the exact signed content needed for later re-verification.

**Consequences:** Storage design must support write-once or tamper-evident retention characteristics for audit records. The subsystem cannot rely solely on derived summaries or logs that omit the original signed inputs. Operational cost increases due to retention of rejected and malformed submissions, but traceability is preserved.

**Rejected alternatives:**  
- Storing only accepted artifacts: rejected because rejected artifacts are necessary to explain enforcement and investigate abuse or integration faults.  
- Retaining only parsed normalized fields instead of original payloads: rejected because normalized records may not support later signature re-verification.  
- Using ephemeral logs as the only audit mechanism: rejected because logs are insufficiently durable and often omit canonical signed content.