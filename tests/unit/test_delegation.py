"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_delegation.py
Purpose: Unit tests for delegation module
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import pytest

from aegistrace.delegation.broker import DelegationBroker, DelegationScope
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService


def make_broker():
    keys = KeyService()
    parent_agent = str(make_identifier("agent", "parent"))
    keys.create_key("aitrace://ca/key/k1", bound_entity_id=parent_agent)
    broker = DelegationBroker(keys)
    return keys, broker, parent_agent


class TestDelegation:
    def test_create_delegation(self) -> None:
        keys, broker, parent = make_broker()
        child = str(make_identifier("agent", "child"))
        dlg = broker.create(
            parent_agent_id=parent,
            parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
            child_agent_id=child,
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=str(make_identifier("controller", "c1")),
            scope=DelegationScope(action_classes=["SEARCH", "READ"], delegation_depth=0),
            signing_key_id="aitrace://ca/key/k1",
        )
        assert dlg.delegation_id.startswith("aitrace://ca/delegation/")
        assert broker.verify(dlg.delegation_id)

    def test_scope_enforcement(self) -> None:
        keys, broker, parent = make_broker()
        child = str(make_identifier("agent", "child"))
        scope = DelegationScope(action_classes=["SEARCH", "READ"])
        broker.create(
            parent_agent_id=parent,
            parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
            child_agent_id=child,
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=str(make_identifier("controller", "c1")),
            scope=scope,
            signing_key_id="aitrace://ca/key/k1",
        )
        assert scope.encompasses(action="SEARCH")
        assert not scope.encompasses(action="DELETE")

    def test_revoke_delegation(self) -> None:
        keys, broker, parent = make_broker()
        child = str(make_identifier("agent", "child"))
        dlg = broker.create(
            parent_agent_id=parent,
            parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
            child_agent_id=child,
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=str(make_identifier("controller", "c1")),
            scope=DelegationScope(action_classes=["SEARCH"]),
            signing_key_id="aitrace://ca/key/k1",
        )
        broker.revoke(dlg.delegation_id)
        assert not broker.verify(dlg.delegation_id)

    def test_inactive_key_cannot_delegate(self) -> None:
        keys, broker, parent = make_broker()
        keys.revoke("aitrace://ca/key/k1")
        with pytest.raises(PermissionError):
            broker.create(
                parent_agent_id=parent,
                parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
                child_agent_id=str(make_identifier("agent", "child")),
                principal_id=str(make_identifier("principal", "p1")),
                controller_id=str(make_identifier("controller", "c1")),
                scope=DelegationScope(action_classes=["SEARCH"]),
                signing_key_id="aitrace://ca/key/k1",
            )
