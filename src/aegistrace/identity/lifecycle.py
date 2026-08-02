"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/identity/lifecycle.py
Purpose: Lifecycle operations for AI Actor entities
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class EntityRecord:
    """Generic registry record for any AI-IDP entity.

    Invariants:
        - entity_id is permanently unique.
        - state transitions are recorded as events.
        - historical states are preserved.
    """

    entity_id: str
    entity_type: str
    state: str = "active"  # proposed | active | suspended | revoked | terminated | archived
    attributes: dict[str, object] = field(default_factory=dict)
    created_at: str = ""
    suspended_at: str | None = None
    revoked_at: str | None = None
    terminated_at: str | None = None
    archived_at: str | None = None
    state_history: list = field(default_factory=list)

    def is_active(self) -> bool:
        return self.state == "active"

    def is_resolvable(self) -> bool:
        """Permanent identifiers remain resolvable after termination/revocation."""
        return True

    def transition(self, new_state: str, reason: str = "") -> None:
        valid = {
            "proposed": {"active"},
            "active": {"suspended", "revoked", "terminated"},
            "suspended": {"active", "revoked", "terminated"},
            "revoked": set(),  # terminal
            "terminated": {"archived"},  # terminated can be archived
            "archived": set(),  # terminal
        }
        allowed = valid.get(self.state, set())
        if new_state not in allowed:
            raise ValueError(f"invalid transition {self.state} -> {new_state}")
        ts = _now()
        self.state_history.append({"from": self.state, "to": new_state, "at": ts, "reason": reason})
        self.state = new_state
        if new_state == "suspended":
            self.suspended_at = ts
        elif new_state == "revoked":
            self.revoked_at = ts
        elif new_state == "terminated":
            self.terminated_at = ts
        elif new_state == "archived":
            self.archived_at = ts


class Registry:
    """In-memory registry for AI-IDP entities.

    Enforces permanent uniqueness and resolvability of identifiers.
    """

    def __init__(self) -> None:
        self._entities: dict[str, EntityRecord] = {}
        self._slugs: set[str] = set()  # to prevent slug reuse across entity types within a jurisdiction

    def register(self, entity_id: str, entity_type: str, attributes: dict[str, object] | None = None) -> EntityRecord:
        if entity_id in self._entities:
            raise ValueError(f"entity_id already exists: {entity_id}")
        rec = EntityRecord(
            entity_id=entity_id,
            entity_type=entity_type,
            state="active",
            attributes=dict(attributes or {}),
            created_at=_now(),
        )
        self._entities[entity_id] = rec
        return rec

    def get(self, entity_id: str) -> EntityRecord | None:
        return self._entities.get(entity_id)

    def resolve(self, entity_id: str) -> EntityRecord:
        rec = self._entities.get(entity_id)
        if rec is None:
            raise KeyError(f"unresolvable entity: {entity_id}")
        return rec

    def update(self, entity_id: str, attributes: dict[str, object]) -> EntityRecord:
        rec = self.resolve(entity_id)
        if not rec.is_active():
            raise PermissionError(f"cannot update non-active entity: {entity_id} (state={rec.state})")
        rec.attributes.update(attributes)
        return rec

    def suspend(self, entity_id: str, reason: str = "") -> EntityRecord:
        rec = self.resolve(entity_id)
        rec.transition("suspended", reason)
        return rec

    def revoke(self, entity_id: str, reason: str = "") -> EntityRecord:
        rec = self.resolve(entity_id)
        rec.transition("revoked", reason)
        return rec

    def terminate(self, entity_id: str, reason: str = "") -> EntityRecord:
        rec = self.resolve(entity_id)
        rec.transition("terminated", reason)
        return rec

    def archive(self, entity_id: str, reason: str = "") -> EntityRecord:
        rec = self.resolve(entity_id)
        rec.transition("archived", reason)
        return rec

    def reactivate(self, entity_id: str) -> EntityRecord:
        rec = self.resolve(entity_id)
        rec.transition("active")  # only valid from suspended
        return rec

    def all_entities(self) -> dict[str, EntityRecord]:
        return dict(self._entities)


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = ["EntityRecord", "Registry"]
