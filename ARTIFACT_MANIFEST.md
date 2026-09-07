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
File: ARTIFACT_MANIFEST.md
Title: Artifact Manifest (Human-Readable)
Purpose: Human-readable artifact manifest
Audience: All readers
Document Classification: Internal
Classification: documentation
Version: 2.0.0
Status: Historical v2.0.0 inventory with current reconciliation overlay
Last Material Revision: 2026-09-06
Dependencies: project-control/ARTIFACT_MANIFEST.csv; project-control/ARTIFACT_MANIFEST_RECONCILIATION_2026-09-06.md
Source Basis: Master Execution Prompt
Invariants: Current membership claims are reconciled against the Git-controlled public corpus
Failure Behaviour: Unreconciled missing artifacts block current completeness claims
Trace Policy: Manifest updates are AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Artifact Manifest

`project-control/ARTIFACT_MANIFEST.csv` is the original v2.0.0 release inventory. It is preserved as historical evidence and is not, by itself, a current working-tree manifest. The current disposition of its 21 absent paths is recorded in `project-control/ARTIFACT_MANIFEST_RECONCILIATION_2026-09-06.md`.

## Categories

The historical inventory covers project control, governance and intellectual-property records, preserved brand originals, research and scientific evidence, 25 specification documents, 14 JSON Schemas, the AegisTrace implementation and adapters, the test suite, examples, documentation, the paper, university materials, Canadian government documents, impact reports, administration, the threat model, deterministic build tools, metadata, checksums, and ten numbered release packages. Some listed privacy-bearing records were intentionally retired, four government deliverables were never tracked in this repository history, and the numbered packages are retained only in the ignored historical archive.

## Checksums

Current Git-controlled public-corpus checksums are in `release/CHECKSUMS.sha256`; `scripts/reconcile_release_checksums.py` derives membership from the Git index so unrelated untracked or ignored files cannot enter the manifest accidentally. `release/NUMBERED_ARCHIVES.sha256` preserves the hashes of the ten historical numbered packages; those packages are not current root-level Git artifacts.

## Validation

Historical validation status is retained in `project-control/VALIDATION_STATUS.md`. It does not replace current verification. Current repository state, limitations, and approval boundaries are maintained in `project-control/PHASE_FOLLOW_UP.md` and the dated reconciliation record.
