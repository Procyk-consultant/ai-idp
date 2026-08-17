"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_state_isolation.py
Purpose: Unit tests for alias-resistant canonical service state
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from aegistrace.delegation.broker import DelegationBroker, DelegationScope
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry


class TestCanonicalStateIsolation:
    def test_key_record_snapshot_cannot_rebind_or_reactivate_key(self) -> None:
        keys = KeyService()
        agent = str(make_identifier("agent", "a1"))
        key_id = str(make_identifier("key", "k1"))
        keys.create_key(key_id, bound_entity_id=agent)
        snapshot = keys.get_record(key_id)
        snapshot.bound_entity_id = str(make_identifier("agent", "attacker"))
        snapshot.state = "revoked"
        canonical = keys.get_record(key_id)
        assert canonical.bound_entity_id == agent
        assert canonical.state == "active"

        keys.revoke(key_id)
        snapshot.state = "active"
        assert keys.get_record(key_id).state == "revoked"
        assert not keys.is_active(key_id)

    def test_registry_snapshots_cannot_rewrite_identity_relationships(self) -> None:
        registry = Registry()
        agent = str(make_identifier("agent", "a1"))
        controller = str(make_identifier("controller", "c1"))
        returned = registry.register(agent, "agent", {"controller_id": controller})
        returned.attributes["controller_id"] = str(make_identifier("controller", "attacker"))
        resolved = registry.resolve(agent)
        assert resolved.attributes["controller_id"] == controller

        resolved.attributes.clear()
        assert registry.resolve(agent).attributes["controller_id"] == controller

    def test_delegation_snapshot_cannot_expand_or_reactivate_authority(self) -> None:
        keys = KeyService()
        parent = str(make_identifier("agent", "parent"))
        child = str(make_identifier("agent", "child"))
        key_id = str(make_identifier("key", "parent-key"))
        keys.create_key(key_id, bound_entity_id=parent)
        broker = DelegationBroker(keys)
        delegation = broker.create(
            parent_agent_id=parent,
            parent_instance_id=str(make_identifier("agent-instance", "parent", version="run-1")),
            child_agent_id=child,
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=str(make_identifier("controller", "c1")),
            scope=DelegationScope(action_classes=["READ"], delegation_depth=0),
            signing_key_id=key_id,
        )
        delegation.scope.action_classes.append("DELETE")
        assert broker.get(delegation.delegation_id).scope.action_classes == ["READ"]  # type: ignore[union-attr]
        assert broker.verify(delegation.delegation_id)

        broker.revoke(delegation.delegation_id)
        delegation.state = "active"
        assert not broker.verify(delegation.delegation_id)
        stored = broker.get(delegation.delegation_id)
        assert stored is not None and stored.state == "revoked"
