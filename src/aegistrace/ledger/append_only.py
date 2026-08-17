"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/ledger/append_only.py
Purpose: Append-only, hash-chained ledger and verifier
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from aegistrace.events.models import Event
from aegistrace.identity.keys import KeyService
from aegistrace.signing.canonical import canonicalize_for_hash, canonicalize_for_signature
from aegistrace.signing.ed25519 import SigningKey, sha256_hex


class AppendOnlyLedger:
    """Append-only, hash-chained event ledger."""

    def __init__(self) -> None:
        self._events: list[Event] = []
        self._event_ids: set[str] = set()

    def append(self, event: Event) -> None:
        if event.event_id in self._event_ids:
            raise ValueError(f"duplicate event_id: {event.event_id}")
        expected_previous = self._events[-1].event_hash if self._events else None
        if event.previous_event_hash != expected_previous:
            raise ValueError(
                f"hash chain broken: expected previous_event_hash={expected_previous}, "
                f"got {event.previous_event_hash}"
            )
        recomputed = sha256_hex(canonicalize_for_hash(event.to_dict()))
        if recomputed != event.event_hash:
            raise ValueError(f"event_hash mismatch: expected {recomputed}, got {event.event_hash}")
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
        for event in self._events:
            if event.event_id == event_id:
                return event
        return None

    def to_jsonl(self) -> str:
        return "\n".join(
            json.dumps(event.to_dict(), sort_keys=True, ensure_ascii=False)
            for event in self._events
        )

    @classmethod
    def from_jsonl(cls, text: str) -> AppendOnlyLedger:
        ledger = cls()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            ledger.append(Event.from_dict(json.loads(line)))
        return ledger

    def save(self, path: Path) -> None:
        path.write_text(self.to_jsonl(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> AppendOnlyLedger:
        return cls.from_jsonl(path.read_text(encoding="utf-8"))


class LedgerVerifier:
    """Verify chain integrity, event hashes, and optionally signatures.

    Signature verification can be parallelized without parallelizing chain/hash
    evaluation. Results are consumed in ledger order so the report remains
    deterministic.
    """

    def __init__(
        self,
        key_service: KeyService,
        verify_signatures: bool = True,
        *,
        parallel_signatures: bool = False,
        max_workers: int | None = None,
    ) -> None:
        self._keys = key_service
        self._verify_signatures = verify_signatures
        self._parallel_signatures = parallel_signatures
        self._max_workers = max_workers

    def verify(self, ledger: AppendOnlyLedger) -> VerificationReport:
        report = VerificationReport(
            signatures_requested=self._verify_signatures,
            parallel_signatures=self._parallel_signatures and self._verify_signatures,
        )
        previous_hash: str | None = None
        seen_event_ids: set[str] = set()
        indexed_events: list[tuple[int, Event]] = []

        for index, event in enumerate(ledger):
            indexed_events.append((index, event))
            if event.event_id in seen_event_ids:
                report.add_failure(event.event_id, f"duplicate event_id at seq {index}: {event.event_id}")
            seen_event_ids.add(event.event_id)

            if event.previous_event_hash != previous_hash:
                report.add_failure(
                    event.event_id,
                    f"hash chain broken at seq {index}: expected prev={previous_hash}, got {event.previous_event_hash}",
                )

            recomputed = sha256_hex(canonicalize_for_hash(event.to_dict()))
            if recomputed != event.event_hash:
                report.add_failure(
                    event.event_id,
                    f"event_hash mismatch at seq {index}: expected {recomputed}, got {event.event_hash}",
                )
            previous_hash = event.event_hash

        if self._verify_signatures:
            if self._parallel_signatures and len(indexed_events) > 1:
                with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                    results = executor.map(self._verify_one_signature, indexed_events)
                    for event_id, failure in results:
                        if failure is None:
                            report.verified_signature_count += 1
                        else:
                            report.add_failure(event_id, failure)
            else:
                for indexed_event in indexed_events:
                    event_id, failure = self._verify_one_signature(indexed_event)
                    if failure is None:
                        report.verified_signature_count += 1
                    else:
                        report.add_failure(event_id, failure)
        return report

    def _verify_one_signature(self, indexed_event: tuple[int, Event]) -> tuple[str, str | None]:
        index, event = indexed_event
        try:
            key_record = self._keys.get_record(event.signing_key_id)
            public_key = SigningKey.from_public_pem(
                event.signing_key_id,
                key_record.public_pem,
            ).public_key
            if not SigningKey.verify(
                public_key,
                canonicalize_for_signature(event.to_dict()),
                event.signature,
            ):
                return event.event_id, f"signature invalid at seq {index}"
            return event.event_id, None
        except KeyError:
            return (
                event.event_id,
                f"verification key unavailable at seq {index}: {event.signing_key_id}",
            )
        except Exception as exc:
            return event.event_id, f"signature verification error at seq {index}: {exc}"


@dataclass
class VerificationReport:
    failures: list[str] = field(default_factory=list)
    failing_event_ids: list[str] = field(default_factory=list)
    signatures_requested: bool = True
    verified_signature_count: int = 0
    parallel_signatures: bool = False

    def add_failure(self, event_id: str, message: str) -> None:
        self.failing_event_ids.append(event_id)
        self.failures.append(message)

    @property
    def ok(self) -> bool:
        return not self.failures

    @property
    def verification_mode(self) -> str:
        if not self.signatures_requested:
            return "hash-chain-only"
        if self.parallel_signatures:
            return "hash-chain+parallel-signatures"
        return "hash-chain+signatures"

    def __str__(self) -> str:
        if self.ok:
            return (
                f"VerificationReport: OK (0 failures; mode={self.verification_mode}; "
                f"verified_signatures={self.verified_signature_count})"
            )
        return f"VerificationReport: {len(self.failures)} failures\n  - " + "\n  - ".join(self.failures)


__all__ = ["AppendOnlyLedger", "LedgerVerifier", "VerificationReport"]
