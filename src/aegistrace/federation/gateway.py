"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/federation/gateway.py
Purpose: Reference federation gateway for cross-registry resolution and verification
Classification: service
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from threading import RLock
from typing import Any, Protocol
from urllib.parse import quote

import requests

from aegistrace.signing.canonical import canonicalize_for_hash, canonicalize_for_signature
from aegistrace.signing.ed25519 import SigningKey, sha256_hex

_PUBLIC_ENTITY_FIELDS = frozenset(
    {"entity_id", "entity_type", "state", "created_at", "attributes"}
)
_PUBLIC_EVENT_FIELDS = frozenset(
    {
        "projection_schema",
        "schema_version",
        "event_id",
        "timestamp",
        "jurisdiction_id",
        "visibility",
        "policy_version",
        "previous_event_hash",
        "event_hash",
        "signature",
        "signing_key_id",
    }
)


class FederationResolutionError(RuntimeError):
    """Raised when a federated operation cannot be completed safely."""


class FederatedRegistryClient(Protocol):
    """Client contract for one remote AI-IDP registry authority."""

    def health(self) -> bool: ...

    def resolve_public_entity(self, entity_id: str) -> dict[str, Any] | None: ...

    def get_public_event(self, event_id: str) -> dict[str, Any] | None: ...

    def get_public_verification_keys(self) -> dict[str, Any]: ...


@dataclass(frozen=True)
class FederationAgreement:
    """Locally configured recognition contract for a remote registry authority."""

    agreement_id: str
    local_authority_id: str
    remote_authority_id: str
    effective_at: str
    expires_at: str | None = None
    allowed_visibility_tiers: tuple[str, ...] = ("PUBLIC",)
    state: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_active(self, *, at: datetime | None = None) -> bool:
        if self.state != "active":
            return False
        moment = at or datetime.now(UTC)
        try:
            if moment < _parse_timestamp(self.effective_at):
                return False
            if self.expires_at is not None and moment >= _parse_timestamp(self.expires_at):
                return False
        except ValueError:
            return False
        return True


@dataclass(frozen=True)
class FederationBreak:
    authority_id: str
    detected_at: str
    reason: str
    agreement_id: str


@dataclass
class _CacheEntry:
    value: dict[str, Any]
    expires_at: datetime


class HTTPFederatedRegistryClient:
    """HTTP client for the public AegisTrace federation surface.

    This client intentionally uses only public endpoints. Controlled/sealed
    federation requires an organization-specific authenticated client that
    implements ``FederatedRegistryClient`` or an extended internal contract.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 5.0,
        session: requests.Session | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        normalized = base_url.rstrip("/")
        if not normalized.startswith(("https://", "http://")):
            raise ValueError("base_url must use http or https")
        self._base_url = normalized
        self._timeout = timeout_seconds
        self._session = session or requests.Session()

    def health(self) -> bool:
        try:
            response = self._session.get(
                f"{self._base_url}/health",
                timeout=self._timeout,
            )
            return response.status_code == 200 and response.json().get("status") == "ok"
        except Exception:
            return False

    def resolve_public_entity(self, entity_id: str) -> dict[str, Any] | None:
        encoded = quote(entity_id, safe="")
        response = self._session.get(
            f"{self._base_url}/registry/{encoded}",
            timeout=self._timeout,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise FederationResolutionError("remote registry entity response is not an object")
        return payload

    def get_public_event(self, event_id: str) -> dict[str, Any] | None:
        response = self._session.get(
            f"{self._base_url}/events/{quote(event_id, safe='')}",
            timeout=self._timeout,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise FederationResolutionError("remote public-event response is not an object")
        return payload

    def get_public_verification_keys(self) -> dict[str, Any]:
        response = self._session.get(
            f"{self._base_url}/verification/keys",
            timeout=self._timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise FederationResolutionError("remote public-key response is not an object")
        return payload


class FederationGateway:
    """Fail-closed reference gateway for recognized registry authorities.

    A remote authority is usable only while an explicit local federation
    agreement is active. Public resolutions are cached with a bounded TTL.
    Remote failures are recorded as federation-break evidence in memory and are
    surfaced to the caller rather than silently treated as authoritative data.
    """

    def __init__(
        self,
        local_authority_id: str,
        *,
        cache_ttl_seconds: int = 300,
    ) -> None:
        if not local_authority_id:
            raise ValueError("local_authority_id is required")
        if cache_ttl_seconds <= 0:
            raise ValueError("cache_ttl_seconds must be positive")
        self.local_authority_id = local_authority_id
        self._cache_ttl = cache_ttl_seconds
        self._agreements: dict[str, FederationAgreement] = {}
        self._authority_agreement: dict[str, str] = {}
        self._clients: dict[str, FederatedRegistryClient] = {}
        self._cache: dict[tuple[str, str], _CacheEntry] = {}
        self._breaks: list[FederationBreak] = []
        self._lock = RLock()

    def register_authority(
        self,
        agreement: FederationAgreement,
        client: FederatedRegistryClient,
    ) -> None:
        if agreement.local_authority_id != self.local_authority_id:
            raise ValueError("federation agreement local authority does not match this gateway")
        if agreement.remote_authority_id == self.local_authority_id:
            raise ValueError("a federation agreement cannot target the local authority itself")
        if "PUBLIC" not in agreement.allowed_visibility_tiers:
            raise ValueError("reference public federation requires PUBLIC visibility permission")
        if not agreement.is_active():
            raise ValueError("federation agreement is not currently active")
        with self._lock:
            existing = self._authority_agreement.get(agreement.remote_authority_id)
            if existing is not None and existing != agreement.agreement_id:
                raise ValueError(
                    f"remote authority already mapped by another agreement: {agreement.remote_authority_id}"
                )
            self._agreements[agreement.agreement_id] = copy.deepcopy(agreement)
            self._authority_agreement[agreement.remote_authority_id] = agreement.agreement_id
            self._clients[agreement.remote_authority_id] = client
            self._invalidate_authority_cache(agreement.remote_authority_id)

    def revoke_agreement(self, agreement_id: str) -> None:
        with self._lock:
            agreement = self._agreements.get(agreement_id)
            if agreement is None:
                raise KeyError(agreement_id)
            revoked = FederationAgreement(
                agreement_id=agreement.agreement_id,
                local_authority_id=agreement.local_authority_id,
                remote_authority_id=agreement.remote_authority_id,
                effective_at=agreement.effective_at,
                expires_at=agreement.expires_at,
                allowed_visibility_tiers=agreement.allowed_visibility_tiers,
                state="revoked",
                metadata=copy.deepcopy(agreement.metadata),
            )
            self._agreements[agreement_id] = revoked
            self._invalidate_authority_cache(agreement.remote_authority_id)

    def resolve_public_entity(
        self,
        remote_authority_id: str,
        entity_id: str,
        *,
        force_refresh: bool = False,
    ) -> dict[str, Any] | None:
        client, agreement = self._authorized_client(remote_authority_id)
        cache_key = (remote_authority_id, entity_id)
        if not force_refresh:
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached
        try:
            payload = client.resolve_public_entity(entity_id)
        except Exception as exc:
            self._record_break(remote_authority_id, agreement, f"entity resolution failed: {exc}")
            raise FederationResolutionError(
                f"remote authority unavailable during entity resolution: {remote_authority_id}"
            ) from exc
        if payload is None:
            return None
        sanitized = self._validate_public_entity(payload, entity_id=entity_id)
        self._cache_put(cache_key, sanitized)
        return copy.deepcopy(sanitized)

    def get_public_event(
        self,
        remote_authority_id: str,
        event_id: str,
    ) -> dict[str, Any] | None:
        client, agreement = self._authorized_client(remote_authority_id)
        try:
            payload = client.get_public_event(event_id)
        except Exception as exc:
            self._record_break(remote_authority_id, agreement, f"public event lookup failed: {exc}")
            raise FederationResolutionError(
                f"remote authority unavailable during event lookup: {remote_authority_id}"
            ) from exc
        if payload is None:
            return None
        return self._validate_public_event(payload, event_id=event_id)

    def get_public_verification_keys(self, remote_authority_id: str) -> dict[str, Any]:
        client, agreement = self._authorized_client(remote_authority_id)
        try:
            payload = client.get_public_verification_keys()
        except Exception as exc:
            self._record_break(remote_authority_id, agreement, f"verification-key lookup failed: {exc}")
            raise FederationResolutionError(
                f"remote authority unavailable during key lookup: {remote_authority_id}"
            ) from exc
        if payload.get("schema") != "aegistrace.public_keys.v1":
            raise FederationResolutionError("remote authority returned an unsupported public-key registry")
        keys = payload.get("keys")
        if not isinstance(keys, list):
            raise FederationResolutionError("remote public-key registry has no key list")
        for record in keys:
            if not isinstance(record, dict):
                raise FederationResolutionError("remote public-key record is malformed")
            if not isinstance(record.get("key_id"), str) or not isinstance(record.get("public_pem"), str):
                raise FederationResolutionError("remote public-key record lacks key_id/public_pem")
        return copy.deepcopy(payload)

    def check_authority(self, remote_authority_id: str) -> bool:
        client, agreement = self._authorized_client(remote_authority_id)
        try:
            healthy = bool(client.health())
        except Exception as exc:
            self._record_break(remote_authority_id, agreement, f"health check failed: {exc}")
            return False
        if not healthy:
            self._record_break(remote_authority_id, agreement, "remote authority health check failed")
        return healthy

    def agreements(self) -> dict[str, FederationAgreement]:
        with self._lock:
            return copy.deepcopy(self._agreements)

    def federation_breaks(self) -> list[FederationBreak]:
        with self._lock:
            return list(self._breaks)

    @staticmethod
    def verify_disclosed_event(
        event: dict[str, Any],
        *,
        public_pem: str,
    ) -> bool:
        """Verify hash and Ed25519 signature of a fully disclosed event record.

        This method intentionally requires the complete event record. A public
        redacted projection is an integrity reference, not enough data to
        recompute the private canonical event hash/signature.
        """
        try:
            key_id = event["signing_key_id"]
            expected_hash = event["event_hash"]
            if sha256_hex(canonicalize_for_hash(event)) != expected_hash:
                return False
            public_key = SigningKey.from_public_pem(key_id, public_pem).public_key
            return SigningKey.verify(
                public_key,
                canonicalize_for_signature(event),
                event["signature"],
            )
        except Exception:
            return False

    def _authorized_client(
        self,
        remote_authority_id: str,
    ) -> tuple[FederatedRegistryClient, FederationAgreement]:
        with self._lock:
            agreement_id = self._authority_agreement.get(remote_authority_id)
            agreement = self._agreements.get(agreement_id) if agreement_id else None
            client = self._clients.get(remote_authority_id)
        if agreement is None or client is None:
            raise FederationResolutionError(
                f"remote authority is not recognized: {remote_authority_id}"
            )
        if not agreement.is_active():
            raise FederationResolutionError(
                f"federation agreement is inactive or expired: {agreement.agreement_id}"
            )
        return client, agreement

    def _cache_get(self, key: tuple[str, str]) -> dict[str, Any] | None:
        now = datetime.now(UTC)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            if entry.expires_at <= now:
                self._cache.pop(key, None)
                return None
            return copy.deepcopy(entry.value)

    def _cache_put(self, key: tuple[str, str], value: dict[str, Any]) -> None:
        with self._lock:
            self._cache[key] = _CacheEntry(
                value=copy.deepcopy(value),
                expires_at=datetime.now(UTC) + timedelta(seconds=self._cache_ttl),
            )

    def _invalidate_authority_cache(self, authority_id: str) -> None:
        for key in [key for key in self._cache if key[0] == authority_id]:
            self._cache.pop(key, None)

    def _record_break(
        self,
        authority_id: str,
        agreement: FederationAgreement,
        reason: str,
    ) -> None:
        record = FederationBreak(
            authority_id=authority_id,
            detected_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            reason=reason,
            agreement_id=agreement.agreement_id,
        )
        with self._lock:
            self._breaks.append(record)

    @staticmethod
    def _validate_public_entity(
        payload: dict[str, Any],
        *,
        entity_id: str,
    ) -> dict[str, Any]:
        if set(payload) - _PUBLIC_ENTITY_FIELDS:
            raise FederationResolutionError("remote public entity contains unreviewed fields")
        if payload.get("entity_id") != entity_id:
            raise FederationResolutionError("remote registry returned a different entity identifier")
        if not isinstance(payload.get("entity_type"), str) or not isinstance(payload.get("state"), str):
            raise FederationResolutionError("remote public entity lacks required identity/state fields")
        attributes = payload.get("attributes", {})
        if not isinstance(attributes, dict):
            raise FederationResolutionError("remote public entity attributes are malformed")
        return copy.deepcopy(payload)

    @staticmethod
    def _validate_public_event(
        payload: dict[str, Any],
        *,
        event_id: str,
    ) -> dict[str, Any]:
        if set(payload) - _PUBLIC_EVENT_FIELDS:
            raise FederationResolutionError("remote public event contains unreviewed fields")
        if payload.get("event_id") != event_id or payload.get("visibility") != "PUBLIC":
            raise FederationResolutionError("remote registry returned an invalid public-event projection")
        if payload.get("projection_schema") != "aegistrace.public_event_proof.v1":
            raise FederationResolutionError("remote registry returned an unsupported public projection")
        return copy.deepcopy(payload)


def _parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(UTC)


__all__ = [
    "FederatedRegistryClient",
    "FederationAgreement",
    "FederationBreak",
    "FederationGateway",
    "FederationResolutionError",
    "HTTPFederatedRegistryClient",
]
