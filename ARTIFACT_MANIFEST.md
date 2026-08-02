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
File: ARTIFACT_MANIFEST.md
Title: Artifact Manifest (Human-Readable)
Purpose: Human-readable artifact manifest
Audience: All readers
Document Classification: Internal
Classification: documentation
Version: 2.0.0
Status: Approved
Last Material Revision: 2026-08-01
Dependencies: project-control/ARTIFACT_MANIFEST.csv
Source Basis: Master Execution Prompt
Invariants: Manifest matches actual artifacts
Failure Behaviour: Missing artifacts are a defect
Trace Policy: Manifest updates are AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Artifact Manifest

The complete machine-readable manifest is `project-control/ARTIFACT_MANIFEST.csv`. This file is a human-readable summary.

## Categories

The manifest covers project control, governance and intellectual-property records, preserved brand originals, research and scientific evidence, 25 specification documents, 14 JSON Schemas, the AegisTrace implementation and adapters, the 113-test suite, examples, documentation, the arXiv paper, university materials, Canadian government documents, impact reports, administration, the threat model, deterministic build tools, metadata, checksums, and the ten numbered release packages.

## Checksums

Canonical-file checksums are in `release/CHECKSUMS.sha256`. Hashes for the ten numbered packages are in `release/NUMBERED_ARCHIVES.sha256`.

## Validation

Each artifact has an associated validation status in `project-control/VALIDATION_STATUS.md`. Major PDFs have per-PDF validation records in their respective `validation/` subdirectories.
