"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_delegation.py
Purpose: Unit tests for delegation lineage and scope enforcement
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import pytest

from aegistrace.authorization.scope import ScopeContext
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
        delegation = broker.create(
            parent_agent_id=parent,
            parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
            child_agent_id=child,
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=str(make_identifier("controller", "c1")),
            scope=DelegationScope(action_classes=["SEARCH", "READ"], delegation_depth=0),
            signing_key_id="aitrace://ca/key/k1",
        )
        assert delegation.delegation_id.startswith("aitrace://ca/delegation/")
        assert broker.verify(delegation.delegation_id)

    def test_scope_enforcement(self) -> None:
        keys, broker, parent = make_broker()
        child = str(make_identifier("agent", "child"))
        scope = DelegationScope(
            action_classes=["SEARCH", "READ"],
            resource_classes=["web"],
            provider_classes=["approved-provider"],
        )
        broker.create(
            parent_agent_id=parent,
            parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
            child_agent_id=child,
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=str(make_identifier("controller", "c1")),
            scope=scope,
            signing_key_id="aitrace://ca/key/k1",
        )
        assert scope.encompasses(
            action="SEARCH",
            resource_class="web",
            provider_class="approved-provider",
        )
        assert not scope.encompasses(
            action="SEARCH",
            resource_class="web",
            provider_class="unapproved-provider",
        )
        assert not scope.encompasses(action="DELETE", resource_class="web", provider_class="approved-provider")

    def test_revoke_delegation(self) -> None:
        keys, broker, parent = make_broker()
        delegation = broker.create(
            parent_agent_id=parent,
            parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
            child_agent_id=str(make_identifier("agent", "child")),
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=str(make_identifier("controller", "c1")),
            scope=DelegationScope(action_classes=["SEARCH"]),
            signing_key_id="aitrace://ca/key/k1",
        )
        broker.revoke(delegation.delegation_id)
        assert not broker.verify(delegation.delegation_id)

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

    def test_signer_must_be_bound_to_authority_chain(self) -> None:
        keys, broker, parent = make_broker()
        keys.create_key("aitrace://ca/key/attacker", bound_entity_id=str(make_identifier("agent", "attacker")))
        with pytest.raises(PermissionError):
            broker.create(
                parent_agent_id=parent,
                parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
                child_agent_id=str(make_identifier("agent", "child")),
                principal_id=str(make_identifier("principal", "p1")),
                controller_id=str(make_identifier("controller", "c1")),
                scope=DelegationScope(action_classes=["SEARCH"]),
                signing_key_id="aitrace://ca/key/attacker",
            )

    def test_nested_delegation_chain_is_bounded_and_verifiable(self) -> None:
        keys, broker, root_agent = make_broker()
        principal = str(make_identifier("principal", "p1"))
        controller = str(make_identifier("controller", "c1"))
        child = str(make_identifier("agent", "child"))
        grandchild = str(make_identifier("agent", "grandchild"))

        root_delegation = broker.create(
            parent_agent_id=root_agent,
            parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
            child_agent_id=child,
            principal_id=principal,
            controller_id=controller,
            scope=DelegationScope(
                action_classes=["SEARCH", "READ", "DELEGATE"],
                resource_classes=["web"],
                provider_classes=["approved-provider"],
                delegation_depth=1,
            ),
            signing_key_id="aitrace://ca/key/k1",
        )

        keys.create_key("aitrace://ca/key/child", bound_entity_id=child)
        nested = broker.create(
            parent_agent_id=child,
            parent_instance_id=str(make_identifier("agent-instance", "child", version="r1")),
            child_agent_id=grandchild,
            principal_id=principal,
            controller_id=controller,
            scope=DelegationScope(
                action_classes=["SEARCH"],
                resource_classes=["web"],
                provider_classes=["approved-provider"],
                delegation_depth=0,
            ),
            signing_key_id="aitrace://ca/key/child",
            parent_delegation_id=root_delegation.delegation_id,
        )

        context = ScopeContext(resource_class="web", provider_class="approved-provider")
        assert broker.verify_action(
            nested.delegation_id,
            child_agent_id=grandchild,
            principal_id=principal,
            controller_id=controller,
            action="SEARCH",
            context=context,
        )
        assert broker.delegation_chain(nested.delegation_id) == [
            root_delegation.delegation_id,
            nested.delegation_id,
        ]

    def test_nested_delegation_cannot_widen_scope_or_depth(self) -> None:
        keys, broker, root_agent = make_broker()
        principal = str(make_identifier("principal", "p1"))
        controller = str(make_identifier("controller", "c1"))
        child = str(make_identifier("agent", "child"))
        root_delegation = broker.create(
            parent_agent_id=root_agent,
            parent_instance_id=str(make_identifier("agent-instance", "parent", version="r1")),
            child_agent_id=child,
            principal_id=principal,
            controller_id=controller,
            scope=DelegationScope(
                action_classes=["SEARCH", "DELEGATE"],
                resource_classes=["web"],
                delegation_depth=1,
            ),
            signing_key_id="aitrace://ca/key/k1",
        )
        keys.create_key("aitrace://ca/key/child", bound_entity_id=child)

        with pytest.raises(PermissionError):
            broker.create(
                parent_agent_id=child,
                parent_instance_id=str(make_identifier("agent-instance", "child", version="r1")),
                child_agent_id=str(make_identifier("agent", "grandchild")),
                principal_id=principal,
                controller_id=controller,
                scope=DelegationScope(
                    action_classes=["SEARCH"],
                    resource_classes=["database"],
                    delegation_depth=1,
                ),
                signing_key_id="aitrace://ca/key/child",
                parent_delegation_id=root_delegation.delegation_id,
            )
