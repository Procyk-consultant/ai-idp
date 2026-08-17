"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/disclosure/public.py
Purpose: Strict public-tier event projection
Classification: service
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from typing import Any, Iterable

from aegistrace.events.models import Event

PUBLIC_EVENT_PROOF_FIELDS = frozenset(
    {
        "projection_schema",
        "schema_version",
        "event_id",
        "timestamp",
        "jurisdiction_id",
        "visibility",
        "policy_version",
        "previous_event_hash",
        "event_hash",
        "signature",
        "signing_key_id",
    }
)

SENSITIVE_EVENT_FIELDS = frozenset(
    {
        "actor",
        "execution_context",
        "task_id",
        "action",
        "delegation_id",
        "delegation_chain",
        "authorization_id",
        "approval_id",
        "approval_ids",
        "scope_context",
        "governance_mode",
        "decision_reason",
        "resource_id",
        "before_digest",
        "after_digest",
    }
)


class PublicProjectionError(PermissionError):
    """Raised when a non-public record is requested through the public projector."""


class PublicEventProjector:
    """Produce a non-sensitive integrity proof for PUBLIC events only.

    The projection is deliberately allow-list based. New Event fields do not
    become public automatically; they remain private until this projector is
    deliberately amended and reviewed.
    """

    projection_schema = "aegistrace.public_event_proof.v1"

    def project(self, event: Event) -> dict[str, Any]:
        if event.visibility != "PUBLIC":
            raise PublicProjectionError("event is not PUBLIC")
        projection: dict[str, Any] = {
            "projection_schema": self.projection_schema,
            "schema_version": event.schema_version,
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "jurisdiction_id": event.jurisdiction_id,
            "visibility": event.visibility,
            "policy_version": event.policy_version,
            "previous_event_hash": event.previous_event_hash,
            "event_hash": event.event_hash,
            "signature": event.signature,
            "signing_key_id": event.signing_key_id,
        }
        unexpected = set(projection) - PUBLIC_EVENT_PROOF_FIELDS
        if unexpected:
            raise RuntimeError(f"public projection contains unreviewed fields: {sorted(unexpected)}")
        return projection

    def project_many(self, events: Iterable[Event]) -> list[dict[str, Any]]:
        return [self.project(event) for event in events if event.visibility == "PUBLIC"]


__all__ = [
    "PUBLIC_EVENT_PROOF_FIELDS",
    "SENSITIVE_EVENT_FIELDS",
    "PublicProjectionError",
    "PublicEventProjector",
]
