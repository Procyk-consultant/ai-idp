"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/events/models.py
Purpose: Event data model
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aegistrace.authorization.scope import ScopeContext

ACTIONS: list[str] = [
    "DISCOVER", "ENUMERATE", "OPEN", "READ", "SEARCH", "QUERY", "CREATE", "GENERATE",
    "MODIFY", "REWRITE", "PATCH", "MOVE", "RENAME", "COPY", "DELETE", "RESTORE",
    "EXECUTE", "RUN", "COMPILE", "BUILD", "TEST", "DEBUG", "INSTALL", "CONFIGURE",
    "CONNECT", "AUTHENTICATE", "AUTHORIZE", "DENY", "TRANSMIT", "RECEIVE", "UPLOAD",
    "DOWNLOAD", "EXPORT", "IMPORT", "PUBLISH", "DEPLOY", "RELEASE", "MERGE", "COMMIT",
    "BRANCH", "TAG", "SIGN", "VERIFY", "APPROVE", "REJECT", "RECOMMEND", "DECIDE",
    "DELEGATE", "CREATE_AGENT", "CREATE_SUB_AGENT", "CHANGE_MODEL", "CHANGE_PROVIDER",
    "CHANGE_TOOL", "CHANGE_PERMISSION", "CHANGE_POLICY", "REVOKE", "PAUSE", "TERMINATE",
    "ROLLBACK", "DESTROY_RESOURCE", "DESTROY_KEY", "ACCESS_SECRET", "USE_CREDENTIAL",
    "CALL_API", "WRITE_DATABASE", "DELETE_DATABASE_RECORD", "ALTER_DATABASE_SCHEMA",
    "MODIFY_INFRASTRUCTURE", "MODIFY_PRODUCTION", "TRIGGER_EXTERNAL_EFFECT",
]
VISIBILITY_TIERS = ("PUBLIC", "CONTROLLED", "ORGANIZATION_PRIVATE", "SEALED")
GOVERNANCE_MODES = ("GOVERNED", "EVIDENCE_ONLY", "DENIAL")
SCHEMA_VERSION = "2.0.0"


@dataclass
class Actor:
    controller_id: str
    principal_id: str
    agent_id: str
    agent_instance_id: str

    def to_dict(self) -> dict[str, str]:
        return {
            "controller_id": self.controller_id,
            "principal_id": self.principal_id,
            "agent_id": self.agent_id,
            "agent_instance_id": self.agent_instance_id,
        }


@dataclass
class ExecutionContext:
    provider_id: str
    model_id: str
    model_version_id: str
    deployment_id: str

    def to_dict(self) -> dict[str, str]:
        return {
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "model_version_id": self.model_version_id,
            "deployment_id": self.deployment_id,
        }


@dataclass
class Event:
    """A signed, hash-chained event record with optional governance evidence."""

    schema_version: str
    event_id: str
    timestamp: str
    jurisdiction_id: str
    actor: Actor
    execution_context: ExecutionContext
    task_id: str
    action: str
    visibility: str
    previous_event_hash: str | None
    event_hash: str
    signature: str
    signing_key_id: str
    delegation_id: str | None = None
    authorization_id: str | None = None
    approval_id: str | None = None
    approval_ids: list[str] = field(default_factory=list)
    delegation_chain: list[str] = field(default_factory=list)
    scope_context: ScopeContext | None = None
    action_intent_digest: str | None = None
    governance_mode: str | None = None
    decision_reason: str | None = None
    resource_id: str | None = None
    before_digest: str | None = None
    after_digest: str | None = None
    policy_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "jurisdiction_id": self.jurisdiction_id,
            "actor": self.actor.to_dict(),
            "execution_context": self.execution_context.to_dict(),
            "task_id": self.task_id,
            "action": self.action,
            "visibility": self.visibility,
            "previous_event_hash": self.previous_event_hash,
            "event_hash": self.event_hash,
            "signature": self.signature,
            "signing_key_id": self.signing_key_id,
            "policy_version": self.policy_version,
        }
        optional = {
            "delegation_id": self.delegation_id,
            "authorization_id": self.authorization_id,
            "approval_id": self.approval_id,
            "action_intent_digest": self.action_intent_digest,
            "governance_mode": self.governance_mode,
            "decision_reason": self.decision_reason,
            "resource_id": self.resource_id,
            "before_digest": self.before_digest,
            "after_digest": self.after_digest,
        }
        for key, value in optional.items():
            if value is not None:
                result[key] = value
        if self.approval_ids:
            result["approval_ids"] = list(self.approval_ids)
        if self.delegation_chain:
            result["delegation_chain"] = list(self.delegation_chain)
        if self.scope_context is not None:
            scope_dict = self.scope_context.to_dict()
            if scope_dict:
                result["scope_context"] = scope_dict
        return result

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Event:
        return cls(
            schema_version=value["schema_version"],
            event_id=value["event_id"],
            timestamp=value["timestamp"],
            jurisdiction_id=value["jurisdiction_id"],
            actor=Actor(**value["actor"]),
            execution_context=ExecutionContext(**value["execution_context"]),
            task_id=value["task_id"],
            action=value["action"],
            visibility=value["visibility"],
            previous_event_hash=value["previous_event_hash"],
            event_hash=value["event_hash"],
            signature=value["signature"],
            signing_key_id=value["signing_key_id"],
            delegation_id=value.get("delegation_id"),
            authorization_id=value.get("authorization_id"),
            approval_id=value.get("approval_id"),
            approval_ids=list(value.get("approval_ids", [])),
            delegation_chain=list(value.get("delegation_chain", [])),
            scope_context=ScopeContext.from_dict(value.get("scope_context")) if value.get("scope_context") else None,
            action_intent_digest=value.get("action_intent_digest"),
            governance_mode=value.get("governance_mode"),
            decision_reason=value.get("decision_reason"),
            resource_id=value.get("resource_id"),
            before_digest=value.get("before_digest"),
            after_digest=value.get("after_digest"),
            policy_version=value.get("policy_version", "1.0.0"),
        )


__all__ = [
    "ACTIONS", "VISIBILITY_TIERS", "GOVERNANCE_MODES", "SCHEMA_VERSION",
    "Actor", "ExecutionContext", "Event",
]
