"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/api/server.py
Purpose: FastAPI server exposing AegisTrace operations
Classification: application
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from aegistrace.events.collector import EventCollector
from aegistrace.events.models import ACTIONS, VISIBILITY_TIERS
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier


class EventRequest(BaseModel):
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
    signing_key_id: str
    jurisdiction_id: str = "ca"
    delegation_id: str | None = None
    authorization_id: str | None = None
    approval_id: str | None = None
    resource_id: str | None = None
    before_digest: str | None = None
    after_digest: str | None = None


def create_app(
    *,
    registry: Registry | None = None,
    key_service: KeyService | None = None,
    ledger: AppendOnlyLedger | None = None,
) -> FastAPI:
    """Create a FastAPI app bound to the given AegisTrace components.

    For production use, supply persistent components; for tests, the
    defaults are in-memory.
    """
    app = FastAPI(
        title="AegisTrace",
        description="Reference HTTP API for the AI-IDP standard",
        version="2.0.0",
    )

    state: dict[str, Any] = {
        "registry": registry or Registry(),
        "keys": key_service or KeyService(),
        "ledger": ledger or AppendOnlyLedger(),
    }
    state["collector"] = EventCollector(state["ledger"], state["keys"])
    state["verifier"] = LedgerVerifier(state["keys"])

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": "2.0.0"}

    @app.get("/actions")
    def list_actions() -> list[str]:
        return list(ACTIONS)

    @app.get("/visibilities")
    def list_visibilities() -> list[str]:
        return list(VISIBILITY_TIERS)

    @app.post("/events")
    def record_event(req: EventRequest) -> dict[str, Any]:
        from aegistrace.events.models import Actor, ExecutionContext
        try:
            actor = Actor(
                controller_id=req.controller_id,
                principal_id=req.principal_id,
                agent_id=req.agent_id,
                agent_instance_id=req.agent_instance_id,
            )
            ec = ExecutionContext(
                provider_id=req.provider_id,
                model_id=req.model_id,
                model_version_id=req.model_version_id,
                deployment_id=req.deployment_id,
            )
            event = state["collector"].record(
                actor=actor,
                execution_context=ec,
                task_id=req.task_id,
                action=req.action,
                visibility=req.visibility,
                signing_key_id=req.signing_key_id,
                jurisdiction_id=req.jurisdiction_id,
                delegation_id=req.delegation_id,
                authorization_id=req.authorization_id,
                approval_id=req.approval_id,
                resource_id=req.resource_id,
                before_digest=req.before_digest,
                after_digest=req.after_digest,
            )
            return event.to_dict()
        except (ValueError, PermissionError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/events")
    def list_events() -> list[dict[str, Any]]:
        return [e.to_dict() for e in state["ledger"].events()]

    @app.get("/events/{event_id}")
    def get_event(event_id: str) -> dict[str, Any]:
        e = state["ledger"].get(event_id)
        if e is None:
            raise HTTPException(status_code=404, detail="event not found")
        return e.to_dict()

    @app.post("/verify")
    def verify_ledger() -> dict[str, Any]:
        report = state["verifier"].verify(state["ledger"])
        return {
            "ok": report.ok,
            "failures": report.failures,
            "failing_event_ids": report.failing_event_ids,
        }

    @app.get("/registry/{entity_id}")
    def get_entity(entity_id: str) -> dict[str, Any]:
        rec = state["registry"].get(entity_id)
        if rec is None:
            raise HTTPException(status_code=404, detail="entity not found")
        return {
            "entity_id": rec.entity_id,
            "entity_type": rec.entity_type,
            "state": rec.state,
            "attributes": rec.attributes,
            "created_at": rec.created_at,
        }

    return app


# Module-level app for `uvicorn aegistrace.api.server:app`
app = create_app()


__all__ = ["create_app", "app", "EventRequest"]
