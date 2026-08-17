"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/identity/keys.py
Purpose: Key service for AI-IDP signing keys
Classification: domain
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Iterable

from aegistrace.signing.ed25519 import SigningKey


@dataclass
class KeyRecord:
    """Registry record for a signing key."""

    key_id: str
    public_pem: str
    state: str = "active"
    created_at: str = ""
    rotated_at: str | None = None
    revoked_at: str | None = None
    terminated_at: str | None = None
    bound_entity_id: str | None = None
    successor_key_id: str | None = None

    def is_active(self) -> bool:
        return self.state == "active"

    def to_public_dict(self, *, include_binding: bool = False) -> dict[str, Any]:
        """Return verify-only material with private bindings omitted by default."""
        result: dict[str, Any] = {
            "key_id": self.key_id,
            "public_pem": self.public_pem,
            "state": self.state,
            "created_at": self.created_at,
            "rotated_at": self.rotated_at,
            "revoked_at": self.revoked_at,
            "terminated_at": self.terminated_at,
            "successor_key_id": self.successor_key_id,
        }
        if include_binding and self.bound_entity_id is not None:
            result["bound_entity_id"] = self.bound_entity_id
        return result


class KeyService:
    """Manage signing-key lifecycles and verify-only public keys.

    Public-key import/export never creates, serializes, or reconstructs private
    material. Public export is allow-listable so an API does not disclose every
    internal signing-key identifier by default.
    """

    VALID_STATES = {"active", "rotated", "suspended", "revoked", "terminated"}

    def __init__(self) -> None:
        self._keys: dict[str, KeyRecord] = {}
        self._signing_keys: dict[str, SigningKey] = {}

    def create_key(self, key_id: str, bound_entity_id: str) -> SigningKey:
        if key_id in self._keys:
            raise ValueError(f"key_id already exists: {key_id}")
        signing_key = SigningKey.generate(key_id)
        record = KeyRecord(
            key_id=key_id,
            public_pem=signing_key.public_pem(),
            state="active",
            created_at=_now(),
            bound_entity_id=bound_entity_id,
        )
        self._keys[key_id] = record
        self._signing_keys[key_id] = signing_key
        return signing_key

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
        if key_id in self._keys:
            raise ValueError(f"key_id already exists: {key_id}")
        if state not in self.VALID_STATES:
            raise ValueError(f"invalid key state: {state}")
        SigningKey.from_public_pem(key_id, public_pem)
        record = KeyRecord(
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
        self._keys[key_id] = record
        return record

    def get_signing_key(self, key_id: str) -> SigningKey:
        record = self._keys.get(key_id)
        if record is None:
            raise KeyError(f"unknown key: {key_id}")
        if not record.is_active():
            raise PermissionError(f"key not active: {key_id} (state={record.state})")
        signing_key = self._signing_keys.get(key_id)
        if signing_key is None:
            raise PermissionError(f"private material not held for key: {key_id}")
        return signing_key

    def get_public_pem(self, key_id: str) -> str:
        record = self._keys.get(key_id)
        if record is None:
            raise KeyError(f"unknown key: {key_id}")
        return record.public_pem

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
        new_signing_key = self.create_key(new_key_id, old.bound_entity_id)
        old.state = "rotated"
        old.rotated_at = _now()
        old.successor_key_id = new_key_id
        return new_signing_key

    def suspend(self, key_id: str) -> None:
        record = self._keys[key_id]
        if record.state != "active":
            raise PermissionError(f"only active keys can be suspended: {key_id} (state={record.state})")
        record.state = "suspended"

    def revoke(self, key_id: str) -> None:
        record = self._keys[key_id]
        if record.state in ("revoked", "terminated"):
            return
        record.state = "revoked"
        record.revoked_at = _now()
        self._signing_keys.pop(key_id, None)

    def terminate(self, key_id: str) -> None:
        record = self._keys[key_id]
        record.state = "terminated"
        record.terminated_at = _now()
        self._signing_keys.pop(key_id, None)

    def reactivate(self, key_id: str) -> None:
        record = self._keys[key_id]
        if record.state != "suspended":
            raise PermissionError(f"only suspended keys can be reactivated: {key_id} (state={record.state})")
        record.state = "active"

    def is_active(self, key_id: str) -> bool:
        record = self._keys.get(key_id)
        return record is not None and record.is_active()

    def all_records(self) -> dict[str, KeyRecord]:
        return dict(self._keys)

    def export_public_registry(
        self,
        *,
        key_ids: Iterable[str] | None = None,
        include_bindings: bool = False,
    ) -> dict[str, Any]:
        """Export selected public verification material without private keys."""
        selected = sorted(set(key_ids) if key_ids is not None else set(self._keys))
        unknown = [key_id for key_id in selected if key_id not in self._keys]
        if unknown:
            raise KeyError(f"unknown keys requested for export: {unknown}")
        return {
            "schema": "aegistrace.public_keys.v1",
            "keys": [
                self._keys[key_id].to_public_dict(include_binding=include_bindings)
                for key_id in selected
            ],
        }


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = ["KeyRecord", "KeyService"]
