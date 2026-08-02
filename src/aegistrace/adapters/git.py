"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/adapters/git.py
Purpose: Git adapter for repository operations
Classification: adapter
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


class GitAdapter:
    """Wraps Git operations and produces AegisTrace-compatible resource references.

    Requires `git` on PATH. Does not push to a remote during this autonomous run.
    """

    def __init__(self, repo_path: Path) -> None:
        self.repo_path = Path(repo_path).resolve()
        if not (self.repo_path / ".git").exists():
            self._run(["git", "init", "--initial-branch=main"], cwd=self.repo_path.parent)
            if not self.repo_path.exists():
                self.repo_path.mkdir(parents=True)

    def _run(self, cmd: list[str], cwd: Path | None = None) -> str:
        result = subprocess.run(cmd, cwd=cwd or self.repo_path, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"git failed: {' '.join(cmd)}\nstdout: {result.stdout}\nstderr: {result.stderr}")
        return result.stdout.strip()

    def add(self, paths: list[str]) -> None:
        self._run(["git", "add", *paths])

    def commit(self, message: str) -> str:
        # Configure a fallback identity if none set
        try:
            self._run(["git", "config", "user.email"])
        except RuntimeError:
            self._run(["git", "config", "user.email", "aegistrace@cognitiveindustries.ca"])
            self._run(["git", "config", "user.name", "AegisTrace"])
        self._run(["git", "commit", "-m", message])
        return self.head()

    def head(self) -> str:
        return self._run(["git", "rev-parse", "HEAD"])

    def branch(self, name: str) -> None:
        self._run(["git", "checkout", "-b", name])

    def checkout(self, name: str) -> None:
        self._run(["git", "checkout", name])

    def merge(self, name: str) -> None:
        self._run(["git", "merge", name])

    def tag(self, name: str, message: str = "") -> None:
        if message:
            self._run(["git", "tag", "-a", name, "-m", message])
        else:
            self._run(["git", "tag", name])

    def log(self, limit: int = 100) -> list[dict[str, str]]:
        out = self._run(["git", "log", f"-n{limit}", "--pretty=format:%H|%an|%ae|%aI|%s"])
        entries = []
        for line in out.splitlines():
            parts = line.split("|", 4)
            if len(parts) == 5:
                entries.append({"hash": parts[0], "author_name": parts[1], "author_email": parts[2], "author_date": parts[3], "subject": parts[4]})
        return entries


__all__ = ["GitAdapter"]
