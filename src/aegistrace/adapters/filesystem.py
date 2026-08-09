"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/adapters/filesystem.py
Purpose: Filesystem watcher adapter
Classification: adapter
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def file_digest(path: Path) -> str:
    """Compute 'sha256:<hex>' of a file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


class FilesystemAdapter:
    """Records filesystem operations as AegisTrace events.

    The adapter does not watch in real time; it provides methods that
    agents call when they perform filesystem operations. The methods
    return digests that the caller includes in the corresponding
    AegisTrace event record.
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir).resolve()

    def _resolve(self, path: Path) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.base_dir / p
        p = p.resolve()
        # Path traversal protection
        try:
            p.relative_to(self.base_dir)
        except ValueError as exc:
            raise PermissionError(f"path traversal blocked: {path}") from exc
        return p

    def before(self, path: Path) -> str | None:
        """Return the current digest of a file, or None if the file does not exist."""
        p = self._resolve(path)
        if not p.exists() or not p.is_file():
            return None
        return file_digest(p)

    def after(self, path: Path) -> str | None:
        """Return the digest of a file after a mutating operation."""
        return self.before(path)

    def resource_id(self, path: Path) -> str:
        """Return a stable resource identifier for a path."""
        p = self._resolve(path)
        rel = p.relative_to(self.base_dir).as_posix()
        return f"urn:aegistrace:file:{self.base_dir.name}:{rel}"

    def create(self, path: Path, content: bytes) -> dict[str, str | None]:
        p = self._resolve(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return {"resource_id": self.resource_id(path), "after_digest": file_digest(p), "before_digest": None}

    def modify(self, path: Path, content: bytes) -> dict[str, str | None]:
        p = self._resolve(path)
        before = file_digest(p) if p.exists() else None
        p.write_bytes(content)
        after = file_digest(p)
        return {"resource_id": self.resource_id(path), "before_digest": before, "after_digest": after}

    def delete(self, path: Path) -> dict[str, str | None]:
        p = self._resolve(path)
        before = file_digest(p) if p.exists() else None
        p.unlink(missing_ok=True)
        return {"resource_id": self.resource_id(path), "before_digest": before, "after_digest": None}


__all__ = ["FilesystemAdapter", "file_digest"]
