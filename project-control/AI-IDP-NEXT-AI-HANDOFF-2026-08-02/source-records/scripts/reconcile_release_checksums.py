"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: scripts/reconcile_release_checksums.py
Purpose: Generate and verify the canonical local-release checksum manifest.
Classification: internal release tooling
Version: 2.0.0
Last Material Revision: 2026-08-02
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = PROJECT_ROOT / "release" / "CHECKSUMS.sha256"
EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "tmp",
}
EXCLUDED_SUFFIXES = {".aux", ".bbl", ".blg", ".log", ".pyc", ".synctex"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_release_file(path: Path) -> bool:
    relative = path.relative_to(PROJECT_ROOT)
    if any(part in EXCLUDED_PARTS or part.startswith(".aitrace-") for part in relative.parts):
        return False
    if any(part.endswith(".egg-info") for part in relative.parts):
        return False
    if relative.parts[:2] == ("project-control", "AI-IDP-NEXT-AI-HANDOFF-2026-08-02"):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if relative.as_posix() in {
        "release/CHECKSUMS.sha256",
        "release/NUMBERED_ARCHIVES.sha256",
        "AI-IDP-NEXT-AI-HANDOFF-2026-08-02.zip",
        "AI-IDP-NEXT-AI-HANDOFF-2026-08-02.zip.sha256",
    }:
        return False
    if len(relative.parts) == 1 and relative.name.startswith("AI-IDP-") and relative.suffix == ".zip":
        return False
    return True


def canonical_files() -> list[Path]:
    return sorted(path for path in PROJECT_ROOT.rglob("*") if path.is_file() and is_release_file(path))


def generate() -> None:
    files = canonical_files()
    lines = [f"{sha256_file(path)}  {path.relative_to(PROJECT_ROOT).as_posix()}" for path in files]
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".CHECKSUMS.", suffix=".tmp", dir=MANIFEST.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_text("\n".join(lines) + "\n", encoding="ascii")
        temporary.replace(MANIFEST)
    finally:
        temporary.unlink(missing_ok=True)


def verify() -> int:
    entries: dict[str, str] = {}
    for line_number, line in enumerate(MANIFEST.read_text(encoding="ascii").splitlines(), 1):
        expected, relative = line.split(maxsplit=1)
        relative = relative.strip()
        if relative in entries:
            raise RuntimeError(f"Duplicate checksum path at line {line_number}: {relative}")
        entries[relative] = expected.lower()
    expected_paths = {path.relative_to(PROJECT_ROOT).as_posix() for path in canonical_files()}
    if set(entries) != expected_paths:
        missing = sorted(expected_paths - set(entries))
        dead = sorted(set(entries) - expected_paths)
        raise RuntimeError(f"Checksum membership mismatch; missing={missing}; dead={dead}")
    for relative, expected in entries.items():
        actual = sha256_file(PROJECT_ROOT / Path(relative))
        if actual != expected:
            raise RuntimeError(f"Checksum mismatch: {relative}")
    return len(entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    if not arguments.verify_only:
        generate()
    count = verify()
    print(f"verified_entries={count}")
    print(f"manifest={MANIFEST.relative_to(PROJECT_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
