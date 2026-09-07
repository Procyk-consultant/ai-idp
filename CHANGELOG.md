---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
Secondary Contact: p.1o9.cognitive@outlook.com
Telephone: 
Location: Saguenay, Québec, Canada
File: CHANGELOG.md
Title: Changelog
Purpose: Record material revisions
Audience: All readers
Document Classification: Public
Classification: documentation
Version: 2.1.0
Status: Published on GitHub main
Last Material Revision: 2026-09-07
Dependencies: release metadata
Source Basis: Master Execution Prompt
Invariants: Revisions are append-only
Failure Behaviour: Missing revisions are a defect
Trace Policy: Revisions are AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Changelog

All material revisions are recorded here. Semantic versioning is used.

## [2.1.0] — 2026-09-07 — Reconciliation, evidence repair, and consumer publication

- Established v2.1.0 as the authoritative project version on GitHub `main` while retaining v2.0.0 as the historical Zenodo baseline.
- Integrated the 124-commit post-v2.0.0 reconciliation line containing authorization, authenticated API writes, replay resistance, durable approval state, public disclosure controls, federation, storage, signing, and test hardening.
- Fixed dependency injection of an empty append-only ledger in the API; the former falsey-value fallback discarded the caller-supplied ledger.
- Added a narrow ledger protocol at the event-collection boundary so both append-only and batched ledgers satisfy the typed contract.
- Hardened GCP KMS public-key verification to reject non-EC keys explicitly.
- Made native liboqs validation opt-in and removed it from the standard full-test extra because importing the package can download and compile native code when liboqs is absent.
- Reconciled the Indigenous engagement rule as contextual: meaningful rights-holder engagement remains required where Indigenous rights, community data, governance authority, or services are materially implicated; it is not a universal gate for unrelated implementations.
- Preserved the historical v2.0.0 release corpus and DOI metadata without rewriting them as v2.1.0 evidence.
- Added a consumer-first GitHub README and a bilingual English/Canadian French plain-language guide.
- Added the official AI-IDP and AegisTrace logo set, colour and typography references, and a checksum-verified brand index without altering the source assets.
- Added eight previously generated AI-IDP/AegisTrace article and social-media visuals, a public gallery, and an evidence-separated media manifest.
- Excluded a duplicate visual and an illustrative payment graphic that could be mistaken for a real transaction.
- Updated the declared test-client dependency from deprecated `httpx` to Starlette's current `httpx2` path and added a metadata regression check.
- Added the Python `build` frontend to the development and full-validation profiles because wheel creation is a documented release gate.
- Modernized package licence metadata to PEP 639 using `LicenseRef-Proprietary` and explicit legal files without changing the All Rights Reserved terms.
- Publication to GitHub `main` was explicitly authorized on 2026-09-07; tagging, GitHub release creation, DOI/Zenodo changes, deployment, and third-party publication remain separate actions.
- Published the consumer/code payload as commit `e9c13b9b4504c1f39e516f8c0b29f7faba3f816f` and independently confirmed the exact GitHub `main` ref after the non-force fast-forward.

## [2.0.0] — 2026-08-01 — Coherence alignment pass

- Coherence alignment pass executed by Hermes on 2026-08-01.
- Aligned `Last Material Revision` to 2026-08-01 across all authored documents.
- Confirmed project version `2.0.0` is uniform across `CITATION.cff`, `pyproject.toml`, `README.md`, paper `main.tex`, all `release/metadata/*.json`, and all `schemas/*.json`.
- Confirmed logo SHA-256 (`c5ed7859f5d7cd5ac4cd174c42f9d0437ae7a2511d9ba25925a3375292ed1d19`) matches official Cognitive Industries bilingual lockup.
- Test count: 11 test files (113 tests confirmed via pytest collection and execution).
- Spec count: 25 files in `spec/` (24 protocol documents + 1 terminology, per classification rule).
- Schema count: 14 JSON Schema files in `schemas/`, all parse cleanly.
- Reference count: 57 entries in `paper/references.bib`.
- French translations (`_FR.md`) created for the 39 documents that previously lacked bilingual coverage; existing 3 FR documents preserved.
- Historical entries below (1.0.0, 1.1.0, original [2.0.0] — 2026-07-28) are preserved unchanged. The original [2.0.0] entry retains its 2026-07-28 stamp as the material revision date of the substance; this new entry documents the coherence-alignment pass executed on 2026-08-01.
- All corrections logged in `RUN_LOG.jsonl` (append-only).
- Audit reports produced under `C:/Cognitive Industries/_AUDIT_AI-IDP_2026-08-01/` (external to the project root to avoid breaking SHA-256 integrity of released archives).


## [2.0.0] — 2026-07-28

### Added — Production Hardening
- PostgreSQL storage backend (`src/aegistrace/storage/postgres.py`) with JSONB columns, BIGSERIAL sequencing, SSL-by-default, access logging, legal holds, Merkle anchor persistence.
- HSM-backed key management interface (`src/aegistrace/signing/hsm.py`) with three backends: InMemoryKeyBackend (development), PKCS11KeyBackend (on-prem HSM via PyKCS11), CloudKMSKeyBackend (AWS KMS / Azure Key Vault / GCP KMS). HSMKeyService factory class with `for_development`, `for_pkcs11`, `for_aws_kms`, `for_azure_kv`, `for_gcp_kms` constructors.
- Higher-throughput batched ledger with write-ahead log (`src/aegistrace/ledger/batched.py`): configurable batch size and flush interval, WAL durability with fsync, backpressure protection, background flush thread, crash recovery via WAL replay.
- OpenTelemetry runtime exporter (`src/aegistrace/adapters/otel.py`): exports AegisTrace events as OTel spans, OTLP/HTTP endpoint, env-based configuration, non-blocking batch span processor, OTelEventHook for EventCollector integration.
- Post-quantum signature migration (`src/aegistrace/signing/pqc.py`): abstract SignatureScheme interface, Ed25519Scheme, MLDSA65Scheme (FIPS 204, formerly CRYSTALS-Dilithium), SLHDSA128sScheme (FIPS 205, formerly SPHINCS+), SchemeRegistry, MigrationService with plan_migration and migrate_events methods.
- Live GitHub remote integration (`src/aegistrace/adapters/github_remote.py`): GitHubRemotePusher with REST API push (file creation/update), git CLI push, Merkle anchor push, revocation status push, certification status push, private evidence push; GitHubRemoteStub for environments without credentials; make_github_pusher factory.

### Added — Tests
- 22 new tests in `tests/unit/test_production_hardening.py` covering PostgreSQL config, HSM backends, batched ledger, PQC schemes, OTel exporter, GitHub remote stub.
- Total: 113 passing tests (89 original + 22 production-hardening + 2 project-metadata tests).

### Added — Deeper Citation Chaining (Depth 3+)
- 14 additional sources in `paper/references.bib` (34 total): FIPS 204/205/203, CAISI, Bill C-27 prorogation status, Schwartz Reisman Institute analysis, Canada's "AI for All" strategy, Canada-UK AI alignment partnership, EU AI Act in-force status, W3C VC v2.0, Quebec Bill 69 status, NCCID First Nations data governance.
- Updated evidence register with 14 new sources (57 total).
- Closed source gaps G-011 (AIDA legislative fate — confirmed Bill C-27 died at prorogation January 2025) and G-012 (CAISI mandate — confirmed establishment November 2024).
- New file: `project-control/LEGAL_STATUS_UPDATE_v2.0.0.md` documenting the legal status updates.

### Added — French Body Translation
- `government/NOTE_DE_SYNTHESE_FR.{md,pdf}` — French executive summary.
- `technical/ARCHITECTURE_TECHNIQUE_FR.{md,pdf}` — French technical architecture summary.
- `impact/IMPACT_CANADIEN_FR.{md,pdf}` — French impact summary.

### Updated
- `pyproject.toml`: version bumped to 1.1.0; added optional dependencies for postgres, otel, pqc, hsm-pkcs11, hsm-aws, hsm-azure, hsm-gcp; added `requests` to core dependencies.
- `src/aegistrace/__init__.py`: version bumped to 2.0.0; exports new modules (PostgresConfig, PostgresStorage, HSMKeyHandle, KeyBackend, InMemoryKeyBackend, PKCS11KeyBackend, CloudKMSKeyBackend, HSMKeyService, BatchConfig, BatchedLedger, BackpressureError, SignatureScheme, KeyPair, Ed25519Scheme, MLDSA65Scheme, SLHDSA128sScheme, SchemeRegistry, SchemeMigrationRecord, MigrationService, default_registry, OTelConfig, OTelExporter, OTelEventHook, GitHubConfig, GitHubRemotePusher, GitHubRemoteStub, make_github_pusher).
- `project-control/VALIDATION_STATUS.md`: updated to v2.0.0 with improved gate status.

### Documentation
- All new modules include comprehensive docstrings with sound engineering practices headers, invariants, failure behaviour, and usage examples.

### Notes
- No external publication performed.
- No public licence applied.
- No brand originals modified.
- All synthetic data clearly labelled.
- Live integrations (HSM, PQC, PostgreSQL, OTel collector, GitHub remote) are interface-complete and tested; activation requires credentials/libraries documented in pyproject.toml optional-dependencies.

## [2.0.0] — 2026-07-28

### Added

- Complete root repository structure per Master Prompt §32.
- Project control files: status, decision log, task graph, artifact manifest, assumption register, blocker register, risk register, source gap register, protocol deviations, validation status, run log, checkpoint, handoff, recovery instructions.
- Verified author data (MD + JSON) and missing-author-data register.
- Brand asset preservation: 3 official PNGs with SHA-256 checksums.
- Brand identity rules: AUTHOR_IDENTITY.md, CONTACT_BLOCKS.md, DOCUMENT_IDENTITY_RULES.md.
- Release metadata: author.json, organization.json, contact.json, publication_metadata.json.
- Research protocol, terminology, source hierarchy, evidence register, contradiction register, cross-domain synthesis.
- University research package (MD + DOCX + PDF).
- Scientific package: hypotheses, variables, experiment protocol, statistical analysis plan, reproducibility.
- Technical specification: 25 specification documents.
- Core JSON schemas: 14 schemas.
- AegisTrace reference implementation: identity, registry, ledger, signing, delegation, authorization, events, manifests, adapters (filesystem, git, github, database, mcp), CLIs (verify, audit, reconstruct, admin), API server, SQLite storage.
- Test suites: unit, integration, security, privacy, permanence, conformance.
- Threat model and attack trees.
- 11 worked examples.
- Documentation: quickstart, developer guide, architecture guide, auditor guide, regulator guide, CLI guide, API guide, security guide, privacy guide, offline guide, federation guide, recovery guide, migration guide, certification guide.
- arXiv LaTeX paper project + compiled PDF (Tectonic).
- Canadian government proposal (MD + DOCX + PDF).
- Canadian policy white paper (MD + PDF).
- Draft statute: Proposed AI Actor Identity and Traceability Act.
- Federal-provincial jurisdiction analysis, Charter analysis, privacy and human-rights analysis.
- Business and operations impact report (MD + PDF).
- HR and labour impact report (MD + PDF).
- Societal impact assessment (MD + PDF).
- Administrative implementation plan.
- Benchmarks with synthetic data (clearly labelled).
- Conformance suite.
- Release package: checksums, validation report, final completion report, archive.

### Notes

No external publication performed. No public licence applied. No brand originals modified. All synthetic data clearly labelled.

<!-- COHERENCE UPDATE 2026-08-01: Last Material Revision date aligned to project delivery date. Historical content above is preserved unchanged. -->
