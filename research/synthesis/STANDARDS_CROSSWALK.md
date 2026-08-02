# Standards Crosswalk

Last Material Revision: 2026-08-01

This document maps AI-IDP requirements to existing standards.

| AI-IDP Requirement | Existing Standard | Relationship |
|--------------------|-------------------|--------------|
| Persistent AI Actor identifiers | W3C DID Core | AI-IDP uses aitrace:// URIs (canonical); can be mapped to DIDs |
| Verifiable credentials | W3C Verifiable Credentials | AI-IDP identifiers can be subjects of VCs |
| Workload identity | SPIFFE/SPIRE | AI-IDP interoperates with SPIFFE for cloud-native workloads |
| Provenance interchange | W3C PROV | AI-IDP events can be projected to PROV |
| Supply-chain attestation | in-toto | AI-IDP quality evidence includes in-toto attestations |
| Supply-chain levels | SLSA | AI-IDP L1-L4 map to SLSA levels |
| Transparency logs and signing | Sigstore/Rekor/Fulcio | AI-IDP Merkle anchoring can use Sigstore |
| Observability | OpenTelemetry | AI-IDP events can be exported as OTLP (future work) |
| Software bill of materials | SPDX, CycloneDX | AI-IDP quality evidence includes SBOM |
| Information security management | ISO/IEC 27001 | AI-IDP L3-L4 align with ISO 27001 controls |
| Privacy information management | ISO/IEC 27701 | AI-IDP privacy safeguards align with ISO 27701 |
| Security controls | NIST SP 800-53 | AI-IDP L3-L4 align with NIST 800-53 controls |
| Identity proofing | NIST SP 800-63 | AI-IDP principal identity proofing aligns with 800-63 |
| Secure software development | NIST SP 800-218 (SSDF) | AI-IDP quality evidence includes SSDF practices |
| Post-quantum signatures | NIST PQC | AI-IDP signing interface supports PQC migration |

# Standards Crosswalk
