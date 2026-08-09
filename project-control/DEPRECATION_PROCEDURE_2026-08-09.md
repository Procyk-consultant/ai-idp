---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Record: Canonical directory and deprecation procedure
Operational date: 2026-08-09
---

# Canonical Directory and Deprecation Procedure

## Canonical root

Use only `C:\Cognitive Industries\AI-IDP-AegisTrace` as the live project root. Work only from its canonical source, documents, project-control records, and release materials. Do not treat a package under `deprecated\` as current source or as a delivery candidate without an explicit recovery decision.

## Directory intent

- `src`, `tests`, `spec`, `schemas`, `paper`, `government`, `impact`, `university`, `technical`, `research`, `science`, `threat-model`, `docs`, `examples`, and `scripts`: canonical working corpus.
- `project-control`: live operational records, current-state reconciliation, decisions, logs, validation, and hand-off material.
- `brand/originals`: immutable brand originals. Do not modify.
- `release`: approved release artefacts only.
- `deprecated`: excluded, reversible archival material. It must never be deleted, staged, committed, packaged, or used as a current source unless Pierre-Edward Procyk explicitly approves recovery.

## Current archival layout

`deprecated\2026-08-09_pre-consolidation\external-parent-items\` contains the former sibling project directories, forensic/audit material, alternate builds, previous hand-offs, and top-level archive files that had cluttered `C:\Cognitive Industries\`.

`deprecated\2026-08-09_pre-consolidation\generated-and-duplicate-root-items\` contains the moved generated output, caches, standalone browser-automation dependency, temporary rendering/browser files, and duplicate local source/hand-off archives.

See `DEPRECATION_MANIFEST_2026-08-09.md` for the exact inventory and verification counts.

## Required procedure for future work

1. Start in the canonical root; inspect `project-control/CURRENT_PUBLICATION_AND_OUTREACH_RECONCILIATION_2026-08-09.md`, `CHECKPOINT.md`, `TRACE_LOG.md`, and the current Git status.
2. Do not move, delete, overwrite, stage, commit, push, publish, submit, or send anything merely to make the tree appear clean.
3. For any new generated output, use a purpose-specific ignored working directory or an approved release location. Do not recreate generic root-level `tmp`, `node_modules`, `.aitrace-*`, or duplicate ZIP files.
4. Before restoring archival material, compare its purpose, date, file count, checksum where available, and authoritative status against the canonical corpus. Obtain explicit approval before any restoration.
5. Do not re-add the retired `tmp` render and style artefacts. Their prior tracked history is preserved by the consolidation commit and their physical copies are retained under `deprecated`. New temporary material belongs in an ignored working directory.
6. Record any future movement in `project-control/TRACE_LOG.md` and append the material state to `CHECKPOINT.md`; preserve a destination manifest with exact paths and verification evidence.
7. Treat untracked output from other agents as unreviewed until it passes source, tooling, and test-scope review. Archive unsupported or stale artefacts instead of allowing them to remain in canonical source, test, or instruction paths.

## Safe recovery

Recovery is a direct move from the dated archival path back to the intended canonical or parent path after a review. Never recover whole trees wholesale. Recover only the named item needed, verify it at the destination, and record the action. Do not overwrite a destination that already exists without explicit approval.
