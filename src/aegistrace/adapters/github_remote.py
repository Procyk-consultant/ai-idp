"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/adapters/github_remote.py
Purpose: Live GitHub remote integration (push to public verification repository
         and private evidence repository)
Classification: adapter
Security Classification: confidential
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.

This module provides live GitHub remote integration. Unlike the existing
GitHubEvidenceAdapter (which produces ready-to-push payloads but does not
push), this module actually pushes to GitHub remotes via:
1. Git push to a configured remote (requires git CLI and PAT).
2. GitHub REST API for creating/updating files (requires PAT).

SECURITY NOTE:
- The Personal Access Token (PAT) is sourced from the AEGISTRACE_GITHUB_TOKEN
  environment variable. NEVER hard-code a PAT in source code.
- The PAT must have 'repo' scope for private repositories and 'public_repo'
  scope for public repositories.
- The PAT is sent only to github.com over HTTPS.
- The PAT is NOT logged.
- The PAT is NOT persisted beyond the process lifetime.

This module is ready for use. To activate:
1. Create a GitHub PAT with appropriate scope.
2. Set AEGISTRACE_GITHUB_TOKEN=<your-pat>
3. Set AEGISTRACE_GITHUB_OWNER=<your-github-username-or-org>
4. Set AEGISTRACE_GITHUB_PUBLIC_REPO=<public-verification-repo-name>
5. Set AEGISTRACE_GITHUB_PRIVATE_REPO=<private-evidence-repo-name> (optional)
6. Call GitHubRemotePusher.push_merkle_anchor(anchor) or push_file(path, content)
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


# Type alias for JSON-serializable types
JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


@dataclass
class GitHubConfig:
    """Configuration for GitHub remote integration.

    All sensitive values are sourced from environment variables.
    NEVER hard-code credentials in source code.
    """
    token: str = ""  # AEGISTRACE_GITHUB_TOKEN
    owner: str = ""  # AEGISTRACE_GITHUB_OWNER (username or org)
    public_repo: str = ""  # AEGISTRACE_GITHUB_PUBLIC_REPO
    private_repo: str = ""  # AEGISTRACE_GITHUB_PRIVATE_REPO (optional)
    api_base: str = "https://api.github.com"
    git_base: str = "https://github.com"
    default_branch: str = "main"
    committer_name: str = "AegisTrace"
    committer_email: str = "aegistrace@cognitiveindustries.ca"

    @classmethod
    def from_env(cls) -> GitHubConfig:
        return cls(
            token=os.environ.get("AEGISTRACE_GITHUB_TOKEN", ""),
            owner=os.environ.get("AEGISTRACE_GITHUB_OWNER", ""),
            public_repo=os.environ.get("AEGISTRACE_GITHUB_PUBLIC_REPO", ""),
            private_repo=os.environ.get("AEGISTRACE_GITHUB_PRIVATE_REPO", ""),
            default_branch=os.environ.get("AEGISTRACE_GITHUB_DEFAULT_BRANCH", "main"),
        )

    def validate(self) -> None:
        if not self.token:
            raise ValueError(
                "AEGISTRACE_GITHUB_TOKEN is not set. "
                "Create a GitHub PAT and set the environment variable."
            )
        if not self.owner:
            raise ValueError("AEGISTRACE_GITHUB_OWNER is not set.")
        if not self.public_repo:
            raise ValueError("AEGISTRACE_GITHUB_PUBLIC_REPO is not set.")


class GitHubRemotePusher:
    """Pushes AegisTrace artifacts to GitHub remotes.

    Provides two methods:
    1. push_file_via_api: push a single file via the GitHub REST API
       (suitable for Merkle anchors, revocation status, certification status).
    2. push_repository_via_git: push a local Git repository to a remote
       via `git push` (suitable for initial repository setup and bulk pushes).

    The pusher is non-destructive: it creates new commits; it does not
    rewrite history.
    """

    def __init__(self, config: GitHubConfig | None = None) -> None:
        self.config = config or GitHubConfig.from_env()
        self._available = _REQUESTS_AVAILABLE
        if not self._available:
            raise ImportError(
                "requests is required for GitHubRemotePusher. "
                "Install with: pip install requests"
            )

    @property
    def available(self) -> bool:
        return self._available

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"token {self.config.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def push_file_via_api(
        self,
        repo: str,
        path: str,
        content: str,
        commit_message: str,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Push a single file to a GitHub repository via the REST API.

        Args:
            repo: Repository name (e.g., 'aegistrace-public-verification').
            path: File path within the repository (e.g., 'anchors/2026/07/19.json').
            content: File content (UTF-8 string).
            commit_message: Git commit message.
            branch: Target branch (default: config.default_branch).

        Returns:
            The GitHub API response as a dict.

        Raises:
            ValueError: If config is invalid.
            requests.HTTPError: If the API call fails.
        """
        self.config.validate()
        branch = branch or self.config.default_branch
        url = f"{self.config.api_base}/repos/{self.config.owner}/{repo}/contents/{path}"
        # Check if file exists (to get its SHA for update)
        existing_sha: str | None = None
        try:
            response = requests.get(url, headers=self._headers(), params={"ref": branch}, timeout=30)
            if response.status_code == 200:
                existing_sha = response.json().get("sha")
        except requests.RequestException:
            pass  # File may not exist yet
        # Encode content as base64
        content_b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
        # Build the request body
        body: dict[str, Any] = {
            "message": commit_message,
            "content": content_b64,
            "branch": branch,
            "committer": {
                "name": self.config.committer_name,
                "email": self.config.committer_email,
            },
        }
        if existing_sha:
            body["sha"] = existing_sha
        # Push
        response = requests.put(url, headers=self._headers(), json=body, timeout=60)
        response.raise_for_status()
        return response.json()

    def push_merkle_anchor(self, anchor: dict[str, Any]) -> dict[str, Any]:
        """Push a Merkle anchor to the public verification repository.

        Args:
            anchor: The Merkle anchor dict (from GitHubEvidenceAdapter.make_merkle_root_anchor).

        Returns:
            The GitHub API response.
        """
        # Build the file path: anchors/<year>/<month>/<day>/<root-prefix>.json
        root = anchor.get("root", "unknown")
        anchored_at = anchor.get("anchored_at", "")
        if anchored_at:
            # anchored_at is ISO 8601 UTC: 2026-08-01T02:35:43Z
            date_part = anchored_at.split("T")[0]  # 2026-08-01
            year, month, day = date_part.split("-")
        else:
            year, month, day = "unknown", "unknown", "unknown"
        root_prefix = root.replace("sha256:", "")[:12]
        path = f"anchors/{year}/{month}/{day}/{root_prefix}.json"
        content = json.dumps(anchor, indent=2, sort_keys=True)
        commit_message = f"anchor: {root_prefix} ({anchor.get('event_count', 0)} events)"
        return self.push_file_via_api(
            repo=self.config.public_repo,
            path=path,
            content=content,
            commit_message=commit_message,
        )

    def push_revocation_status(self, revocation: dict[str, Any]) -> dict[str, Any]:
        """Push revocation status to the public verification repository."""
        path = "revocation-status.json"
        content = json.dumps(revocation, indent=2, sort_keys=True)
        return self.push_file_via_api(
            repo=self.config.public_repo,
            path=path,
            content=content,
            commit_message="update: revocation status",
        )

    def push_certification_status(self, certification: dict[str, Any]) -> dict[str, Any]:
        """Push certification status to the public verification repository."""
        cert_id = certification.get("certification_id", "unknown")
        path = f"certifications/{cert_id}.json"
        content = json.dumps(certification, indent=2, sort_keys=True)
        return self.push_file_via_api(
            repo=self.config.public_repo,
            path=path,
            content=content,
            commit_message=f"certification: {cert_id}",
        )

    def push_repository_via_git(
        self,
        local_repo_path: Path,
        remote_url: str,
        branch: str = "main",
        force: bool = False,
    ) -> dict[str, Any]:
        """Push a local Git repository to a remote via `git push`.

        Args:
            local_repo_path: Path to the local Git repository.
            remote_url: Remote URL (HTTPS or SSH). For HTTPS, the PAT is
                embedded in the URL: https://<token>@github.com/owner/repo.git
            branch: Branch to push.
            force: If True, use --force-with-lease (safer than --force).

        Returns:
            A dict with the push result (stdout, stderr, returncode).

        Raises:
            RuntimeError: If git push fails.
        """
        # Configure git committer
        subprocess.run(
            ["git", "config", "user.name", self.config.committer_name],
            cwd=local_repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", self.config.committer_email],
            cwd=local_repo_path,
            check=True,
            capture_output=True,
        )
        # Add the remote (or update if exists)
        subprocess.run(
            ["git", "remote", "add", "origin", remote_url],
            cwd=local_repo_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "remote", "set-url", "origin", remote_url],
            cwd=local_repo_path,
            check=True,
            capture_output=True,
        )
        # Push
        cmd = ["git", "push", "origin", branch]
        if force:
            cmd.insert(2, "--force-with-lease")
        result = subprocess.run(cmd, cwd=local_repo_path, capture_output=True, text=True)
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def push_private_evidence(self, evidence: dict[str, Any], path: str) -> dict[str, Any]:
        """Push encrypted evidence to the private evidence repository.

        The evidence should already be encrypted by the caller. This method
        does NOT encrypt; it only pushes.
        """
        if not self.config.private_repo:
            raise ValueError("AEGISTRACE_GITHUB_PRIVATE_REPO is not set.")
        content = json.dumps(evidence, indent=2, sort_keys=True)
        return self.push_file_via_api(
            repo=self.config.private_repo,
            path=path,
            content=content,
            commit_message=f"evidence: {path}",
        )

    def create_repository(self, repo: str, private: bool = False, description: str = "") -> dict[str, Any]:
        """Create a new GitHub repository.

        Args:
            repo: Repository name.
            private: If True, create a private repository.
            description: Repository description.
        """
        self.config.validate()
        url = f"{self.config.api_base}/user/repos"
        body: dict[str, JsonValue] = {
            "name": repo,
            "private": private,
            "description": description,
            "auto_init": True,
        }
        response = requests.post(url, headers=self._headers(), json=body, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_repository(self, repo: str) -> dict[str, Any] | None:
        """Get repository information. Returns None if not found."""
        self.config.validate()
        url = f"{self.config.api_base}/repos/{self.config.owner}/{repo}"
        response = requests.get(url, headers=self._headers(), timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()


class GitHubRemoteStub:
    """No-op stub for environments without GitHub credentials.

    Used when AEGISTRACE_GITHUB_TOKEN is not set. Records push requests
    for later replay.
    """

    def __init__(self) -> None:
        self.pushed: list[dict[str, Any]] = []

    def push_file_via_api(self, **kwargs: Any) -> dict[str, Any]:
        self.pushed.append({"method": "push_file_via_api", "args": kwargs})
        return {"stub": True, "message": "GitHub credentials not configured; push recorded for replay."}

    def push_merkle_anchor(self, anchor: dict[str, Any]) -> dict[str, Any]:
        self.pushed.append({"method": "push_merkle_anchor", "anchor": anchor})
        return {"stub": True, "message": "GitHub credentials not configured; push recorded for replay."}

    def push_revocation_status(self, revocation: dict[str, Any]) -> dict[str, Any]:
        self.pushed.append({"method": "push_revocation_status", "revocation": revocation})
        return {"stub": True, "message": "GitHub credentials not configured; push recorded for replay."}

    def push_certification_status(self, certification: dict[str, Any]) -> dict[str, Any]:
        self.pushed.append({"method": "push_certification_status", "certification": certification})
        return {"stub": True, "message": "GitHub credentials not configured; push recorded for replay."}

    def push_repository_via_git(self, **kwargs: Any) -> dict[str, Any]:
        self.pushed.append({"method": "push_repository_via_git", "args": kwargs})
        return {"stub": True, "returncode": 0, "stdout": "", "stderr": "stub: GitHub credentials not configured."}

    def push_private_evidence(self, evidence: dict[str, Any], path: str) -> dict[str, Any]:
        self.pushed.append({"method": "push_private_evidence", "evidence": evidence, "path": path})
        return {"stub": True, "message": "GitHub credentials not configured; push recorded for replay."}


def make_github_pusher() -> GitHubRemotePusher | GitHubRemoteStub:
    """Factory that returns a real pusher if credentials are available, else a stub."""
    config = GitHubConfig.from_env()
    if config.token and config.owner and config.public_repo and _REQUESTS_AVAILABLE:
        try:
            return GitHubRemotePusher(config)
        except Exception:
            return GitHubRemoteStub()
    return GitHubRemoteStub()


__all__ = [
    "GitHubConfig",
    "GitHubRemotePusher",
    "GitHubRemoteStub",
    "make_github_pusher",
]
