"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/identity/lifecycle.py
Purpose: Lifecycle operations for AI-IDP entities
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import UTC, datetime

from aegistrace.identity.ids import require_identifier_type


@dataclass
class EntityRecord:
    """Generic registry record for an AI-IDP entity."""

    entity_id: str
    entity_type: str
    state: str = "active"
    attributes: dict[str, object] = field(default_factory=dict)
    created_at: str = ""
    suspended_at: str | None = None
    revoked_at: str | None = None
    terminated_at: str | None = None
    archived_at: str | None = None
    state_history: list[dict[str, str]] = field(default_factory=list)

    def is_active(self) -> bool:
        return self.state == "active"

    def is_resolvable(self) -> bool:
        return True

    def transition(self, new_state: str, reason: str = "") -> None:
        valid = {
            "proposed": {"active"},
            "active": {"suspended", "revoked", "terminated"},
            "suspended": {"active", "revoked", "terminated"},
            "revoked": set(),
            "terminated": {"archived"},
            "archived": set(),
        }
        allowed = valid.get(self.state, set())
        if new_state not in allowed:
            raise ValueError(f"invalid transition {self.state} -> {new_state}")
        timestamp = _now()
        self.state_history.append(
            {"from": self.state, "to": new_state, "at": timestamp, "reason": reason}
        )
        self.state = new_state
        if new_state == "suspended":
            self.suspended_at = timestamp
        elif new_state == "revoked":
            self.revoked_at = timestamp
        elif new_state == "terminated":
            self.terminated_at = timestamp
        elif new_state == "archived":
            self.archived_at = timestamp


class Registry:
    """In-memory reference registry with isolated record snapshots.

    Identifiers are permanently unique within the registry. Public read methods
    return deep copies so callers cannot silently rewrite registered identity or
    lifecycle state by retaining object aliases.
    """

    def __init__(self) -> None:
        self._entities: dict[str, EntityRecord] = {}

    def _resolve_internal(self, entity_id: str) -> EntityRecord:
        record = self._entities.get(entity_id)
        if record is None:
            raise KeyError(f"unresolvable entity: {entity_id}")
        return record

    def register(
        self,
        entity_id: str,
        entity_type: str,
        attributes: dict[str, object] | None = None,
    ) -> EntityRecord:
        require_identifier_type(entity_id, entity_type)
        if entity_id in self._entities:
            raise ValueError(f"entity_id already exists: {entity_id}")
        record = EntityRecord(
            entity_id=entity_id,
            entity_type=entity_type,
            state="active",
            attributes=copy.deepcopy(attributes or {}),
            created_at=_now(),
        )
        self._entities[entity_id] = record
        return copy.deepcopy(record)

    def get(self, entity_id: str) -> EntityRecord | None:
        record = self._entities.get(entity_id)
        return copy.deepcopy(record) if record is not None else None

    def resolve(self, entity_id: str) -> EntityRecord:
        return copy.deepcopy(self._resolve_internal(entity_id))

    def update(self, entity_id: str, attributes: dict[str, object]) -> EntityRecord:
        record = self._resolve_internal(entity_id)
        if not record.is_active():
            raise PermissionError(
                f"cannot update non-active entity: {entity_id} (state={record.state})"
            )
        record.attributes.update(copy.deepcopy(attributes))
        return copy.deepcopy(record)

    def suspend(self, entity_id: str, reason: str = "") -> EntityRecord:
        record = self._resolve_internal(entity_id)
        record.transition("suspended", reason)
        return copy.deepcopy(record)

    def revoke(self, entity_id: str, reason: str = "") -> EntityRecord:
        record = self._resolve_internal(entity_id)
        record.transition("revoked", reason)
        return copy.deepcopy(record)

    def terminate(self, entity_id: str, reason: str = "") -> EntityRecord:
        record = self._resolve_internal(entity_id)
        record.transition("terminated", reason)
        return copy.deepcopy(record)

    def archive(self, entity_id: str, reason: str = "") -> EntityRecord:
        record = self._resolve_internal(entity_id)
        record.transition("archived", reason)
        return copy.deepcopy(record)

    def reactivate(self, entity_id: str) -> EntityRecord:
        record = self._resolve_internal(entity_id)
        record.transition("active")
        return copy.deepcopy(record)

    def all_entities(self) -> dict[str, EntityRecord]:
        return copy.deepcopy(self._entities)


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = ["EntityRecord", "Registry"]
