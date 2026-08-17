"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/governance/service.py
Purpose: Fail-closed governed execution boundary
Classification: service
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from threading import RLock

from aegistrace.authorization.engine import PolicyEngine
from aegistrace.authorization.scope import ScopeContext
from aegistrace.delegation.broker import DelegationBroker
from aegistrace.events.collector import EventCollector
from aegistrace.events.models import Actor, Event, ExecutionContext
from aegistrace.identity.lifecycle import EntityRecord, Registry


class GovernanceDenied(PermissionError):
    """Raised when an action cannot cross the governed execution boundary."""

    def __init__(self, reason: str, *, denial_event_id: str | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.denial_event_id = denial_event_id


class GovernedEventService:
    """Authorize an action before it becomes canonical AegisTrace evidence.

    The low-level ``EventCollector`` remains available for evidence import,
    verification fixtures, and explicitly evidence-only workflows. Operational
    action execution should cross this service instead. The service serializes
    in-process governance decisions so approval selection, canonical append,
    and approval consumption cannot interleave with another governed write.
    """

    def __init__(
        self,
        *,
        collector: EventCollector,
        policy_engine: PolicyEngine,
        delegation_broker: DelegationBroker,
        registry: Registry,
    ) -> None:
        self._collector = collector
        self._policy = policy_engine
        self._delegations = delegation_broker
        self._registry = registry
        self._lock = RLock()

    def record(
        self,
        *,
        actor: Actor,
        execution_context: ExecutionContext,
        task_id: str,
        action: str,
        visibility: str,
        signing_key_id: str,
        authorization_id: str,
        jurisdiction_id: str = "ca",
        delegation_id: str | None = None,
        approval_id: str | None = None,
        approval_ids: list[str] | tuple[str, ...] | None = None,
        scope_context: ScopeContext | None = None,
        resource_id: str | None = None,
        before_digest: str | None = None,
        after_digest: str | None = None,
        record_denial: bool = True,
    ) -> Event:
        with self._lock:
            try:
                self._validate_registry_chain(
                    actor=actor,
                    execution_context=execution_context,
                    task_id=task_id,
                )
                authorization = self._policy.get_authorization(authorization_id)
                if authorization is None:
                    raise GovernanceDenied("authorization not found")
                if authorization.controller_id != actor.controller_id:
                    raise GovernanceDenied("authorization controller does not match actor controller")
                if authorization.principal_id != actor.principal_id:
                    raise GovernanceDenied("authorization principal does not match actor principal")
                if authorization.agent_id != actor.agent_id:
                    raise GovernanceDenied("authorization agent does not match actor agent")
                if authorization.task_id != task_id:
                    raise GovernanceDenied("authorization task does not match event task")

                if authorization.delegation_id != delegation_id:
                    if authorization.delegation_id is not None or delegation_id is not None:
                        raise GovernanceDenied("authorization and event delegation references do not match")

                decision = self._policy.evaluate(
                    action=action,
                    authorization_id=authorization_id,
                    approval_id=approval_id,
                    approval_ids=approval_ids,
                    scope_context=scope_context,
                )
                if not decision.permitted:
                    raise GovernanceDenied(decision.reason)

                delegation_chain: list[str] = []
                if delegation_id is not None:
                    if not self._delegations.verify_action(
                        delegation_id,
                        child_agent_id=actor.agent_id,
                        principal_id=actor.principal_id,
                        controller_id=actor.controller_id,
                        action=action,
                        context=scope_context,
                    ):
                        raise GovernanceDenied("delegation chain is missing, invalid, revoked, expired, or outside scope")
                    delegation_chain = self._delegations.delegation_chain(delegation_id)
                    agent_record = self._registry.resolve(actor.agent_id)
                    expected_parent_delegation = agent_record.attributes.get("parent_delegation_id")
                    if expected_parent_delegation is not None and expected_parent_delegation != delegation_id:
                        raise GovernanceDenied("agent registry binding points to a different parent delegation")
                else:
                    agent_record = self._registry.resolve(actor.agent_id)
                    if agent_record.attributes.get("parent_delegation_id") is not None:
                        raise GovernanceDenied("delegated child agent is missing its parent delegation reference")

                event = self._collector.record(
                    actor=actor,
                    execution_context=execution_context,
                    task_id=task_id,
                    action=action,
                    visibility=visibility,
                    signing_key_id=signing_key_id,
                    jurisdiction_id=jurisdiction_id,
                    delegation_id=delegation_id,
                    delegation_chain=delegation_chain,
                    authorization_id=authorization_id,
                    approval_id=approval_id,
                    approval_ids=list(decision.satisfied_approval_ids),
                    scope_context=scope_context,
                    governance_mode="GOVERNED",
                    resource_id=resource_id,
                    before_digest=before_digest,
                    after_digest=after_digest,
                    policy_version=authorization.policy_version,
                )

                if decision.satisfied_approval_ids and not self._policy.consume_approvals(
                    decision.satisfied_approval_ids
                ):
                    raise RuntimeError(
                        "canonical event was appended but approval consumption failed; "
                        "the ledger must be treated as incident evidence"
                    )
                return event
            except GovernanceDenied as exc:
                denial_event_id = None
                if record_denial:
                    denial_event_id = self._record_denial(
                        actor=actor,
                        execution_context=execution_context,
                        task_id=task_id,
                        requested_action=action,
                        visibility=visibility,
                        signing_key_id=signing_key_id,
                        jurisdiction_id=jurisdiction_id,
                        delegation_id=delegation_id,
                        authorization_id=authorization_id,
                        scope_context=scope_context,
                        resource_id=resource_id,
                        reason=exc.reason,
                    )
                raise GovernanceDenied(exc.reason, denial_event_id=denial_event_id) from exc

    def _validate_registry_chain(
        self,
        *,
        actor: Actor,
        execution_context: ExecutionContext,
        task_id: str,
    ) -> None:
        controller = self._require_active(actor.controller_id, "controller")
        principal = self._require_active(actor.principal_id, "principal")
        agent = self._require_active(actor.agent_id, "agent")
        instance = self._require_active(actor.agent_instance_id, "agent-instance")
        self._require_active(execution_context.provider_id, "provider")
        self._require_active(execution_context.model_id, "model")
        self._require_active(execution_context.model_version_id, "model")
        self._require_active(execution_context.deployment_id, "deployment")
        self._require_active(task_id, "task")

        del controller, principal
        bound_controller = agent.attributes.get("controller_id")
        if bound_controller is None:
            raise GovernanceDenied("agent registry record is missing controller_id binding")
        if bound_controller != actor.controller_id:
            raise GovernanceDenied("agent registry controller binding does not match actor controller")

        bound_agent = instance.attributes.get("agent_id")
        if bound_agent is None:
            raise GovernanceDenied("agent-instance registry record is missing agent_id binding")
        if bound_agent != actor.agent_id:
            raise GovernanceDenied("agent-instance registry binding does not match persistent agent")

    def _require_active(self, entity_id: str, expected_type: str) -> EntityRecord:
        try:
            record = self._registry.resolve(entity_id)
        except KeyError as exc:
            raise GovernanceDenied(f"unresolvable {expected_type}: {entity_id}") from exc
        if record.entity_type != expected_type:
            raise GovernanceDenied(
                f"registry entity type mismatch for {entity_id}: {record.entity_type} != {expected_type}"
            )
        if not record.is_active():
            raise GovernanceDenied(f"{expected_type} is not active: {entity_id} (state={record.state})")
        return record

    def _record_denial(
        self,
        *,
        actor: Actor,
        execution_context: ExecutionContext,
        task_id: str,
        requested_action: str,
        visibility: str,
        signing_key_id: str,
        jurisdiction_id: str,
        delegation_id: str | None,
        authorization_id: str,
        scope_context: ScopeContext | None,
        resource_id: str | None,
        reason: str,
    ) -> str | None:
        """Best-effort denial evidence; denial itself never becomes permission."""
        try:
            event = self._collector.record(
                actor=actor,
                execution_context=execution_context,
                task_id=task_id,
                action="DENY",
                visibility=visibility,
                signing_key_id=signing_key_id,
                jurisdiction_id=jurisdiction_id,
                delegation_id=delegation_id,
                authorization_id=authorization_id,
                scope_context=scope_context,
                governance_mode="DENIAL",
                decision_reason=f"requested_action={requested_action}; reason={reason}",
                resource_id=resource_id,
                policy_version=self._policy.policy_version,
            )
            return event.event_id
        except Exception:
            return None


__all__ = ["GovernanceDenied", "GovernedEventService"]
