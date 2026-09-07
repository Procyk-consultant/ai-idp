---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/ARTIFACT_MANIFEST_RECONCILIATION_2026-09-06.md
Purpose: Reconcile historically listed artifacts with the current Git-controlled public corpus
Classification: internal control record
Version: 2.0.0
Status: Current reconciliation
Operational date: 2026-09-06
Licence Status: No public licence is granted.
---

# Artifact Manifest Reconciliation — 2026-09-06

## Decision boundary

This record reconciles evidence; it does not restore, delete, publish, or recreate any historical artifact. The original `project-control/ARTIFACT_MANIFEST.csv`, release reports, and archive hash manifest remain preserved as historical records. Current public-corpus membership is defined by Git-controlled files and verified by `scripts/reconcile_release_checksums.py`.

## Verified discrepancy

The historical CSV contains 184 rows marked `complete`. On 2026-09-06, 163 listed paths existed in the canonical working tree and 21 did not. The absent paths divide into three evidence-supported classes.

### Intentionally retired privacy-bearing records — 7

| Historical path | Current disposition | Evidence |
|---|---|---|
| `project-control/VERIFIED_AUTHOR_DATA.md` | Intentionally retired; do not restore automatically | Removed in commit `aefb3eb` because it contained personal contact and author data; removal rationale is preserved in `project-control/TRACE_LOG.md`. |
| `project-control/VERIFIED_CONTACT_DATA.json` | Intentionally retired; do not restore automatically | Removed in commit `aefb3eb` because it contained personal contact data; removal rationale is preserved in `project-control/TRACE_LOG.md`. |
| `project-control/MISSING_AUTHOR_DATA.md` | Intentionally retired; do not restore automatically | Removed in commit `aefb3eb` because it enumerated absent personal-data fields; removal rationale is preserved in `project-control/TRACE_LOG.md`. |
| `CITATION.cff` | Intentionally retired; a privacy-safe replacement would require separate content approval | Removed in commit `aefb3eb` because it contained a personal email address; removal rationale is preserved in `project-control/TRACE_LOG.md`. |
| `release/metadata/author.json` | Intentionally retired; do not restore automatically | Removed in commit `aefb3eb` as personal author metadata. |
| `release/metadata/organization.json` | Intentionally retired; do not restore automatically | Removed in commit `aefb3eb` as organization contact metadata. |
| `release/metadata/contact.json` | Intentionally retired; do not restore automatically | Removed in commit `aefb3eb` as personal contact metadata. |

### Historical, never tracked in this repository history — 4

| Historical path | Current disposition | Evidence |
|---|---|---|
| `government/OFFICIAL_PROJECT_DOCUMENT_EN.md` | Historical-only; content review required before any restoration | Absent from the current tree and every inspected repository revision, including initial commit `079fd59`, current `main`, and `reconcile-2026-08-14`. |
| `OFFICIAL_PROJECT_DOCUMENT_EN.pdf` | Historical-only; do not reintroduce an archived binary without source and privacy validation | Absent from inspected Git history; older intact copies exist only in the ignored deprecation archive. |
| `government/DOCUMENT_OFFICIEL_PROJET_FR.md` | Historical-only; content review required before any restoration | Absent from the current tree and every inspected repository revision, including initial commit `079fd59`, current `main`, and `reconcile-2026-08-14`. |
| `DOCUMENT_OFFICIEL_PROJET_FR.pdf` | Historical-only; do not reintroduce an archived binary without source and privacy validation | Absent from inspected Git history; older intact copies exist only in the ignored deprecation archive. |

The active tracked government corpus uses the current `government/` materials, including the Canadian national project proposal, policy white paper, bilingual synthesis note, jurisdiction and rights analyses, procurement profile, and proposed Act. This classification does not claim those current documents are byte-for-byte replacements for the four historical paths.

### Historical numbered release packages — 10

| Historical path | Current disposition |
|---|---|
| `AI-IDP-01-ARXIV-PAPER.zip` | Preserved under `deprecated/2026-08-09_pre-consolidation/external-parent-items/`; SHA-256 matches `release/NUMBERED_ARCHIVES.sha256`. |
| `AI-IDP-02-SOURCE-CODE.zip` | Preserved under the same ignored archive; SHA-256 matches. |
| `AI-IDP-03-SPECS-SCHEMAS.zip` | Preserved under the same ignored archive; SHA-256 matches. |
| `AI-IDP-04-GOVERNMENT.zip` | Preserved under the same ignored archive; SHA-256 matches. |
| `AI-IDP-05-IMPACT-REPORTS.zip` | Preserved under the same ignored archive; SHA-256 matches. |
| `AI-IDP-06-UNIVERSITY-TECHNICAL.zip` | Preserved under the same ignored archive; SHA-256 matches. |
| `AI-IDP-07-RESEARCH.zip` | Preserved under the same ignored archive; SHA-256 matches. |
| `AI-IDP-08-PROJECT-CONTROL.zip` | Preserved under the same ignored archive; SHA-256 matches. |
| `AI-IDP-09-BRAND.zip` | Preserved under the same ignored archive; SHA-256 matches. |
| `AI-IDP-10-ROOT-AND-DELIVERABLES.zip` | Preserved under the same ignored archive; SHA-256 matches. |

The packages remain recoverable historical evidence, not active root-level Git artifacts. No ZIP was copied, rebuilt, staged, or published during this reconciliation.

## Result

- The 21 absent historical paths are fully accounted for without reconstructing or exposing sensitive material.
- `project-control/ARTIFACT_MANIFEST.csv` is retained unchanged as a historical v2.0.0 inventory.
- `release/NUMBERED_ARCHIVES.sha256` is retained unchanged as historical archive evidence.
- `release/CHECKSUMS.sha256` is regenerated only from staged Git blobs, after exact-path staging and an unstaged-change check, and then verified against those repository bytes.
- A release-completeness claim still requires the separate gates in `RELEASE_POLICY.md`; this reconciliation alone is not a release, deployment, or publication receipt.
