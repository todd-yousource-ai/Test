# DECISIONS.md

## Use protocol-defined wire formats as the only external contract
**Status:** Accepted  
**Context:** The Validation subsystem must interoperate with other platform components that already define protocol-level message structures. Divergence at the validation boundary would create ambiguity in parsing, signing, verification, and audit behavior across services.  
**Decision:** Implement the Validation subsystem to accept, validate, emit, and reason over only the protocol-defined wire formats for CTX-ID, TrustFlow events, DTL labels, and VTZ enforcement decisions:
- CTX-ID: JWT-like, signed with the TrustLock agent key
- TrustFlow event: `{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}`
- DTL label: `{label_id, classification, source_id, issued_at, sig}`
- VTZ decision: `{ctx_id, tool_id, verdict: allow|restrict|block, reason}`  
**Consequences:** Validation logic is constrained to these exact externally visible structures. Any internal models must map losslessly to these formats. Fields not present in the protocol references must not be required for validation success. Compatibility work must happen through versioned protocol evolution, not subsystem-specific extensions.  
**Rejected alternatives:** Defining Validation-specific wrapper schemas was rejected because it would create dual contracts and increase translation errors. Allowing loosely structured JSON payloads was rejected because it weakens deterministic validation and signature coverage. Inferring missing fields from surrounding context was rejected because protocol integrity must be explicit in the message.

## Verify signatures as a mandatory validation gate
**Status:** Accepted  
**Context:** All referenced protocol artifacts include signed content or are explicitly tied to signed provenance. The Validation subsystem exists in a trust-sensitive path and cannot treat authenticity as optional.  
**Decision:** Require cryptographic signature verification as a mandatory validation step for all signed artifacts:
- Verify CTX-ID using the TrustLock agent key
- Verify TrustFlow event signature over the event schema
- Verify DTL label signature over the label wire format  
Treat signature verification failure as validation failure and do not continue with downstream semantic acceptance of the artifact.  
**Consequences:** Validation is dependent on trusted key material and deterministic canonical handling of signed fields. The subsystem must distinguish malformed input from failed authenticity checks. Unsigned or unverifiable artifacts cannot be upgraded to valid through policy or configuration.  
**Rejected alternatives:** Making signature verification configurable was rejected because it creates unsafe deployment modes. Deferring signature checks to downstream services was rejected because validation would no longer be authoritative. Accepting artifacts with missing signatures in development paths was rejected because it encourages non-production behavior that diverges from the protocol contract.

## Validate required fields exactly as defined by each protocol schema
**Status:** Accepted  
**Context:** The protocol references define minimal required field sets for each artifact type. Validation must be deterministic and consistent across producers and consumers.  
**Decision:** Validate presence and structural correctness of every required field in each referenced schema and reject artifacts missing any required field:
- TrustFlow event requires `event_id`, `session_id`, `ctx_id`, `ts`, `event_type`, `payload_hash`, `sig`
- DTL label requires `label_id`, `classification`, `source_id`, `issued_at`, `sig`
- VTZ decision requires `ctx_id`, `tool_id`, `verdict`, `reason`
- CTX-ID must conform to its JWT-like signed wire format and required fields defined by that format  
**Consequences:** The subsystem cannot silently tolerate missing protocol fields. Producers must fully populate protocol artifacts before submission. Validation outcomes become stable and auditable because acceptance criteria are explicit.  
**Rejected alternatives:** Best-effort validation with warnings was rejected because downstream consumers may interpret warnings inconsistently. Defaulting missing values was rejected because it invents protocol state not present on the wire. Schema-by-schema custom leniency was rejected because it would fragment subsystem behavior.

## Enforce enumerated verdict values for VTZ decisions
**Status:** Accepted  
**Context:** The VTZ enforcement decision protocol defines a closed set of verdict outcomes: `allow`, `restrict`, or `block`. Validation must preserve these semantics exactly to avoid ambiguity at enforcement points.  
**Decision:** Accept only the enumerated `verdict` values `allow`, `restrict`, and `block` in VTZ enforcement decisions, and reject any other value.  
**Consequences:** Enforcement integrations can rely on a finite decision space. Validation must not reinterpret unknown verdicts or map vendor-specific terms into the protocol values. Any expansion of verdict semantics requires protocol change rather than local adaptation.  
**Rejected alternatives:** Allowing unknown verdict strings to pass through was rejected because enforcement behavior would become undefined. Mapping synonyms such as `deny` to `block` was rejected because it hides producer non-compliance. Treating unknown verdicts as `restrict` by default was rejected because it changes protocol meaning implicitly.

## Bind validation of related artifacts through ctx_id
**Status:** Accepted  
**Context:** Multiple protocol artifacts reference `ctx_id`, which serves as the linkage key across context identity, event records, and enforcement decisions. Validation must ensure these artifacts are not evaluated in isolation when correlation is required.  
**Decision:** Treat `ctx_id` as the canonical cross-artifact binding identifier and require exact-match correlation wherever artifacts are validated together or used in the same validation transaction.  
**Consequences:** The subsystem must reject cross-artifact combinations that do not share the same `ctx_id` when correlation is expected. Correlation logic must not substitute session-level or source-level identifiers for `ctx_id`. Audit trails can rely on a single identity handle for joined validation outcomes.  
**Rejected alternatives:** Correlating primarily on `session_id` was rejected because not all protocol artifacts carry it. Using heuristic joins across timestamps or source identifiers was rejected because it is non-deterministic. Allowing unbound mixed-context validation bundles was rejected because it risks validating artifacts from different trust scopes together.

## Treat payload integrity in TrustFlow events as first-class
**Status:** Accepted  
**Context:** TrustFlow events include `payload_hash` in the protocol schema, indicating that event payload integrity is part of the contract rather than auxiliary metadata. Validation must ensure the hash is meaningful and not merely present.  
**Decision:** Validate that every TrustFlow event includes `payload_hash` as a required integrity field and treat absent, malformed, or unusable payload hashes as validation failure. Where payload bytes are available to the subsystem, validate consistency between the payload and `payload_hash`.  
**Consequences:** Event acceptance is constrained by payload integrity expectations, not only event signature presence. Producers must compute payload hashes consistently. Consumers of validation output can rely on the event carrying an integrity anchor even when payload verification is deferred due to payload unavailability.  
**Rejected alternatives:** Treating `payload_hash` as informational metadata was rejected because the schema names it explicitly as a core field. Ignoring hash format correctness when payload is unavailable was rejected because malformed integrity data should not pass validation. Replacing payload-hash validation with signature-only checks was rejected because payload integrity and event authenticity address different failure modes.

## Preserve timestamp fields as protocol data, not inferred state
**Status:** Accepted  
**Context:** The referenced protocols include explicit time fields such as `ts` and `issued_at`. Validation must not replace protocol-declared times with receipt time or processing time, because that would alter signed or audited meaning.  
**Decision:** Validate protocol timestamp fields as supplied on the wire and preserve them unchanged in validation outcomes and audit records. Do not synthesize replacement timestamps for missing or invalid protocol time fields.  
**Consequences:** The subsystem must distinguish artifact time from system processing time. Missing or malformed timestamps result in validation failure rather than normalization. Audit consumers can trust that recorded protocol times match transmitted artifacts.  
**Rejected alternatives:** Substituting receipt timestamps was rejected because it changes artifact meaning. Auto-correcting malformed timestamps was rejected because it weakens protocol discipline. Ignoring timestamps during validation was rejected because time is part of the defined schema and often part of signed content.

## Do not extend signed protocol artifacts with validation-owned fields
**Status:** Accepted  
**Context:** Signed artifacts depend on stable wire representations. Adding subsystem-owned fields into externally exchanged objects risks breaking verification semantics and creating disagreement over what was signed.  
**Decision:** Keep validation annotations, processing metadata, and diagnostic details outside the protocol-defined signed artifacts. Store or emit such information in separate internal records or envelope structures that do not alter the referenced wire formats.  
**Consequences:** The Validation subsystem must maintain a strict separation between protocol artifacts and local processing state. Signature verification remains stable because signed content is not mutated. Integrators cannot rely on Validation-specific fields appearing inside CTX-ID, TrustFlow events, DTL labels, or VTZ decisions.  
**Rejected alternatives:** Injecting validation status fields directly into artifacts was rejected because it can invalidate signatures or create canonicalization ambiguity. Appending non-signed extension fields to exchanged artifacts was rejected because different consumers may disagree on whether they are covered by validation. Using ad hoc per-artifact extensions was rejected because it couples local implementation to protocol contracts.