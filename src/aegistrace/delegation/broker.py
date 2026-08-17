"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/delegation/broker.py
Purpose: Delegation broker and lineage verification
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from aegistrace.authorization.scope import ScopeContext, evaluate_child_scope, evaluate_scope
from aegistrace.identity.ids import make_identifier, make_slug
from aegistrace.identity.keys import KeyService
from aegistrace.signing.canonical import canonicalize
from aegistrace.signing.ed25519 import SigningKey


@dataclass
class DelegationScope:
    task_classes: list[str] = field(default_factory=list)
    resource_classes: list[str] = field(default_factory=list)
    action_classes: list[str] = field(default_factory=list)
    time_bounds: dict[str, str] | None = None
    geography: list[str] = field(default_factory=list)
    tool_classes: list[str] = field(default_factory=list)
    model_classes: list[str] = field(default_factory=list)
    provider_classes: list[str] = field(default_factory=list)
    delegation_depth: int = 0

    def __post_init__(self) -> None:
        if self.delegation_depth < 0:
            raise ValueError("delegation_depth cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"delegation_depth": self.delegation_depth}
        if self.task_classes:
            result["task_classes"] = list(self.task_classes)
        if self.resource_classes:
            result["resource_classes"] = list(self.resource_classes)
        if self.action_classes:
            result["action_classes"] = list(self.action_classes)
        if self.time_bounds:
            result["time_bounds"] = dict(self.time_bounds)
        if self.geography:
            result["geography"] = list(self.geography)
        if self.tool_classes:
            result["tool_classes"] = list(self.tool_classes)
        if self.model_classes:
            result["model_classes"] = list(self.model_classes)
        if self.provider_classes:
            result["provider_classes"] = list(self.provider_classes)
        return result

    def encompasses(
        self,
        *,
        action: str | None = None,
        resource_class: str | None = None,
        task_class: str | None = None,
        geography: str | None = None,
        tool_class: str | None = None,
        model_class: str | None = None,
        provider_class: str | None = None,
        evaluated_at: str | None = None,
        requested_delegation_depth: int | None = None,
    ) -> bool:
        context = ScopeContext(
            task_class=task_class,
            resource_class=resource_class,
            geography=geography,
            tool_class=tool_class,
            model_class=model_class,
            provider_class=provider_class,
            evaluated_at=evaluated_at,
            requested_delegation_depth=requested_delegation_depth,
        )
        try:
            return evaluate_scope(
                self.to_dict(),
                action=action if action is not None else "__UNSPECIFIED__",
                context=context,
            ).allowed
        except (TypeError, ValueError):
            return False

    def contains_child_scope(self, child_scope: DelegationScope) -> bool:
        try:
            return evaluate_child_scope(self.to_dict(), child_scope.to_dict()).allowed
        except (TypeError, ValueError):
            return False


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
    parent_delegation_id: str | None = None
    state: str = "active"
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
        result: dict[str, Any] = {
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
        if self.parent_delegation_id:
            result["parent_delegation_id"] = self.parent_delegation_id
        if self.expires_at:
            result["expires_at"] = self.expires_at
        return result


class DelegationBroker:
    """Create, verify, revoke, and resolve bounded delegation chains."""

    def __init__(self, key_service: KeyService) -> None:
        self._keys = key_service
        self._delegations: dict[str, Delegation] = {}

    def _signing_key_is_authorized(
        self,
        *,
        signing_key_id: str,
        parent_agent_id: str,
        principal_id: str,
        controller_id: str,
    ) -> bool:
        try:
            record = self._keys.get_record(signing_key_id)
        except KeyError:
            return False
        return record.bound_entity_id in {parent_agent_id, principal_id, controller_id}

    def _signed_record(self, delegation: Delegation) -> dict[str, Any]:
        result: dict[str, Any] = {
            "delegation_id": delegation.delegation_id,
            "parent_agent_id": delegation.parent_agent_id,
            "parent_instance_id": delegation.parent_instance_id,
            "child_agent_id": delegation.child_agent_id,
            "principal_id": delegation.principal_id,
            "controller_id": delegation.controller_id,
            "scope": delegation.scope.to_dict(),
            "revocable": delegation.revocable,
            "created_at": delegation.created_at,
            "signing_key_id": delegation.signing_key_id,
        }
        if delegation.parent_delegation_id:
            result["parent_delegation_id"] = delegation.parent_delegation_id
        if delegation.expires_at:
            result["expires_at"] = delegation.expires_at
        return result

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
        parent_delegation_id: str | None = None,
    ) -> Delegation:
        if parent_agent_id == child_agent_id:
            raise ValueError("an agent cannot delegate to itself")
        if not self._keys.is_active(signing_key_id):
            raise PermissionError(f"signing key not active: {signing_key_id}")
        if not self._signing_key_is_authorized(
            signing_key_id=signing_key_id,
            parent_agent_id=parent_agent_id,
            principal_id=principal_id,
            controller_id=controller_id,
        ):
            raise PermissionError("delegation signing key is not bound to the parent agent, principal, or controller")

        if parent_delegation_id is not None:
            parent = self._delegations.get(parent_delegation_id)
            if parent is None or not self.verify(parent_delegation_id):
                raise PermissionError("parent delegation is missing or invalid")
            if parent.child_agent_id != parent_agent_id:
                raise PermissionError("parent delegation does not authorize the delegating agent")
            if parent.principal_id != principal_id or parent.controller_id != controller_id:
                raise PermissionError("nested delegation changes principal or accountable controller")
            parent_scope = parent.scope.to_dict()
            child_scope = scope.to_dict()
            try:
                child_decision = evaluate_child_scope(parent_scope, child_scope)
                delegate_decision = evaluate_scope(
                    parent_scope,
                    action="DELEGATE",
                    context=ScopeContext(requested_delegation_depth=scope.delegation_depth),
                )
            except (TypeError, ValueError) as exc:
                raise PermissionError(f"parent delegation scope is malformed: {exc}") from exc
            if not child_decision.allowed:
                raise PermissionError(child_decision.reason)
            if not delegate_decision.allowed:
                raise PermissionError(delegate_decision.reason)

        delegation = Delegation(
            delegation_id=str(make_identifier("delegation", make_slug("dlg"))),
            parent_agent_id=parent_agent_id,
            parent_instance_id=parent_instance_id,
            child_agent_id=child_agent_id,
            principal_id=principal_id,
            controller_id=controller_id,
            scope=scope,
            expires_at=expires_at,
            revocable=revocable,
            created_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            parent_delegation_id=parent_delegation_id,
            signing_key_id=signing_key_id,
        )
        delegation.signature = self._keys.get_signing_key(signing_key_id).sign(
            canonicalize(self._signed_record(delegation))
        )
        self._delegations[delegation.delegation_id] = delegation
        return delegation

    def get(self, delegation_id: str) -> Delegation | None:
        return self._delegations.get(delegation_id)

    def verify(self, delegation_id: str) -> bool:
        return self._verify_structural(delegation_id, visited=set())

    def _verify_structural(self, delegation_id: str, *, visited: set[str]) -> bool:
        if delegation_id in visited:
            return False
        visited.add(delegation_id)
        delegation = self._delegations.get(delegation_id)
        if delegation is None or not delegation.is_active():
            return False
        if not self._signing_key_is_authorized(
            signing_key_id=delegation.signing_key_id,
            parent_agent_id=delegation.parent_agent_id,
            principal_id=delegation.principal_id,
            controller_id=delegation.controller_id,
        ):
            return False
        try:
            record = self._keys.get_record(delegation.signing_key_id)
            public_key = SigningKey.from_public_pem(delegation.signing_key_id, record.public_pem).public_key
            if not SigningKey.verify(
                public_key,
                canonicalize(self._signed_record(delegation)),
                delegation.signature,
            ):
                return False
        except Exception:
            return False

        if delegation.parent_delegation_id is None:
            return True
        parent = self._delegations.get(delegation.parent_delegation_id)
        if parent is None:
            return False
        if parent.child_agent_id != delegation.parent_agent_id:
            return False
        if parent.principal_id != delegation.principal_id or parent.controller_id != delegation.controller_id:
            return False
        if not parent.scope.contains_child_scope(delegation.scope):
            return False
        if not self._verify_structural(delegation.parent_delegation_id, visited=visited):
            return False
        return True

    def verify_action(
        self,
        delegation_id: str,
        *,
        child_agent_id: str,
        principal_id: str,
        controller_id: str,
        action: str,
        context: ScopeContext | None = None,
    ) -> bool:
        """Verify the complete delegation lineage for a proposed child action."""
        delegation = self._delegations.get(delegation_id)
        if delegation is None or not self.verify(delegation_id):
            return False
        if delegation.child_agent_id != child_agent_id:
            return False
        if delegation.principal_id != principal_id or delegation.controller_id != controller_id:
            return False
        try:
            if not evaluate_scope(delegation.scope.to_dict(), action=action, context=context).allowed:
                return False
        except (TypeError, ValueError):
            return False

        if delegation.parent_delegation_id is None:
            return True
        return self.verify_action(
            delegation.parent_delegation_id,
            child_agent_id=delegation.parent_agent_id,
            principal_id=principal_id,
            controller_id=controller_id,
            action=action,
            context=context,
        )

    def delegation_chain(self, delegation_id: str) -> list[str]:
        """Return a verified root-to-leaf delegation chain."""
        if not self.verify(delegation_id):
            raise PermissionError(f"delegation chain is invalid: {delegation_id}")
        chain: list[str] = []
        current_id: str | None = delegation_id
        seen: set[str] = set()
        while current_id is not None:
            if current_id in seen:
                raise PermissionError("delegation cycle detected")
            seen.add(current_id)
            delegation = self._delegations[current_id]
            chain.append(current_id)
            current_id = delegation.parent_delegation_id
        chain.reverse()
        return chain

    def revoke(self, delegation_id: str) -> None:
        delegation = self._delegations.get(delegation_id)
        if delegation is None:
            raise KeyError(delegation_id)
        if not delegation.revocable:
            raise PermissionError(f"delegation not revocable: {delegation_id}")
        delegation.state = "revoked"

    def all_delegations(self) -> dict[str, Delegation]:
        return dict(self._delegations)


__all__ = ["DelegationScope", "Delegation", "DelegationBroker"]
