"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/manifests/resource.py
Purpose: Resource manifests for protected directories
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class ResourceManifest:
    directory_id: str
    resource_owner: str
    first_ai_access: str
    latest_ai_access: str
    agent_ids: set[str] = field(default_factory=set)
    instance_ids: set[str] = field(default_factory=set)
    controller_references: set[str] = field(default_factory=set)
    task_references: set[str] = field(default_factory=set)
    action_summaries: dict[str, int] = field(default_factory=dict)
    registry_references: dict[str, str] = field(default_factory=dict)
    policy_version: str = "1.0.0"
    current_state_digest: str = ""
    latest_ledger_sequence: int = 0
    integrity_status: str = "unverified"
    legal_hold_status: str = "none"
    incident_status: str = "none"
    verification_procedure: str = "AegisTrace verify v2.0"

    def to_dict(self) -> dict:
        return {
            "directory_id": self.directory_id,
            "resource_owner": self.resource_owner,
            "first_ai_access": self.first_ai_access,
            "latest_ai_access": self.latest_ai_access,
            "agent_ids": sorted(self.agent_ids),
            "instance_ids": sorted(self.instance_ids),
            "controller_references": sorted(self.controller_references),
            "task_references": sorted(self.task_references),
            "action_summaries": self.action_summaries,
            "registry_references": self.registry_references,
            "policy_version": self.policy_version,
            "current_state_digest": self.current_state_digest,
            "latest_ledger_sequence": self.latest_ledger_sequence,
            "integrity_status": self.integrity_status,
            "legal_hold_status": self.legal_hold_status,
            "incident_status": self.incident_status,
            "verification_procedure": self.verification_procedure,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ResourceManifest:
        m = cls(
            directory_id=d["directory_id"],
            resource_owner=d["resource_owner"],
            first_ai_access=d["first_ai_access"],
            latest_ai_access=d["latest_ai_access"],
            policy_version=d.get("policy_version", "1.0.0"),
            current_state_digest=d.get("current_state_digest", ""),
            latest_ledger_sequence=d.get("latest_ledger_sequence", 0),
            integrity_status=d.get("integrity_status", "unverified"),
            legal_hold_status=d.get("legal_hold_status", "none"),
            incident_status=d.get("incident_status", "none"),
            verification_procedure=d.get("verification_procedure", "AegisTrace verify v2.0"),
        )
        m.agent_ids = set(d.get("agent_ids", []))
        m.instance_ids = set(d.get("instance_ids", []))
        m.controller_references = set(d.get("controller_references", []))
        m.task_references = set(d.get("task_references", []))
        m.action_summaries = dict(d.get("action_summaries", {}))
        m.registry_references = dict(d.get("registry_references", {}))
        return m


def compute_directory_digest(path: Path) -> str:
    """Compute SHA-256 over the deterministic listing of a directory tree.

    Walks the directory, hashes each file's relative path and content,
    and returns 'sha256:<hex>'.
    """
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file() and ".aitrace" not in p.parts:
            rel = p.relative_to(path).as_posix()
            h.update(rel.encode("utf-8"))
            h.update(b"\x00")
            h.update(p.read_bytes())
            h.update(b"\x00")
    return "sha256:" + h.hexdigest()


def write_aitrace_directory(directory: Path, manifest: ResourceManifest, ledger_jsonl: str) -> Path:
    """Write a .aitrace/ sidecar directory with manifest and ledger."""
    ait_dir = directory / ".aitrace"
    ait_dir.mkdir(exist_ok=True)
    (ait_dir / "resource_manifest.json").write_text(
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
    )
    (ait_dir / "ledger.jsonl").write_text(ledger_jsonl, encoding="utf-8")
    (ait_dir / "README.md").write_text(
        "# AegisTrace manifest\n\nThis directory contains the AI-IDP trace manifest for the parent directory.\n",
        encoding="utf-8",
    )
    (ait_dir / "AUDIT.md").write_text(
        "# Audit notes\n\nAudit findings are appended here.\n",
        encoding="utf-8",
    )
    (ait_dir / "registry_refs.json").write_text("{}", encoding="utf-8")
    (ait_dir / "policies.json").write_text(json.dumps({"policy_version": manifest.policy_version}, indent=2), encoding="utf-8")
    (ait_dir / "verification.json").write_text(
        json.dumps({"integrity_status": manifest.integrity_status, "verified_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")}, indent=2),
        encoding="utf-8",
    )
    (ait_dir / "evidence").mkdir(exist_ok=True)
    return ait_dir


__all__ = ["ResourceManifest", "compute_directory_digest", "write_aitrace_directory"]
