"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_scope.py
Purpose: Unit tests for authorization/delegation scope evaluation
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from aegistrace.authorization.scope import ScopeContext, evaluate_child_scope, evaluate_scope


class TestScopeEvaluation:
    def test_restricted_dimension_requires_runtime_value(self) -> None:
        decision = evaluate_scope(
            {"action_classes": ["READ"], "resource_classes": ["document"]},
            action="READ",
            context=ScopeContext(),
        )
        assert not decision.allowed
        assert "resource_class" in decision.reason

    def test_all_scope_dimensions_are_enforced(self) -> None:
        scope = {
            "action_classes": ["READ"],
            "task_classes": ["research"],
            "resource_classes": ["document"],
            "geography": ["ca-qc"],
            "tool_classes": ["browser"],
            "model_classes": ["llm-approved"],
            "provider_classes": ["provider-approved"],
            "time_bounds": {
                "not_before": "2026-08-17T00:00:00Z",
                "not_after": "2026-08-18T00:00:00Z",
            },
        }
        context = ScopeContext(
            task_class="research",
            resource_class="document",
            geography="ca-qc",
            tool_class="browser",
            model_class="llm-approved",
            provider_class="provider-approved",
            evaluated_at="2026-08-17T12:00:00Z",
        )
        assert evaluate_scope(scope, action="READ", context=context).allowed
        assert not evaluate_scope(
            scope,
            action="READ",
            context=ScopeContext(**{**context.to_dict(), "provider_class": "unapproved"}),
        ).allowed

    def test_time_window_fails_closed(self) -> None:
        scope = {
            "action_classes": ["READ"],
            "time_bounds": {"not_after": "2026-08-17T10:00:00Z"},
        }
        decision = evaluate_scope(
            scope,
            action="READ",
            context=ScopeContext(evaluated_at="2026-08-17T10:00:01Z"),
        )
        assert not decision.allowed
        assert "expired" in decision.reason

    def test_child_scope_cannot_widen_parent(self) -> None:
        parent = {
            "action_classes": ["READ", "SEARCH", "DELEGATE"],
            "resource_classes": ["document", "web"],
            "geography": ["ca-qc"],
            "delegation_depth": 2,
        }
        child = {
            "action_classes": ["READ"],
            "resource_classes": ["document"],
            "geography": ["ca-qc"],
            "delegation_depth": 1,
        }
        assert evaluate_child_scope(parent, child).allowed

        widened = dict(child)
        widened["resource_classes"] = ["document", "database"]
        assert not evaluate_child_scope(parent, widened).allowed

    def test_leaf_delegation_cannot_delegate_further(self) -> None:
        parent = {"action_classes": ["DELEGATE"], "delegation_depth": 0}
        child = {"action_classes": ["READ"], "delegation_depth": 0}
        decision = evaluate_child_scope(parent, child)
        assert not decision.allowed
        assert "leaf" in decision.reason
