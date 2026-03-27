# DECISIONS.md

## Validate all protocol artifacts against canonical wire formats at subsystem boundaries
**Status:** Accepted

**Context:** The Validation subsystem must determine correctness and trustworthiness of inputs exchanged across architecture boundaries. The TRDs define canonical wire formats for CTX-ID, TrustFlow events, DTL labels, and VTZ enforcement decisions. Without strict boundary validation, downstream components could process malformed, ambiguous, or spoofed artifacts.

**Decision:** Enforce schema validation for every inbound and outbound protocol artifact at the Validation subsystem boundary using the canonical wire formats:
- CTX-ID: JWT-like token signed with the TrustLock agent key and containing the defined fields
- TrustFlow event: `{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}`
- DTL label: `{label_id, classification, source_id, issued_at, sig}`
- VTZ enforcement decision: `{ctx_id, tool_id, verdict: allow|restrict|block, reason}`

Reject artifacts that are missing required fields, contain unknown structural variants where strict parsing is required, or violate type and format constraints.

**Consequences:** The subsystem is constrained to implement explicit parsers and validators per protocol artifact. Compatibility behavior must preserve canonical field names and structures. Producers and consumers cannot rely on implicit coercion or best-effort parsing. Validation failures become first-class outcomes and must prevent further trust-sensitive processing.

**Rejected alternatives:** Allowing permissive parsing with field inference was rejected because it creates ambiguity and expands the attack surface. Deferring validation to downstream services was rejected because malformed artifacts could propagate across trust boundaries. Supporting multiple ad hoc wire formats for the same artifact was rejected because it undermines interoperability and auditability.

## Verify signatures before accepting trust-bearing artifacts
**Status:** Accepted

**Context:** CTX-ID, TrustFlow events, and DTL labels all carry signatures in their protocol definitions. These artifacts are trust-bearing and may influence authorization, lineage, or enforcement. Accepting them without cryptographic verification would make the Validation subsystem ineffective as a security control.

**Decision:** Perform cryptographic signature verification for every signed protocol artifact before it is accepted as valid:
- Verify CTX-ID signatures using the TrustLock agent key
- Verify TrustFlow event signatures using the configured signer trust material
- Verify DTL label signatures using the configured source trust material

Treat missing, unverifiable, expired, malformed, or untrusted signatures as validation failures.

**Consequences:** The subsystem must integrate with trusted key material and key selection logic. Validation is constrained to fail closed for signature-related errors. Unsigned or improperly signed artifacts cannot be used to derive context, provenance, or classification. Operationally, key rotation and trust store management become required inputs to subsystem design.

**Rejected alternatives:** Treating signatures as optional metadata was rejected because it would allow spoofed artifacts to appear valid. Verifying signatures only during periodic audit was rejected because invalid artifacts could influence live decisions before detection. Trusting transport security alone was rejected because protocol artifacts may persist, replay, or cross systems beyond a single transport session.

## Validate cross-artifact referential integrity using ctx_id as the primary correlation key
**Status:** Accepted

**Context:** The protocol references establish `ctx_id` as the common identifier across CTX-ID, TrustFlow events, and VTZ enforcement decisions. The Validation subsystem must ensure that related artifacts refer to the same context and are not stitched together incorrectly or maliciously.

**Decision:** Enforce referential integrity checks across artifacts by treating `ctx_id` as the authoritative correlation key. Require:
- TrustFlow events to reference a valid `ctx_id`
- VTZ enforcement decisions to reference the same `ctx_id` used by the triggering or associated context
- Cross-checks between artifacts to ensure that correlated records do not mix mismatched contexts

Fail validation when a referenced `ctx_id` is absent, malformed, unverifiable, or inconsistent across the related artifact set.

**Consequences:** Validation is constrained to include contextual lookups or correlation logic rather than only isolated schema checks. Pipelines that process artifacts independently must still preserve enough state to verify `ctx_id` consistency. Audit trails become more reliable because events and enforcement outcomes are tied to a single validated context.

**Rejected alternatives:** Using `session_id` as the primary correlation key was rejected because it is not present on all protocol artifacts. Allowing loose correlation based on timestamps or source heuristics was rejected because it is error-prone and vulnerable to manipulation. Validating each artifact in complete isolation was rejected because structurally valid but contextually inconsistent records could be accepted.

## Treat payload integrity in TrustFlow events as mandatory
**Status:** Accepted

**Context:** The TrustFlow event schema includes `payload_hash` and `sig`, indicating that event content integrity is part of the protocol contract. Validation must ensure that an event’s declared payload identity matches the content being processed or referenced.

**Decision:** Require TrustFlow event validation to verify `payload_hash` against the associated payload or canonical payload representation before accepting the event as valid. Treat hash mismatches, unsupported hash representations, or missing payload integrity data as validation failures.

**Consequences:** The subsystem must define and implement canonical hashing inputs for event payload validation. Event ingestion paths are constrained to preserve payload fidelity until validation completes. TrustFlow consumers cannot rely solely on event signatures if payload identity cannot also be confirmed.

**Rejected alternatives:** Verifying only the event signature and ignoring `payload_hash` was rejected because a signed wrapper alone does not guarantee the integrity of the referenced payload. Making payload hash verification best-effort was rejected because inconsistent enforcement would reduce the reliability of lineage and audit records. Allowing producer-specific hashing conventions without canonicalization was rejected because it would create interoperability failures.

## Enforce closed verdict semantics for VTZ decisions
**Status:** Accepted

**Context:** The VTZ enforcement decision protocol defines `verdict` as one of `allow|restrict|block`. These values drive enforcement behavior and must not be interpreted loosely. Any ambiguity in verdict handling could create unsafe default behavior.

**Decision:** Validate VTZ enforcement decisions against a closed enumeration of verdict values: `allow`, `restrict`, or `block`. Reject any decision containing unknown verdicts, alternate spellings, casing variants, or inferred defaults. Require `reason` to be present as the explanatory basis for the verdict.

**Consequences:** The subsystem is constrained to implement strict enum validation and cannot silently map noncanonical values. Enforcement integrations must emit only canonical verdict values. Requiring `reason` improves auditability and post-incident analysis but also makes missing rationale a hard validation failure.

**Rejected alternatives:** Allowing unknown verdicts to downgrade to `restrict` or `block` was rejected because implicit coercion hides producer defects and creates inconsistent behavior. Accepting case-insensitive or synonym-based verdict parsing was rejected because protocol values are part of the wire contract. Making `reason` optional was rejected because enforcement decisions require traceable justification.

## Validate DTL labels as authoritative classification artifacts, not advisory metadata
**Status:** Accepted

**Context:** DTL labels encode classification with `{label_id, classification, source_id, issued_at, sig}`. Because classification may influence handling, routing, and enforcement, the Validation subsystem must treat these labels as authoritative only when fully validated.

**Decision:** Accept a DTL label as authoritative only if its structure is valid, its signature verifies, its `source_id` is trusted, and its issuance metadata is valid. Reject labels that cannot establish provenance or that contain invalid classification encodings.

**Consequences:** The subsystem must maintain trust relationships for `source_id` and cannot treat arbitrary labels as equivalent. Classification-driven behaviors downstream are constrained to depend only on validated labels. Operationally, source onboarding and trust revocation become part of validation governance.

**Rejected alternatives:** Treating labels as informational regardless of provenance was rejected because downstream systems could act on forged or stale classifications. Trusting any syntactically valid `source_id` was rejected because provenance is essential to classification authority. Allowing invalid labels to pass through with warnings was rejected because it encourages unsafe consumption.

## Fail closed on validation uncertainty
**Status:** Accepted

**Context:** The Validation subsystem protects trust-sensitive flows involving identity, provenance, classification, and enforcement. In this role, uncertainty such as parse ambiguity, signature verification failure, missing trust material, or referential inconsistency must not result in permissive handling.

**Decision:** Fail closed whenever validation cannot establish artifact correctness and trust. Produce an explicit validation failure outcome rather than inferring acceptance, partial validity, or permissive defaults.

**Consequences:** Implementations are constrained to prefer rejection over continuation under uncertainty. Availability may be reduced during trust store outages, key resolution failures, or protocol incompatibilities, but the security posture remains consistent. Callers must be designed to handle hard validation failures explicitly.

**Rejected alternatives:** Failing open for operational continuity was rejected because it would allow untrusted artifacts into trust-sensitive workflows. Returning partial-validity states for downstream interpretation was rejected because it diffuses security responsibility and creates inconsistent policy handling. Auto-retrying indefinitely before producing a verdict was rejected because it obscures failure semantics and can stall processing.

## Emit validation outcomes in a deterministic, auditable form
**Status:** Accepted

**Context:** Validation decisions affect whether protocol artifacts are admitted into the broader system. To support audit, troubleshooting, and reproducibility, the subsystem must produce outcomes that clearly explain what was validated and why acceptance or rejection occurred.

**Decision:** Record validation outcomes in a deterministic and auditable form that identifies the artifact type, artifact identifiers where present, validation result, and failure reasons when rejected. Use canonical protocol identifiers such as `ctx_id`, `event_id`, `label_id`, `session_id`, and `tool_id` where applicable.

**Consequences:** The subsystem is constrained to preserve sufficient metadata during validation to support traceability. Logging and audit records must avoid ambiguous identifiers and must consistently report the same failure classes for the same invalid inputs. This improves incident response but requires disciplined error taxonomy and redaction-aware logging design.

**Rejected alternatives:** Emitting only boolean pass/fail results was rejected because it is insufficient for audit and remediation. Using free-form error strings without stable structure was rejected because it impairs automation and correlation. Omitting protocol identifiers from outcomes was rejected because it weakens traceability across related artifacts.