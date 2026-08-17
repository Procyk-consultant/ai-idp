"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/authorization/engine.py
Purpose: Policy engine for authorization and approval
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from typing import Any

from aegistrace.authorization.scope import ScopeContext, evaluate_scope
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


@dataclass(frozen=True)
class PolicyDecision:
    deny: bool
    reason: str
    approval_required: bool = False
    satisfied_approval_ids: tuple[str, ...] = ()

    @property
    def permitted(self) -> bool:
        return not self.deny


class PolicyEngine:
    """Evaluate signed authorizations and approvals against policy.

    Authority records returned to callers are snapshots. Canonical authorization
    and approval state can only be changed through service operations.
    """

    def __init__(self, key_service: KeyService, policy_version: str = "1.0.0") -> None:
        self._keys = key_service
        self.policy_version = policy_version
        self._authorizations: dict[str, Authorization] = {}
        self._approvals: dict[str, Approval] = {}
        self._lock = RLock()

    def _key_is_bound_to(self, signing_key_id: str, allowed_entity_ids: set[str]) -> bool:
        try:
            record = self._keys.get_record(signing_key_id)
        except KeyError:
            return False
        return record.bound_entity_id in allowed_entity_ids

    def _authorization_record(self, authorization: Authorization) -> dict[str, Any]:
        record: dict[str, Any] = {
            "authorization_id": authorization.authorization_id,
            "principal_id": authorization.principal_id,
            "controller_id": authorization.controller_id,
            "agent_id": authorization.agent_id,
            "task_id": authorization.task_id,
            "scope": authorization.scope,
            "policy_version": authorization.policy_version,
            "issued_at": authorization.issued_at,
        }
        if authorization.expires_at:
            record["expires_at"] = authorization.expires_at
        if authorization.delegation_id:
            record["delegation_id"] = authorization.delegation_id
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
        with self._lock:
            authorization = self._authorizations.get(authorization_id)
            if authorization is None or not authorization.is_active():
                return False
            if authorization.policy_version != self.policy_version:
                return False
            if not self._key_is_bound_to(
                authorization.signing_key_id,
                {authorization.principal_id, authorization.controller_id},
            ):
                return False
            try:
                record = self._keys.get_record(authorization.signing_key_id)
                public_key = SigningKey.from_public_pem(
                    authorization.signing_key_id,
                    record.public_pem,
                ).public_key
                return SigningKey.verify(
                    public_key,
                    canonicalize(self._authorization_record(authorization)),
                    authorization.signature,
                )
            except Exception:
                return False

    def verify_approval(self, approval_id: str) -> bool:
        with self._lock:
            approval = self._approvals.get(approval_id)
            if approval is None or not approval.is_usable():
                return False
            if approval.policy_version != self.policy_version:
                return False
            authorization = self._authorizations.get(approval.authorization_id)
            if authorization is None or not self.verify_authorization(authorization.authorization_id):
                return False
            if not self._key_is_bound_to(approval.signing_key_id, {approval.approver_id}):
                return False
            try:
                record = self._keys.get_record(approval.signing_key_id)
                public_key = SigningKey.from_public_pem(
                    approval.signing_key_id,
                    record.public_pem,
                ).public_key
                return SigningKey.verify(
                    public_key,
                    canonicalize(self._approval_record(approval)),
                    approval.signature,
                )
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

        authorization = Authorization(
            authorization_id=str(make_identifier("authorization", make_slug("auth"))),
            principal_id=principal_id,
            controller_id=controller_id,
            agent_id=agent_id,
            task_id=task_id,
            scope=copy.deepcopy(scope or {}),
            policy_version=self.policy_version,
            issued_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            expires_at=expires_at,
            delegation_id=delegation_id,
            signing_key_id=signing_key_id,
        )
        authorization.signature = self._keys.get_signing_key(signing_key_id).sign(
            canonicalize(self._authorization_record(authorization))
        )
        with self._lock:
            self._authorizations[authorization.authorization_id] = copy.deepcopy(authorization)
        return copy.deepcopy(authorization)

    def get_authorization(self, authorization_id: str) -> Authorization | None:
        with self._lock:
            authorization = self._authorizations.get(authorization_id)
            return copy.deepcopy(authorization) if authorization is not None else None

    def get_approval(self, approval_id: str) -> Approval | None:
        with self._lock:
            approval = self._approvals.get(approval_id)
            return copy.deepcopy(approval) if approval is not None else None

    def revoke_authorization(self, authorization_id: str) -> None:
        with self._lock:
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
        with self._lock:
            authorization = self._authorizations.get(authorization_id)
            if authorization is None:
                raise KeyError(f"authorization not found: {authorization_id}")
        if not self.verify_authorization(authorization_id):
            raise PermissionError("authorization is not valid")
        if not self._keys.is_active(signing_key_id):
            raise PermissionError(f"signing key not active: {signing_key_id}")
        if not self._key_is_bound_to(signing_key_id, {approver_id}):
            raise PermissionError("approval signing key is not bound to the approver")

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
        with self._lock:
            self._approvals[approval.approval_id] = copy.deepcopy(approval)
        return copy.deepcopy(approval)

    def required_approval_count(self, action: str) -> int:
        if action in DUAL_APPROVAL_REQUIRED:
            return 2
        if action in APPROVAL_REQUIRED:
            return 1
        return 0

    def evaluate(
        self,
        *,
        action: str,
        authorization_id: str,
        approval_id: str | None = None,
        approval_ids: list[str] | tuple[str, ...] | None = None,
        scope_context: ScopeContext | None = None,
    ) -> PolicyDecision:
        if action not in ACTIONS:
            return PolicyDecision(deny=True, reason=f"invalid action: {action}")

        with self._lock:
            authorization = self._authorizations.get(authorization_id)
            if authorization is None:
                return PolicyDecision(deny=True, reason="authorization not found")
            authorization_snapshot = copy.deepcopy(authorization)
        if not self.verify_authorization(authorization_id):
            return PolicyDecision(
                deny=True,
                reason="authorization invalid, inactive, stale, or signature verification failed",
            )

        try:
            scope_decision = evaluate_scope(
                authorization_snapshot.scope,
                action=action,
                context=scope_context,
            )
        except (TypeError, ValueError) as exc:
            return PolicyDecision(deny=True, reason=f"authorization scope is malformed: {exc}")
        if not scope_decision.allowed:
            return PolicyDecision(deny=True, reason=scope_decision.reason)

        candidate_ids: list[str] = []
        for candidate_id in approval_ids or ():
            if candidate_id not in candidate_ids:
                candidate_ids.append(candidate_id)
        if approval_id is not None and approval_id not in candidate_ids:
            candidate_ids.append(approval_id)

        required_count = self.required_approval_count(action)
        if required_count == 0:
            return PolicyDecision(deny=False, reason="permitted")
        if not candidate_ids:
            return PolicyDecision(
                deny=True,
                reason=f"approval required for {action}",
                approval_required=True,
            )

        valid_approvals: list[Approval] = []
        for candidate_id in candidate_ids:
            with self._lock:
                approval = self._approvals.get(candidate_id)
                approval_snapshot = copy.deepcopy(approval) if approval is not None else None
            if approval_snapshot is None or not self.verify_approval(candidate_id):
                continue
            if approval_snapshot.action != action or approval_snapshot.authorization_id != authorization_id:
                continue
            valid_approvals.append(approval_snapshot)

        distinct: dict[str, Approval] = {}
        for approval in valid_approvals:
            distinct.setdefault(approval.approver_id, approval)
        selected = list(distinct.values())[:required_count]
        if len(selected) < required_count:
            requirement = "two distinct approvals" if required_count == 2 else "a valid approval"
            return PolicyDecision(
                deny=True,
                reason=f"{requirement} required for {action}",
                approval_required=True,
            )

        return PolicyDecision(
            deny=False,
            reason="permitted",
            satisfied_approval_ids=tuple(approval.approval_id for approval in selected),
        )

    def consume_approvals(self, approval_ids: list[str] | tuple[str, ...]) -> bool:
        unique_ids = tuple(dict.fromkeys(approval_ids))
        if not unique_ids:
            return True
        with self._lock:
            if not all(self.verify_approval(approval_id) for approval_id in unique_ids):
                return False
            used_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            for approval_id in unique_ids:
                approval = self._approvals[approval_id]
                approval.used = True
                approval.used_at = used_at
            return True

    def use_approval(self, approval_id: str) -> bool:
        return self.consume_approvals((approval_id,))


__all__ = [
    "APPROVAL_REQUIRED",
    "DUAL_APPROVAL_REQUIRED",
    "FAIL_CLOSED",
    "Authorization",
    "Approval",
    "PolicyEngine",
    "PolicyDecision",
]
