# Cross-Domain Synthesis

Last Material Revision: 2026-08-01

## Integrated Causal Model

The AI accountability gap (cause) leads to harm to affected persons, organizations, regulators, and insurers (effect). The harm is widening as AI deployment grows (intervening factor). AI-IDP addresses the gap by providing universal persistent identity, permanent traceability, delegation, quality evidence, accountability, and conformity (intervention).

## Integrated Governance Model

The integrated governance model combines: (1) national standard (Standards Council of Canada); (2) administrative amendment (Treasury Board Directive); (3) legislation (proposed AI Actor Identity and Traceability Act); (4) procurement (federal procurement profile); (5) AIA extension; (6) cooperative federalism (national minimum standard with provincial equivalent-or-stronger regimes); (7) sectoral certification (regulated sectors); (8) insurance and liability (AI liability insurance, statutory civil liability).

## Requirement Matrix

| Requirement | Source | Implementation | Test |
|-------------|--------|---------------|------|
| Persistent AI Actor identifiers | spec/IDENTITY_PROTOCOL.md | identity/ids.py | tests/unit/test_identity.py |
| Permanent resolvability | spec/IDENTITY_LIFECYCLE.md | identity/lifecycle.py | tests/permanence/test_permanence.py |
| Append-only ledger | spec/EVENT_PROTOCOL.md | ledger/append_only.py | tests/unit/test_ledger.py |
| Hash-chain integrity | spec/EVENT_PROTOCOL.md | ledger/append_only.py | tests/unit/test_ledger.py |
| Ed25519 signatures | spec/EVENT_PROTOCOL.md | signing/ed25519.py | tests/unit/test_signing.py |
| Delegation | spec/DELEGATION_PROTOCOL.md | delegation/broker.py | tests/unit/test_delegation.py |
| Authorization and approval | spec/AUTHORIZATION_PROTOCOL.md, spec/APPROVAL_PROTOCOL.md | authorization/engine.py | tests/unit/test_authorization.py |
| Visibility tiers | spec/REGISTRY_PROTOCOL.md | events/models.py | tests/privacy/test_redaction.py |
| Conformance levels | spec/CONFORMANCE_LEVELS.md | spec/CONFORMANCE_LEVELS.md | tests/conformance/test_conformance.py |
| Quality evidence | spec/QUALITY_EVIDENCE_PROTOCOL.md | quality-evidence.schema.json | tests/conformance/test_conformance.py |
| Privacy safeguards | spec/DISCLOSURE_PROTOCOL.md | events/models.py, identity/lifecycle.py | tests/privacy/test_redaction.py |

## Conflict Matrix

| Conflict | Resolution |
|----------|-----------|
| Permanent traceability vs privacy | Permanent minimal metadata; pseudonymous identifiers; sealed records; content separation; access logging; recourse |
| Universal scope vs small-developer burden | Tiered conformance (L1-L4); small-developer profile; open-source profile |
| Federal jurisdiction vs provincial jurisdiction | Cooperative federalism; national minimum standard; provincial equivalence |
| Permanence vs cryptographic obsolescence | Interface-isolated signing; documented PQC migration path; long-term signature migration |
| Public verification vs sealed records | Visibility tiers; PUBLIC tier for non-sensitive fields; SEALED tier for sensitive records |
| Canadian framework vs international interoperation | Federation protocol; standards crosswalk (W3C PROV, DID, VC; SPIFFE; in-toto; SLSA; Sigstore; OpenTelemetry) |
| AI-IDP vs Indigenous data sovereignty | OCAP®-aligned handling; distinctions-based approach; TRC Calls to Action alignment; consultation precondition |

## Design Constraints

1. The framework must use established cryptographic primitives (no custom crypto).
2. The framework must be provider-neutral (no provider-specific assumptions).
3. The framework must be jurisdiction-aware (Canadian primary; provincial sub-authority).
4. The framework must accommodate offline operation.
5. The framework must support federation.
6. The framework must respect Indigenous data sovereignty.
7. The framework must be Charter-compliant.
8. The framework must be privacy-law-compliant (PIPEDA, Privacy Act, provincial statutes).
9. The framework must be implementable at low cost for L1.
10. The framework must be enforceable through Canadian law.

# Cross-Domain Synthesis
