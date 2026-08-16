"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/ledger/append_only.py
Purpose: Append-only, hash-chained ledger
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-16
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from aegistrace.events.models import Event
from aegistrace.identity.keys import KeyService
from aegistrace.signing.canonical import canonicalize_for_hash, canonicalize_for_signature
from aegistrace.signing.ed25519 import SigningKey, sha256_hex


class AppendOnlyLedger:
    """Append-only, hash-chained event ledger.

    Invariants:
        - Events are append-only: no modification or deletion through the public API.
        - Event IDs are unique within a ledger.
        - Each event's previous_event_hash matches the prior event's event_hash.
        - The first event has previous_event_hash = None.
        - Event hashes are SHA-256 of the canonical form.
    """

    def __init__(self) -> None:
        self._events: list[Event] = []
        self._event_ids: set[str] = set()

    def append(self, event: Event) -> None:
        if event.event_id in self._event_ids:
            raise ValueError(f"duplicate event_id: {event.event_id}")
        expected_prev = self._events[-1].event_hash if self._events else None
        if event.previous_event_hash != expected_prev:
            raise ValueError(
                f"hash chain broken: expected previous_event_hash={expected_prev}, "
                f"got {event.previous_event_hash}"
            )
        canon = canonicalize_for_hash(event.to_dict())
        recomputed = sha256_hex(canon)
        if recomputed != event.event_hash:
            raise ValueError(
                f"event_hash mismatch: expected {recomputed}, got {event.event_hash}"
            )
        self._events.append(event)
        self._event_ids.add(event.event_id)

    def last_event_hash(self) -> str | None:
        return self._events[-1].event_hash if self._events else None

    def events(self) -> list[Event]:
        return list(self._events)

    def __iter__(self) -> Iterator[Event]:
        return iter(self._events)

    def __len__(self) -> int:
        return len(self._events)

    def get(self, event_id: str) -> Event | None:
        for e in self._events:
            if e.event_id == event_id:
                return e
        return None

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(e.to_dict(), sort_keys=True, ensure_ascii=False) for e in self._events)

    @classmethod
    def from_jsonl(cls, text: str) -> AppendOnlyLedger:
        ledger = cls()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            ledger.append(Event.from_dict(d))
        return ledger

    def save(self, path: Path) -> None:
        path.write_text(self.to_jsonl(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> AppendOnlyLedger:
        return cls.from_jsonl(path.read_text(encoding="utf-8"))


class LedgerVerifier:
    """Verify hash-chain integrity, event hashes, and optionally signatures.

    Strict signature verification is the default. When signatures are
    requested, an unknown verification key is a verification failure rather
    than a silent success. Hash-only verification must be requested explicitly
    with ``verify_signatures=False``.
    """

    def __init__(self, key_service: KeyService, verify_signatures: bool = True) -> None:
        self._keys = key_service
        self._verify_signatures = verify_signatures

    def verify(self, ledger: AppendOnlyLedger) -> VerificationReport:
        report = VerificationReport(signatures_requested=self._verify_signatures)
        prev_hash: str | None = None
        seen_event_ids: set[str] = set()
        for i, event in enumerate(ledger):
            if event.event_id in seen_event_ids:
                report.add_failure(event.event_id, f"duplicate event_id at seq {i}: {event.event_id}")
            seen_event_ids.add(event.event_id)

            if event.previous_event_hash != prev_hash:
                report.add_failure(
                    event.event_id,
                    f"hash chain broken at seq {i}: expected prev={prev_hash}, got {event.previous_event_hash}",
                )

            canon = canonicalize_for_hash(event.to_dict())
            recomputed = sha256_hex(canon)
            if recomputed != event.event_hash:
                report.add_failure(
                    event.event_id,
                    f"event_hash mismatch at seq {i}: expected {recomputed}, got {event.event_hash}",
                )

            if self._verify_signatures:
                try:
                    rec = self._keys.get_record(event.signing_key_id)
                    pub = SigningKey.from_public_pem(event.signing_key_id, rec.public_pem).public_key
                    canon_sig = canonicalize_for_signature(event.to_dict())
                    if not SigningKey.verify(pub, canon_sig, event.signature):
                        report.add_failure(event.event_id, f"signature invalid at seq {i}")
                    else:
                        report.verified_signature_count += 1
                except KeyError:
                    report.add_failure(
                        event.event_id,
                        f"verification key unavailable at seq {i}: {event.signing_key_id}",
                    )
                except Exception as e:
                    report.add_failure(event.event_id, f"signature verification error at seq {i}: {e}")
            prev_hash = event.event_hash
        return report


@dataclass
class VerificationReport:
    failures: list[str] = field(default_factory=list)
    failing_event_ids: list[str] = field(default_factory=list)
    signatures_requested: bool = True
    verified_signature_count: int = 0

    def add_failure(self, event_id: str, message: str) -> None:
        self.failing_event_ids.append(event_id)
        self.failures.append(message)

    @property
    def ok(self) -> bool:
        return not self.failures

    @property
    def verification_mode(self) -> str:
        return "hash-chain+signatures" if self.signatures_requested else "hash-chain-only"

    def __str__(self) -> str:
        if self.ok:
            return (
                f"VerificationReport: OK (0 failures; mode={self.verification_mode}; "
                f"verified_signatures={self.verified_signature_count})"
            )
        return f"VerificationReport: {len(self.failures)} failures\n  - " + "\n  - ".join(self.failures)


__all__ = ["AppendOnlyLedger", "LedgerVerifier", "VerificationReport"]
