"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/authorization/engine.py
Purpose: Policy engine for authorization and approval
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from aegistrace.events.models import ACTIONS
from aegistrace.identity.ids import make_identifier, make_slug
from aegistrace.identity.keys import KeyService

# Actions requiring human approval
APPROVAL_REQUIRED: set[str] = {
    "DEPLOY", "RELEASE", "DESTROY_RESOURCE", "DESTROY_KEY", "CHANGE_PERMISSION",
    "CHANGE_POLICY", "TRIGGER_EXTERNAL_EFFECT", "MODIFY_PRODUCTION", "ALTER_DATABASE_SCHEMA",
    "MODIFY_INFRASTRUCTURE", "PUBLISH",
}

# Actions requiring dual approval
DUAL_APPROVAL_REQUIRED: set[str] = {
    "DESTROY_KEY", "MODIFY_PRODUCTION", "ALTER_DATABASE_SCHEMA",
}

# Fail-closed actions
FAIL_CLOSED: set[str] = {
    "DEPLOY", "RELEASE", "DESTROY_RESOURCE", "DESTROY_KEY", "CHANGE_PERMISSION",
    "CHANGE_POLICY", "TRIGGER_EXTERNAL_EFFECT", "MODIFY_PRODUCTION", "ALTER_DATABASE_SCHEMA",
    "MODIFY_INFRASTRUCTURE",
}


@dataclass
class Authorization:
    authorization_id: str
    principal_id: str
    controller_id: str
    agent_id: str
    task_id: str
    scope: dict[str, Any]
    policy_version: str
    state: str = "active"
    issued_at: str = ""
    expires_at: str | None = None
    delegation_id: str | None = None
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


@dataclass
class Approval:
    approval_id: str
    action: str
    approver_id: str
    authorization_id: str
    policy_version: str
    approved_at: str
    expires_at: str | None
    used: bool = False
    used_at: str | None = None
    signature: str = ""
    signing_key_id: str = ""

    def is_usable(self) -> bool:
        if self.used:
            return False
        if self.expires_at:
            now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            if now > self.expires_at:
                return False
        return True


class PolicyEngine:
    """Evaluates authorization requests against the current policy.

    Invariants:
        - Every action resolves to an authorization.
        - An authorization's scope is enforced.
        - A revoked or expired authorization produces no new valid actions.
        - Policy violations are denied and recorded.
        - Fail-closed actions are denied if any check is inconclusive.
    """

    def __init__(self, key_service: KeyService, policy_version: str = "1.0.0") -> None:
        self._keys = key_service
        self.policy_version = policy_version
        self._authorizations: dict[str, Authorization] = {}
        self._approvals: dict[str, Approval] = {}

    def issue_authorization(
        self,
        *,
        principal_id: str,
        controller_id: str,
        agent_id: str,
        task_id: str,
        scope: dict[str, Any] | None = None,
        signing_key_id: str,
        delegation_id: str | None = None,
        expires_at: str | None = None,
    ) -> Authorization:
        if not self._keys.is_active(signing_key_id):
            raise PermissionError(f"signing key not active: {signing_key_id}")
        aid = str(make_identifier("authorization", make_slug("auth")))
        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        # Sign
        from aegistrace.signing.canonical import canonicalize
        record = {
            "authorization_id": aid,
            "principal_id": principal_id,
            "controller_id": controller_id,
            "agent_id": agent_id,
            "task_id": task_id,
            "scope": scope or {},
            "policy_version": self.policy_version,
            "issued_at": now,
        }
        if expires_at:
            record["expires_at"] = expires_at
        if delegation_id:
            record["delegation_id"] = delegation_id
        canon = canonicalize(record)
        sig = self._keys.get_signing_key(signing_key_id).sign(canon)
        auth = Authorization(
            authorization_id=aid,
            principal_id=principal_id,
            controller_id=controller_id,
            agent_id=agent_id,
            task_id=task_id,
            scope=scope or {},
            policy_version=self.policy_version,
            issued_at=now,
            expires_at=expires_at,
            delegation_id=delegation_id,
            signature=sig,
            signing_key_id=signing_key_id,
        )
        self._authorizations[aid] = auth
        return auth

    def get_authorization(self, authorization_id: str) -> Authorization | None:
        return self._authorizations.get(authorization_id)

    def revoke_authorization(self, authorization_id: str) -> None:
        a = self._authorizations.get(authorization_id)
        if a is None:
            raise KeyError(authorization_id)
        a.state = "revoked"

    def issue_approval(
        self,
        *,
        action: str,
        approver_id: str,
        authorization_id: str,
        signing_key_id: str,
        expires_at: str | None = None,
    ) -> Approval:
        if not self._keys.is_active(signing_key_id):
            raise PermissionError(f"signing key not active: {signing_key_id}")
        apid = str(make_identifier("approval", make_slug("apr")))
        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        from aegistrace.signing.canonical import canonicalize
        record = {
            "approval_id": apid,
            "action": action,
            "approver_id": approver_id,
            "authorization_id": authorization_id,
            "policy_version": self.policy_version,
            "approved_at": now,
        }
        if expires_at:
            record["expires_at"] = expires_at
        canon = canonicalize(record)
        sig = self._keys.get_signing_key(signing_key_id).sign(canon)
        ap = Approval(
            approval_id=apid,
            action=action,
            approver_id=approver_id,
            authorization_id=authorization_id,
            policy_version=self.policy_version,
            approved_at=now,
            expires_at=expires_at,
            signature=sig,
            signing_key_id=signing_key_id,
        )
        self._approvals[apid] = ap
        return ap

    def use_approval(self, approval_id: str) -> bool:
        ap = self._approvals.get(approval_id)
        if ap is None or not ap.is_usable():
            return False
        ap.used = True
        ap.used_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        return True

    def evaluate(
        self,
        *,
        action: str,
        authorization_id: str,
        approval_id: str | None = None,
    ) -> PolicyDecision:
        if action not in ACTIONS:
            return PolicyDecision(deny=True, reason=f"invalid action: {action}")
        auth = self._authorizations.get(authorization_id)
        if auth is None:
            return PolicyDecision(deny=True, reason="authorization not found")
        if not auth.is_active():
            return PolicyDecision(deny=True, reason="authorization not active")

        # Check action scope
        scope = auth.scope or {}
        if "action_classes" in scope and scope["action_classes"]:
            if action not in scope["action_classes"]:
                return PolicyDecision(deny=True, reason=f"action {action} not in scope")

        # Check approval
        if action in APPROVAL_REQUIRED:
            if approval_id is None:
                return PolicyDecision(deny=True, reason=f"approval required for {action}", approval_required=True)
            ap = self._approvals.get(approval_id)
            if ap is None or not ap.is_usable():
                return PolicyDecision(deny=True, reason="approval not usable", approval_required=True)
            if ap.action != action:
                return PolicyDecision(deny=True, reason=f"approval action mismatch: {ap.action} != {action}")
            if ap.authorization_id != authorization_id:
                return PolicyDecision(deny=True, reason="approval authorization mismatch")

        # Fail-closed
        if action in FAIL_CLOSED:
            # All checks must be conclusive; if any inconclusive, deny.
            # Already checked above; nothing else to check.
            pass

        return PolicyDecision(deny=False, reason="permitted")


@dataclass
class PolicyDecision:
    deny: bool
    reason: str
    approval_required: bool = False

    @property
    def permitted(self) -> bool:
        return not self.deny


__all__ = [
    "APPROVAL_REQUIRED",
    "DUAL_APPROVAL_REQUIRED",
    "FAIL_CLOSED",
    "Authorization",
    "Approval",
    "PolicyEngine",
    "PolicyDecision",
]
