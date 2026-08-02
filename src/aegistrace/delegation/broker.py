"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/delegation/broker.py
Purpose: Delegation broker
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from aegistrace.identity.ids import make_identifier, make_slug
from aegistrace.identity.keys import KeyService


@dataclass
class DelegationScope:
    task_classes: list[str] = field(default_factory=list)
    resource_classes: list[str] = field(default_factory=list)
    action_classes: list[str] = field(default_factory=list)
    time_bounds: dict[str, str] | None = None  # not_before / not_after
    geography: list[str] = field(default_factory=list)
    tool_classes: list[str] = field(default_factory=list)
    model_classes: list[str] = field(default_factory=list)
    provider_classes: list[str] = field(default_factory=list)
    delegation_depth: int = 0  # 0 means leaf; cannot delegate further

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        if self.task_classes:
            d["task_classes"] = self.task_classes
        if self.resource_classes:
            d["resource_classes"] = self.resource_classes
        if self.action_classes:
            d["action_classes"] = self.action_classes
        if self.time_bounds:
            d["time_bounds"] = self.time_bounds
        if self.geography:
            d["geography"] = self.geography
        if self.tool_classes:
            d["tool_classes"] = self.tool_classes
        if self.model_classes:
            d["model_classes"] = self.model_classes
        if self.provider_classes:
            d["provider_classes"] = self.provider_classes
        d["delegation_depth"] = self.delegation_depth
        return d

    def encompasses(self, *, action: str | None = None, resource_class: str | None = None, task_class: str | None = None) -> bool:
        if action is not None and self.action_classes and action not in self.action_classes:
            return False
        if resource_class is not None and self.resource_classes and resource_class not in self.resource_classes:
            return False
        if task_class is not None and self.task_classes and task_class not in self.task_classes:
            return False
        if self.time_bounds:
            now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            if "not_before" in self.time_bounds and now < self.time_bounds["not_before"]:
                return False
            if "not_after" in self.time_bounds and now > self.time_bounds["not_after"]:
                return False
        return True


@dataclass
class Delegation:
    delegation_id: str
    parent_agent_id: str
    parent_instance_id: str
    child_agent_id: str
    principal_id: str
    controller_id: str
    scope: DelegationScope
    expires_at: str | None
    revocable: bool
    created_at: str
    state: str = "active"  # active | revoked | expired
    signature: str = ""
    signing_key_id: str = ""

    def is_active(self) -> bool:
        if self.state != "active":
            return False
        if self.expires_at:
            now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            if now > self.expires_at:
                return False
        return True

    def to_dict(self) -> dict[str, Any]:
        d = {
            "delegation_id": self.delegation_id,
            "parent_agent_id": self.parent_agent_id,
            "parent_instance_id": self.parent_instance_id,
            "child_agent_id": self.child_agent_id,
            "principal_id": self.principal_id,
            "controller_id": self.controller_id,
            "scope": self.scope.to_dict(),
            "revocable": self.revocable,
            "created_at": self.created_at,
            "state": self.state,
            "signature": self.signature,
            "signing_key_id": self.signing_key_id,
        }
        if self.expires_at:
            d["expires_at"] = self.expires_at
        return d


class DelegationBroker:
    """Creates and verifies delegations.

    Invariants:
        - Every child agent resolves to a parent delegation.
        - A delegation's scope is enforced.
        - A revoked or expired delegation produces no new valid child actions.
    """

    def __init__(self, key_service: KeyService) -> None:
        self._keys = key_service
        self._delegations: dict[str, Delegation] = {}

    def create(
        self,
        *,
        parent_agent_id: str,
        parent_instance_id: str,
        child_agent_id: str,
        principal_id: str,
        controller_id: str,
        scope: DelegationScope,
        signing_key_id: str,
        expires_at: str | None = None,
        revocable: bool = True,
    ) -> Delegation:
        if not self._keys.is_active(signing_key_id):
            raise PermissionError(f"signing key not active: {signing_key_id}")
        delegation_id = str(make_identifier("delegation", make_slug("dlg")))
        created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        # Sign the delegation record
        from aegistrace.signing.canonical import canonicalize
        record = {
            "delegation_id": delegation_id,
            "parent_agent_id": parent_agent_id,
            "parent_instance_id": parent_instance_id,
            "child_agent_id": child_agent_id,
            "principal_id": principal_id,
            "controller_id": controller_id,
            "scope": scope.to_dict(),
            "revocable": revocable,
            "created_at": created_at,
            "signing_key_id": signing_key_id,
        }
        if expires_at:
            record["expires_at"] = expires_at
        canon = canonicalize(record)
        sig = self._keys.get_signing_key(signing_key_id).sign(canon)
        dlg = Delegation(
            delegation_id=delegation_id,
            parent_agent_id=parent_agent_id,
            parent_instance_id=parent_instance_id,
            child_agent_id=child_agent_id,
            principal_id=principal_id,
            controller_id=controller_id,
            scope=scope,
            expires_at=expires_at,
            revocable=revocable,
            created_at=created_at,
            signature=sig,
            signing_key_id=signing_key_id,
        )
        self._delegations[delegation_id] = dlg
        return dlg

    def get(self, delegation_id: str) -> Delegation | None:
        return self._delegations.get(delegation_id)

    def verify(self, delegation_id: str) -> bool:
        d = self._delegations.get(delegation_id)
        if d is None:
            return False
        if not d.is_active():
            return False
        # Verify signature
        try:
            rec = self._keys.get_record(d.signing_key_id)
            from aegistrace.signing.canonical import canonicalize
            from aegistrace.signing.ed25519 import SigningKey
            pub = SigningKey.from_public_pem(d.signing_key_id, rec.public_pem).public_key
            # Reconstruct the same record that was signed originally
            record = {
                "delegation_id": d.delegation_id,
                "parent_agent_id": d.parent_agent_id,
                "parent_instance_id": d.parent_instance_id,
                "child_agent_id": d.child_agent_id,
                "principal_id": d.principal_id,
                "controller_id": d.controller_id,
                "scope": d.scope.to_dict(),
                "revocable": d.revocable,
                "created_at": d.created_at,
                "signing_key_id": d.signing_key_id,
            }
            if d.expires_at:
                record["expires_at"] = d.expires_at
            canon = canonicalize(record)
            if not SigningKey.verify(pub, canon, d.signature):
                return False
        except Exception:
            return False
        return True

    def revoke(self, delegation_id: str) -> None:
        d = self._delegations.get(delegation_id)
        if d is None:
            raise KeyError(delegation_id)
        if not d.revocable:
            raise PermissionError(f"delegation not revocable: {delegation_id}")
        d.state = "revoked"

    def all_delegations(self) -> dict[str, Delegation]:
        return dict(self._delegations)


__all__ = ["DelegationScope", "Delegation", "DelegationBroker"]
