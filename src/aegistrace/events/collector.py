"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/events/collector.py
Purpose: Event collector that builds, signs, and appends evidence records
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from aegistrace.authorization.scope import ScopeContext
from aegistrace.events.models import (
    ACTIONS, GOVERNANCE_MODES, SCHEMA_VERSION, VISIBILITY_TIERS, Actor, Event, ExecutionContext,
)
from aegistrace.identity.ids import VALID_JURISDICTIONS, make_event_id, require_identifier_type
from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger
from aegistrace.signing.canonical import canonicalize_for_hash, canonicalize_for_signature
from aegistrace.signing.ed25519 import sha256_hex

_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


class EventCollector:
    """Build, sign, and append cryptographic evidence events.

    This low-level evidence boundary validates structure, identifiers, digests,
    key binding, and chain integrity. Operational authorization is enforced by
    ``GovernedEventService`` before it invokes this collector.
    """

    def __init__(self, ledger: AppendOnlyLedger, key_service: KeyService) -> None:
        self._ledger = ledger
        self._keys = key_service

    def record(
        self,
        *,
        actor: Actor,
        execution_context: ExecutionContext,
        task_id: str,
        action: str,
        visibility: str,
        signing_key_id: str,
        jurisdiction_id: str = "ca",
        delegation_id: str | None = None,
        authorization_id: str | None = None,
        approval_id: str | None = None,
        approval_ids: list[str] | tuple[str, ...] | None = None,
        delegation_chain: list[str] | tuple[str, ...] | None = None,
        scope_context: ScopeContext | None = None,
        action_intent_digest: str | None = None,
        governance_mode: str | None = None,
        decision_reason: str | None = None,
        resource_id: str | None = None,
        before_digest: str | None = None,
        after_digest: str | None = None,
        policy_version: str = "1.0.0",
    ) -> Event:
        if action not in ACTIONS:
            raise ValueError(f"invalid action: {action!r}")
        if visibility not in VISIBILITY_TIERS:
            raise ValueError(f"invalid visibility: {visibility!r}")
        if governance_mode is not None and governance_mode not in GOVERNANCE_MODES:
            raise ValueError(f"invalid governance_mode: {governance_mode!r}")
        if jurisdiction_id not in VALID_JURISDICTIONS:
            raise ValueError(f"invalid jurisdiction_id: {jurisdiction_id!r}")
        if not policy_version:
            raise ValueError("policy_version cannot be empty")
        for field_name, digest in (
            ("action_intent_digest", action_intent_digest),
            ("before_digest", before_digest),
            ("after_digest", after_digest),
        ):
            if digest is not None and not _DIGEST_PATTERN.fullmatch(digest):
                raise ValueError(f"{field_name} must be a sha256 digest")

        self._validate_identifiers(
            actor=actor,
            execution_context=execution_context,
            task_id=task_id,
            signing_key_id=signing_key_id,
            delegation_id=delegation_id,
            authorization_id=authorization_id,
            approval_id=approval_id,
            approval_ids=approval_ids,
            delegation_chain=delegation_chain,
        )
        if not self._keys.is_active(signing_key_id):
            raise PermissionError(f"signing key not active: {signing_key_id}")
        key_record = self._keys.get_record(signing_key_id)
        if key_record.bound_entity_id not in {actor.agent_id, actor.controller_id}:
            raise PermissionError(
                f"signing key {signing_key_id} is not bound to actor agent or controller"
            )

        normalized_approvals: list[str] = []
        for candidate in approval_ids or ():
            if candidate not in normalized_approvals:
                normalized_approvals.append(candidate)
        if approval_id is not None and approval_id not in normalized_approvals:
            normalized_approvals.insert(0, approval_id)
        primary_approval = approval_id or (normalized_approvals[0] if normalized_approvals else None)

        event_dict: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "event_id": make_event_id(),
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "jurisdiction_id": jurisdiction_id,
            "actor": actor.to_dict(),
            "execution_context": execution_context.to_dict(),
            "task_id": task_id,
            "action": action,
            "visibility": visibility,
            "previous_event_hash": self._ledger.last_event_hash(),
            "signing_key_id": signing_key_id,
            "policy_version": policy_version,
        }
        optional = {
            "delegation_id": delegation_id,
            "authorization_id": authorization_id,
            "approval_id": primary_approval,
            "action_intent_digest": action_intent_digest,
            "governance_mode": governance_mode,
            "decision_reason": decision_reason,
            "resource_id": resource_id,
            "before_digest": before_digest,
            "after_digest": after_digest,
        }
        for key, value in optional.items():
            if value is not None:
                event_dict[key] = value
        if normalized_approvals:
            event_dict["approval_ids"] = normalized_approvals
        if delegation_chain:
            event_dict["delegation_chain"] = list(delegation_chain)
        if scope_context is not None:
            scope_dict = scope_context.to_dict()
            if scope_dict:
                event_dict["scope_context"] = scope_dict

        event_dict["event_hash"] = sha256_hex(canonicalize_for_hash(event_dict))
        event_dict["signature"] = self._keys.get_signing_key(signing_key_id).sign(
            canonicalize_for_signature(event_dict)
        )
        event = Event.from_dict(event_dict)
        self._ledger.append(event)
        return event

    def _validate_identifiers(
        self,
        *,
        actor: Actor,
        execution_context: ExecutionContext,
        task_id: str,
        signing_key_id: str,
        delegation_id: str | None,
        authorization_id: str | None,
        approval_id: str | None,
        approval_ids: list[str] | tuple[str, ...] | None,
        delegation_chain: list[str] | tuple[str, ...] | None,
    ) -> None:
        require_identifier_type(actor.controller_id, "controller")
        require_identifier_type(actor.principal_id, "principal")
        require_identifier_type(actor.agent_id, "agent")
        require_identifier_type(actor.agent_instance_id, "agent-instance")
        require_identifier_type(execution_context.provider_id, "provider")
        require_identifier_type(execution_context.model_id, "model")
        require_identifier_type(execution_context.model_version_id, {"model", "model-version"})
        require_identifier_type(execution_context.deployment_id, "deployment")
        require_identifier_type(task_id, "task")
        require_identifier_type(signing_key_id, "key")
        if delegation_id is not None:
            require_identifier_type(delegation_id, "delegation")
        if authorization_id is not None:
            require_identifier_type(authorization_id, "authorization")
        if approval_id is not None:
            require_identifier_type(approval_id, "approval")
        for candidate in approval_ids or ():
            require_identifier_type(candidate, "approval")
        for candidate in delegation_chain or ():
            require_identifier_type(candidate, "delegation")


__all__ = ["EventCollector"]
