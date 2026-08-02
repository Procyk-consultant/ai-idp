---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/DECISION_LOG.md
Title: Decision Log
Purpose: Record all material design and implementation decisions made autonomously
Version: 2.0.0
Last Material Revision: 2026-08-01
---

# Decision Log

The Master Execution Prompt authorizes autonomous reasonable, documented, reversible decisions when multiple valid implementation options exist. This file records every such decision.

## D-001 — Project root location
- **Decision:** Place the root at `/home/z/my-project/download/ai-idp-aegistrace/`.
- **Rationale:** The `download/` directory is the user-visible deliverable surface; the `ai-idp-aegistrace/` name matches the Master Prompt §32 repository name.
- **Reversible:** Yes — directory can be moved.
- **Date:** 2026-08-01.

## D-002 — Brand asset preservation
- **Decision:** Copy the three uploaded brand PNGs verbatim into `brand/originals/`, compute SHA-256 checksums, and never modify the originals. Derivatives go only in `brand/derivatives/`.
- **Rationale:** Master Prompt §F mandates preservation, checksums, no recolouring, no regeneration.
- **Reversible:** No (originals must never be touched).
- **Date:** 2026-08-01.

## D-003 — Implementation language and framework
- **Decision:** Python 3.12, FastAPI-style Pydantic v2 models for canonical records, standard library `hashlib` and `cryptography` Ed25519 for signatures, SQLite for local canonical storage, JSON Schema for validation, pytest for tests.
- **Rationale:** Master Prompt §21 default technical stack. Provider-neutral, mature, available in the environment.
- **Reversible:** Yes — core domain types are isolated from persistence.
- **Date:** 2026-08-01.

## D-004 — Cryptographic signature scheme
- **Decision:** Ed25519 via the `cryptography` library (RFC 8032). No custom primitives.
- **Rationale:** Master Prompt §21 mandates established libraries and a justified modern scheme; Ed25519 is deterministic, fast, compact, and widely implemented.
- **Reversible:** Yes — `signing/` module abstracts the scheme; future migration to Ed448 or a post-quantum scheme can be added behind the same interface.
- **Date:** 2026-08-01.

## D-005 — Hash function
- **Decision:** SHA-256 for content digests and event hashes; BLAKE2b-256 available for optional high-throughput paths.
- **Rationale:** SHA-256 is universally available, well analysed, and sufficient for the threat model; BLAKE2b is a documented fallback for performance-critical paths.
- **Reversible:** Yes.
- **Date:** 2026-08-01.

## D-006 — Ledger structure
- **Decision:** Append-only JSON Lines (`ledger.jsonl`) as the canonical local ledger; each event carries `previous_event_hash` and `event_hash` forming a hash chain. A periodic Merkle root is anchored to a public verification surface for tamper-evidence beyond the local store.
- **Rationale:** Master Prompt §7 specifies append-only, sequence-aware, tamper-evident, independently verifiable records; hash-chained JSONL is simple, auditable, and trivially diff-able.
- **Reversible:** Yes — storage engine is behind an interface.
- **Date:** 2026-08-01.

## D-007 — Identity URI scheme
- **Decision:** Use URIs of the form `aitrace://ca/<entity>/<slug>#<version-or-instance>` for all canonical identities. The `ca` authority segment encodes the primary jurisdiction.
- **Rationale:** Resolvable, human-readable, jurisdiction-aware, and stable across provider switches. Avoids prematurely committing to a DID method that may not survive standardization.
- **Reversible:** Yes — URIs are strings; the resolver indirection supports future DID/W3C mapping.
- **Date:** 2026-08-01.

## D-008 — Visibility tiers
- **Decision:** Four visibility tiers: `PUBLIC`, `CONTROLLED`, `ORGANIZATION_PRIVATE`, `SEALED`.
- **Rationale:** Master Prompt §5 implies tiered disclosure; sealed records support judicial/regulator access without exposing raw content.
- **Reversible:** Yes.
- **Date:** 2026-08-01.

## D-009 — GitHub integration scope
- **Decision:** Implement a GitHub adapter that produces commit-attestation payloads, Git-notes evidence, and Merkle-root anchors suitable for a private evidence repository and a public verification repository. The adapter does not push to a live remote during this autonomous run.
- **Rationale:** Master Prompt §0 forbids external publication; §8 requires GitHub integration as an evidence surface. The adapter is fully functional against local Git repositories and produces ready-to-push payloads.
- **Reversible:** Yes.
- **Date:** 2026-08-01.

## D-010 — arXiv compilation
- **Decision:** Compile the arXiv paper using Tectonic with a clean working directory; emulate the standard `arxiv` class behaviour via `article` plus `hyperref`, `cleveref`, `booktabs`, `amsmath`, and `biblatex`/`bibtex` fallback.
- **Rationale:** Tectonic is the available LaTeX engine; the paper must compile from a clean environment per Gate 10.
- **Reversible:** Yes.
- **Date:** 2026-08-01.

## D-011 — PDF rendering for reports
- **Decision:** Use ReportLab (via the project's pdf skill) for major MD+PDF pairs, with the Cognitive Industries palette and Manrope typography. Covers use restrained brand treatment with navy/gold.
- **Rationale:** Master Prompt Addendum D requires visually rich PDFs; ReportLab produces vector PDFs with reliable font embedding and consistent pagination.
- **Reversible:** Yes.
- **Date:** 2026-08-01.

## D-012 — Bilingual treatment
- **Decision:** Bilingual identity is applied to the organization name, the government proposal cover, and the arXiv title page (English primary, French subtitle). Body content is English with French key-term annotations where the Canadian legal context requires it (e.g., *Loi sur l'intelligence artificielle*).
- **Rationale:** Master Prompt §34 mandates bilingual organization identity; full bilingual body would multiply authoring cost without proportional benefit at this stage.
- **Reversible:** Yes — full French translation is a documented future work item.
- **Date:** 2026-08-01.

## D-013 — Open-source licence
- **Decision:** No public licence applied. The `LICENSING_STATUS.md` file records that no licence is selected unless approved in writing by Pierre-Edward Procyk.
- **Rationale:** Master Prompt §0 and §K forbid applying a public licence without authorization.
- **Reversible:** Yes — a licence file can be added when authorized.
- **Date:** 2026-08-01.

## D-014 — Synthetic vs. real data
- **Decision:** All benchmark and example data are explicitly labelled synthetic, generated by reproducible scripts with fixed random seeds. No synthetic datum is represented as an external empirical observation.
- **Rationale:** Master Prompt §17 and §35 forbid fabricated data and require synthetic data to be labelled.
- **Reversible:** Yes.
- **Date:** 2026-08-01.

## D-015 — Research evidence handling
- **Decision:** Canadian primary sources are cited from official public references (Parliament of Canada, Department of Justice Canada, OPC, Treasury Board, ISED, CAISI, Public Safety, CSE, Library and Archives Canada, Standards Council of Canada, provincial legislatures and privacy regulators, CanLII). Where a primary source is referenced, the citation includes the official title and publishing body; URLs are recorded in the bibliography. The project does not claim to have downloaded and stored full-text copies of every cited instrument; in those cases the citation is to the public reference and labelled as such.
- **Rationale:** Master Prompt §13 requires source records with title/author/organization/date/URL; §35 forbids fabrication.
- **Reversible:** Yes.
- **Date:** 2026-08-01.

## D-016 — Canonical Windows root and numbered release suite
- **Decision:** The canonical operating root is `C:\Cognitive Industries\AI-IDP-AegisTrace`. The release is delivered as ten audience- and function-specific numbered ZIP packages, not as a nonexistent monolithic release archive. Each package must CRC-validate and every packaged file must byte-match its canonical path.
- **Rationale:** The final corpus audit found obsolete build-environment paths, false monolithic-archive claims, and package drift. Reconciliation to the real Windows root and existing ten-package partition preserves the intended handoff structure without inventing an artifact.
- **Reversible:** Yes — package scope can change through a documented future release decision, but current v2.0.0 records and hashes must remain internally coherent.
- **Date:** 2026-08-02.
