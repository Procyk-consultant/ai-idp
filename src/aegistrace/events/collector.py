"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/events/collector.py
Purpose: Event collector that builds, signs, and appends events to the ledger
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from aegistrace.events.models import ACTIONS, SCHEMA_VERSION, VISIBILITY_TIERS, Actor, Event, ExecutionContext
from aegistrace.identity.ids import make_event_id
from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger
from aegistrace.signing.canonical import canonicalize_for_hash, canonicalize_for_signature
from aegistrace.signing.ed25519 import sha256_hex


class EventCollector:
    """Builds, signs, and appends events to the ledger.

    Invariants enforced:
        - Every event has a unique event_id.
        - Every event is hash-chained to the previous event.
        - Every event is signed by an active key bound to the actor's agent.
        - Action and visibility are canonical.
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
        resource_id: str | None = None,
        before_digest: str | None = None,
        after_digest: str | None = None,
        policy_version: str = "1.0.0",
    ) -> Event:
        if action not in ACTIONS:
            raise ValueError(f"invalid action: {action!r}")
        if visibility not in VISIBILITY_TIERS:
            raise ValueError(f"invalid visibility: {visibility!r}")
        if not self._keys.is_active(signing_key_id):
            raise PermissionError(f"signing key not active: {signing_key_id}")

        # Verify key is bound to this actor's agent
        rec = self._keys.get_record(signing_key_id)
        if rec.bound_entity_id != actor.agent_id:
            # Also allow keys bound to the controller (controller-level signing)
            if rec.bound_entity_id != actor.controller_id:
                raise PermissionError(
                    f"signing key {signing_key_id} (bound to {rec.bound_entity_id}) "
                    f"is not bound to actor.agent_id={actor.agent_id} or "
                    f"actor.controller_id={actor.controller_id}"
                )

        prev_hash = self._ledger.last_event_hash()

        event_id = make_event_id()
        timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build the event dict without event_hash or signature
        event_dict: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "event_id": event_id,
            "timestamp": timestamp,
            "jurisdiction_id": jurisdiction_id,
            "actor": actor.to_dict(),
            "execution_context": execution_context.to_dict(),
            "task_id": task_id,
            "action": action,
            "visibility": visibility,
            "previous_event_hash": prev_hash,
            "signing_key_id": signing_key_id,
            "policy_version": policy_version,
        }
        if delegation_id is not None:
            event_dict["delegation_id"] = delegation_id
        if authorization_id is not None:
            event_dict["authorization_id"] = authorization_id
        if approval_id is not None:
            event_dict["approval_id"] = approval_id
        if resource_id is not None:
            event_dict["resource_id"] = resource_id
        if before_digest is not None:
            event_dict["before_digest"] = before_digest
        if after_digest is not None:
            event_dict["after_digest"] = after_digest

        # Compute event_hash
        canon_for_hash = canonicalize_for_hash(event_dict)
        event_hash = sha256_hex(canon_for_hash)
        event_dict["event_hash"] = event_hash

        # Sign
        sk = self._keys.get_signing_key(signing_key_id)
        canon_for_sig = canonicalize_for_signature(event_dict)
        signature = sk.sign(canon_for_sig)
        event_dict["signature"] = signature

        # Build typed Event and append to ledger
        event = Event.from_dict(event_dict)
        self._ledger.append(event)
        return event


__all__ = ["EventCollector"]
