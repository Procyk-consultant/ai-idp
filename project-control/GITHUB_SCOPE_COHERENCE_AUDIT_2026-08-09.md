---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
File: project-control/GITHUB_SCOPE_COHERENCE_AUDIT_2026-08-09.md
Title: GitHub Scope and Repository-Coherence Audit
Purpose: Verify that the public repository represented by origin/main coheres with the approved AI-IDP / AegisTrace scope.
Audience: Project authority and downstream maintainers
Classification: internal control record
Version: 2.0.0
Status: Historical audit with current verification addendum
Audit date: 2026-08-09
Current verification date: 2026-09-06
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Licence Status: No public licence is granted.
---

# GitHub Scope and Repository-Coherence Audit

## Method and boundary

This audit compared the local canonical checkout with `origin/main` after a fresh fetch on 2026-08-09. Both resolve to commit `b13e51baa51c9e2bb0a5bff4f3911a6902b51206` at the time of comparison. The review examined the public repository tree, README paths, licensing language, the active reference-implementation claims, and current public-record links. It did not infer platform analytics, external endorsements, production deployment, or past correspondence.

## Verified public identity

| Item | Verified value | Treatment |
|---|---|---|
| Repository | https://github.com/Procyk-consultant/ai-idp | Public code and technical-material location. |
| Default public branch | `main` | Matches the canonical checkout at the audit point. |
| Citable archive | https://zenodo.org/records/21769036 | Public archival record; DOI https://doi.org/10.5281/zenodo.21769036. |
| Project status | Proposed Canadian standard and functional reference implementation | Do not characterize as enacted law, a government program, an endorsed standard, or a deployed national registry. |
| Rights | All Rights Reserved | Do not describe the repository, its L1 profile, or its code as open source. |

## Coherence findings

| Area | Result | Evidence and treatment |
|---|---|---|
| Scope | Pass | README, `PROJECT_CHARTER.md`, specifications, government package, research package, and implementation consistently describe AI-IDP as a proposed Canadian framework and AegisTrace as its reference implementation. |
| Repository structure | Pass | The README's cited project paths exist in `origin/main`; no tracked virtual environment, cache, `tmp`, `node_modules`, demo ledger, or release ZIP was found. |
| Public links | Pass | README points to the public GitHub repository and Zenodo DOI. arXiv is expressly deferred. |
| Licensing | Pass | README, `LICENSE`, and `LICENSING_STATUS.md` state All Rights Reserved and do not grant a public licence. |
| Capability wording | Corrected locally | The README previously presented all production-oriented components as if they were already operational. The wording now distinguishes included components from live infrastructure, deployment, and independent operational validation. |
| Current-status records | Controlled by follow-up record | Older dated final-delivery records remain historical evidence. Current GitHub, Zenodo, and outreach status is carried by `PHASE_FOLLOW_UP.md` and the 2026-08-09 reconciliation record; it must not be retroactively forced into archived derivatives. |
| Brand assets | Needs a future consolidation decision | `originals/` and `brand/originals/` contain byte-identical copies of the same three protected assets and checksum file. They are not edited or moved by this audit because their references and release provenance require a separately approved, reference-aware consolidation. |

## Material limitations to preserve in public-facing language

- AegisTrace is a functional reference implementation, not evidence of a live public registry or a production deployment.
- Some production-oriented components require external systems or optional dependencies: PostgreSQL infrastructure, HSM/KMS services, a post-quantum cryptographic provider, OpenTelemetry collection, and GitHub credentials/repositories for live anchoring.
- The project is proposed policy and technical work, not current Canadian law or a government-approved standard.
- Zenodo is the public archival route. arXiv has no assigned identifier and must not be cited as a publication destination.

## Next controlled action

Before a future GitHub release change, re-run the remote/local comparison, the relevant test suite, and this claim check. A future approved cleanup may analyse whether the duplicate protected asset directory can be consolidated without breaking references, manifests, or archived-release verification.

## Verification addendum — 2026-09-06

### Repository and remote state

| Item | Verified result |
|---|---|
| Canonical checkout | `C:\Cognitive Industries\AI-IDP-AegisTrace` |
| Baseline branch and SHA | local `main` at `b13e51baa51c9e2bb0a5bff4f3911a6902b51206` |
| Live remote baseline | `git ls-remote` reported `origin/main` at the same full SHA; baseline divergence was zero before branch creation |
| Remote | `https://github.com/Procyk-consultant/ai-idp.git` |
| Controlled update branch | `github-update/2026-09-06-verified-state`, created from the verified baseline |
| Existing side branch | `reconcile-2026-08-14` remains at `e148cf484b782872416121704a7887935a21bc71`; GitHub's comparison reports 124 commits and 72 changed files, so it is not merged or imported by this bounded update |
| Version and tags | package version remains `2.0.0`; no Git tags were present in the verified baseline |

### Local verification before correction

- Python `3.12.10` from the project virtual environment executed the full suite: 113 tests passed.
- MyPy `2.3.0` passed all 45 source files.
- `pip check` reported no broken requirements.
- Ruff `0.16.1` passed `src` and reported five F841 unused-local findings in tests; the controlled branch corrects only those findings.
- Docker CLI `28.4` was present, but its engine was unavailable. Container validation was therefore not claimed.
- No receiver was listening at `localhost:4318`; the passing tests ended with a non-fatal OpenTelemetry exporter warning.

### Integrity and publication findings

- The pre-change `release/CHECKSUMS.sha256` did not describe the current tree: 21 paths were absent and 76 present paths had changed hashes.
- The historical `project-control/ARTIFACT_MANIFEST.csv` listed 184 complete artifacts, of which 21 were absent. Their current dispositions are recorded in `ARTIFACT_MANIFEST_RECONCILIATION_2026-09-06.md`.
- The checksum generator previously scanned all physical files. It is constrained on this branch to Git-index membership so unrelated workspaces, raw extracts, outreach drafts, ignored archives, and nested repositories cannot enter the public checksum manifest accidentally.
- The latest visible GitHub Actions run at the verification point, run 31344416895, failed before job execution because the GitHub account was locked for a billing issue. That external account state is not treated as a code-test failure, and successful hosted CI is not claimed.
- This update does not establish v2.1.0, production deployment, a new release, or independent validation. It prepares and verifies one review branch only.

### Controlled-branch verification

- Ruff passes the full `src tests` scope and the modified checksum script.
- MyPy passes all 45 files under `src/aegistrace` as a hard gate; the CI workflow and Makefile no longer suppress type-check failures.
- `pip check` reports no broken requirements.
- Pytest passes 115 tests, including two new checksum membership and verification regressions.
- Checksum generation and immediate verification report 258 Git-controlled public-corpus entries.
- `git diff --check` reports no whitespace defects. Line-ending notices identify the repository's Windows checkout conversion behaviour and are not content failures.
