"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/api/authentication.py
Purpose: Cryptographic authentication and replay resistance for action requests
Classification: service
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from typing import Any, Mapping

from aegistrace.identity.ids import require_identifier_type
from aegistrace.identity.keys import KeyService
from aegistrace.signing.canonical import canonicalize
from aegistrace.signing.ed25519 import SigningKey

_SIGNED_FIELDS = (
    "controller_id",
    "principal_id",
    "agent_id",
    "agent_instance_id",
    "provider_id",
    "model_id",
    "model_version_id",
    "deployment_id",
    "task_id",
    "action",
    "visibility",
    "signing_key_id",
    "authorization_id",
    "jurisdiction_id",
    "delegation_id",
    "approval_id",
    "approval_ids",
    "scope_context",
    "resource_id",
    "before_digest",
    "after_digest",
    "request_timestamp",
    "request_nonce",
)


class RequestAuthenticationError(PermissionError):
    """Raised when a submitted action request is unauthenticated or replayed."""


def normalize_action_request(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize the exact fields covered by an action-request signature."""
    normalized: dict[str, Any] = {}
    for field_name in _SIGNED_FIELDS:
        if field_name not in payload:
            continue
        value = payload[field_name]
        if value is None:
            continue
        if field_name == "approval_ids":
            normalized[field_name] = list(value or [])
        elif field_name == "scope_context" and hasattr(value, "model_dump"):
            normalized[field_name] = value.model_dump(exclude_none=True)
        else:
            normalized[field_name] = value
    normalized.setdefault("approval_ids", [])
    normalized.setdefault("jurisdiction_id", "ca")
    return normalized


def action_request_message(payload: Mapping[str, Any]) -> bytes:
    """Return deterministic bytes that an agent signs before API submission."""
    return canonicalize(normalize_action_request(payload))


class ActionRequestAuthenticator:
    """Verify agent proof-of-possession and reject request replays.

    The default replay cache is process-local and suitable for the reference
    server. A high-assurance multi-node deployment must back this contract with
    shared durable nonce storage so replay protection survives restarts and
    coordinates across replicas.
    """

    def __init__(self, key_service: KeyService, *, max_clock_skew_seconds: int = 300) -> None:
        if max_clock_skew_seconds <= 0:
            raise ValueError("max_clock_skew_seconds must be positive")
        self._keys = key_service
        self._max_clock_skew_seconds = max_clock_skew_seconds
        self._used_nonces: set[tuple[str, str]] = set()
        self._lock = RLock()

    def verify_and_reserve(self, payload: Mapping[str, Any], signature: str) -> None:
        key_id = _required_string(payload, "signing_key_id")
        agent_id = _required_string(payload, "agent_id")
        request_timestamp = _required_string(payload, "request_timestamp")
        nonce = _required_string(payload, "request_nonce")

        require_identifier_type(key_id, "key")
        require_identifier_type(agent_id, "agent")
        if len(nonce) < 16 or len(nonce) > 256:
            raise RequestAuthenticationError("request_nonce must be between 16 and 256 characters")

        try:
            timestamp = _parse_timestamp(request_timestamp)
        except ValueError as exc:
            raise RequestAuthenticationError(f"invalid request_timestamp: {exc}") from exc
        skew = abs((datetime.now(UTC) - timestamp).total_seconds())
        if skew > self._max_clock_skew_seconds:
            raise RequestAuthenticationError("request_timestamp is outside the accepted clock-skew window")

        try:
            key_record = self._keys.get_record(key_id)
        except KeyError as exc:
            raise RequestAuthenticationError("request signing key is unknown") from exc
        if not key_record.is_active():
            raise RequestAuthenticationError("request signing key is not active")
        if key_record.bound_entity_id != agent_id:
            raise RequestAuthenticationError("request signing key is not bound to the acting agent")

        try:
            public_key = SigningKey.from_public_pem(key_id, key_record.public_pem).public_key
        except Exception as exc:
            raise RequestAuthenticationError("request verification key is invalid") from exc
        if not SigningKey.verify(public_key, action_request_message(payload), signature):
            raise RequestAuthenticationError("request signature is invalid")

        nonce_key = (key_id, nonce)
        with self._lock:
            if nonce_key in self._used_nonces:
                raise RequestAuthenticationError("request nonce has already been used")
            self._used_nonces.add(nonce_key)


def _required_string(payload: Mapping[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value:
        raise RequestAuthenticationError(f"{field_name} is required")
    return value


def _parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timezone is required")
    return parsed.astimezone(UTC)


__all__ = [
    "ActionRequestAuthenticator",
    "RequestAuthenticationError",
    "action_request_message",
    "normalize_action_request",
]
