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

from datetime import UTC, datetime
from typing import Any

from aegistrace.authorization.scope import ScopeContext
from aegistrace.events.models import (
    ACTIONS,
    GOVERNANCE_MODES,
    SCHEMA_VERSION,
    VISIBILITY_TIERS,
    Actor,
    Event,
    ExecutionContext,
)
from aegistrace.identity.ids import VALID_JURISDICTIONS, make_event_id, require_identifier_type
from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger
from aegistrace.signing.canonical import canonicalize_for_hash, canonicalize_for_signature
from aegistrace.signing.ed25519 import sha256_hex


class EventCollector:
    """Build, sign, and append cryptographic evidence events.

    This is the low-level evidence boundary. It validates event structure,
    identifier classes, signing-key binding, and chain integrity. It does not
    by itself decide whether an action is authorized; governed execution uses
    ``GovernedEventService`` before calling this collector.
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
                f"signing key {signing_key_id} (bound to {key_record.bound_entity_id}) "
                f"is not bound to actor.agent_id={actor.agent_id} or "
                f"actor.controller_id={actor.controller_id}"
            )

        normalized_approval_ids: list[str] = []
        for candidate_id in approval_ids or ():
            if candidate_id not in normalized_approval_ids:
                normalized_approval_ids.append(candidate_id)
        if approval_id is not None and approval_id not in normalized_approval_ids:
            normalized_approval_ids.insert(0, approval_id)
        primary_approval_id = approval_id or (normalized_approval_ids[0] if normalized_approval_ids else None)

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
        if delegation_id is not None:
            event_dict["delegation_id"] = delegation_id
        if authorization_id is not None:
            event_dict["authorization_id"] = authorization_id
        if primary_approval_id is not None:
            event_dict["approval_id"] = primary_approval_id
        if normalized_approval_ids:
            event_dict["approval_ids"] = normalized_approval_ids
        if delegation_chain:
            event_dict["delegation_chain"] = list(delegation_chain)
        if scope_context is not None:
            scope_dict = scope_context.to_dict()
            if scope_dict:
                event_dict["scope_context"] = scope_dict
        if governance_mode is not None:
            event_dict["governance_mode"] = governance_mode
        if decision_reason is not None:
            event_dict["decision_reason"] = decision_reason
        if resource_id is not None:
            event_dict["resource_id"] = resource_id
        if before_digest is not None:
            event_dict["before_digest"] = before_digest
        if after_digest is not None:
            event_dict["after_digest"] = after_digest

        event_dict["event_hash"] = sha256_hex(canonicalize_for_hash(event_dict))
        signing_key = self._keys.get_signing_key(signing_key_id)
        event_dict["signature"] = signing_key.sign(canonicalize_for_signature(event_dict))

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
        for candidate_id in approval_ids or ():
            require_identifier_type(candidate_id, "approval")
        for candidate_id in delegation_chain or ():
            require_identifier_type(candidate_id, "delegation")


__all__ = ["EventCollector"]
