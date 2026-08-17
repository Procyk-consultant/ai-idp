"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_authorization.py
Purpose: Unit tests for authorization and approval policy enforcement
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import pytest

from aegistrace.authorization.engine import PolicyEngine
from aegistrace.authorization.scope import ScopeContext
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService


def make_engine():
    keys = KeyService()
    controller = str(make_identifier("controller", "c1"))
    principal = str(make_identifier("principal", "p1"))
    keys.create_key("aitrace://ca/key/controller", bound_entity_id=controller)
    keys.create_key("aitrace://ca/key/principal", bound_entity_id=principal)
    engine = PolicyEngine(keys)
    return keys, engine, controller, principal


def issue(engine: PolicyEngine, controller: str, principal: str, *, actions: list[str], scope: dict | None = None):
    effective_scope = dict(scope or {})
    effective_scope.setdefault("action_classes", actions)
    return engine.issue_authorization(
        principal_id=principal,
        controller_id=controller,
        agent_id=str(make_identifier("agent", "a1")),
        task_id=str(make_identifier("task", "t1")),
        scope=effective_scope,
        signing_key_id="aitrace://ca/key/controller",
    )


class TestPolicyEngine:
    def test_issue_authorization(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["SEARCH", "READ"])
        assert authorization.authorization_id.startswith("aitrace://ca/authorization/")
        assert engine.verify_authorization(authorization.authorization_id)

    def test_evaluate_permitted(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["SEARCH", "READ"])
        decision = engine.evaluate(action="SEARCH", authorization_id=authorization.authorization_id)
        assert decision.permitted

    def test_evaluate_action_not_in_scope(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["SEARCH"])
        decision = engine.evaluate(action="DELETE", authorization_id=authorization.authorization_id)
        assert not decision.permitted

    def test_evaluate_revoked_authorization(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["SEARCH"])
        engine.revoke_authorization(authorization.authorization_id)
        assert not engine.evaluate(
            action="SEARCH",
            authorization_id=authorization.authorization_id,
        ).permitted

    def test_approval_required_for_deploy(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["DEPLOY"])
        decision = engine.evaluate(action="DEPLOY", authorization_id=authorization.authorization_id)
        assert not decision.permitted
        assert decision.approval_required

        approval = engine.issue_approval(
            action="DEPLOY",
            approver_id=principal,
            authorization_id=authorization.authorization_id,
            signing_key_id="aitrace://ca/key/principal",
        )
        decision_2 = engine.evaluate(
            action="DEPLOY",
            authorization_id=authorization.authorization_id,
            approval_id=approval.approval_id,
        )
        assert decision_2.permitted
        assert decision_2.satisfied_approval_ids == (approval.approval_id,)
        assert engine.consume_approvals(decision_2.satisfied_approval_ids)
        assert not engine.evaluate(
            action="DEPLOY",
            authorization_id=authorization.authorization_id,
            approval_id=approval.approval_id,
        ).permitted

    def test_approval_single_use(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["DESTROY_RESOURCE"])
        approval = engine.issue_approval(
            action="DESTROY_RESOURCE",
            approver_id=principal,
            authorization_id=authorization.authorization_id,
            signing_key_id="aitrace://ca/key/principal",
        )
        assert engine.use_approval(approval.approval_id)
        assert not engine.use_approval(approval.approval_id)

    def test_approval_key_must_be_bound_to_approver(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["PUBLISH"])
        with pytest.raises(PermissionError):
            engine.issue_approval(
                action="PUBLISH",
                approver_id=principal,
                authorization_id=authorization.authorization_id,
                signing_key_id="aitrace://ca/key/controller",
            )

    def test_dual_approval_requires_two_distinct_approvers(self) -> None:
        keys, engine, controller, principal = make_engine()
        approver_2 = str(make_identifier("principal", "p2"))
        keys.create_key("aitrace://ca/key/principal-2", bound_entity_id=approver_2)
        authorization = issue(engine, controller, principal, actions=["DESTROY_KEY"])
        approval_1 = engine.issue_approval(
            action="DESTROY_KEY",
            approver_id=principal,
            authorization_id=authorization.authorization_id,
            signing_key_id="aitrace://ca/key/principal",
        )
        approval_2 = engine.issue_approval(
            action="DESTROY_KEY",
            approver_id=approver_2,
            authorization_id=authorization.authorization_id,
            signing_key_id="aitrace://ca/key/principal-2",
        )

        one = engine.evaluate(
            action="DESTROY_KEY",
            authorization_id=authorization.authorization_id,
            approval_ids=[approval_1.approval_id],
        )
        assert not one.permitted

        two = engine.evaluate(
            action="DESTROY_KEY",
            authorization_id=authorization.authorization_id,
            approval_ids=[approval_1.approval_id, approval_2.approval_id],
        )
        assert two.permitted
        assert set(two.satisfied_approval_ids) == {approval_1.approval_id, approval_2.approval_id}

    def test_tampered_authorization_signature_is_rejected(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["SEARCH"])
        authorization.signature = "Ed25519:" + "A" * 88
        assert not engine.verify_authorization(authorization.authorization_id)
        assert not engine.evaluate(
            action="SEARCH",
            authorization_id=authorization.authorization_id,
        ).permitted

    def test_scope_dimensions_fail_closed(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(
            engine,
            controller,
            principal,
            actions=["READ"],
            scope={
                "resource_classes": ["document"],
                "provider_classes": ["approved-provider"],
            },
        )
        missing_context = engine.evaluate(
            action="READ",
            authorization_id=authorization.authorization_id,
        )
        assert not missing_context.permitted

        allowed = engine.evaluate(
            action="READ",
            authorization_id=authorization.authorization_id,
            scope_context=ScopeContext(
                resource_class="document",
                provider_class="approved-provider",
            ),
        )
        assert allowed.permitted

        denied = engine.evaluate(
            action="READ",
            authorization_id=authorization.authorization_id,
            scope_context=ScopeContext(
                resource_class="document",
                provider_class="unapproved-provider",
            ),
        )
        assert not denied.permitted
