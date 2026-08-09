---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Record: Deprecation and consolidation manifest
Operational date: 2026-08-09
Authority: Pierre-Edward Procyk — local consolidation instruction
---

# Deprecation Manifest — 2026-08-09

## Purpose and boundary

This record documents a reversible local consolidation. `C:\Cognitive Industries\AI-IDP-AegisTrace` remains the canonical project root. No source content was edited, no material was deleted, and no external service was contacted. The archival destination is excluded from Git to prevent large historical material from being staged accidentally.

## External parent items moved intact

All of the following were moved from `C:\Cognitive Industries\` to `deprecated\2026-08-09_pre-consolidation\external-parent-items\` inside the canonical root. Post-move verification confirmed that every former source path was absent and every destination path existed.

| Item | Kind | Pre-move verification |
|---|---|---:|
| `_AUDIT_AI-IDP_2026-08-01` | directory | 4,539 files |
| `AI-IDP-AegisTrace - old version` | directory | 5,440 files |
| `AI-IDP-AegisTrace_REBUILT_20260728_123644` | directory | 258 files |
| `AI-IDP-AegisTrace-FINAL` | directory | 267 files |
| `AI-IDP-AegisTrace-NOTEBOOKLM` | directory | 180 files |
| `AI-IDP-NEXT-AI-HANDOFF-2026-08-02` | directory | 31 files |
| `GLM_AI-IDP-AegisTrace` | directory | 431 files |
| `forensics` | directory | 11 files |
| `_AUDIT_AI-IDP_2026-08-01.zip` | file | 111,262,377 bytes |
| `ai-idp_aegistrace_project-planner.html` | file | 11,472 bytes |
| `AI-IDP-01-ARXIV-PAPER.zip` | file | 205,621 bytes |
| `AI-IDP-02-SOURCE-CODE.zip` | file | 128,674 bytes |
| `AI-IDP-03-SPECS-SCHEMAS.zip` | file | 79,447 bytes |
| `AI-IDP-04-GOVERNMENT.zip` | file | 14,533,969 bytes |
| `AI-IDP-05-IMPACT-REPORTS.zip` | file | 9,648,645 bytes |
| `AI-IDP-06-UNIVERSITY-TECHNICAL.zip` | file | 7,305,048 bytes |
| `AI-IDP-07-RESEARCH.zip` | file | 39,574 bytes |
| `AI-IDP-08-PROJECT-CONTROL.zip` | file | 80,487 bytes |
| `AI-IDP-09-BRAND.zip` | file | 6,343,346 bytes |
| `AI-IDP-10-ROOT-AND-DELIVERABLES.zip` | file | 4,903,517 bytes |
| `AI-IDP-AegisTrace - old version.zip` | file | 178,577,225 bytes |
| `AI-IDP-AegisTrace.zip` | file | 226,392,922 bytes |

Totals: 8 directories containing 11,157 files, plus 14 standalone files totaling 559,512,324 bytes.

## Generated and duplicate canonical-root items moved intact

The following were moved from the canonical root to `deprecated\2026-08-09_pre-consolidation\generated-and-duplicate-root-items\`. They are retained as historical or regenerated material, not deleted.

| Item | Classification | Pre-move verification |
|---|---|---:|
| `.aitrace-demo` | demo runtime output | 2 files |
| `.aitrace-final-demo-20260802` | demo runtime output | 2 files |
| `.aitrace-reverify` | re-verification runtime output | 2 files |
| `.mypy_cache` | type-check cache | 18 files |
| `.pytest_cache` | test cache | 5 files |
| `.ruff_cache` | lint cache | 19 files |
| `node_modules` | standalone browser-automation dependency | 180 files |
| `tmp` | generated renders and Zenodo/browser working material | 103 files |
| `CUsersAgenczenodo_upload.log` | local upload log | 2,601 bytes |
| `AI-IDP-AegisTrace-2.0.0-source.zip` | duplicate source archive | 187,358,118 bytes |
| `AI-IDP-NEXT-AI-HANDOFF-2026-08-02.zip` | duplicate hand-off archive | 130,678 bytes |
| `AI-IDP-NEXT-AI-HANDOFF-2026-08-02.zip.sha256` | duplicate hand-off checksum | 105 bytes |
| `package.json` | standalone Playwright dependency manifest | 56 bytes |
| `package-lock.json` | standalone Playwright dependency lockfile | 1,601 bytes |

## Repository alignment

`tmp` included 91 Git-tracked generated render and style artefacts. Their intact copies are retained in the ignored archival area; the consolidation commit formally retires only their canonical tracked copies. This is the intended repository outcome: the current source tree is clean of generated temporary material while Git history retains the former versions. Existing unrelated dirty working-tree changes are excluded from this commit.

## Safeguards added

- `.gitignore` now contains `/deprecated/`.
- `git check-ignore --no-index` confirmed the archival destination is ignored.
- Canonical `.git`, `.github`, `.venv`, source directories, project-control records, and `brand/originals` were not moved.
