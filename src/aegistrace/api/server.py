"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/api/server.py
Purpose: Public-safe FastAPI server exposing authenticated governed AegisTrace operations
Classification: presentation
Version: 2.1.0
Last Material Revision: 2026-09-07
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from aegistrace.api.authentication import ActionRequestAuthenticator, RequestAuthenticationError
from aegistrace.api.replay import ReplayReservationStore
from aegistrace.authorization.consumption import ApprovalConsumptionStore
from aegistrace.authorization.engine import PolicyEngine
from aegistrace.authorization.entitlements import ApproverEntitlementProvider
from aegistrace.authorization.scope import ScopeContext
from aegistrace.delegation.broker import DelegationBroker
from aegistrace.disclosure.public import PublicEventProjector, PublicProjectionError
from aegistrace.events.collector import EventCollector
from aegistrace.events.models import ACTIONS, VISIBILITY_TIERS, Actor, ExecutionContext
from aegistrace.governance.service import GovernanceDenied, GovernedEventService
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier
from aegistrace.version import __version__


class ScopeContextRequest(BaseModel):
    task_class: str | None = None
    resource_class: str | None = None
    geography: str | None = None
    tool_class: str | None = None
    model_class: str | None = None
    provider_class: str | None = None
    evaluated_at: str | None = None
    requested_delegation_depth: int | None = Field(default=None, ge=0)

    def to_domain(self) -> ScopeContext:
        return ScopeContext(**self.model_dump())


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
    authorization_id: str
    jurisdiction_id: str = "ca"
    delegation_id: str | None = None
    approval_id: str | None = None
    approval_ids: list[str] = Field(default_factory=list)
    scope_context: ScopeContextRequest | None = None
    resource_id: str | None = None
    before_digest: str | None = None
    after_digest: str | None = None
    request_timestamp: str
    request_nonce: str = Field(min_length=16, max_length=256)
    request_signature: str


def create_app(
    *,
    registry: Registry | None = None,
    key_service: KeyService | None = None,
    ledger: AppendOnlyLedger | None = None,
    policy_engine: PolicyEngine | None = None,
    delegation_broker: DelegationBroker | None = None,
    request_authenticator: ActionRequestAuthenticator | None = None,
    replay_store: ReplayReservationStore | None = None,
    approval_consumption_store: ApprovalConsumptionStore | None = None,
    approver_entitlements: ApproverEntitlementProvider | None = None,
) -> FastAPI:
    """Create a fail-closed public API bound to shared AegisTrace services.

    Operational writes require two independent checks before canonical append:
    cryptographic request authentication (agent proof-of-possession + atomic
    nonce reservation) and AI-IDP governance authorization/delegation/approval
    evaluation. Public reads expose only explicit disclosure projections.

    High-assurance deployments should inject the same durable storage backend
    (for example PostgresStorage) as both ``replay_store`` and
    ``approval_consumption_store``. If a preconfigured PolicyEngine or request
    authenticator is supplied, their corresponding stores must be configured on
    those objects instead of also passing them here.
    """
    if policy_engine is not None and (
        approval_consumption_store is not None or approver_entitlements is not None
    ):
        raise ValueError(
            "approval_consumption_store/approver_entitlements cannot be supplied "
            "with a preconfigured policy_engine"
        )
    if request_authenticator is not None and replay_store is not None:
        raise ValueError(
            "replay_store cannot be supplied with a preconfigured request_authenticator"
        )

    keys = key_service or KeyService()
    entity_registry = registry or Registry()
    # AppendOnlyLedger implements ``__len__``. An injected empty ledger is
    # therefore falsey and must be distinguished from no ledger being supplied.
    event_ledger = ledger if ledger is not None else AppendOnlyLedger()
    policy = policy_engine or PolicyEngine(
        keys,
        approval_consumption_store=approval_consumption_store,
        approver_entitlements=approver_entitlements,
    )
    delegations = delegation_broker or DelegationBroker(keys)
    collector = EventCollector(event_ledger, keys)
    governed = GovernedEventService(
        collector=collector,
        policy_engine=policy,
        delegation_broker=delegations,
        registry=entity_registry,
    )
    verifier = LedgerVerifier(keys)
    projector = PublicEventProjector()
    authenticator = request_authenticator or ActionRequestAuthenticator(
        keys,
        replay_store=replay_store,
    )

    app = FastAPI(
        title="AegisTrace",
        description="Reference HTTP API for the proposed AI-IDP standard",
        version=__version__,
    )
    app.state.aegistrace = {
        "registry": entity_registry,
        "keys": keys,
        "ledger": event_ledger,
        "policy": policy,
        "delegations": delegations,
        "collector": collector,
        "governed": governed,
        "verifier": verifier,
        "projector": projector,
        "authenticator": authenticator,
    }

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "version": __version__,
            "write_boundary": "authenticated+governed",
        }

    @app.get("/actions")
    def list_actions() -> list[str]:
        return list(ACTIONS)

    @app.get("/visibilities")
    def list_visibilities() -> list[str]:
        return list(VISIBILITY_TIERS)

    @app.post("/events")
    def record_event(request: EventRequest) -> dict[str, Any]:
        signed_payload = request.model_dump(exclude={"request_signature"}, exclude_none=True)
        try:
            authenticator.verify_and_reserve(signed_payload, request.request_signature)
        except RequestAuthenticationError as exc:
            raise HTTPException(status_code=401, detail="action request authentication failed") from exc

        actor = Actor(
            controller_id=request.controller_id,
            principal_id=request.principal_id,
            agent_id=request.agent_id,
            agent_instance_id=request.agent_instance_id,
        )
        execution_context = ExecutionContext(
            provider_id=request.provider_id,
            model_id=request.model_id,
            model_version_id=request.model_version_id,
            deployment_id=request.deployment_id,
        )
        scope_context = request.scope_context.to_domain() if request.scope_context else None
        try:
            event = governed.record(
                actor=actor,
                execution_context=execution_context,
                task_id=request.task_id,
                action=request.action,
                visibility=request.visibility,
                signing_key_id=request.signing_key_id,
                authorization_id=request.authorization_id,
                jurisdiction_id=request.jurisdiction_id,
                delegation_id=request.delegation_id,
                approval_id=request.approval_id,
                approval_ids=request.approval_ids,
                scope_context=scope_context,
                resource_id=request.resource_id,
                before_digest=request.before_digest,
                after_digest=request.after_digest,
            )
            return event.to_dict()
        except GovernanceDenied as exc:
            raise HTTPException(
                status_code=403,
                detail={"reason": exc.reason, "denial_event_id": exc.denial_event_id},
            ) from exc
        except (ValueError, PermissionError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/events")
    def list_public_events() -> list[dict[str, Any]]:
        return projector.project_many(event_ledger.events())

    @app.get("/events/{event_id}")
    def get_public_event(event_id: str) -> dict[str, Any]:
        event = event_ledger.get(event_id)
        if event is None or event.visibility != "PUBLIC":
            raise HTTPException(status_code=404, detail="public event not found")
        try:
            return projector.project(event)
        except PublicProjectionError as exc:
            raise HTTPException(status_code=404, detail="public event not found") from exc

    @app.post("/verify")
    def verify_ledger() -> dict[str, Any]:
        report = verifier.verify(event_ledger)
        return {
            "ok": report.ok,
            "failure_count": len(report.failures),
            "verification_mode": report.verification_mode,
            "verified_signature_count": report.verified_signature_count,
        }

    @app.get("/verification/keys")
    def public_verification_keys() -> dict[str, Any]:
        public_key_ids = {
            event.signing_key_id for event in event_ledger.events() if event.visibility == "PUBLIC"
        }
        return keys.export_public_registry(key_ids=public_key_ids)

    @app.get("/registry/{entity_id:path}")
    def get_public_entity(entity_id: str) -> dict[str, Any]:
        record = entity_registry.get(entity_id)
        if record is None or record.attributes.get("public") is not True:
            raise HTTPException(status_code=404, detail="public entity not found")
        public_attributes = record.attributes.get("public_attributes", {})
        if not isinstance(public_attributes, dict):
            raise HTTPException(status_code=500, detail="invalid public registry projection")
        return {
            "entity_id": record.entity_id,
            "entity_type": record.entity_type,
            "state": record.state,
            "created_at": record.created_at,
            "attributes": dict(public_attributes),
        }

    return app


app = create_app()


__all__ = ["create_app", "app", "EventRequest", "ScopeContextRequest"]
