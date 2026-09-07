"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/authorization/scope.py
Purpose: Typed scope evaluation for authorization and delegation
Classification: domain
Version: 2.1.0
Last Material Revision: 2026-09-07
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

_SCOPE_LIST_FIELDS = (
    ("task_classes", "task_class"),
    ("resource_classes", "resource_class"),
    ("geography", "geography"),
    ("tool_classes", "tool_class"),
    ("model_classes", "model_class"),
    ("provider_classes", "provider_class"),
)


@dataclass(frozen=True)
class ScopeContext:
    """Runtime facts used to evaluate a bounded authorization/delegation scope."""

    task_class: str | None = None
    resource_class: str | None = None
    geography: str | None = None
    tool_class: str | None = None
    model_class: str | None = None
    provider_class: str | None = None
    evaluated_at: str | None = None
    requested_delegation_depth: int | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for field_name in (
            "task_class",
            "resource_class",
            "geography",
            "tool_class",
            "model_class",
            "provider_class",
            "evaluated_at",
            "requested_delegation_depth",
        ):
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value
        return result

    @classmethod
    def from_dict(cls, value: Mapping[str, Any] | None) -> ScopeContext:
        if not value:
            return cls()
        return cls(
            task_class=_optional_str(value.get("task_class")),
            resource_class=_optional_str(value.get("resource_class")),
            geography=_optional_str(value.get("geography")),
            tool_class=_optional_str(value.get("tool_class")),
            model_class=_optional_str(value.get("model_class")),
            provider_class=_optional_str(value.get("provider_class")),
            evaluated_at=_optional_str(value.get("evaluated_at")),
            requested_delegation_depth=_optional_int(value.get("requested_delegation_depth")),
        )


@dataclass(frozen=True)
class ScopeDecision:
    allowed: bool
    reason: str


def evaluate_scope(
    scope: Mapping[str, Any] | None,
    *,
    action: str,
    context: ScopeContext | None = None,
) -> ScopeDecision:
    """Evaluate an action and runtime context against a bounded scope.

    Restricted dimensions fail closed when the corresponding runtime fact is
    absent. An empty/omitted list means that dimension is not restricted.
    """
    scope = scope or {}
    context = context or ScopeContext()

    actions = _normalized_str_set(scope.get("action_classes"))
    if actions and action not in actions:
        return ScopeDecision(False, f"action {action} is outside scope")

    for scope_field, context_field in _SCOPE_LIST_FIELDS:
        allowed_values = _normalized_str_set(scope.get(scope_field))
        if not allowed_values:
            continue
        actual_value = getattr(context, context_field)
        if actual_value is None:
            return ScopeDecision(False, f"scope requires {context_field}, but no runtime value was supplied")
        if actual_value not in allowed_values:
            return ScopeDecision(False, f"{context_field} {actual_value!r} is outside scope")

    time_bounds = scope.get("time_bounds")
    if time_bounds:
        if not isinstance(time_bounds, Mapping):
            return ScopeDecision(False, "time_bounds is malformed")
        try:
            evaluated_at = _parse_timestamp(context.evaluated_at) if context.evaluated_at else datetime.now(UTC)
            not_before_value = time_bounds.get("not_before")
            not_after_value = time_bounds.get("not_after")
            if not_before_value is not None and evaluated_at < _parse_timestamp(str(not_before_value)):
                return ScopeDecision(False, "scope is not active yet")
            if not_after_value is not None and evaluated_at > _parse_timestamp(str(not_after_value)):
                return ScopeDecision(False, "scope has expired")
        except (TypeError, ValueError) as exc:
            return ScopeDecision(False, f"invalid scope timestamp: {exc}")

    if context.requested_delegation_depth is not None:
        try:
            maximum_depth = int(scope.get("delegation_depth", 0))
        except (TypeError, ValueError):
            return ScopeDecision(False, "delegation_depth is malformed")
        if context.requested_delegation_depth < 0:
            return ScopeDecision(False, "requested_delegation_depth cannot be negative")
        if context.requested_delegation_depth > maximum_depth:
            return ScopeDecision(
                False,
                f"requested delegation depth {context.requested_delegation_depth} exceeds scope maximum {maximum_depth}",
            )

    return ScopeDecision(True, "scope permits action")


def evaluate_child_scope(parent_scope: Mapping[str, Any], child_scope: Mapping[str, Any]) -> ScopeDecision:
    """Verify that a nested delegation is strictly within its parent scope.

    Empty lists mean unrestricted. Therefore a child cannot omit a restriction
    that is present on its parent. Each nested delegation consumes one unit of
    delegation depth.
    """
    try:
        parent_depth = int(parent_scope.get("delegation_depth", 0))
        child_depth = int(child_scope.get("delegation_depth", 0))
    except (TypeError, ValueError):
        return ScopeDecision(False, "delegation_depth is malformed")
    if parent_depth <= 0:
        return ScopeDecision(False, "parent delegation is a leaf and cannot delegate further")
    if child_depth < 0:
        return ScopeDecision(False, "child delegation_depth cannot be negative")

    parent_actions = _normalized_str_set(parent_scope.get("action_classes"))
    child_actions = _normalized_str_set(child_scope.get("action_classes"))
    decision = _subset_decision(parent_actions, child_actions, "action_classes")
    if not decision.allowed:
        return decision

    for scope_field, _ in _SCOPE_LIST_FIELDS:
        parent_values = _normalized_str_set(parent_scope.get(scope_field))
        child_values = _normalized_str_set(child_scope.get(scope_field))
        decision = _subset_decision(parent_values, child_values, scope_field)
        if not decision.allowed:
            return decision

    try:
        parent_not_before, parent_not_after = _time_window(parent_scope.get("time_bounds"))
        child_not_before, child_not_after = _time_window(child_scope.get("time_bounds"))
    except (TypeError, ValueError) as exc:
        return ScopeDecision(False, f"invalid delegation time bounds: {exc}")

    if parent_not_before is not None:
        if child_not_before is None or child_not_before < parent_not_before:
            return ScopeDecision(False, "child time window starts outside the parent scope")
    if parent_not_after is not None:
        if child_not_after is None or child_not_after > parent_not_after:
            return ScopeDecision(False, "child time window ends outside the parent scope")

    if child_depth > parent_depth - 1:
        return ScopeDecision(
            False,
            f"child delegation_depth {child_depth} exceeds remaining depth {parent_depth - 1}",
        )

    return ScopeDecision(True, "child scope is contained by parent scope")


def _subset_decision(parent_values: set[str], child_values: set[str], field_name: str) -> ScopeDecision:
    if not parent_values:
        return ScopeDecision(True, f"parent {field_name} is unrestricted")
    if not child_values:
        return ScopeDecision(False, f"child {field_name} cannot be unrestricted when parent is restricted")
    if not child_values.issubset(parent_values):
        extra = sorted(child_values - parent_values)
        return ScopeDecision(False, f"child {field_name} exceeds parent scope: {extra}")
    return ScopeDecision(True, f"child {field_name} is contained")


def _normalized_str_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if not isinstance(value, (list, tuple, set, frozenset)):
        raise TypeError("scope list field must be an array")
    return {str(item) for item in value}


def _time_window(value: Any) -> tuple[datetime | None, datetime | None]:
    if value in (None, {}):
        return None, None
    if not isinstance(value, Mapping):
        raise TypeError("time_bounds must be an object")
    not_before = value.get("not_before")
    not_after = value.get("not_after")
    return (
        _parse_timestamp(str(not_before)) if not_before is not None else None,
        _parse_timestamp(str(not_after)) if not_after is not None else None,
    )


def _parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(UTC)


def _optional_str(value: Any) -> str | None:
    return None if value is None else str(value)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


__all__ = ["ScopeContext", "ScopeDecision", "evaluate_scope", "evaluate_child_scope"]
