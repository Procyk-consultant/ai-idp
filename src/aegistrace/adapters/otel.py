"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/adapters/otel.py
Purpose: OpenTelemetry runtime exporter for AegisTrace events
Classification: adapter
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.

This adapter exports AegisTrace events as OpenTelemetry spans, allowing
integration with existing observability stacks (Jaeger, Tempo, Datadog,
Honeycomb, New Relic, etc.) that consume OTLP.

The adapter does NOT replace the canonical AegisTrace ledger. It
complements the ledger by providing real-time observability of agent
operations. The ledger remains the source of truth for accountability;
the OTel exporter provides operational visibility.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import SpanKind, Status, StatusCode
    _OTEL_AVAILABLE = True
except ImportError:
    _OTEL_AVAILABLE = False


@dataclass
class OTelConfig:
    """Configuration for the OpenTelemetry exporter.

    Default OTLP endpoint is http://localhost:4318/v1/traces (standard
    OTLP/HTTP). Production deployments should set the endpoint via env:
        OTEL_EXPORTER_OTLP_ENDPOINT=https://your-collector:4318
        OTEL_EXPORTER_OTLP_HEADERS=x-api-key=your-key
    """
    service_name: str = "aegistrace"
    service_namespace: str = "cognitive-industries"
    service_version: str = "2.0.0"
    endpoint: str = ""  # if empty, uses OTEL_EXPORTER_OTLP_ENDPOINT env
    headers: dict[str, str] = None  # type: ignore

    @classmethod
    def from_env(cls) -> OTelConfig:
        return cls(
            service_name=os.environ.get("OTEL_SERVICE_NAME", "aegistrace"),
            service_namespace=os.environ.get("OTEL_SERVICE_NAMESPACE", "cognitive-industries"),
            service_version=os.environ.get("OTEL_SERVICE_VERSION", "2.0.0"),
            endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", ""),
            headers=dict(pair.split("=", 1) for pair in os.environ.get("OTEL_EXPORTER_OTLP_HEADERS", "").split(",") if "=" in pair) or None,
        )


class OTelExporter:
    """Exports AegisTrace events as OpenTelemetry spans.

    The exporter creates a span for each event, with:
        - Span name: "aegistrace.event.<action>"
        - Span kind: INTERNAL (or CLIENT for external-effect actions)
        - Attributes: all event fields (event_id, timestamp, actor, execution_context, etc.)
        - Status: OK if the event was recorded successfully; ERROR otherwise

    The exporter is non-blocking: events are queued and sent in batches
    by the OpenTelemetry SDK's BatchSpanProcessor.

    The exporter is optional: if OpenTelemetry is not installed, the
    exporter is a no-op.
    """

    def __init__(self, config: OTelConfig | None = None) -> None:
        self.config = config or OTelConfig.from_env()
        self._tracer: Any | None = None
        if not _OTEL_AVAILABLE:
            self._available = False
            return
        self._available = True
        self._init_tracer()

    def _init_tracer(self) -> None:
        resource = Resource.create({
            "service.name": self.config.service_name,
            "service.namespace": self.config.service_namespace,
            "service.version": self.config.service_version,
        })
        provider = TracerProvider(resource=resource)
        endpoint = self.config.endpoint or None
        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            headers=self.config.headers,
        )
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        self._tracer = trace.get_tracer("aegistrace")

    @property
    def available(self) -> bool:
        return self._available

    # Actions that involve external effects (use CLIENT span kind)
    EXTERNAL_ACTIONS = {
        "TRANSMIT", "RECEIVE", "UPLOAD", "DOWNLOAD", "EXPORT", "IMPORT",
        "PUBLISH", "DEPLOY", "RELEASE", "CALL_API", "TRIGGER_EXTERNAL_EFFECT",
    }

    def export_event(self, event_dict: dict[str, Any]) -> None:
        """Export an AegisTrace event as an OTel span.

        Args:
            event_dict: The event as a dict (Event.to_dict() output).
        """
        if not self._available or self._tracer is None:
            return
        action = event_dict.get("action", "UNKNOWN")
        span_name = f"aegistrace.event.{action.lower()}"
        kind = SpanKind.CLIENT if action in self.EXTERNAL_ACTIONS else SpanKind.INTERNAL
        # Build attributes from the event
        attributes: dict[str, Any] = {
            "aegistrace.event_id": event_dict.get("event_id", ""),
            "aegistrace.timestamp": event_dict.get("timestamp", ""),
            "aegistrace.jurisdiction": event_dict.get("jurisdiction_id", ""),
            "aegistrace.action": action,
            "aegistrace.visibility": event_dict.get("visibility", ""),
            "aegistrace.policy_version": event_dict.get("policy_version", ""),
            "aegistrace.event_hash": event_dict.get("event_hash", ""),
            "aegistrace.signing_key_id": event_dict.get("signing_key_id", ""),
        }
        # Actor
        actor = event_dict.get("actor", {})
        if actor:
            attributes["aegistrace.actor.controller_id"] = actor.get("controller_id", "")
            attributes["aegistrace.actor.principal_id"] = actor.get("principal_id", "")
            attributes["aegistrace.actor.agent_id"] = actor.get("agent_id", "")
            attributes["aegistrace.actor.agent_instance_id"] = actor.get("agent_instance_id", "")
        # Execution context
        ec = event_dict.get("execution_context", {})
        if ec:
            attributes["aegistrace.ec.provider_id"] = ec.get("provider_id", "")
            attributes["aegistrace.ec.model_id"] = ec.get("model_id", "")
            attributes["aegistrace.ec.model_version_id"] = ec.get("model_version_id", "")
            attributes["aegistrace.ec.deployment_id"] = ec.get("deployment_id", "")
        # Optional fields
        for field in ("task_id", "delegation_id", "authorization_id", "approval_id", "resource_id", "before_digest", "after_digest"):
            if field in event_dict and event_dict[field] is not None:
                attributes[f"aegistrace.{field}"] = str(event_dict[field])
        # Create the span
        with self._tracer.start_as_current_span(span_name, kind=kind) as span:
            for k, v in attributes.items():
                span.set_attribute(k, v)
            span.set_status(Status(StatusCode.OK))

    def flush(self) -> None:
        """Flush pending spans to the OTLP endpoint."""
        if not self._available:
            return
        provider = trace.get_tracer_provider()
        if hasattr(provider, "force_flush"):
            provider.force_flush()


class OTelEventHook:
    """Hook that connects the AegisTrace EventCollector to the OTel exporter.

    Usage:
        exporter = OTelExporter()
        hook = OTelEventHook(exporter)
        collector.on_append = hook.on_event
    """

    def __init__(self, exporter: OTelExporter) -> None:
        self._exporter = exporter

    def on_event(self, event: Any) -> None:
        """Called when an event is appended to the ledger."""
        if hasattr(event, "to_dict"):
            self._exporter.export_event(event.to_dict())
        elif isinstance(event, dict):
            self._exporter.export_event(event)


__all__ = ["OTelConfig", "OTelExporter", "OTelEventHook"]
