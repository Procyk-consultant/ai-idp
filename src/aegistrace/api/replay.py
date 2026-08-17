"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/api/replay.py
Purpose: Replay-reservation contract for authenticated action requests
Classification: service
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from typing import Protocol


class ReplayReservationStore(Protocol):
    """Atomically reserve request nonces across the intended trust boundary."""

    def reserve_nonce(
        self,
        key_id: str,
        nonce: str,
        *,
        expires_at: str,
    ) -> bool:
        """Return True only when this key/nonce pair was not previously reserved."""
        ...

    def prune_expired_nonces(self, *, before: str | None = None) -> int:
        """Delete expired replay reservations and return the number removed."""
        ...


class InMemoryReplayReservationStore:
    """Process-local replay store for development and single-process reference use."""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], datetime] = {}
        self._lock = RLock()

    def reserve_nonce(self, key_id: str, nonce: str, *, expires_at: str) -> bool:
        expiry = _parse_timestamp(expires_at)
        now = datetime.now(UTC)
        if expiry <= now:
            raise ValueError("replay reservation expiry must be in the future")
        key = (key_id, nonce)
        with self._lock:
            self._prune_locked(now)
            if key in self._entries:
                return False
            self._entries[key] = expiry
            return True

    def prune_expired_nonces(self, *, before: str | None = None) -> int:
        cutoff = _parse_timestamp(before) if before is not None else datetime.now(UTC)
        with self._lock:
            return self._prune_locked(cutoff)

    def _prune_locked(self, cutoff: datetime) -> int:
        expired = [key for key, expiry in self._entries.items() if expiry <= cutoff]
        for key in expired:
            self._entries.pop(key, None)
        return len(expired)


def _parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(UTC)


__all__ = ["ReplayReservationStore", "InMemoryReplayReservationStore"]
