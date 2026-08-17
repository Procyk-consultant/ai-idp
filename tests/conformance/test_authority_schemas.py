"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/conformance/test_authority_schemas.py
Purpose: Conformance tests for signed authorization and exact-action approval schemas
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from aegistrace.authorization.engine import Approval, Authorization, PolicyEngine
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"
ACTION_DIGEST = "sha256:" + "a" * 64


def _load(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


def _authorization_dict(record: Authorization) -> dict:
    result = {
        "authorization_id": record.authorization_id,
        "principal_id": record.principal_id,
        "controller_id": record.controller_id,
        "agent_id": record.agent_id,
        "task_id": record.task_id,
        "scope": record.scope,
        "policy_version": record.policy_version,
        "state": record.state,
        "issued_at": record.issued_at,
        "signature": record.signature,
        "signing_key_id": record.signing_key_id,
    }
    if record.delegation_id is not None:
        result["delegation_id"] = record.delegation_id
    if record.expires_at is not None:
        result["expires_at"] = record.expires_at
    return result


def _approval_dict(record: Approval) -> dict:
    result = {
        "approval_id": record.approval_id,
        "action": record.action,
        "action_digest": record.action_digest,
        "approver_id": record.approver_id,
        "authorization_id": record.authorization_id,
        "policy_version": record.policy_version,
        "approved_at": record.approved_at,
        "used": record.used,
        "signature": record.signature,
        "signing_key_id": record.signing_key_id,
    }
    if record.expires_at is not None:
        result["expires_at"] = record.expires_at
    if record.used_at is not None:
        result["used_at"] = record.used_at
    return result


class TestAuthoritySchemas:
    def test_signed_authorization_conforms_to_schema(self) -> None:
        keys = KeyService()
        controller = str(make_identifier("controller", "c1"))
        principal = str(make_identifier("principal", "p1"))
        key_id = str(make_identifier("key", "controller-key"))
        keys.create_key(key_id, bound_entity_id=controller)
        engine = PolicyEngine(keys)
        authorization = engine.issue_authorization(
            principal_id=principal,
            controller_id=controller,
            agent_id=str(make_identifier("agent", "a1")),
            task_id=str(make_identifier("task", "t1")),
            scope={
                "action_classes": ["PUBLISH"],
                "resource_classes": ["artifact"],
                "geography": ["ca-qc"],
            },
            signing_key_id=key_id,
        )
        jsonschema.validate(_authorization_dict(authorization), _load("authorization"))

    def test_signed_exact_action_approval_conforms_to_schema_before_and_after_use(self) -> None:
        keys = KeyService()
        controller = str(make_identifier("controller", "c1"))
        principal = str(make_identifier("principal", "p1"))
        controller_key = str(make_identifier("key", "controller-key"))
        principal_key = str(make_identifier("key", "principal-key"))
        keys.create_key(controller_key, bound_entity_id=controller)
        keys.create_key(principal_key, bound_entity_id=principal)
        engine = PolicyEngine(keys)
        authorization = engine.issue_authorization(
            principal_id=principal,
            controller_id=controller,
            agent_id=str(make_identifier("agent", "a1")),
            task_id=str(make_identifier("task", "t1")),
            scope={"action_classes": ["PUBLISH"]},
            signing_key_id=controller_key,
        )
        approval = engine.issue_approval(
            action="PUBLISH",
            action_digest=ACTION_DIGEST,
            approver_id=principal,
            authorization_id=authorization.authorization_id,
            signing_key_id=principal_key,
        )
        jsonschema.validate(_approval_dict(approval), _load("approval"))
        assert engine.use_approval(approval.approval_id)
        used = engine.get_approval(approval.approval_id)
        assert used is not None and used.used and used.used_at is not None
        jsonschema.validate(_approval_dict(used), _load("approval"))
