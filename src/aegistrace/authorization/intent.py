"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/authorization/intent.py
Purpose: Canonical proposed-action identity for approval binding
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aegistrace.authorization.scope import ScopeContext
from aegistrace.events.models import VISIBILITY_TIERS
from aegistrace.signing.canonical import canonicalize
from aegistrace.signing.ed25519 import sha256_hex


@dataclass(frozen=True)
class ActionIntent:
    """Exact material action facts that a single-use approval authorizes."""

    controller_id: str
    principal_id: str
    agent_id: str
    agent_instance_id: str
    provider_id: str
    model_id: str
    model_version_id: str
    deployment_id: str
    task_id: str
    action: str
    visibility: str
    jurisdiction_id: str = "ca"
    delegation_id: str | None = None
    resource_id: str | None = None
    before_digest: str | None = None
    after_digest: str | None = None
    scope_context: ScopeContext | None = None

    def __post_init__(self) -> None:
        if self.visibility not in VISIBILITY_TIERS:
            raise ValueError(f"invalid visibility: {self.visibility!r}")

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "controller_id": self.controller_id,
            "principal_id": self.principal_id,
            "agent_id": self.agent_id,
            "agent_instance_id": self.agent_instance_id,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "model_version_id": self.model_version_id,
            "deployment_id": self.deployment_id,
            "task_id": self.task_id,
            "action": self.action,
            "visibility": self.visibility,
            "jurisdiction_id": self.jurisdiction_id,
        }
        if self.delegation_id is not None:
            result["delegation_id"] = self.delegation_id
        if self.resource_id is not None:
            result["resource_id"] = self.resource_id
        if self.before_digest is not None:
            result["before_digest"] = self.before_digest
        if self.after_digest is not None:
            result["after_digest"] = self.after_digest
        if self.scope_context is not None:
            scope = self.scope_context.to_dict()
            if scope:
                result["scope_context"] = scope
        return result

    def digest(self) -> str:
        return sha256_hex(canonicalize(self.to_dict()))


__all__ = ["ActionIntent"]
