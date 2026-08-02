"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/adapters/github.py
Purpose: GitHub evidence adapter (private + public repositories)
Classification: adapter
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.

NOTE: This adapter operates locally only during the autonomous run.
It produces ready-to-push payloads (commit-attestation JSON, Git notes,
Merkle-root anchors) but does NOT push to a live GitHub remote. Pushing
requires separate authorization from Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime

from aegistrace.events.models import Event
from aegistrace.ledger.merkle import merkle_proof, merkle_root
from aegistrace.signing.canonical import canonicalize
from aegistrace.signing.ed25519 import sha256_hex


@dataclass
class CommitAttestation:
    """Attestation payload to attach to a Git commit (e.g., via Git notes)."""
    commit_hash: str
    attestation_type: str  # 'aegistrace.event' | 'aegistrace.merkle_root' | 'aegistrace.release'
    payload: dict
    signature: str
    signing_key_id: str
    created_at: str

    def to_json(self) -> str:
        return json.dumps(self.__dict__, sort_keys=True, indent=2)


class GitHubEvidenceAdapter:
    """Produces payloads for the GitHub dual-repository evidence pattern.

    PRIVATE EVIDENCE REPOSITORY payloads (encrypted sensitive evidence,
    provider/model/agent registrations, action ledgers).
    PUBLIC VERIFICATION REPOSITORY payloads (signed Merkle roots,
    revocation status, certification status, public schemas).
    """

    def __init__(self, signing_key_id: str, public_pem: str) -> None:
        self.signing_key_id = signing_key_id
        self.public_pem = public_pem

    def make_commit_attestation(self, commit_hash: str, event: Event, signature: str) -> CommitAttestation:
        payload = {
            "event_id": event.event_id,
            "event_hash": event.event_hash,
            "action": event.action,
            "actor": event.actor.to_dict(),
            "execution_context": event.execution_context.to_dict(),
            "timestamp": event.timestamp,
        }
        return CommitAttestation(
            commit_hash=commit_hash,
            attestation_type="aegistrace.event",
            payload=payload,
            signature=signature,
            signing_key_id=self.signing_key_id,
            created_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    def make_merkle_root_anchor(self, events: list[Event]) -> dict:
        """Produce a Merkle-root anchor for the public verification repository."""
        root = merkle_root(events)
        anchor = {
            "schema": "aegistrace.merkle_root.v1",
            "root": root,
            "event_count": len(events),
            "first_event_id": events[0].event_id if events else None,
            "last_event_id": events[-1].event_id if events else None,
            "anchored_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "signing_key_id": self.signing_key_id,
        }
        canon = canonicalize({k: v for k, v in anchor.items() if k != "signature"})
        anchor["root_hash"] = sha256_hex(canon)
        return anchor

    def make_merkle_proof(self, events: list[Event], index: int) -> dict:
        """Produce a Merkle proof for the public verification repository."""
        proof = merkle_proof(events, index)
        return {
            "schema": "aegistrace.merkle_proof.v1",
            "event_id": events[index].event_id,
            "event_hash": events[index].event_hash,
            "proof": proof,
            "root": merkle_root(events),
        }

    def make_revocation_status(self, revoked_ids: list[str]) -> dict:
        return {
            "schema": "aegistrace.revocation_status.v1",
            "revoked_ids": sorted(revoked_ids),
            "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "signing_key_id": self.signing_key_id,
        }

    def make_release_attestation(self, release_version: str, artifact_hashes: dict[str, str]) -> dict:
        return {
            "schema": "aegistrace.release_attestation.v1",
            "release_version": release_version,
            "artifact_hashes": artifact_hashes,
            "attested_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "signing_key_id": self.signing_key_id,
            "public_key_pem": self.public_pem,
        }


__all__ = ["CommitAttestation", "GitHubEvidenceAdapter"]
