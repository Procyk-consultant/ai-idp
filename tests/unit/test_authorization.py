"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_authorization.py
Purpose: Unit tests for authorization and exact-action approval policy enforcement
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import pytest

from aegistrace.authorization.engine import PolicyEngine
from aegistrace.authorization.entitlements import (
    CompositeApproverEntitlementProvider,
    PrincipalApproverEntitlementProvider,
    StaticApproverEntitlementProvider,
)
from aegistrace.authorization.scope import ScopeContext
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService

ACTION_DIGEST = "sha256:" + "1" * 64
OTHER_ACTION_DIGEST = "sha256:" + "2" * 64


def make_engine(*, entitlements=None):
    keys = KeyService()
    controller = str(make_identifier("controller", "c1"))
    principal = str(make_identifier("principal", "p1"))
    keys.create_key("aitrace://ca/key/controller", bound_entity_id=controller)
    keys.create_key("aitrace://ca/key/principal", bound_entity_id=principal)
    return (
        keys,
        PolicyEngine(keys, approver_entitlements=entitlements),
        controller,
        principal,
    )


def issue(
    engine: PolicyEngine,
    controller: str,
    principal: str,
    *,
    actions: list[str],
    scope: dict | None = None,
):
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

    def test_evaluate_permitted_and_out_of_scope(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["SEARCH", "READ"])
        assert engine.evaluate(action="SEARCH", authorization_id=authorization.authorization_id).permitted
        assert not engine.evaluate(action="DELETE", authorization_id=authorization.authorization_id).permitted

    def test_evaluate_revoked_authorization(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["SEARCH"])
        engine.revoke_authorization(authorization.authorization_id)
        assert not engine.evaluate(action="SEARCH", authorization_id=authorization.authorization_id).permitted

    def test_approval_required_consumed_and_not_reusable(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["DEPLOY"])
        decision = engine.evaluate(
            action="DEPLOY",
            authorization_id=authorization.authorization_id,
            action_digest=ACTION_DIGEST,
        )
        assert not decision.permitted and decision.approval_required
        approval = engine.issue_approval(
            action="DEPLOY",
            action_digest=ACTION_DIGEST,
            approver_id=principal,
            authorization_id=authorization.authorization_id,
            signing_key_id="aitrace://ca/key/principal",
        )
        permitted = engine.evaluate(
            action="DEPLOY",
            authorization_id=authorization.authorization_id,
            action_digest=ACTION_DIGEST,
            approval_id=approval.approval_id,
        )
        assert permitted.permitted
        assert engine.consume_approvals(permitted.satisfied_approval_ids)
        assert not engine.evaluate(
            action="DEPLOY",
            authorization_id=authorization.authorization_id,
            action_digest=ACTION_DIGEST,
            approval_id=approval.approval_id,
        ).permitted

    def test_approval_cannot_be_retargeted_to_different_action_intent(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["PUBLISH"])
        approval = engine.issue_approval(
            action="PUBLISH",
            action_digest=ACTION_DIGEST,
            approver_id=principal,
            authorization_id=authorization.authorization_id,
            signing_key_id="aitrace://ca/key/principal",
        )
        assert engine.evaluate(
            action="PUBLISH",
            authorization_id=authorization.authorization_id,
            action_digest=ACTION_DIGEST,
            approval_id=approval.approval_id,
        ).permitted
        mismatch = engine.evaluate(
            action="PUBLISH",
            authorization_id=authorization.authorization_id,
            action_digest=OTHER_ACTION_DIGEST,
            approval_id=approval.approval_id,
        )
        assert not mismatch.permitted and mismatch.approval_required

    def test_approval_single_use(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["DESTROY_RESOURCE"])
        approval = engine.issue_approval(
            action="DESTROY_RESOURCE",
            action_digest=ACTION_DIGEST,
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
                action_digest=ACTION_DIGEST,
                approver_id=principal,
                authorization_id=authorization.authorization_id,
                signing_key_id="aitrace://ca/key/controller",
            )

    def test_unentitled_approver_is_rejected(self) -> None:
        keys, engine, controller, principal = make_engine()
        outsider = str(make_identifier("principal", "outsider"))
        keys.create_key("aitrace://ca/key/outsider", bound_entity_id=outsider)
        authorization = issue(engine, controller, principal, actions=["PUBLISH"])
        with pytest.raises(PermissionError, match="not entitled"):
            engine.issue_approval(
                action="PUBLISH",
                action_digest=ACTION_DIGEST,
                approver_id=outsider,
                authorization_id=authorization.authorization_id,
                signing_key_id="aitrace://ca/key/outsider",
            )

    def test_dual_approval_requires_two_distinct_entitled_approvers_for_same_intent(self) -> None:
        second_approver = str(make_identifier("principal", "p2"))
        entitlements = CompositeApproverEntitlementProvider(
            PrincipalApproverEntitlementProvider(),
            StaticApproverEntitlementProvider({second_approver: ["DESTROY_KEY"]}),
        )
        keys, engine, controller, principal = make_engine(entitlements=entitlements)
        keys.create_key("aitrace://ca/key/principal-2", bound_entity_id=second_approver)
        authorization = issue(engine, controller, principal, actions=["DESTROY_KEY"])
        approval_1 = engine.issue_approval(
            action="DESTROY_KEY",
            action_digest=ACTION_DIGEST,
            approver_id=principal,
            authorization_id=authorization.authorization_id,
            signing_key_id="aitrace://ca/key/principal",
        )
        approval_2 = engine.issue_approval(
            action="DESTROY_KEY",
            action_digest=ACTION_DIGEST,
            approver_id=second_approver,
            authorization_id=authorization.authorization_id,
            signing_key_id="aitrace://ca/key/principal-2",
        )
        assert not engine.evaluate(
            action="DESTROY_KEY",
            authorization_id=authorization.authorization_id,
            action_digest=ACTION_DIGEST,
            approval_ids=[approval_1.approval_id],
        ).permitted
        permitted = engine.evaluate(
            action="DESTROY_KEY",
            authorization_id=authorization.authorization_id,
            action_digest=ACTION_DIGEST,
            approval_ids=[approval_1.approval_id, approval_2.approval_id],
        )
        assert permitted.permitted
        assert set(permitted.satisfied_approval_ids) == {
            approval_1.approval_id,
            approval_2.approval_id,
        }

    def test_returned_authorization_is_snapshot_not_mutable_canonical_state(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["SEARCH"])
        authorization.signature = "Ed25519:" + "A" * 88
        authorization.scope["action_classes"] = ["DELETE"]
        assert engine.verify_authorization(authorization.authorization_id)
        assert engine.evaluate(action="SEARCH", authorization_id=authorization.authorization_id).permitted
        assert not engine.evaluate(action="DELETE", authorization_id=authorization.authorization_id).permitted

    def test_returned_approval_is_snapshot_not_mutable_canonical_state(self) -> None:
        keys, engine, controller, principal = make_engine()
        authorization = issue(engine, controller, principal, actions=["PUBLISH"])
        approval = engine.issue_approval(
            action="PUBLISH",
            action_digest=ACTION_DIGEST,
            approver_id=principal,
            authorization_id=authorization.authorization_id,
            signing_key_id="aitrace://ca/key/principal",
        )
        approval.used = True
        approval.action_digest = OTHER_ACTION_DIGEST
        stored = engine.get_approval(approval.approval_id)
        assert stored is not None and stored.used is False
        assert stored.action_digest == ACTION_DIGEST
        assert engine.verify_approval(approval.approval_id)

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
        assert not engine.evaluate(action="READ", authorization_id=authorization.authorization_id).permitted
        assert engine.evaluate(
            action="READ",
            authorization_id=authorization.authorization_id,
            scope_context=ScopeContext(
                resource_class="document",
                provider_class="approved-provider",
            ),
        ).permitted
        assert not engine.evaluate(
            action="READ",
            authorization_id=authorization.authorization_id,
            scope_context=ScopeContext(
                resource_class="document",
                provider_class="unapproved-provider",
            ),
        ).permitted
