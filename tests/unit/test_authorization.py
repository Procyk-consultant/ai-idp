"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_authorization.py
Purpose: Unit tests for authorization engine
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from aegistrace.authorization.engine import PolicyEngine
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService


def make_engine():
    keys = KeyService()
    controller = str(make_identifier("controller", "c1"))
    keys.create_key("aitrace://ca/key/k1", bound_entity_id=controller)
    engine = PolicyEngine(keys)
    return keys, engine, controller


class TestPolicyEngine:
    def test_issue_authorization(self) -> None:
        keys, engine, controller = make_engine()
        auth = engine.issue_authorization(
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=controller,
            agent_id=str(make_identifier("agent", "a1")),
            task_id=str(make_identifier("task", "t1")),
            scope={"action_classes": ["SEARCH", "READ"]},
            signing_key_id="aitrace://ca/key/k1",
        )
        assert auth.authorization_id.startswith("aitrace://ca/authorization/")

    def test_evaluate_permitted(self) -> None:
        keys, engine, controller = make_engine()
        auth = engine.issue_authorization(
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=controller,
            agent_id=str(make_identifier("agent", "a1")),
            task_id=str(make_identifier("task", "t1")),
            scope={"action_classes": ["SEARCH", "READ"]},
            signing_key_id="aitrace://ca/key/k1",
        )
        decision = engine.evaluate(action="SEARCH", authorization_id=auth.authorization_id)
        assert decision.permitted

    def test_evaluate_action_not_in_scope(self) -> None:
        keys, engine, controller = make_engine()
        auth = engine.issue_authorization(
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=controller,
            agent_id=str(make_identifier("agent", "a1")),
            task_id=str(make_identifier("task", "t1")),
            scope={"action_classes": ["SEARCH"]},
            signing_key_id="aitrace://ca/key/k1",
        )
        decision = engine.evaluate(action="DELETE", authorization_id=auth.authorization_id)
        assert not decision.permitted

    def test_evaluate_revoked_authorization(self) -> None:
        keys, engine, controller = make_engine()
        auth = engine.issue_authorization(
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=controller,
            agent_id=str(make_identifier("agent", "a1")),
            task_id=str(make_identifier("task", "t1")),
            scope={"action_classes": ["SEARCH"]},
            signing_key_id="aitrace://ca/key/k1",
        )
        engine.revoke_authorization(auth.authorization_id)
        decision = engine.evaluate(action="SEARCH", authorization_id=auth.authorization_id)
        assert not decision.permitted

    def test_approval_required_for_deploy(self) -> None:
        keys, engine, controller = make_engine()
        auth = engine.issue_authorization(
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=controller,
            agent_id=str(make_identifier("agent", "a1")),
            task_id=str(make_identifier("task", "t1")),
            scope={"action_classes": ["DEPLOY"]},
            signing_key_id="aitrace://ca/key/k1",
        )
        # Without approval
        decision = engine.evaluate(action="DEPLOY", authorization_id=auth.authorization_id)
        assert not decision.permitted
        assert decision.approval_required
        # With approval
        ap = engine.issue_approval(
            action="DEPLOY",
            approver_id=str(make_identifier("principal", "p1")),
            authorization_id=auth.authorization_id,
            signing_key_id="aitrace://ca/key/k1",
        )
        decision2 = engine.evaluate(action="DEPLOY", authorization_id=auth.authorization_id, approval_id=ap.approval_id)
        assert decision2.permitted
        # Approval is single-use; consume it and verify reuse is rejected
        assert engine.use_approval(ap.approval_id)
        decision3 = engine.evaluate(action="DEPLOY", authorization_id=auth.authorization_id, approval_id=ap.approval_id)
        assert not decision3.permitted

    def test_approval_single_use(self) -> None:
        keys, engine, controller = make_engine()
        auth = engine.issue_authorization(
            principal_id=str(make_identifier("principal", "p1")),
            controller_id=controller,
            agent_id=str(make_identifier("agent", "a1")),
            task_id=str(make_identifier("task", "t1")),
            scope={"action_classes": ["DESTROY_RESOURCE"]},
            signing_key_id="aitrace://ca/key/k1",
        )
        ap = engine.issue_approval(
            action="DESTROY_RESOURCE",
            approver_id=str(make_identifier("principal", "p1")),
            authorization_id=auth.authorization_id,
            signing_key_id="aitrace://ca/key/k1",
        )
        assert engine.use_approval(ap.approval_id)
        assert not engine.use_approval(ap.approval_id)  # already used
