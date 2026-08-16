"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/identity/keys.py
Purpose: Key service for AI-IDP signing keys
Classification: domain
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-16
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from aegistrace.signing.ed25519 import SigningKey


@dataclass
class KeyRecord:
    """Registry record for a signing key.

    Invariants:
        - key_id is permanently unique.
        - state transitions are append-only (recorded in the ledger).
        - The SigningKey object holds the private material only when the
          key is active and held by the controller; verify-only registries
          hold public material only.
    """

    key_id: str
    public_pem: str
    state: str = "active"  # active | rotated | suspended | revoked | terminated
    created_at: str = ""
    rotated_at: str | None = None
    revoked_at: str | None = None
    terminated_at: str | None = None
    bound_entity_id: str | None = None
    successor_key_id: str | None = None

    def is_active(self) -> bool:
        return self.state == "active"

    def to_public_dict(self) -> dict[str, Any]:
        """Return a public, verify-only representation of this key record."""
        return {
            "key_id": self.key_id,
            "public_pem": self.public_pem,
            "state": self.state,
            "created_at": self.created_at,
            "rotated_at": self.rotated_at,
            "revoked_at": self.revoked_at,
            "terminated_at": self.terminated_at,
            "bound_entity_id": self.bound_entity_id,
            "successor_key_id": self.successor_key_id,
        }


class KeyService:
    """Manages signing-key lifecycles and verify-only public keys.

    Invariants:
        - Key IDs are never reassigned.
        - Revoked or terminated keys cannot produce valid new events.
        - Rotated keys remain verifiable.
        - Public-key import never creates or reconstructs private material.
    """

    VALID_STATES = {"active", "rotated", "suspended", "revoked", "terminated"}

    def __init__(self) -> None:
        self._keys: dict[str, KeyRecord] = {}
        self._signing_keys: dict[str, SigningKey] = {}  # only for keys we hold private material for

    def create_key(self, key_id: str, bound_entity_id: str) -> SigningKey:
        if key_id in self._keys:
            raise ValueError(f"key_id already exists: {key_id}")
        sk = SigningKey.generate(key_id)
        rec = KeyRecord(
            key_id=key_id,
            public_pem=sk.public_pem(),
            state="active",
            created_at=_now(),
            bound_entity_id=bound_entity_id,
        )
        self._keys[key_id] = rec
        self._signing_keys[key_id] = sk
        return sk

    def register_public_key(
        self,
        *,
        key_id: str,
        public_pem: str,
        bound_entity_id: str | None = None,
        state: str = "active",
        created_at: str = "",
        rotated_at: str | None = None,
        revoked_at: str | None = None,
        terminated_at: str | None = None,
        successor_key_id: str | None = None,
    ) -> KeyRecord:
        """Register an Ed25519 public key for independent verification.

        This method is intentionally verify-only: no private material is
        created, imported, or retained. Existing key IDs cannot be replaced.
        """
        if key_id in self._keys:
            raise ValueError(f"key_id already exists: {key_id}")
        if state not in self.VALID_STATES:
            raise ValueError(f"invalid key state: {state}")
        # Parse and type-check the public key before accepting the record.
        SigningKey.from_public_pem(key_id, public_pem)
        rec = KeyRecord(
            key_id=key_id,
            public_pem=public_pem,
            state=state,
            created_at=created_at,
            rotated_at=rotated_at,
            revoked_at=revoked_at,
            terminated_at=terminated_at,
            bound_entity_id=bound_entity_id,
            successor_key_id=successor_key_id,
        )
        self._keys[key_id] = rec
        return rec

    def get_signing_key(self, key_id: str) -> SigningKey:
        rec = self._keys.get(key_id)
        if rec is None:
            raise KeyError(f"unknown key: {key_id}")
        if not rec.is_active():
            raise PermissionError(f"key not active: {key_id} (state={rec.state})")
        sk = self._signing_keys.get(key_id)
        if sk is None:
            raise PermissionError(f"private material not held for key: {key_id}")
        return sk

    def get_public_pem(self, key_id: str) -> str:
        rec = self._keys.get(key_id)
        if rec is None:
            raise KeyError(f"unknown key: {key_id}")
        return rec.public_pem

    def get_record(self, key_id: str) -> KeyRecord:
        return self._keys[key_id]

    def rotate(self, old_key_id: str, new_key_id: str) -> SigningKey:
        old = self._keys.get(old_key_id)
        if old is None:
            raise KeyError(f"unknown key: {old_key_id}")
        if not old.is_active():
            raise PermissionError(f"key not active: {old_key_id}")
        if old.bound_entity_id is None:
            raise ValueError("cannot rotate key without bound entity")
        new_sk = self.create_key(new_key_id, old.bound_entity_id)
        old.state = "rotated"
        old.rotated_at = _now()
        old.successor_key_id = new_key_id
        # Old public material is retained for historical verification. The
        # old private object may remain in memory but get_signing_key() cannot
        # return it once the record is no longer active.
        return new_sk

    def suspend(self, key_id: str) -> None:
        rec = self._keys[key_id]
        if rec.state != "active":
            raise PermissionError(f"only active keys can be suspended: {key_id} (state={rec.state})")
        rec.state = "suspended"

    def revoke(self, key_id: str) -> None:
        rec = self._keys[key_id]
        if rec.state in ("revoked", "terminated"):
            return  # idempotent
        rec.state = "revoked"
        rec.revoked_at = _now()
        self._signing_keys.pop(key_id, None)

    def terminate(self, key_id: str) -> None:
        rec = self._keys[key_id]
        rec.state = "terminated"
        rec.terminated_at = _now()
        self._signing_keys.pop(key_id, None)

    def reactivate(self, key_id: str) -> None:
        rec = self._keys[key_id]
        if rec.state != "suspended":
            raise PermissionError(f"only suspended keys can be reactivated: {key_id} (state={rec.state})")
        rec.state = "active"

    def is_active(self, key_id: str) -> bool:
        rec = self._keys.get(key_id)
        return rec is not None and rec.is_active()

    def all_records(self) -> dict[str, KeyRecord]:
        return dict(self._keys)

    def export_public_registry(self) -> dict[str, Any]:
        """Export public verification material without private keys."""
        return {
            "schema": "aegistrace.public_keys.v1",
            "keys": [self._keys[key_id].to_public_dict() for key_id in sorted(self._keys)],
        }


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = ["KeyRecord", "KeyService"]
