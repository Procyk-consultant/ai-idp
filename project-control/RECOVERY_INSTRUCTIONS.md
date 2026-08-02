---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/RECOVERY_INSTRUCTIONS.md
Title: Recovery Instructions
Version: 2.0.0
Last Material Revision: 2026-08-01
---

# Recovery Instructions

If the autonomous execution context is lost (e.g., context window closes, session ends, crash), follow this procedure exactly.

## Step 1 — Verify project root

```powershell
Get-ChildItem -LiteralPath 'C:\Cognitive Industries\AI-IDP-AegisTrace'
```

If the directory does not exist, the project was not started or was deleted; restart from the comprehension response in the master prompt.

## Step 2 — Verify project-control integrity

```powershell
Get-ChildItem -LiteralPath 'C:\Cognitive Industries\AI-IDP-AegisTrace\project-control'
Get-Content -LiteralPath 'C:\Cognitive Industries\AI-IDP-AegisTrace\project-control\CHECKPOINT.md'
```

The checkpoint file contains the exact state, next actions, open processes, validation state, and blockers at the moment of the last successful checkpoint.

## Step 3 — Verify brand originals

```powershell
Set-Location -LiteralPath 'C:\Cognitive Industries\AI-IDP-AegisTrace\brand\originals'
Get-Content -LiteralPath 'SHA256SUMS.txt' | ForEach-Object {
    $expected, $relativePath = $_ -split '\s+', 2
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $relativePath.Trim()).Hash.ToLowerInvariant()
    if ($actual -ne $expected.ToLowerInvariant()) { throw "Brand checksum mismatch: $relativePath" }
}
```

If any checksum fails, the originals have been modified; restore from `brand/originals/SHA256SUMS.txt` and the original uploads.

## Step 4 — Verify implementation

```powershell
Set-Location -LiteralPath 'C:\Cognitive Industries\AI-IDP-AegisTrace'
.\.venv\Scripts\python.exe -m pytest tests\ -v
```

If tests fail, identify the failure, consult `DECISION_LOG.md`, and apply the minimal corrective change.

## Step 5 — Verify compilation

```powershell
Set-Location -LiteralPath 'C:\Cognitive Industries\AI-IDP-AegisTrace\paper'
tectonic main.tex
```

If compilation fails, inspect the LaTeX error, consult `paper/validation/`, and apply the minimal corrective change.

## Step 6 — Continue

Resume from the lowest-indexed incomplete gate in `project-control/VALIDATION_STATUS.md`.

## Anti-Patterns (Forbidden Recovery Actions)

- Do NOT regenerate the project from scratch if a checkpoint exists.
- Do NOT overwrite `project-control/` files without reading them first.
- Do NOT modify `brand/originals/`.
- Do NOT fabricate missing artifacts to satisfy the manifest; mark them as incomplete in `VALIDATION_STATUS.md` instead.
- Do NOT apply a public licence or perform external submission to "complete" the project.
