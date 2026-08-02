"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: scripts/rebuild_numbered_archives.py
Purpose: Rebuild and verify the ten numbered local handoff archives from canonical files.
Classification: internal release tooling
Version: 2.0.0
Last Material Revision: 2026-08-02
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_NAMES = (
    "AI-IDP-01-ARXIV-PAPER.zip",
    "AI-IDP-02-SOURCE-CODE.zip",
    "AI-IDP-03-SPECS-SCHEMAS.zip",
    "AI-IDP-04-GOVERNMENT.zip",
    "AI-IDP-05-IMPACT-REPORTS.zip",
    "AI-IDP-06-UNIVERSITY-TECHNICAL.zip",
    "AI-IDP-07-RESEARCH.zip",
    "AI-IDP-08-PROJECT-CONTROL.zip",
    "AI-IDP-09-BRAND.zip",
    "AI-IDP-10-ROOT-AND-DELIVERABLES.zip",
)
PATH_REPLACEMENTS = {
    "project-control/LEGAL_STATUS_UPDATE_v1.3.0.md":
        "project-control/LEGAL_STATUS_UPDATE_v2.0.0.md",
}
ADDITIONS = {
    "AI-IDP-02-SOURCE-CODE.zip": (
        "scripts/build_release_derivatives.py",
        "scripts/build_next_ai_handoff.py",
        "scripts/rebuild_numbered_archives.py",
        "scripts/reconcile_release_checksums.py",
        "tests/unit/test_project_metadata.py",
    ),
}
ZIP_TIMESTAMP = (2026, 8, 1, 0, 0, 0)
ARCHIVE_HASH_MANIFEST = PROJECT_ROOT / "release" / "NUMBERED_ARCHIVES.sha256"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def archive_paths() -> list[Path]:
    paths = [PROJECT_ROOT / name for name in ARCHIVE_NAMES]
    missing = [path.name for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing numbered archives: {missing}")
    return paths


def canonical_members(archive: Path) -> tuple[str, ...]:
    with zipfile.ZipFile(archive) as package:
        corrupt = package.testzip()
        if corrupt is not None:
            raise RuntimeError(f"CRC failure in {archive.name}: {corrupt}")
        members = {
            PATH_REPLACEMENTS.get(info.filename, info.filename)
            for info in package.infolist()
            if not info.is_dir()
        }
    members.update(ADDITIONS.get(archive.name, ()))
    return tuple(sorted(members))


def validate_partition(specification: dict[str, tuple[str, ...]]) -> None:
    owners: dict[str, list[str]] = defaultdict(list)
    missing: list[str] = []
    for archive_name, members in specification.items():
        for member in members:
            owners[member].append(archive_name)
            if not (PROJECT_ROOT / Path(member)).is_file():
                missing.append(f"{archive_name}: {member}")
    duplicates = {member: names for member, names in owners.items() if len(names) > 1}
    if missing:
        raise FileNotFoundError("Canonical package members are missing:\n" + "\n".join(missing))
    if duplicates:
        raise RuntimeError(f"Duplicate member paths across numbered archives: {duplicates}")


def zip_info(member: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(member, ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def build_archive(archive: Path, members: tuple[str, ...]) -> None:
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{archive.stem}.", suffix=".tmp.zip", dir=archive.parent
    )
    os.close(file_descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as package:
            for member in members:
                package.writestr(zip_info(member), (PROJECT_ROOT / Path(member)).read_bytes())
        verify_archive(temporary, members)
        temporary.replace(archive)
    finally:
        temporary.unlink(missing_ok=True)


def verify_archive(archive: Path, expected_members: tuple[str, ...]) -> None:
    with zipfile.ZipFile(archive) as package:
        corrupt = package.testzip()
        if corrupt is not None:
            raise RuntimeError(f"CRC failure in {archive.name}: {corrupt}")
        actual_members = tuple(sorted(info.filename for info in package.infolist() if not info.is_dir()))
        if actual_members != expected_members:
            raise RuntimeError(f"Member-set mismatch in {archive.name}")
        for member in actual_members:
            packaged = package.read(member)
            canonical = (PROJECT_ROOT / Path(member)).read_bytes()
            if packaged != canonical:
                raise RuntimeError(f"Canonical byte mismatch in {archive.name}: {member}")


def write_hash_manifest(paths: list[Path]) -> None:
    lines = [f"{sha256_file(path).lower()}  {path.name}" for path in paths]
    ARCHIVE_HASH_MANIFEST.write_text("\n".join(lines) + "\n", encoding="ascii")


def main() -> int:
    paths = archive_paths()
    specification = {path.name: canonical_members(path) for path in paths}
    validate_partition(specification)
    for path in paths:
        build_archive(path, specification[path.name])
    for path in paths:
        verify_archive(path, specification[path.name])
    write_hash_manifest(paths)
    print(f"archives={len(paths)}")
    print(f"unique_members={sum(len(members) for members in specification.values())}")
    for path in paths:
        print(
            f"{path.name}|members={len(specification[path.name])}|"
            f"bytes={path.stat().st_size}|sha256={sha256_file(path)}"
        )
    print(f"hash_manifest={ARCHIVE_HASH_MANIFEST.relative_to(PROJECT_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
