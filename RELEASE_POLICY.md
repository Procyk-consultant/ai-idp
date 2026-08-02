---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
Secondary Contact: p.1o9.cognitive@outlook.com
Telephone: +1 (581) 668-2372
Location: Saguenay, Québec, Canada
File: RELEASE_POLICY.md
Title: Release Policy
Purpose: Define release discipline
Audience: A35 release controller, all agents
Document Classification: Internal
Classification: release
Version: 2.0.0
Status: Approved
Last Material Revision: 2026-08-01
Dependencies: VALIDATION_STATUS.md
Source Basis: Master Execution Prompt
Invariants: Releases are assembled only from validated artifacts
Failure Behaviour: Releases with critical defects are blocked
Trace Policy: Release events are AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Release Policy

## Release Authority

Pierre-Edward Procyk is the sole release authority. No package may leave the local repository without his separate written authorization.

## Release Gates

A release may be prepared only when all 13 validation gates in `project-control/VALIDATION_STATUS.md` are PASSED or PARTIAL with documented limitations; all tests pass (`pytest tests/ -v`); all conformance, security, privacy, and permanence tests pass; the arXiv paper compiles from a clean environment (`cd paper && tectonic main.tex`); all major PDFs have been visually inspected; checksums have been computed for all artifacts; the artifact manifest is complete and consistent; the validation report is complete; the final completion report is complete; and the archive has been created and its integrity verified.

## Release Artefacts

The release control directory contains `release/metadata/` (author, organization, contact, publication metadata), `release/CHECKSUMS.sha256` (canonical-file checksums), `release/NUMBERED_ARCHIVES.sha256` (hashes for the ten numbered root-level ZIP packages), `release/VALIDATION_REPORT.md`, `release/FINAL_COMPLETION_REPORT.md`, and `release/release_summary.json`.

## Versioning

Semantic versioning (MAJOR.MINOR.PATCH). Pre-1.0 versions are research releases. 2.0.0 is the first submission-ready release. Post-1.0 versions require authorization and a documented revision in `CHANGELOG.md`.

## External Release

External release (arXiv submission, government submission, public repository publication, public licence application) requires separate written authorization from Pierre-Edward Procyk. The authorization is recorded in `project-control/DECISION_LOG.md` and `project-control/PUBLICATION_METADATA_STATUS.md`.
