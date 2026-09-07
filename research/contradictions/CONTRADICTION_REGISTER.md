# Contradiction Register

Last Material Revision: 2026-09-07

This register documents contradictions and opposing arguments found during research, with responses and mitigations.

## C-001: Permanent identifiers as surveillance enablers

**Claim:** Permanent AI Actor identifiers could enable correlation of individuals' AI activity across contexts, creating a surveillance system.

**Source:** Privacy and human-rights literature; civil-society analysis.

**Response:** AI-IDP's pseudonymous identifiers by default prevent correlation. Sealed identity resolution requires judicial or regulator authority. Content separation (permanent minimal metadata and commitments, not full content) limits what is preserved. Access logging, recourse, civil-society oversight, regulator oversight, and parliamentary oversight provide additional safeguards.

**Mitigation:** The framework's success depends on robust implementation of the privacy safeguards. Without these safeguards, the framework could become a surveillance system.

**Status:** Mitigated (with caveats).

## C-002: Federal jurisdiction over AI agent identity

**Claim:** The federal government lacks jurisdiction to enact a universal AI agent identity and traceability regime; the regime falls under provincial jurisdiction over property and civil rights (s. 92(13)).

**Source:** Constitutional interpretation literature.

**Response:** The federal government has multiple heads of power: trade and commerce (s. 91(2)) for interprovincial AI services; criminal law (s. 91(27)) for AI-related offences; POGG (national concern doctrine) for a novel regulatory subject; telecommunications (s. 92(10)(a)) for AI agents operating via telecommunications infrastructure. The cooperative-federalism model preserves provincial authority while establishing a national minimum standard.

**Mitigation:** The framework's cooperative-federalism model addresses the jurisdiction concern. Provincial equivalence allows provinces to operate their own regimes.

**Status:** Mitigated.

## C-003: Privacy-permanence conflict

**Claim:** Permanent traceability conflicts with privacy principles (retention, correction, erasure) under PIPEDA and provincial privacy statutes.

**Source:** Privacy literature; OPC guidance.

**Response:** The framework resolves the conflict through: permanent minimal metadata (not full content); permanent cryptographic commitments (not plaintext); protected identity resolution (pseudonymous by default, sealed when needed); encrypted evidence payloads; access-controlled vaults; sealed records for judicial or regulator access; long-term signature migration; append-only corrections (not erasure).

**Mitigation:** The framework's privacy safeguards are designed to comply with PIPEDA, the Privacy Act, and provincial privacy statutes.

**Status:** Mitigated (requires robust implementation).

## C-004: Small-developer burden

**Claim:** AI-IDP's conformance costs could harm small developers and open-source projects, chilling innovation.

**Source:** Industry analysis; open-source community feedback.

**Response:** The framework's tiered conformance levels (L1-L4) accommodate small developers and open-source projects. L1 is achievable at low cost using the open-source AegisTrace reference implementation. Small-developer and open-source compliance profiles provide reduced-burden paths. The framework's success depends on the L1 baseline being achievable at low cost.

**Mitigation:** Tiered conformance; compliance profiles; open-source reference implementation.

**Status:** Mitigated.

## C-005: Foreign-provider non-cooperation

**Claim:** Foreign providers cannot be effectively regulated; foreign hosting becomes a simple avoidance mechanism.

**Source:** International regulatory literature.

**Response:** The framework's jurisdictional nexus test prevents foreign hosting from becoming a simple avoidance mechanism: the controlling organization remains accountable regardless of where the AI agent is hosted. The framework's controlling-organization liability, provider-duty framework, procurement controls, data-localization for evidence, and enforcement options (including service suspension) address foreign-provider non-cooperation.

**Mitigation:** Jurisdictional nexus test; controlling-organization liability; enforcement options.

**Status:** Mitigated (requires international cooperation).

## C-006: Cryptographic obsolescence

**Claim:** Ed25519 and SHA-256 may become obsolete over the planning horizon (10+ years), invalidating the framework's permanent signatures.

**Source:** Cryptographic literature; NIST PQC standardization.

**Response:** The signing interface is abstract. Ed25519 can be migrated to a post-quantum scheme (CRYSTALS-Dilithium, SLH-DSA) when standardized and mature. The migration is documented: a new scheme is adopted, existing signatures are re-signed with the new scheme, the re-signing is recorded as new signed events, and the original signatures are preserved.

**Mitigation:** Interface-isolated signing; documented PQC migration path.

**Status:** Mitigated (interface-ready; migration not implemented).

## C-007: Indigenous data sovereignty conflict

**Claim:** AI-IDP's permanent records conflict with Indigenous data sovereignty (OCAP® principles, First Nations, Inuit, and Métis distinctions).

**Source:** Indigenous data-governance literature.

**Response:** The framework's Indigenous data-governance provisions recognize Indigenous data sovereignty through OCAP®-aligned handling, First Nations, Inuit, and Métis distinctions-based approaches, TRC Calls to Action alignment, community-controlled access where applicable, and meaningful rights-holder engagement for deployments that materially affect Indigenous rights, community data, governance authority, or services. This is not a universal precondition for unrelated implementations.

**Mitigation:** OCAP®-aligned handling and context-specific rights-holder engagement where materially implicated.

**Status:** Mitigated (requires consultation with rights-holders).

## C-008: Cost and complexity

**Claim:** AI-IDP's implementation and ongoing compliance costs are excessive, particularly for small and medium organizations.

**Source:** Industry analysis; cost-benefit literature.

**Response:** The cost-benefit analysis finds that AI-IDP creates a net positive business and operational impact over a five-to-ten-year horizon for most Canadian organizations, with payback in 18-30 months for mid-size enterprises. The L1 baseline is achievable at low cost. Tiered conformance and compliance profiles reduce small-developer and open-source burden.

**Mitigation:** Tiered conformance; compliance profiles; open-source reference implementation; tax credits or grants for small-developer L2-L3 conformance.

**Status:** Mitigated (requires support programs).

# Contradiction Register
