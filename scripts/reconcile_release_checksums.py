"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: scripts/reconcile_release_checksums.py
Purpose: Generate and verify the Git-controlled public-corpus checksum manifest.
Classification: internal release tooling
Version: 2.0.0
Last Material Revision: 2026-09-06
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
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


def sha256_index_file(path: Path) -> str:
    """Hash the staged Git blob so the manifest is checkout-platform neutral."""
    relative = path.relative_to(PROJECT_ROOT).as_posix()
    try:
        result = subprocess.run(
            ["git", "show", f":{relative}"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"Unable to read staged Git content: {relative}") from exc
    return hashlib.sha256(result.stdout).hexdigest()


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
    """Return existing Git-controlled files that belong to the public corpus.

    The repository can contain ignored archives and unrelated untracked working
    material.  Using Git's index as the membership boundary prevents those
    files from being added to the release manifest accidentally.  Newly
    approved files must therefore be staged before manifest generation.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("Unable to enumerate the Git-controlled public corpus") from exc

    relative_paths = [item for item in result.stdout.decode("utf-8").split("\0") if item]
    files: list[Path] = []
    for relative_path in relative_paths:
        path = PROJECT_ROOT / Path(relative_path)
        if not path.is_file():
            raise RuntimeError(f"Git-controlled path is absent or not a file: {relative_path}")
        if is_release_file(path):
            files.append(path)
    return sorted(files)


def require_staged_working_tree(files: list[Path]) -> None:
    """Reject tracked public-corpus changes that are not represented in the index."""
    relative_paths = [path.relative_to(PROJECT_ROOT).as_posix() for path in files]
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", *relative_paths],
        cwd=PROJECT_ROOT,
        check=False,
    )
    if result.returncode == 1:
        raise RuntimeError("Git-controlled public corpus contains unstaged changes")
    if result.returncode != 0:
        raise RuntimeError("Unable to verify staged public-corpus state")


def generate() -> None:
    files = canonical_files()
    require_staged_working_tree(files)
    lines = [f"{sha256_index_file(path)}  {path.relative_to(PROJECT_ROOT).as_posix()}" for path in files]
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
    files = canonical_files()
    require_staged_working_tree(files)
    expected_paths = {path.relative_to(PROJECT_ROOT).as_posix() for path in files}
    if set(entries) != expected_paths:
        missing = sorted(expected_paths - set(entries))
        dead = sorted(set(entries) - expected_paths)
        raise RuntimeError(f"Checksum membership mismatch; missing={missing}; dead={dead}")
    for relative, expected in entries.items():
        actual = sha256_index_file(PROJECT_ROOT / Path(relative))
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
