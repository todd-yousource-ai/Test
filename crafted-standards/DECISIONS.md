# DECISIONS.md

## Use protocol-defined wire formats as the only external contract
**Status:** Accepted  
**Context:** The Validation subsystem exchanges identity, event, label, and enforcement data with other Forge subsystems. Interoperability depends on strict adherence to shared protocol references rather than subsystem-local schemas.  
**Decision:** Implement all Validation subsystem ingress and egress using only the protocol-defined wire formats:
- CTX-ID as a JWT-like token signed with the TrustLock agent key
- TrustFlow events as `{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}`
- DTL labels as `{label_id, classification, source_id, issued_at, sig}`
- VTZ enforcement decisions as `{ctx_id, tool_id, verdict: allow|restrict|block, reason}`

Do not add required external fields, rename fields, or reinterpret field semantics in Validation-specific adapters. Any internal model must be mapped losslessly to and from these protocol shapes.  
**Consequences:** Validation is constrained to validate, store, and emit protocol-compliant artifacts. Internal representations may evolve, but external contracts cannot diverge. Backward-incompatible schema changes must be handled through explicit protocol versioning outside this subsystem.  
**Rejected alternatives:**  
- **Define Validation-specific external DTOs:** Rejected because it would create schema drift and force translation layers across subsystems.  
- **Permit optional subsystem-specific extensions in primary payloads:** Rejected because it weakens interoperability and creates inconsistent validation behavior.  
- **Treat protocol references as advisory rather than binding:** Rejected because it would allow incompatible implementations and break end-to-end verification.

## Verify signatures at trust boundaries before accepting artifacts
**Status:** Accepted  
**Context:** All referenced protocol artifacts include signatures or are derived from signed sources. The Validation subsystem exists to determine authenticity and integrity; therefore, acceptance without cryptographic verification would undermine the trust model.  
**Decision:** Require signature verification for every signed artifact at the first Validation trust boundary before the artifact is accepted, persisted, or used for downstream decisions:
- Verify CTX-ID signatures against the TrustLock agent key
- Verify TrustFlow event signatures using the configured signer trust roots
- Verify DTL label signatures using the configured label issuer trust roots

Reject artifacts with missing, invalid, untrusted, or unverifiable signatures. Do not defer signature checks until after business logic execution.  
**Consequences:** Validation must have access to key material or trust roots required for verification and must fail closed when verification cannot be completed. Downstream components may assume accepted artifacts have already passed authenticity checks.  
**Rejected alternatives:**  
- **Verify signatures lazily only when artifacts affect enforcement:** Rejected because unverified data could pollute storage, audit trails, and derived state.  
- **Accept signed artifacts optimistically and re-verify asynchronously:** Rejected because it introduces race conditions and allows transient use of untrusted inputs.  
- **Rely on upstream components to verify signatures:** Rejected because Validation must independently enforce trust boundaries and cannot assume upstream correctness.

## Bind all validation operations to CTX-ID
**Status:** Accepted  
**Context:** Protocol references make CTX-ID the common linkage across events and enforcement decisions. Validation needs a stable correlation handle to reason about provenance, session continuity, and policy outcomes.  
**Decision:** Require every validation operation to be associated with a CTX-ID, either directly from input artifacts or through deterministic derivation from already validated context. Use `ctx_id` as the primary correlation key for:
- linking TrustFlow events
- attaching DTL labels to context
- producing VTZ enforcement decisions
- audit and trace retrieval

Do not process or emit context-bearing artifacts without a valid CTX-ID association.  
**Consequences:** Validation APIs, storage, and logs must index by `ctx_id`. Orphaned artifacts without CTX-ID linkage must be rejected or quarantined according to failure policy, not silently accepted.  
**Rejected alternatives:**  
- **Use `session_id` as the primary correlation key:** Rejected because VTZ decisions and CTX-scoped trust semantics are defined around `ctx_id`, not session lifecycle alone.  
- **Allow best-effort processing for artifacts missing `ctx_id`:** Rejected because it breaks provenance guarantees and makes downstream enforcement ambiguous.  
- **Generate new local correlation IDs for incomplete inputs:** Rejected because local IDs cannot substitute for protocol-level context identity.

## Enforce exact field-level validation for TrustFlow events
**Status:** Accepted  
**Context:** TrustFlow events are a signed protocol artifact with a fixed schema. Validation must ensure both structural correctness and semantic completeness before events are used as evidence or audit records.  
**Decision:** Validate every TrustFlow event against the exact schema `{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}` and reject events that:
- omit any required field
- include malformed field values
- contain invalid signatures
- cannot be bound to an accepted CTX-ID

Treat `payload_hash` as the integrity reference for event payload content; do not substitute raw payload comparison as the primary integrity mechanism.  
**Consequences:** Event ingestion requires strict schema validation and integrity checks. Storage and processing pipelines cannot rely on partially populated or schema-flexible event objects. Event producers must conform exactly to the shared schema.  
**Rejected alternatives:**  
- **Accept partial events and infer missing fields:** Rejected because inferred security metadata is not trustworthy.  
- **Store raw events first and validate later:** Rejected because invalid events would contaminate audit and evidence stores.  
- **Use ad hoc payload checks instead of `payload_hash`:** Rejected because the protocol explicitly defines hashed payload integrity and signatures over event data.

## Treat DTL labels as signed attestations, not mutable annotations
**Status:** Accepted  
**Context:** DTL labels communicate classification and source attribution in a signed wire format. Validation must preserve their evidentiary value and prevent local mutation from invalidating provenance.  
**Decision:** Handle DTL labels as immutable signed attestations with the wire format `{label_id, classification, source_id, issued_at, sig}`. After verification, do not modify any signed field in place. If enrichment is required, store enrichment separately as unsigned Validation metadata linked to `label_id` and `ctx_id`.  
**Consequences:** Validation storage must distinguish between signed label content and local derived metadata. Consumers must not expect Validation to rewrite label classifications, issuer identifiers, or issuance timestamps. Corrections require issuance of a new label, not mutation of an existing one.  
**Rejected alternatives:**  
- **Normalize or rewrite label fields after ingestion:** Rejected because it destroys signature validity and provenance.  
- **Merge local annotations directly into the label object:** Rejected because it blurs attested data with local opinion and complicates verification.  
- **Treat labels as advisory tags with no signature enforcement:** Rejected because the protocol defines them as signed artifacts with source accountability.

## Emit only explicit VTZ verdicts and reasons
**Status:** Accepted  
**Context:** The Validation subsystem contributes to enforcement by producing decisions consumed by VTZ. The protocol reference defines a narrow decision shape with a constrained verdict set.  
**Decision:** Emit enforcement decisions only in the format `{ctx_id, tool_id, verdict: allow|restrict|block, reason}`. Restrict verdict values to the enumerated set `allow`, `restrict`, or `block`. Always include a machine-usable `reason` explaining the basis for the decision. Do not emit implicit allow, null verdicts, or subsystem-specific verdict extensions.  
**Consequences:** Decision producers must map all internal outcomes into the three allowed verdicts. Consumers can rely on a stable, closed decision vocabulary. If more nuance is required, it must be encoded in `reason` or handled by a separately versioned protocol change.  
**Rejected alternatives:**  
- **Add extra verdicts such as `warn`, `defer`, or `unknown`:** Rejected because they are outside the protocol and create ambiguity in enforcement behavior.  
- **Omit `reason` for successful decisions:** Rejected because auditability and policy traceability require justification for every verdict.  
- **Use booleans instead of verdict enums:** Rejected because the protocol requires three-state enforcement semantics, not binary authorization.

## Fail closed on validation ambiguity or trust resolution failure
**Status:** Accepted  
**Context:** The Validation subsystem operates on signed security artifacts and influences enforcement outcomes. Ambiguous validation states, unavailable trust roots, or unresolved context links must not degrade into permissive behavior.  
**Decision:** Fail closed whenever Validation cannot conclusively verify authenticity, integrity, schema compliance, or CTX-ID binding. In such cases:
- reject inbound artifacts from acceptance paths
- quarantine artifacts only if they are excluded from normal decision flows
- emit VTZ decisions as `restrict` or `block`, never `allow`, when enforcement must proceed under unresolved validation state

Do not substitute defaults that mask verification failure.  
**Consequences:** Operational outages in key resolution, signer trust configuration, or schema validation will reduce availability in favor of safety. System operators must provide observability and recovery paths for quarantined or blocked items.  
**Rejected alternatives:**  
- **Fail open during transient verifier or key-service outages:** Rejected because it would permit untrusted artifacts to influence enforcement.  
- **Downgrade all uncertain cases to warnings while allowing execution:** Rejected because warnings are not an enforcement outcome in the protocol and do not preserve safety.  
- **Silently drop unverifiable artifacts:** Rejected because it impairs auditability and incident investigation.

## Preserve protocol artifacts in canonical form for audit and replay
**Status:** Accepted  
**Context:** Validation decisions may need to be audited, re-evaluated, or replayed as trust configuration changes. This requires preserving what was actually received and verified, not only normalized internal projections.  
**Decision:** Store the canonical received form of CTX-ID, TrustFlow events, DTL labels, and emitted VTZ decisions alongside validation results and timestamps. Any internal normalization must be supplemental and must not replace the original verified artifact representation.  
**Consequences:** Audit and replay workflows can reconstruct verification inputs exactly as processed. Storage design must account for canonical artifact retention and linkage to validation outcomes. Internal model changes will not invalidate historical evidence.  
**Rejected alternatives:**  
- **Store only normalized internal records:** Rejected because normalization can lose verification-relevant details and prevents exact replay.  
- **Store only hashes of validated artifacts:** Rejected because hashes alone are insufficient for full audit reconstruction and debugging.  
- **Retain originals only for failed validations:** Rejected because successful decisions also require traceability and potential re-verification.