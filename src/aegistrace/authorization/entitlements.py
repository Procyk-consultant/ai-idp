"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/authorization/entitlements.py
Purpose: Approver-entitlement policy contract
Classification: domain
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class ApproverEntitlementProvider(Protocol):
    """Resolve whether a principal may approve an action under an authorization."""

    def can_approve(
        self,
        *,
        approver_id: str,
        action: str,
        authorization_principal_id: str,
        authorization_controller_id: str,
    ) -> bool:
        ...


class PrincipalApproverEntitlementProvider:
    """Fail-closed default: only the authorization principal may approve."""

    def can_approve(
        self,
        *,
        approver_id: str,
        action: str,
        authorization_principal_id: str,
        authorization_controller_id: str,
    ) -> bool:
        del action, authorization_controller_id
        return approver_id == authorization_principal_id


class StaticApproverEntitlementProvider:
    """Explicit action grants for reference deployments and tests.

    Production organizations can replace this provider with an IAM/directory
    adapter while preserving the same fail-closed PolicyEngine contract.
    """

    def __init__(self, grants: dict[str, Iterable[str]] | None = None) -> None:
        self._grants: dict[str, frozenset[str]] = {
            approver_id: frozenset(actions)
            for approver_id, actions in (grants or {}).items()
        }

    def grant(self, approver_id: str, actions: Iterable[str]) -> None:
        existing = set(self._grants.get(approver_id, frozenset()))
        existing.update(actions)
        self._grants[approver_id] = frozenset(existing)

    def can_approve(
        self,
        *,
        approver_id: str,
        action: str,
        authorization_principal_id: str,
        authorization_controller_id: str,
    ) -> bool:
        del authorization_principal_id, authorization_controller_id
        allowed = self._grants.get(approver_id, frozenset())
        return "*" in allowed or action in allowed


class CompositeApproverEntitlementProvider:
    """Permit approval when any configured entitlement source permits it."""

    def __init__(self, *providers: ApproverEntitlementProvider) -> None:
        if not providers:
            raise ValueError("at least one entitlement provider is required")
        self._providers = providers

    def can_approve(
        self,
        *,
        approver_id: str,
        action: str,
        authorization_principal_id: str,
        authorization_controller_id: str,
    ) -> bool:
        return any(
            provider.can_approve(
                approver_id=approver_id,
                action=action,
                authorization_principal_id=authorization_principal_id,
                authorization_controller_id=authorization_controller_id,
            )
            for provider in self._providers
        )


__all__ = [
    "ApproverEntitlementProvider",
    "PrincipalApproverEntitlementProvider",
    "StaticApproverEntitlementProvider",
    "CompositeApproverEntitlementProvider",
]
