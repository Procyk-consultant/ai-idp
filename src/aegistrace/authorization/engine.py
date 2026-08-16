"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/authorization/engine.py
Purpose: Policy engine for authorization and approval
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-16
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from aegistrace.events.models import ACTIONS
from aegistrace.identity.ids import make_identifier, make_slug
from aegistrace.identity.keys import KeyService
from aegistrace.signing.canonical import canonicalize
from aegistrace.signing.ed25519 import SigningKey

APPROVAL_REQUIRED: set[str] = {
    "DEPLOY", "RELEASE", "DESTROY_RESOURCE", "DESTROY_KEY", "CHANGE_PERMISSION",
    "CHANGE_POLICY", "TRIGGER_EXTERNAL_EFFECT", "MODIFY_PRODUCTION", "ALTER_DATABASE_SCHEMA",
    "MODIFY_INFRASTRUCTURE", "PUBLISH", "DELETE",
}

DUAL_APPROVAL_REQUIRED: set[str] = {
    "DESTROY_KEY", "MODIFY_PRODUCTION", "ALTER_DATABASE_SCHEMA",
}

FAIL_CLOSED: set[str] = {
    "DEPLOY", "RELEASE", "DESTROY_RESOURCE", "DESTROY_KEY", "CHANGE_PERMISSION",
    "CHANGE_POLICY", "TRIGGER_EXTERNAL_EFFECT", "MODIFY_PRODUCTION", "ALTER_DATABASE_SCHEMA",
    "MODIFY_INFRASTRUCTURE", "PUBLISH", "DELETE",
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
    """Evaluate signed authorizations and approvals against policy.

    The engine fails closed for invalid signatures, stale policy versions,
    inactive records, scope violations, missing approvals, and inconclusive
    high-risk decisions.
    """

    def __init__(self, key_service: KeyService, policy_version: str = "1.0.0") -> None:
        self._keys = key_service
        self.policy_version = policy_version
        self._authorizations: dict[str, Authorization] = {}
        self._approvals: dict[str, Approval] = {}

    def _key_is_bound_to(self, signing_key_id: str, allowed_entity_ids: set[str]) -> bool:
        try:
            rec = self._keys.get_record(signing_key_id)
        except KeyError:
            return False
        return rec.bound_entity_id in allowed_entity_ids

    def _authorization_record(self, auth: Authorization) -> dict[str, Any]:
        record: dict[str, Any] = {
            "authorization_id": auth.authorization_id,
            "principal_id": auth.principal_id,
            "controller_id": auth.controller_id,
            "agent_id": auth.agent_id,
            "task_id": auth.task_id,
            "scope": auth.scope,
            "policy_version": auth.policy_version,
            "issued_at": auth.issued_at,
        }
        if auth.expires_at:
            record["expires_at"] = auth.expires_at
        if auth.delegation_id:
            record["delegation_id"] = auth.delegation_id
        return record

    def _approval_record(self, approval: Approval) -> dict[str, Any]:
        record: dict[str, Any] = {
            "approval_id": approval.approval_id,
            "action": approval.action,
            "approver_id": approval.approver_id,
            "authorization_id": approval.authorization_id,
            "policy_version": approval.policy_version,
            "approved_at": approval.approved_at,
        }
        if approval.expires_at:
            record["expires_at"] = approval.expires_at
        return record

    def verify_authorization(self, authorization_id: str) -> bool:
        auth = self._authorizations.get(authorization_id)
        if auth is None or not auth.is_active():
            return False
        if auth.policy_version != self.policy_version:
            return False
        if not self._key_is_bound_to(auth.signing_key_id, {auth.principal_id, auth.controller_id}):
            return False
        try:
            rec = self._keys.get_record(auth.signing_key_id)
            public_key = SigningKey.from_public_pem(auth.signing_key_id, rec.public_pem).public_key
            return SigningKey.verify(public_key, canonicalize(self._authorization_record(auth)), auth.signature)
        except Exception:
            return False

    def verify_approval(self, approval_id: str) -> bool:
        approval = self._approvals.get(approval_id)
        if approval is None or not approval.is_usable():
            return False
        if approval.policy_version != self.policy_version:
            return False
        auth = self._authorizations.get(approval.authorization_id)
        if auth is None:
            return False
        if not self._key_is_bound_to(approval.signing_key_id, {approval.approver_id, auth.controller_id}):
            return False
        try:
            rec = self._keys.get_record(approval.signing_key_id)
            public_key = SigningKey.from_public_pem(approval.signing_key_id, rec.public_pem).public_key
            return SigningKey.verify(public_key, canonicalize(self._approval_record(approval)), approval.signature)
        except Exception:
            return False

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
        if not self._key_is_bound_to(signing_key_id, {principal_id, controller_id}):
            raise PermissionError("authorization signing key is not bound to the principal or accountable controller")

        aid = str(make_identifier("authorization", make_slug("auth")))
        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
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
            signing_key_id=signing_key_id,
        )
        auth.signature = self._keys.get_signing_key(signing_key_id).sign(
            canonicalize(self._authorization_record(auth))
        )
        self._authorizations[aid] = auth
        return auth

    def get_authorization(self, authorization_id: str) -> Authorization | None:
        return self._authorizations.get(authorization_id)

    def revoke_authorization(self, authorization_id: str) -> None:
        authorization = self._authorizations.get(authorization_id)
        if authorization is None:
            raise KeyError(authorization_id)
        authorization.state = "revoked"

    def issue_approval(
        self,
        *,
        action: str,
        approver_id: str,
        authorization_id: str,
        signing_key_id: str,
        expires_at: str | None = None,
    ) -> Approval:
        if action not in ACTIONS:
            raise ValueError(f"invalid action: {action}")
        auth = self._authorizations.get(authorization_id)
        if auth is None:
            raise KeyError(f"authorization not found: {authorization_id}")
        if not self.verify_authorization(authorization_id):
            raise PermissionError("authorization is not valid")
        if not self._keys.is_active(signing_key_id):
            raise PermissionError(f"signing key not active: {signing_key_id}")
        if not self._key_is_bound_to(signing_key_id, {approver_id, auth.controller_id}):
            raise PermissionError("approval signing key is not bound to the approver or accountable controller")

        approval = Approval(
            approval_id=str(make_identifier("approval", make_slug("apr"))),
            action=action,
            approver_id=approver_id,
            authorization_id=authorization_id,
            policy_version=self.policy_version,
            approved_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            expires_at=expires_at,
            signing_key_id=signing_key_id,
        )
        approval.signature = self._keys.get_signing_key(signing_key_id).sign(
            canonicalize(self._approval_record(approval))
        )
        self._approvals[approval.approval_id] = approval
        return approval

    def use_approval(self, approval_id: str) -> bool:
        if not self.verify_approval(approval_id):
            return False
        approval = self._approvals[approval_id]
        approval.used = True
        approval.used_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        return True

    def evaluate(
        self,
        *,
        action: str,
        authorization_id: str,
        approval_id: str | None = None,
        approval_ids: list[str] | None = None,
    ) -> PolicyDecision:
        if action not in ACTIONS:
            return PolicyDecision(deny=True, reason=f"invalid action: {action}")

        auth = self._authorizations.get(authorization_id)
        if auth is None:
            return PolicyDecision(deny=True, reason="authorization not found")
        if not self.verify_authorization(authorization_id):
            return PolicyDecision(deny=True, reason="authorization invalid, inactive, stale, or signature verification failed")

        scope = auth.scope or {}
        if scope.get("action_classes") and action not in scope["action_classes"]:
            return PolicyDecision(deny=True, reason=f"action {action} not in scope")

        candidate_ids = list(approval_ids or [])
        if approval_id is not None and approval_id not in candidate_ids:
            candidate_ids.append(approval_id)

        if action in APPROVAL_REQUIRED:
            if not candidate_ids:
                return PolicyDecision(deny=True, reason=f"approval required for {action}", approval_required=True)

            valid_approvals: list[Approval] = []
            for candidate_id in candidate_ids:
                approval = self._approvals.get(candidate_id)
                if approval is None or not self.verify_approval(candidate_id):
                    continue
                if approval.action != action or approval.authorization_id != authorization_id:
                    continue
                valid_approvals.append(approval)

            required_count = 2 if action in DUAL_APPROVAL_REQUIRED else 1
            distinct_approvers = {approval.approver_id for approval in valid_approvals}
            if len(valid_approvals) < required_count or len(distinct_approvers) < required_count:
                requirement = "two distinct approvals" if required_count == 2 else "a valid approval"
                return PolicyDecision(
                    deny=True,
                    reason=f"{requirement} required for {action}",
                    approval_required=True,
                )

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
