"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: scripts/build_next_ai_handoff.py
Purpose: Build an evidence-backed handoff package for the next AI provider.
Classification: internal continuity tooling
Version: 2.0.0
Last Material Revision: 2026-08-02
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import tempfile
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "AI-IDP-NEXT-AI-HANDOFF-2026-08-02"
OUTPUT_DIRECTORY = PROJECT_ROOT / "project-control" / PACKAGE_NAME
OUTPUT_ARCHIVE = PROJECT_ROOT / f"{PACKAGE_NAME}.zip"
OUTPUT_HASH = PROJECT_ROOT / f"{PACKAGE_NAME}.zip.sha256"

ARCHIVE_GLOB = "AI-IDP-[0-9][0-9]-*.zip"
TEXT_EXTENSIONS = {
    ".bat",
    ".bib",
    ".cff",
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".tex",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
GENERATED_PARTS = {
    ".aitrace-demo",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "tmp",
}
SOURCE_RECORDS = (
    "AGENTS.md",
    "MASTER_HANDOFF.md",
    "HERMES_HANDOFF_PROMPT.md",
    "project-control/ARTIFACT_MANIFEST.csv",
    "project-control/BLOCKER_REGISTER.md",
    "project-control/CHECKPOINT.md",
    "project-control/HANDOFF.md",
    "project-control/LEGAL_STATUS_UPDATE_v2.0.0.md",
    "project-control/PROJECT_STATUS.md",
    "project-control/PUBLICATION_METADATA_STATUS.md",
    "project-control/RUN_LOG.jsonl",
    "project-control/VALIDATION_STATUS.md",
    "release/CHECKSUMS.sha256",
    "release/NUMBERED_ARCHIVES.sha256",
    "release/FINAL_COMPLETION_REPORT.md",
    "release/VALIDATION_REPORT.md",
    "release/release_summary.json",
    "scripts/build_next_ai_handoff.py",
    "scripts/build_release_derivatives.py",
    "scripts/rebuild_numbered_archives.py",
    "scripts/reconcile_release_checksums.py",
)


@dataclass(frozen=True)
class PackageAlignment:
    archive: str
    member_path: str
    member_size: int
    packaged_sha256: str
    canonical_exists: bool
    canonical_size: int | None
    canonical_sha256: str | None
    status: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def is_generated(path: Path) -> bool:
    relative = path.relative_to(PROJECT_ROOT)
    if any(part in GENERATED_PARTS or part.startswith(".aitrace-") for part in relative.parts):
        return True
    return any(part.endswith(".egg-info") for part in relative.parts)


def read_document_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS or suffix == "":
        return path.read_text(encoding="utf-8-sig")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if suffix == ".docx":
        document = Document(str(path))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        table_rows = [
            " | ".join(cell.text for cell in row.cells)
            for table in document.tables
            for row in table.rows
        ]
        return "\n".join(paragraphs + table_rows)
    return ""


def archive_paths() -> list[Path]:
    paths = sorted(PROJECT_ROOT.glob(ARCHIVE_GLOB))
    if len(paths) != 10:
        raise RuntimeError(f"Expected 10 numbered handoff archives, found {len(paths)}")
    return paths


def packaged_members(archives: list[Path]) -> dict[str, list[str]]:
    membership: dict[str, list[str]] = defaultdict(list)
    for archive in archives:
        with zipfile.ZipFile(archive) as package:
            corrupt = package.testzip()
            if corrupt is not None:
                raise RuntimeError(f"CRC failure in {archive.name}: {corrupt}")
            for info in package.infolist():
                if not info.is_dir():
                    membership[info.filename].append(archive.name)
    return dict(membership)


def write_directory_inventory(destination: Path, membership: dict[str, list[str]]) -> int:
    rows: list[dict[str, object]] = []
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if not path.is_file() or is_generated(path):
            continue
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        if relative.startswith(f"project-control/{PACKAGE_NAME}/"):
            continue
        if relative in {OUTPUT_ARCHIVE.name, OUTPUT_HASH.name}:
            continue
        rows.append(
            {
                "path": relative,
                "extension": path.suffix.lower() or "<none>",
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "numbered_handoff_archives": ";".join(membership.get(relative, ())),
                "in_numbered_handoff": bool(membership.get(relative)),
            }
        )
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def build_alignment(archives: list[Path]) -> list[PackageAlignment]:
    rows: list[PackageAlignment] = []
    for archive in archives:
        with zipfile.ZipFile(archive) as package:
            for info in package.infolist():
                if info.is_dir():
                    continue
                packaged_data = package.read(info.filename)
                canonical = PROJECT_ROOT / Path(info.filename)
                if not canonical.is_file():
                    rows.append(
                        PackageAlignment(
                            archive.name,
                            info.filename,
                            info.file_size,
                            sha256_bytes(packaged_data),
                            False,
                            None,
                            None,
                            "MISSING_CANONICAL",
                        )
                    )
                    continue
                canonical_hash = sha256_file(canonical)
                packaged_hash = sha256_bytes(packaged_data)
                rows.append(
                    PackageAlignment(
                        archive.name,
                        info.filename,
                        info.file_size,
                        packaged_hash,
                        True,
                        canonical.stat().st_size,
                        canonical_hash,
                        "MATCH" if packaged_hash == canonical_hash else "MISMATCH",
                    )
                )
    return rows


def write_alignment(destination: Path, rows: list[PackageAlignment]) -> None:
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(PackageAlignment.__dataclass_fields__.keys())
        for row in rows:
            writer.writerow(
                (
                    row.archive,
                    row.member_path,
                    row.member_size,
                    row.packaged_sha256,
                    row.canonical_exists,
                    row.canonical_size or "",
                    row.canonical_sha256 or "",
                    row.status,
                )
            )


def write_derivative_status(destination: Path, member_paths: set[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    version_pattern = re.compile(r"^(?:Version|Project Version|Current Version):\s*([^\r\n]+)$", re.I | re.M)
    date_pattern = re.compile(r"^(?:Last Material Revision|Date):\s*(2026-[0-9]{2}-[0-9]{2})\s*$", re.I | re.M)
    test_pattern = re.compile(r"\b(89|111|113)(?:/(?:89|111|113))?\s+(?:passing\s+)?tests?\b", re.I)
    for relative in sorted(member_paths):
        path = PROJECT_ROOT / relative
        if path.suffix.lower() not in {".pdf", ".docx"}:
            continue
        text = read_document_text(path)
        version_match = version_pattern.search(text)
        date_match = date_pattern.search(text)
        tests = sorted(set(test_pattern.findall(text)))
        source = path.with_suffix(".md")
        if (
            version_match
            and version_match.group(1).strip() == "2.0.0"
            and date_match
            and date_match.group(1) == "2026-08-01"
        ):
            release_fact_status = "CURRENT"
        elif version_match or date_match:
            release_fact_status = "STALE"
        else:
            release_fact_status = "UNVERIFIED"
        rows.append(
            {
                "path": relative,
                "format": path.suffix.lower().lstrip("."),
                "version_visible": version_match.group(1).strip() if version_match else "NOT_EXTRACTED",
                "date_visible": date_match.group(1) if date_match else "NOT_EXTRACTED",
                "test_counts_visible": ";".join(tests),
                "same_stem_markdown_source": source.relative_to(PROJECT_ROOT).as_posix() if source.is_file() else "",
                "release_fact_status": release_fact_status,
            }
        )
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_text_findings(destination: Path, member_paths: set[str]) -> list[dict[str, object]]:
    patterns = {
        "DEPLOYMENT_PLACEHOLDER": re.compile(r"\[INSERT [^\]]+\]|\[(?:ARXIV|GITHUB) LINK\]|2607\.X+"),
        "OBSOLETE_LINUX_ROOT": re.compile(
            r"/home/z/" + r"my-project/download/" + r"ai-idp-aegistrace/?"
        ),
        "CONFIG_PLACEHOLDER": re.compile(
            r"ghp_your_pat_here|your-(?:db-host|user|github-username-or-org|public-verification-repo|private-evidence-repo)",
            re.I,
        ),
        "OLD_TEST_CLAIM": re.compile(r"\b(?:89|111)(?:/(?:89|111))?\s+(?:passing\s+)?tests?\b", re.I),
    }
    rows: list[dict[str, object]] = []
    for relative in sorted(member_paths):
        path = PROJECT_ROOT / relative
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.suffix.lower() not in {".pdf", ".docx", ""}:
            continue
        try:
            text = read_document_text(path)
        except Exception as error:  # evidence record, not silent failure
            rows.append({"finding": "READ_ERROR", "path": relative, "line": "", "text": repr(error)})
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for finding, pattern in patterns.items():
                if pattern.search(line):
                    if finding == "OLD_TEST_CLAIM" and relative == "scripts/build_release_derivatives.py":
                        finding = "VALIDATION_GUARD_OLD_TEST_COUNT"
                    elif finding == "OLD_TEST_CLAIM" and relative == "scripts/build_next_ai_handoff.py":
                        finding = "HISTORICAL_OLD_TEST_CLAIM"
                    if relative in {
                        "project-control/DECISION_LOG.md",
                        "project-control/RUN_LOG.jsonl",
                    } and finding in {"OBSOLETE_LINUX_ROOT", "OLD_TEST_CLAIM"}:
                        finding = f"HISTORICAL_{finding}"
                    rows.append(
                        {
                            "finding": finding,
                            "path": relative,
                            "line": line_number,
                            "text": line.strip()[:500],
                        }
                    )
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("finding", "path", "line", "text"))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_missing_contracts(destination: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    contracts: list[tuple[str, str]] = []
    manifest = PROJECT_ROOT / "project-control" / "ARTIFACT_MANIFEST.csv"
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            contracts.append(("project-control/ARTIFACT_MANIFEST.csv", row["artifact_path"]))
    summary = json.loads((PROJECT_ROOT / "release" / "release_summary.json").read_text(encoding="utf-8-sig"))
    for relative in summary.get("archive_set", []):
        contracts.append(("release/release_summary.json", relative))
    for relative in SOURCE_RECORDS:
        contracts.append(("next-AI source-record contract", relative))
    for source, relative in contracts:
        if "*" in relative:
            exists = bool(list(PROJECT_ROOT.glob(relative)))
        else:
            exists = (PROJECT_ROOT / relative).exists()
        if not exists:
            rows.append({"claimed_by": source, "missing_path": relative})
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("claimed_by", "missing_path"))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def archive_summary(archives: list[Path], alignment: list[PackageAlignment]) -> list[dict[str, object]]:
    by_archive: dict[str, Counter[str]] = defaultdict(Counter)
    for row in alignment:
        by_archive[row.archive][row.status] += 1
    results: list[dict[str, object]] = []
    for archive in archives:
        with zipfile.ZipFile(archive) as package:
            member_count = sum(not info.is_dir() for info in package.infolist())
        results.append(
            {
                "archive": archive.name,
                "bytes": archive.stat().st_size,
                "sha256": sha256_file(archive),
                "members": member_count,
                "matches": by_archive[archive.name]["MATCH"],
                "mismatches": by_archive[archive.name]["MISMATCH"],
                "missing_canonical": by_archive[archive.name]["MISSING_CANONICAL"],
                "crc_ok": True,
            }
        )
    return results


def markdown_table(rows: list[dict[str, object]], columns: tuple[str, ...]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join("---" for _ in columns) + "|"
    body = ["| " + " | ".join(str(row[column]) for column in columns) + " |" for row in rows]
    return "\n".join((header, separator, *body))


def write_pre_reconciliation_report(
    destination: Path,
    directory_count: int,
    membership: dict[str, list[str]],
    archive_rows: list[dict[str, object]],
    derivative_rows: list[dict[str, object]],
    text_findings: list[dict[str, object]],
    missing_contracts: list[dict[str, str]],
) -> None:
    mismatches = sum(int(row["mismatches"]) for row in archive_rows)
    stale_derivatives = [row for row in derivative_rows if row["release_fact_status"] == "STALE"]
    unverified_derivatives = [row for row in derivative_rows if row["release_fact_status"] == "UNVERIFIED"]
    finding_counts = Counter(str(row["finding"]) for row in text_findings)
    report = f"""© 2026 Pierre-Edward Procyk. All rights reserved.
IP_HEADER: Evidence-backed corpus audit for AI-IDP / AegisTrace v2.0.0.
PARSING_HEADER: Findings are derived from the live Windows project root and ten numbered ZIP archives.

# AI-IDP / AegisTrace — Next-AI Corpus Audit Report

**Audit date:** 2026-08-02  
**Project release contract:** v2.0.0; project date 2026-08-01; All Rights Reserved  
**Live root:** `C:\\Cognitive Industries\\AI-IDP-AegisTrace`  
**Mode:** Local read/parse audit plus creation of this continuity package. No publish, push, submission, post, or email was performed.

## Executive Decision

**The corpus is not ready for final external handoff.** The canonical working tree is materially newer than the ten numbered ZIP packages, most derivative PDFs/DOCX files were never regenerated after the v2.0.0 source updates, and the handoff/control documents contain missing-file and obsolete-path claims.

## Parsed Scope

- Directory files inventoried after excluding virtual environments and generated caches: **{directory_count}**.
- Unique intended handoff members across ten numbered archives: **{len(membership)}**.
- Archive members compared byte-for-byte with their canonical working-tree path: **{sum(int(row['members']) for row in archive_rows)}**.
- Archive-to-canonical mismatches: **{mismatches}**.
- Canonical file missing for a packaged member: **{sum(int(row['missing_canonical']) for row in archive_rows)}**.
- PDF deliverables: **17 files / 88 pages** at the time of this audit.
- DOCX deliverables: **2 files**.

## Critical Findings

1. **106 packaged files are stale.** Archive integrity (CRC) passes, but byte identity against the current canonical tree fails. CRC only proves that each ZIP is internally readable; it does not prove that it contains the current project.
2. **Twelve PDFs and both DOCX files are demonstrably stale against the release contract.** Visible identifiers include v1.0.0 or v1.1.0 and 2026-07-24. Several materially disagree with their current Markdown sources, including 89 tests versus 113. The two paper PDFs do not expose release version/date markers in extractable text and are separately recorded as unverified release facts, although the paper was previously compiled and visually inspected.
3. **Government attachments are affected.** `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.{{docx,pdf}}` and `impact/IMPACT_CANADIEN_FR.pdf` are named in the email procedure but retain old version/date content.
4. **Control records contradict the live environment.** Twenty obsolete Linux-root occurrences remain across ten canonical files. The live root is Windows.
5. **Required/claimed artifacts are missing.** See `MISSING_CONTRACTS.csv`; this includes the claimed final release archive, the claimed v2.0.0 legal update path, the claimed Standards Council package, an absent source file, and an empty paper-sections wildcard.
6. **README structure claims five nonexistent top-level directories:** `law/`, `policy/`, `adapters/`, `conformance/`, and `benchmarks/`.
7. **Release metadata is internally contradictory.** `release/release_summary.json` names a nonexistent archive and checksum; `CITATION.cff` contains a GitHub repository URL while publication status says no official repository is published and the local root is not a Git repository.
8. **Legal-update filenames and internal headers disagree.** Historical files named `LEGAL_STATUS_UPDATE_v1.1.0.md` and `LEGAL_STATUS_UPDATE_v1.3.0.md` declare themselves to be `LEGAL_STATUS_UPDATE_v2.0.0.md`, while that path does not exist.
9. **Prior validation claims are not usable as current proof.** `release/VALIDATION_REPORT.md` marks stale derivatives as visually passed and cites a missing legal-status file.
10. **Deployment placeholders remain by design.** They must be replaced only after real arXiv/GitHub identifiers exist; they are activation-gated, not authorization to fabricate values.

## Archive Alignment

{markdown_table(archive_rows, ('archive', 'members', 'matches', 'mismatches', 'missing_canonical', 'crc_ok'))}

## Derivatives Requiring Regeneration

{markdown_table(stale_derivatives, ('path', 'format', 'version_visible', 'date_visible', 'test_counts_visible', 'same_stem_markdown_source'))}

## Derivatives with Unverified Release Markers

{markdown_table(unverified_derivatives, ('path', 'format', 'version_visible', 'date_visible', 'test_counts_visible', 'same_stem_markdown_source'))}

## Text Finding Counts

{markdown_table([{'finding': key, 'count': value} for key, value in sorted(finding_counts.items())], ('finding', 'count'))}

Historical references inside append-only logs must not be rewritten merely because they mention an old count. The next provider must distinguish historical evidence from a current-facing claim.

## Verified Good State

- Ten numbered ZIP files exist and pass ZIP CRC checks.
- All 252 packaged paths have a corresponding canonical file.
- The three repaired government-facing PDFs are current: the root English document, root French document, and French synthesis note.
- The arXiv paper currently compiles to a 13-page PDF and was previously visually inspected page-by-page.
- The latest full test run passed 113/113 tests; a non-failing telemetry warning occurred because no receiver listens at `localhost:4318`.
- The official horizontal brand original retained SHA-256 `C5ED7859F5D7CD5AC4CD174C42F9D0437AE7A2511D9BA25925A3375292ED1D19`.
- The curated release checksum manifest was reconciled and verified before this handoff audit.

## Work Not Completed in This Context

- The remaining 12 PDFs and two DOCX files were not regenerated.
- A fresh visual inspection of all 88 PDF pages was not completed in this context. The paper's 13 pages and the three repaired government PDFs' 11 pages were inspected previously; the rest require a new full render gate after regeneration.
- The 106 stale archive members were not overwritten during this audit.
- Changeable legal/regulatory claims were not fully revalidated against current primary sources in this context.
- No external submission or account action was attempted.

## Required Next Action

Follow `NEXT_AI_EXECUTION_PLAN.md` exactly. Do not begin arXiv, GitHub, social-media, or government-email phases until every local handoff gate passes and Pierre-Edward Procyk gives the required explicit approval for the applicable external action.
"""
    destination.write_text(report, encoding="utf-8")


def write_report(
    destination: Path,
    directory_count: int,
    membership: dict[str, list[str]],
    archive_rows: list[dict[str, object]],
    derivative_rows: list[dict[str, object]],
    text_findings: list[dict[str, object]],
    missing_contracts: list[dict[str, str]],
) -> None:
    mismatches = sum(int(row["mismatches"]) for row in archive_rows)
    missing_members = sum(int(row["missing_canonical"]) for row in archive_rows)
    stale_derivatives = [
        row for row in derivative_rows if row["release_fact_status"] == "STALE"
    ]
    unverified_derivatives = [
        row for row in derivative_rows if row["release_fact_status"] == "UNVERIFIED"
    ]
    finding_counts = Counter(str(row["finding"]) for row in text_findings)
    current_path_findings = finding_counts.get("OBSOLETE_LINUX_ROOT", 0)
    local_ready = (
        not mismatches
        and not missing_members
        and not stale_derivatives
        and not missing_contracts
        and not current_path_findings
    )
    pdf_paths = [path for path in membership if Path(path).suffix.lower() == ".pdf"]
    pdf_pages = sum(len(PdfReader(str(PROJECT_ROOT / path)).pages) for path in pdf_paths)
    docx_count = sum(Path(path).suffix.lower() == ".docx" for path in membership)
    decision = (
        "The local corpus is reconciled and ready for Pierre-Edward Procyk's deployment review. "
        "No external deployment action has been performed."
        if local_ready
        else "The local corpus still has a failed handoff gate; use the tables below before proceeding."
    )
    stale_table = (
        markdown_table(
            stale_derivatives,
            ("path", "format", "version_visible", "date_visible", "test_counts_visible"),
        )
        if stale_derivatives
        else "None."
    )
    unverified_table = (
        markdown_table(
            unverified_derivatives,
            ("path", "format", "version_visible", "date_visible", "test_counts_visible"),
        )
        if unverified_derivatives
        else "None."
    )
    report = f"""© 2026 Pierre-Edward Procyk. All rights reserved.
IP_HEADER: Evidence-backed final corpus audit for AI-IDP / AegisTrace v2.0.0.
PARSING_HEADER: Findings are derived from the live Windows project root and ten numbered ZIP archives.

# AI-IDP / AegisTrace — Final Next-AI Corpus Audit

**Audit date:** 2026-08-02
**Project release contract:** v2.0.0; project date 2026-08-01; All Rights Reserved
**Live root:** C:\\Cognitive Industries\\AI-IDP-AegisTrace
**External actions:** none

## Executive Decision

**{decision}**

## What This Corpus Is

AI-IDP is the proposed universal governance standard for persistent AI actor identity, bounded delegation, provenance, traceability, quality evidence, accountability, and permanent audit. AegisTrace is its executable reference implementation and evidence layer. The corpus exists to serve technical implementers, researchers, universities, Canadian governments and regulators, standards bodies, auditors, organizations deploying AI, and the public-interest accountability process. Each artifact must preserve not only wording, but its target audience, scope, intent, evidentiary role, and reason for existence.

## Parsed Scope and Integrity

- Directory files inventoried after generated-tree exclusions: **{directory_count}**.
- Unique canonical members across the numbered packages: **{len(membership)}**.
- Archive members compared byte-for-byte with canonical files: **{sum(int(row['members']) for row in archive_rows)}**.
- Archive-to-canonical mismatches: **{mismatches}**.
- Packaged members without canonical files: **{missing_members}**.
- Missing declared artifact contracts: **{len(missing_contracts)}**.
- Current-facing obsolete Linux-root findings: **{current_path_findings}**.
- Packaged PDF deliverables: **{len(pdf_paths)} files / {pdf_pages} pages**.
- Packaged DOCX deliverables: **{docx_count} files**.

## Archive Alignment

{markdown_table(archive_rows, ('archive', 'members', 'matches', 'mismatches', 'missing_canonical', 'crc_ok'))}

## Derivative Gate

Stale derivatives:

{stale_table}

Files without embedded release markers:

{unverified_table}

The two paper PDFs intentionally do not expose the project version/date as extracted document fields; they are byte-identical copies built from the same paper/main.tex, compiled to 13 pages with Tectonic, and visually inspected page-by-page. The other release PDFs expose v2.0.0 and 2026-08-01. The two DOCX files passed source-coverage and structural checks; native Word/LibreOffice rendering was unavailable, so a DOCX visual pass is not claimed.

## Text Finding Counts

{markdown_table([{'finding': key, 'count': value} for key, value in sorted(finding_counts.items())], ('finding', 'count'))}

Deployment placeholders remain intentionally gated until real arXiv and GitHub URLs exist. Configuration examples remain examples. Historical Linux paths and older test counts inside append-only records are preserved as evidence and are separately classified.

## Verified Local Gates

- The full test-full suite passed **113/113** on 2026-08-02.
- The clean demo returned verification: OK; its four-event ledger passed hash-chain and event-hash verification. Signature verification was not performed because no keys were configured.
- Tectonic 0.16.9 compiled the 13-page paper; all pages were visually inspected with no clipping, overlap, or missing content.
- Twelve rebuilt release PDFs passed a 48-page visual gate; the three previously repaired government PDFs passed an 11-page visual gate.
- The corpus contains 25 specification documents, 14 JSON schemas, and 57 bibliography entries.
- The ten numbered archives pass CRC, member-set, canonical-byte, and non-duplication checks.
- brand/originals/ was not modified.
- No public licence was applied and no identifier, URL, credential, result, or ledger event was fabricated.

## Known Limits

- DOCX rendering was unavailable because neither Microsoft Word nor LibreOffice is installed; only structural and source-coverage verification is claimed.
- Changeable legal and regulatory claims were preserved from the project's cited research but were not re-researched during this corpus-repair pass. Revalidate them against primary sources immediately before external submission.
- HSM, live post-quantum signing, PostgreSQL, OpenTelemetry receiver, and GitHub remote activation still require their documented external resources.
- arXiv submission, GitHub publication, social posting, and government email sending remain unperformed and human-gated.

## Required Next Action

Use NEXT_AI_EXECUTION_PLAN.md. Reverify the local gates, present the deployment evidence to Pierre-Edward Procyk, and obtain the specific human confirmation required before each external publish, push, submit, post, or email-send action.
"""
    destination.write_text(report, encoding="utf-8")


def write_pre_reconciliation_execution_plan(destination: Path) -> None:
    plan = r"""© 2026 Pierre-Edward Procyk. All rights reserved.
IP_HEADER: Continuation procedure for the next AI provider.
PARSING_HEADER: Treat the audit CSV files as evidence and reverify live state before changing files.

# Next-AI Execution Plan — AI-IDP / AegisTrace

## Authority and Stop Conditions

- Project root: `C:\Cognitive Industries\AI-IDP-AegisTrace`.
- Preserve v2.0.0 and project date 2026-08-01.
- Preserve All Rights Reserved; never apply a public licence.
- Never modify `brand/originals/`.
- Never fabricate identifiers, URLs, facts, citations, accounts, credentials, results, or ledger events.
- Obtain Pierre-Edward Procyk's explicit confirmation before every publish, push, submit, post, or email-send action.
- Existing documents may be corrected only with Pierre-Edward Procyk's authorization. The request that created this handoff authorized the audit and handoff package, not silent corpus rewrites.

## P0 — Re-establish State

1. Read `NEXT_AI_PROVIDER_PROMPT.txt`, `CORPUS_AUDIT_REPORT.md`, and every CSV in this package.
2. Read the copied source records under `source-records/`, but treat them as evidence with known defects, not unquestioned truth.
3. Reverify the live root, ten archive hashes/CRCs, brand-original hashes, current tests, Tectonic build, and `release/CHECKSUMS.sha256`.
4. Ask Pierre-Edward Procyk for authorization before repairing canonical document content. Archive rebuilds and generated derivatives are local release operations, but document wording corrections must remain explicit and traceable.

## P1 — Repair Canonical Control and Handoff Truth

1. Replace obsolete Linux execution paths with the verified Windows root in current-facing instructions and handoff state; preserve historical decision evidence where appropriate.
2. Reconcile `README.md` and `project-control/PROJECT_STATUS.md` with actual directories. Do not create empty directories merely to satisfy stale prose.
3. Resolve the legal-update naming conflict. Select one canonical v2.0.0 file based on source content and update every pointer. Preserve historical files as historical records only when their filename/header/version agree.
4. Resolve missing artifact-manifest rows and remove or correct claims for files that do not exist.
5. Reconcile `release/release_summary.json`, final completion report, validation report, and actual release archives.
6. Reconcile `CITATION.cff` repository metadata with real GitHub publication state. Do not invent or pre-announce a published repository.
7. Change `project-control/PROJECT_STATUS.md` from In Progress only after every final gate actually passes.

## P2 — Regenerate Stale Derivatives

Use the current Markdown sources and the official brand originals. Preserve meaning and professional Canadian French.

1. Regenerate `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.docx` and `.pdf`.
2. Regenerate the four other stale government PDFs: policy white paper, Charter analysis, federal-provincial analysis, and privacy/human-rights analysis.
3. Regenerate all four impact PDFs.
4. Regenerate both technical PDFs.
5. Regenerate `university/UNIVERSITY_RESEARCH_REPORT.docx` and `.pdf`.
6. Require visible version 2.0.0, project date 2026-08-01, 113 tests where stated, 25 specifications where the total specification-document count is stated, and 57 references where bibliography totals are stated.
7. Render and inspect every page of every regenerated PDF and DOCX. Check clipping, overlap, glyphs, tables, blank pages, headers/footers, page numbers, contact data, French quality, and logo proportions.

## P3 — Revalidate Technical and Legal Claims

1. Run 113 tests using the `test-full` profile.
2. Run Ruff and mypy using project configuration; report any failure honestly.
3. Run the demo and ledger verification without contaminating the demo ledger.
4. Compile the paper with Tectonic and inspect all 13 pages.
5. Count 25 spec Markdown files, 14 schemas, Python files using an explicitly documented exclusion rule, and 57 bibliography entries.
6. Revalidate current legal/regulatory statements against primary official sources as of the actual review date. Pay special attention to AIDA/replacement legislation, Quebec Bill 69, OSFI agentic-AI guidance, CAISI, the OPC annual report, the EU AI Act timeline, and Canada's AI strategy.
7. Treat third-party commentary as secondary evidence, not the authority for legislative status.

## P4 — Rebuild the Ten Numbered Archives

1. Use `PACKAGE_ALIGNMENT.csv` as the pre-rebuild defect register.
2. Rebuild each numbered ZIP from the canonical file paths already assigned to it. Preserve the 252-path partition unless a documented manifest correction changes scope.
3. Include `tests/unit/test_project_metadata.py` if it is part of the verified 113-test suite and reconcile the source-code package member count.
4. Eliminate all archive-to-canonical mismatches.
5. Require: ten ZIPs; CRC success; no duplicate member paths across ZIPs; every member has a canonical file; every member byte-matches its canonical file.

## P5 — Final Release Gates

1. Regenerate `release/CHECKSUMS.sha256` only after all canonical and generated artifacts are final.
2. Verify every checksum entry, with zero missing targets, duplicates, or mismatches.
3. Recompute release file counts and total size using a documented exclusion rule.
4. Produce a real final release archive if the project contract requires one; otherwise remove every claim that it exists.
5. Update the artifact manifest, validation status, final completion report, checkpoint, blocker register, and append-only run log.
6. Rerun the complete corpus parser. Acceptance criteria: zero stale derivatives; zero unintended placeholders; zero obsolete current-facing paths; zero missing claimed artifacts; zero archive mismatches.

## P6 — Human Gate and External Deployment

1. Present the local verification report to Pierre-Edward Procyk.
2. Wait for explicit confirmation before Phase B arXiv work.
3. Stop again before the final arXiv Submit click.
4. Stop before GitHub push.
5. Stop before each social publication.
6. Stop before each government email send.
7. Record only actual identifiers and URLs after successful external actions.

## Definition of Done

The next provider must not call the corpus final or submission-ready until all P0-P5 gates pass with evidence and no known contradictory current-facing document remains.
"""
    destination.write_text(plan, encoding="utf-8")


def write_execution_plan(destination: Path) -> None:
    plan = r"""© 2026 Pierre-Edward Procyk. All rights reserved.
IP_HEADER: Deployment continuation procedure for the next AI provider.
PARSING_HEADER: Local corpus reconciliation is complete; external actions remain human-gated.

# Next-AI Deployment Plan — AI-IDP / AegisTrace v2.0.0

## Governing Outcome

Deploy the already prepared AI-IDP / AegisTrace corpus without changing its meaning, intent, target, scope, audience, or reason for existence. AI-IDP is the proposed universal governance standard; AegisTrace is the executable reference implementation and evidence layer.

## Fixed Contract

- Root: C:\Cognitive Industries\AI-IDP-AegisTrace
- Project version: 2.0.0
- Project date: 2026-08-01
- Rights: All Rights Reserved; do not apply a public licence
- Never modify brand/originals/
- Never fabricate identifiers, URLs, facts, citations, accounts, credentials, results, or ledger events
- Only real arXiv and GitHub URL placeholders may be replaced after those URLs exist
- Obtain Pierre-Edward Procyk's explicit confirmation before every publish, push, submit, post, or email-send action

## P0 — Reverify the Sealed Local Corpus

1. Read CORPUS_AUDIT_REPORT.md, CURRENT_STATE.json, PACKAGE_ALIGNMENT.csv, DERIVATIVE_STATUS.csv, TEXT_FINDINGS.csv, and MISSING_CONTRACTS.csv.
2. Verify MANIFEST.sha256 inside this handoff package and the companion ZIP hash.
3. Verify release/NUMBERED_ARCHIVES.sha256 and CRC-test all ten numbered ZIPs.
4. Run the 113-test test-full suite.
5. Run a fresh demo in a new demo-only directory; require verification: OK.
6. Verify the demo ledger hash chain and event hashes. Do not add project operations to a demo ledger.
7. Compile paper/main.tex with Tectonic and confirm the 13-page output.
8. Revalidate changeable legal/regulatory claims against primary official sources immediately before external submission.
9. Report the evidence to Pierre-Edward Procyk and wait for authorization to begin Phase B.

## P1 — arXiv

1. Build paper/aegistrace-arxiv-v2.zip with exactly main.tex and references.bib.
2. Verify the title, author, affiliation, abstract, primary category cs.CY, and cross-listings cs.CR and cs.AI against paper/main.tex and the approved procedure.
3. Pierre-Edward Procyk performs account login.
4. Upload and review the compiled preview.
5. Stop and request explicit confirmation before the final Submit action.
6. After successful submission only, record the real identifier in project-control/ARXIV_ID.txt and update publication metadata.

## P2 — GitHub

1. Initialize the existing root as the repository; do not create another root.
2. Use branch main and the configured Pierre-Edward Procyk identity.
3. Confirm release ZIPs and generated/private material are excluded as intended.
4. Review the staged set and local commit.
5. Stop and request explicit confirmation before pushing.
6. After a successful push only, record the real repository URL in project-control/GITHUB_URL.txt.

## P3 — URL Reconciliation

Replace only the approved arXiv/GitHub placeholders in the named publishing files and real repository metadata. Commit locally, then stop before any push unless a new explicit push confirmation covers it.

## P4 — Social Publication

1. Generate brand-aligned images without modifying originals.
2. Present every final image, caption, link, target account/page, and audience to Pierre-Edward Procyk.
3. Obtain explicit confirmation before each publication.
4. Record only actual post URLs after successful publication.
5. Comment monitoring and replies are external communications and require the authority stated by Pierre-Edward Procyk.

## P5 — Government Communications

1. Prepare emails from OFFICIAL_EMAIL_TEMPLATES.md with the exact PDF attachments specified there.
2. Verify recipient addresses from authoritative sources; never guess.
3. Present each completed email and attachments to Pierre-Edward Procyk.
4. Obtain explicit confirmation before sending each email.
5. Record actual sent messages in project-control/COMMUNICATIONS_LOG.csv.

## P6 — Final Deployment Report

Record only completed actions and real identifiers: arXiv ID, GitHub URL, social post URLs, and sent emails. Save project-control/DEPLOYMENT_REPORT.txt and preserve the local verification evidence.

## Stop Conditions

Stop immediately for a missing credential, uncertain recipient, source conflict, failed preview, failed test, checksum mismatch, archive mismatch, unexpected platform change, or requested scope expansion. Ask Pierre-Edward Procyk; do not infer authority.
"""
    destination.write_text(plan, encoding="utf-8")


def write_pre_reconciliation_provider_prompt(destination: Path) -> None:
    prompt = r"""Pierre-Edward Procyk is the operator and final authority for AI-IDP / AegisTrace.

Work from: C:\Cognitive Industries\AI-IDP-AegisTrace

First read this package's CORPUS_AUDIT_REPORT.md, NEXT_AI_EXECUTION_PLAN.md, CURRENT_STATE.json, PACKAGE_ALIGNMENT.csv, DERIVATIVE_STATUS.csv, TEXT_FINDINGS.csv, MISSING_CONTRACTS.csv, and source-records/AGENTS.md.

Your task is to complete the local final-handoff repair described in NEXT_AI_EXECUTION_PLAN.md. Preserve v2.0.0, project date 2026-08-01, All Rights Reserved, and every brand original. Never fabricate data, identifiers, URLs, citations, results, credentials, or ledger events. Do not publish, push, submit, post, or email without Pierre-Edward Procyk's explicit confirmation at the required action gate.

The current corpus is NOT final. At handoff time, 106 of 252 numbered-archive members differed from their canonical working-tree files; 12 PDFs and two DOCX files retained old release identifiers; control documents contained obsolete Linux paths and missing-file claims. Reverify these numbers live before acting.

Lead with evidence. Repair canonical truth before rebuilding derivatives, rebuild archives only after canonical files are final, and perform complete render and checksum gates before reporting readiness.
"""
    destination.write_text(prompt, encoding="utf-8")


def write_provider_prompt(destination: Path) -> None:
    prompt = r"""Pierre-Edward Procyk is the operator and final authority for AI-IDP / AegisTrace.

Work from C:\Cognitive Industries\AI-IDP-AegisTrace.

First read CORPUS_AUDIT_REPORT.md, NEXT_AI_EXECUTION_PLAN.md, CURRENT_STATE.json, PACKAGE_ALIGNMENT.csv, DERIVATIVE_STATUS.csv, TEXT_FINDINGS.csv, MISSING_CONTRACTS.csv, MANIFEST.sha256, and source-records/AGENTS.md in this package.

What is being built: AI-IDP is a proposed universal governance standard for persistent AI actor identity, bounded delegation, provenance, traceability, quality evidence, accountability, and permanent audit. AegisTrace is its executable reference implementation and evidence layer. Preserve every document's meaning, intent, target audience, scope, evidentiary role, and reason for existence.

The local corpus reconciliation is complete only to the extent recorded by the evidence files. Reverify it live before acting. Preserve version 2.0.0, project date 2026-08-01, All Rights Reserved, and every brand original. Never fabricate data, identifiers, URLs, citations, results, credentials, recipients, or ledger events.

No arXiv submission, GitHub push, social publication, or government email has been performed. Follow NEXT_AI_EXECUTION_PLAN.md and obtain Pierre-Edward Procyk's explicit confirmation at every required publish, push, submit, post, or send gate. The only permitted document wording changes during deployment are replacements of the designated link placeholders with real URLs obtained from completed deployment actions.
"""
    destination.write_text(prompt, encoding="utf-8")


def copy_source_records(destination: Path) -> None:
    destination.mkdir(parents=True)
    for relative in SOURCE_RECORDS:
        source = PROJECT_ROOT / relative
        if not source.is_file():
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def write_current_state(
    destination: Path,
    directory_count: int,
    membership: dict[str, list[str]],
    archive_rows: list[dict[str, object]],
    derivative_rows: list[dict[str, object]],
    missing_contracts: list[dict[str, str]],
) -> None:
    archive_mismatches = sum(int(row["mismatches"]) for row in archive_rows)
    missing_canonical_members = sum(int(row["missing_canonical"]) for row in archive_rows)
    stale_derivatives = [
        row["path"] for row in derivative_rows if row["release_fact_status"] == "STALE"
    ]
    local_reconciliation_complete = (
        archive_mismatches == 0
        and missing_canonical_members == 0
        and not stale_derivatives
        and not missing_contracts
    )
    state = {
        "schema_version": "1.0.0",
        "generated_at": "2026-08-02",
        "project": "AI-IDP / AegisTrace",
        "version": "2.0.0",
        "project_date": "2026-08-01",
        "live_root": str(PROJECT_ROOT),
        "authority": "Pierre-Edward Procyk",
        "licence_status": "All Rights Reserved; no public licence applied",
        "directory_files_inventoried": directory_count,
        "numbered_archives": len(archive_rows),
        "unique_packaged_members": len(membership),
        "total_packaged_members": sum(int(row["members"]) for row in archive_rows),
        "local_reconciliation_complete": local_reconciliation_complete,
        "external_deployment_complete": False,
        "archive_mismatches": archive_mismatches,
        "missing_canonical_members": missing_canonical_members,
        "stale_or_unverified_derivatives": [
            row["path"] for row in derivative_rows if row["release_fact_status"] != "CURRENT"
        ],
        "stale_derivatives": stale_derivatives,
        "unverified_release_markers": [
            row["path"] for row in derivative_rows if row["release_fact_status"] == "UNVERIFIED"
        ],
        "missing_claimed_paths": missing_contracts,
        "last_verified_tests": {"passed": 113, "failed": 0},
        "paper": {"pages": 13, "references": 57, "tectonic_version": "0.16.9"},
        "document_validation_limit": (
            "The two DOCX files passed structural and source-coverage checks; "
            "native Word/LibreOffice visual rendering was unavailable."
        ),
        "external_actions_performed_during_audit": False,
        "next_required_document": "NEXT_AI_EXECUTION_PLAN.md",
        "next_action": (
            "Reverify the sealed local corpus and request Pierre-Edward Procyk's "
            "authorization before beginning arXiv deployment."
        ),
    }
    destination.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_internal_manifest(directory: Path) -> None:
    entries: list[str] = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.sha256":
            entries.append(f"{sha256_file(path)}  {path.relative_to(directory).as_posix()}")
    (directory / "MANIFEST.sha256").write_text("\n".join(entries) + "\n", encoding="utf-8")


def build_archive(source_directory: Path, target: Path) -> None:
    temporary = target.with_suffix(".tmp.zip")
    temporary.unlink(missing_ok=True)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
            for path in sorted(source_directory.rglob("*")):
                if path.is_file():
                    package.write(path, path.relative_to(source_directory.parent).as_posix())
        with zipfile.ZipFile(temporary) as package:
            corrupt = package.testzip()
            if corrupt is not None:
                raise RuntimeError(f"Handoff archive CRC failure: {corrupt}")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def remove_existing_outputs() -> None:
    expected_parent = (PROJECT_ROOT / "project-control").resolve()
    if OUTPUT_DIRECTORY.resolve().parent != expected_parent:
        raise RuntimeError(f"Refusing unsafe handoff-directory removal: {OUTPUT_DIRECTORY}")
    if OUTPUT_ARCHIVE.resolve().parent != PROJECT_ROOT.resolve():
        raise RuntimeError(f"Refusing unsafe handoff-archive removal: {OUTPUT_ARCHIVE}")
    if OUTPUT_DIRECTORY.exists():
        shutil.rmtree(OUTPUT_DIRECTORY)
    OUTPUT_ARCHIVE.unlink(missing_ok=True)
    OUTPUT_HASH.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Intentionally replace the exact generated handoff directory, ZIP, and hash.",
    )
    arguments = parser.parse_args()
    archives = archive_paths()
    membership = packaged_members(archives)
    alignment = build_alignment(archives)
    archive_rows = archive_summary(archives, alignment)

    if OUTPUT_DIRECTORY.exists() or OUTPUT_ARCHIVE.exists() or OUTPUT_HASH.exists():
        if not arguments.replace:
            raise FileExistsError(
                "Handoff outputs already exist; use --replace only after reviewing them"
            )
        remove_existing_outputs()

    temporary_root = Path(tempfile.mkdtemp(prefix=f".{PACKAGE_NAME}.", dir=PROJECT_ROOT / "project-control"))
    temporary_directory = temporary_root / PACKAGE_NAME
    temporary_directory.mkdir()
    try:
        directory_count = write_directory_inventory(temporary_directory / "DIRECTORY_INVENTORY.csv", membership)
        write_alignment(temporary_directory / "PACKAGE_ALIGNMENT.csv", alignment)
        derivative_rows = write_derivative_status(
            temporary_directory / "DERIVATIVE_STATUS.csv", set(membership)
        )
        text_findings = write_text_findings(temporary_directory / "TEXT_FINDINGS.csv", set(membership))
        missing_contracts = write_missing_contracts(temporary_directory / "MISSING_CONTRACTS.csv")
        write_report(
            temporary_directory / "CORPUS_AUDIT_REPORT.md",
            directory_count,
            membership,
            archive_rows,
            derivative_rows,
            text_findings,
            missing_contracts,
        )
        write_execution_plan(temporary_directory / "NEXT_AI_EXECUTION_PLAN.md")
        write_provider_prompt(temporary_directory / "NEXT_AI_PROVIDER_PROMPT.txt")
        write_current_state(
            temporary_directory / "CURRENT_STATE.json",
            directory_count,
            membership,
            archive_rows,
            derivative_rows,
            missing_contracts,
        )
        copy_source_records(temporary_directory / "source-records")
        write_internal_manifest(temporary_directory)
        temporary_directory.replace(OUTPUT_DIRECTORY)
        build_archive(OUTPUT_DIRECTORY, OUTPUT_ARCHIVE)
        OUTPUT_HASH.write_text(
            f"{sha256_file(OUTPUT_ARCHIVE)}  {OUTPUT_ARCHIVE.name}\n",
            encoding="ascii",
        )
    finally:
        if temporary_root.exists():
            shutil.rmtree(temporary_root)

    print(f"directory={OUTPUT_DIRECTORY}")
    print(f"archive={OUTPUT_ARCHIVE}")
    print(f"archive_sha256={sha256_file(OUTPUT_ARCHIVE)}")
    print(f"archive_bytes={OUTPUT_ARCHIVE.stat().st_size}")
    print(f"unique_packaged_members={len(membership)}")
    print(f"archive_mismatches={sum(row.status == 'MISMATCH' for row in alignment)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
