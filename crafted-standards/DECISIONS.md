# DECISIONS.md

## Canonical Validation Inputs and Wire Formats
**Status:** Accepted  
**Context:** The Validation subsystem must verify artifacts emitted by adjacent subsystems without reinterpretation drift. Protocol references define concrete wire formats for CTX-ID, TrustFlow events, DTL labels, and VTZ enforcement decisions. A single canonical interpretation is required so signature verification, hashing, and rule evaluation remain deterministic across services.

**Decision:** Treat the protocol reference wire formats as the only canonical validation inputs. Validate the following structures exactly at subsystem boundaries:
- **CTX-ID:** JWT-like token signed with the TrustLock agent key.
- **TrustFlow event:** `{event_id, session_id, ctx_id, ts, event_type, payload_hash, sig}`
- **DTL label:** `{label_id, classification, source_id, issued_at, sig}`
- **VTZ enforcement decision:** `{ctx_id, tool_id, verdict: allow|restrict|block, reason}`

Reject inputs that omit required fields, include malformed field types, use unsupported verdict values, or cannot be parsed into the canonical structures before any higher-level validation logic runs.

**Consequences:** The subsystem is constrained to schema-first validation and cannot silently coerce malformed or partially compatible inputs. Upstream producers must conform exactly to these structures. Downstream logic can assume normalized, structurally valid objects. Backward-incompatible protocol evolution requires an explicit schema/versioning change rather than permissive parsing.

**Rejected alternatives:**  
- **Best-effort parsing with field inference:** Rejected because it creates ambiguity in signed content and undermines deterministic validation.  
- **Supporting multiple equivalent wire shapes per artifact:** Rejected because it increases attack surface and complicates signature and hash verification.  
- **Delaying structural validation until business-rule evaluation:** Rejected because invalid inputs must be rejected before trust decisions are computed.

## Signature Verification Is Mandatory for Signed Artifacts
**Status:** Accepted  
**Context:** The protocol references define signatures on CTX-ID, TrustFlow events, and DTL labels. The Validation subsystem exists to establish artifact authenticity and integrity before any trust or enforcement decision depends on them.

**Decision:** Verify cryptographic signatures on every signed artifact as a mandatory validation step:
- Verify **CTX-ID** using the TrustLock agent key.
- Verify **TrustFlow event** signatures against the trusted signer set defined for event producers.
- Verify **DTL label** signatures against the trusted signer set defined for label issuers.

Fail validation if a signature is missing where required, invalid, unverifiable, produced by an untrusted key, or detached from the canonical payload representation.

**Consequences:** No unsigned or improperly signed CTX-ID, event, or label may participate in context propagation, policy evaluation, or audit acceptance. Key management and trust-anchor configuration become hard dependencies of the Validation subsystem. Validation results are binary with respect to authenticity: unverifiable artifacts are rejected, not downgraded.

**Rejected alternatives:**  
- **Accepting unsigned artifacts from “trusted networks”:** Rejected because network location is not a cryptographic trust boundary.  
- **Allowing signature verification failures to degrade into warnings:** Rejected because authenticity is foundational, not advisory.  
- **Verifying signatures only during audit or asynchronous processing:** Rejected because invalid artifacts must not influence real-time decisions.

## Hash and Payload Integrity Must Bind TrustFlow Events
**Status:** Accepted  
**Context:** TrustFlow events include `payload_hash` in the defined schema. The Validation subsystem must ensure that event metadata and payload remain bound together so tampering is detectable even when payload handling is distributed.

**Decision:** Validate that each TrustFlow event’s `payload_hash` matches the canonical hash of the associated payload before accepting the event as valid. Perform hash verification in addition to signature verification, not as a substitute for it. Reject events when the payload is unavailable, the hash cannot be recomputed, or the recomputed hash differs from `payload_hash`.

**Consequences:** Event acceptance depends on both metadata authenticity and payload integrity. Systems integrating with Validation must preserve canonical payload bytes or a canonical serialization sufficient for deterministic hashing. Event processing pipelines cannot treat payload retrieval or canonicalization as optional.

**Rejected alternatives:**  
- **Relying on the event signature alone:** Rejected because a signed event record does not by itself prove that an external or separately stored payload is unchanged.  
- **Making payload hash verification best-effort:** Rejected because it allows tampered or mismatched payloads to enter trust evaluation.  
- **Hashing non-canonical payload representations:** Rejected because inconsistent serialization would cause false failures and nondeterministic validation.

## Fail Closed on Validation Errors
**Status:** Accepted  
**Context:** The Validation subsystem feeds trust and enforcement paths. If validation behavior is permissive under ambiguity, parsing failure, missing trust anchors, or verification errors, untrusted artifacts may influence access decisions.

**Decision:** Enforce fail-closed behavior for all validation outcomes. When structural validation, signature verification, hash verification, trust-anchor resolution, or required field checks fail, return a rejection outcome and prevent the artifact from being used in subsequent decision logic.

**Consequences:** Availability issues in key resolution, schema handling, or payload retrieval will surface as rejected validations rather than degraded trust. Integrators must handle negative validation outcomes explicitly. Operational resilience must be addressed through redundancy and observability, not permissive acceptance.

**Rejected alternatives:**  
- **Fail-open during dependency outages:** Rejected because it converts operational faults into security bypasses.  
- **Partial acceptance with risk flags:** Rejected because downstream consumers may mishandle advisory states and treat them as acceptable.  
- **Artifact-type-specific permissiveness:** Rejected because inconsistent failure semantics make the trust model difficult to reason about.

## Validation Must Precede Enforcement Decision Consumption
**Status:** Accepted  
**Context:** VTZ enforcement decisions carry `{ctx_id, tool_id, verdict: allow|restrict|block, reason}` and depend on trustworthy context. The Validation subsystem must ensure that enforcement consumers do not act on decisions tied to invalid or untrusted context.

**Decision:** Require successful validation of the referenced `ctx_id` before a VTZ enforcement decision is accepted for use. Validate that:
- `ctx_id` is present and structurally valid.
- `tool_id` is present and well-formed.
- `verdict` is exactly one of `allow`, `restrict`, or `block`.
- `reason` is present for auditability.

Reject enforcement decisions that reference invalid, missing, or unverifiable context.

**Consequences:** Enforcement pipelines are constrained to consume only decisions bound to validated context. A syntactically correct VTZ decision is insufficient if its context cannot be validated. Tool integrations must provide context linkage that survives transport and audit.

**Rejected alternatives:**  
- **Treating VTZ decisions as authoritative without revalidating context linkage:** Rejected because detached or forged context references could drive incorrect enforcement.  
- **Allowing unknown verdict extensions by default:** Rejected because open-ended verdict values create undefined enforcement behavior.  
- **Making `reason` optional:** Rejected because rejected or restrictive decisions must remain explainable and auditable.

## Canonical Field Semantics Over Transport-Specific Semantics
**Status:** Accepted  
**Context:** The same artifacts may traverse different transports or be embedded in different envelopes. Validation must operate on protocol-defined field semantics rather than transport-specific metadata to remain portable and deterministic.

**Decision:** Validate only protocol-defined fields and their canonical semantics as the source of truth. Do not derive trust decisions from transport metadata when equivalent protocol fields exist. Specifically:
- Use `ctx_id` from the artifact payload, not from headers as an override.
- Use `ts` from the TrustFlow event body as the event timestamp of record.
- Use signed field contents as authoritative over unsiged transport annotations.

**Consequences:** Gateways and adapters cannot alter validation meaning by injecting or rewriting transport-level metadata. The subsystem remains portable across transports and storage layers. Any transport-carried hints are advisory only unless promoted into the canonical signed artifact definition.

**Rejected alternatives:**  
- **Allowing headers or envelope fields to override artifact contents:** Rejected because it breaks signature assumptions and enables confusion attacks.  
- **Transport-specific validation plugins with divergent semantics:** Rejected because they fragment the trust model.  
- **Merging protocol fields with transport metadata heuristically:** Rejected because heuristic precedence rules are brittle and non-auditable.

## Deterministic Validation Results for Auditability
**Status:** Accepted  
**Context:** Validation outcomes must be explainable and reproducible for incident analysis, policy debugging, and compliance review. Given the same artifact, trust configuration, and payload bytes, the subsystem should not produce different outcomes across executions.

**Decision:** Implement validation as a deterministic pipeline with stable ordering: structural checks, canonicalization, signature verification, hash verification, and semantic field validation. Produce explicit rejection reasons tied to the failed validation stage. Do not use nondeterministic heuristics, probabilistic scoring, or environment-dependent fallback logic in core validation.

**Consequences:** Operators can reproduce validation outcomes and trace failures to a specific cause. The subsystem design is constrained away from “smart” recovery behaviors that vary across deployments. Test fixtures can assert exact outcomes for exact inputs.

**Rejected alternatives:**  
- **Heuristic validation with confidence scores:** Rejected because trust establishment must be binary and reproducible at the protocol layer.  
- **Parallel checks with race-dependent first-failure reporting:** Rejected because it reduces consistency of audit output.  
- **Environment-tuned fallback behavior:** Rejected because identical artifacts would validate differently across deployments.

## Validation Scope Excludes Policy Derivation Beyond Protocol Semantics
**Status:** Accepted  
**Context:** The Validation subsystem is responsible for establishing structural integrity, authenticity, and basic semantic correctness of protocol artifacts. Policy derivation and business-specific trust interpretation belong to downstream systems.

**Decision:** Limit Validation to verifying protocol compliance, signatures, payload integrity, and required semantic constraints explicitly expressed by the protocol references. Do not embed business policy such as classification-specific access rules, tool-specific allowlists, or organization-specific trust scoring into the Validation subsystem.

**Consequences:** The subsystem remains narrow, predictable, and reusable across deployment contexts. Downstream policy engines must consume validated artifacts and apply business rules separately. Changes in organizational policy do not require changes to core validation logic unless protocol semantics change.

**Rejected alternatives:**  
- **Embedding classification-based access policy into DTL label validation:** Rejected because label authenticity and policy interpretation are separate concerns.  
- **Including tool authorization logic in VTZ decision validation:** Rejected because validation should confirm shape and linkage, not decide organizational entitlement.  
- **Combining validation and policy into a single subsystem:** Rejected because it obscures responsibility boundaries and reduces testability.