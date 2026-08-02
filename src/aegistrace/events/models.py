"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/events/models.py
Purpose: Event data model
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Canonical action vocabulary (Master Prompt §6)
ACTIONS: list[str] = [
    "DISCOVER", "ENUMERATE", "OPEN", "READ", "SEARCH", "QUERY",
    "CREATE", "GENERATE", "MODIFY", "REWRITE", "PATCH", "MOVE",
    "RENAME", "COPY", "DELETE", "RESTORE", "EXECUTE", "RUN",
    "COMPILE", "BUILD", "TEST", "DEBUG", "INSTALL", "CONFIGURE",
    "CONNECT", "AUTHENTICATE", "AUTHORIZE", "DENY", "TRANSMIT",
    "RECEIVE", "UPLOAD", "DOWNLOAD", "EXPORT", "IMPORT", "PUBLISH",
    "DEPLOY", "RELEASE", "MERGE", "COMMIT", "BRANCH", "TAG",
    "SIGN", "VERIFY", "APPROVE", "REJECT", "RECOMMEND", "DECIDE",
    "DELEGATE", "CREATE_AGENT", "CREATE_SUB_AGENT", "CHANGE_MODEL",
    "CHANGE_PROVIDER", "CHANGE_TOOL", "CHANGE_PERMISSION",
    "CHANGE_POLICY", "REVOKE", "PAUSE", "TERMINATE", "ROLLBACK",
    "DESTROY_RESOURCE", "DESTROY_KEY", "ACCESS_SECRET", "USE_CREDENTIAL",
    "CALL_API", "WRITE_DATABASE", "DELETE_DATABASE_RECORD",
    "ALTER_DATABASE_SCHEMA", "MODIFY_INFRASTRUCTURE", "MODIFY_PRODUCTION",
    "TRIGGER_EXTERNAL_EFFECT",
]

VISIBILITY_TIERS = ("PUBLIC", "CONTROLLED", "ORGANIZATION_PRIVATE", "SEALED")

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
    """A signed, hash-chained event record.

    Invariants (verified at append time):
        - schema_version is current.
        - event_id is unique.
        - timestamp is ISO 8601 UTC.
        - jurisdiction_id is a valid Canadian jurisdiction.
        - actor has all four identifier fields.
        - execution_context has all four identifier fields.
        - action is one of the canonical ACTIONS.
        - visibility is one of the canonical VISIBILITY_TIERS.
        - previous_event_hash matches the previous event's event_hash.
        - event_hash is correctly computed.
        - signature is a valid Ed25519 signature over the canonical form.
        - signing_key_id is bound to the actor.agent_id at signing time.
    """

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
    resource_id: str | None = None
    before_digest: str | None = None
    after_digest: str | None = None
    policy_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
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
        if self.delegation_id is not None:
            d["delegation_id"] = self.delegation_id
        if self.authorization_id is not None:
            d["authorization_id"] = self.authorization_id
        if self.approval_id is not None:
            d["approval_id"] = self.approval_id
        if self.resource_id is not None:
            d["resource_id"] = self.resource_id
        if self.before_digest is not None:
            d["before_digest"] = self.before_digest
        if self.after_digest is not None:
            d["after_digest"] = self.after_digest
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Event:
        actor = Actor(
            controller_id=d["actor"]["controller_id"],
            principal_id=d["actor"]["principal_id"],
            agent_id=d["actor"]["agent_id"],
            agent_instance_id=d["actor"]["agent_instance_id"],
        )
        ec = ExecutionContext(
            provider_id=d["execution_context"]["provider_id"],
            model_id=d["execution_context"]["model_id"],
            model_version_id=d["execution_context"]["model_version_id"],
            deployment_id=d["execution_context"]["deployment_id"],
        )
        return cls(
            schema_version=d["schema_version"],
            event_id=d["event_id"],
            timestamp=d["timestamp"],
            jurisdiction_id=d["jurisdiction_id"],
            actor=actor,
            execution_context=ec,
            task_id=d["task_id"],
            action=d["action"],
            visibility=d["visibility"],
            previous_event_hash=d["previous_event_hash"],
            event_hash=d["event_hash"],
            signature=d["signature"],
            signing_key_id=d["signing_key_id"],
            delegation_id=d.get("delegation_id"),
            authorization_id=d.get("authorization_id"),
            approval_id=d.get("approval_id"),
            resource_id=d.get("resource_id"),
            before_digest=d.get("before_digest"),
            after_digest=d.get("after_digest"),
            policy_version=d.get("policy_version", "1.0.0"),
        )


__all__ = ["ACTIONS", "VISIBILITY_TIERS", "SCHEMA_VERSION", "Actor", "ExecutionContext", "Event"]
