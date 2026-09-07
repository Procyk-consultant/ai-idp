"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/ledger/batched.py
Purpose: Higher-throughput batched ledger with evidence-preserving write-ahead log
Classification: infrastructure
Security Classification: internal
Version: 2.1.0
Last Material Revision: 2026-09-07
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import threading
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import IO

from aegistrace.events.models import Event
from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier, VerificationReport
from aegistrace.signing.canonical import canonicalize_for_hash
from aegistrace.signing.ed25519 import sha256_hex


@dataclass
class BatchConfig:
    batch_size: int = 100
    flush_interval_ms: int = 100
    wal_path: Path | None = None
    wal_fsync: bool = True
    max_buffer_size: int = 100_000
    parallel_verify: bool = True
    verify_workers: int | None = None

    def __post_init__(self) -> None:
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.flush_interval_ms <= 0:
            raise ValueError("flush_interval_ms must be positive")
        if self.max_buffer_size < self.batch_size:
            raise ValueError("max_buffer_size must be greater than or equal to batch_size")
        if self.verify_workers is not None and self.verify_workers <= 0:
            raise ValueError("verify_workers must be positive when supplied")


class WALRecoveryError(RuntimeError):
    """Raised when a WAL cannot be recovered without losing evidence."""

    def __init__(self, message: str, *, wal_path: Path, quarantine_path: Path | None = None) -> None:
        super().__init__(message)
        self.wal_path = wal_path
        self.quarantine_path = quarantine_path


class BackgroundFlushError(RuntimeError):
    """Raised after the background flush loop encounters a persistent error."""


class BatchedLedger:
    """Batched append-only ledger with fail-closed durable WAL recovery.

    Validated events are deep-copied before WAL persistence and buffering so a
    caller cannot mutate acknowledged-but-unflushed canonical candidates.
    """

    def __init__(self, config: BatchConfig | None = None) -> None:
        self.config = config or BatchConfig()
        self._buffer: list[Event] = []
        self._buffer_lock = threading.RLock()
        self._last_flush = time.monotonic()
        self._flush_lock = threading.Lock()
        self._closed = False
        self._wal_file: IO[bytes] | None = None
        self._wal_lock = threading.Lock()
        self._on_flush: Callable[[list[Event]], None] | None = None
        self._background_thread: threading.Thread | None = None
        self._background_error: Exception | None = None
        self._stop_event = threading.Event()
        self._canonical = AppendOnlyLedger()
        self._event_ids: set[str] = set()
        if self.config.wal_path is not None:
            self._init_wal(self.config.wal_path)

    def _init_wal(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > 0:
            self._replay_wal(path)
        self._event_ids = {event.event_id for event in self._canonical.events()}
        self._wal_file = open(path, "ab", buffering=0)

    def _quarantine_wal(self, path: Path) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        quarantine = path.with_name(f"{path.name}.corrupt.{timestamp}")
        shutil.copy2(path, quarantine)
        return quarantine

    def _replay_wal(self, path: Path) -> None:
        recovered = AppendOnlyLedger()
        try:
            with open(path, "rb") as file_handle:
                for line_number, raw_line in enumerate(file_handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        recovered.append(Event.from_dict(json.loads(line.decode("utf-8"))))
                    except Exception as exc:
                        quarantine = self._quarantine_wal(path)
                        raise WALRecoveryError(
                            f"WAL recovery failed at line {line_number}: {exc}",
                            wal_path=path,
                            quarantine_path=quarantine,
                        ) from exc
        except WALRecoveryError:
            raise
        except Exception as exc:
            quarantine_path = self._quarantine_wal(path) if path.exists() else None
            raise WALRecoveryError(
                f"WAL recovery failed: {exc}",
                wal_path=path,
                quarantine_path=quarantine_path,
            ) from exc
        self._canonical = recovered

    def set_on_flush(self, callback: Callable[[list[Event]], None]) -> None:
        self._on_flush = callback

    def start_background_flush(self) -> None:
        self._raise_background_error()
        if self._background_thread is not None:
            return
        self._background_thread = threading.Thread(target=self._background_flush_loop, daemon=True)
        self._background_thread.start()

    def _background_flush_loop(self) -> None:
        interval_seconds = self.config.flush_interval_ms / 1000.0
        while not self._stop_event.wait(interval_seconds):
            try:
                self.flush()
            except Exception as exc:
                self._background_error = exc
                self._stop_event.set()
                return

    def _raise_background_error(self) -> None:
        if self._background_error is not None:
            raise BackgroundFlushError(
                f"background flush failed: {self._background_error}"
            ) from self._background_error

    def _validate_candidate(self, event: Event) -> None:
        if event.event_id in self._event_ids:
            raise ValueError(f"duplicate event_id: {event.event_id}")
        expected_previous = (
            self._buffer[-1].event_hash if self._buffer else self._canonical.last_event_hash()
        )
        if event.previous_event_hash != expected_previous:
            raise ValueError(
                f"hash chain broken: expected previous_event_hash={expected_previous}, "
                f"got {event.previous_event_hash}"
            )
        recomputed = sha256_hex(canonicalize_for_hash(event.to_dict()))
        if recomputed != event.event_hash:
            raise ValueError(f"event_hash mismatch: expected {recomputed}, got {event.event_hash}")

    def append(self, event: Event) -> None:
        self._raise_background_error()
        if self._closed:
            raise RuntimeError("ledger is closed")

        with self._buffer_lock:
            if len(self._buffer) >= self.config.max_buffer_size:
                raise BackpressureError(
                    f"buffer full: {len(self._buffer)} >= {self.config.max_buffer_size}"
                )
            self._validate_candidate(event)
            canonical_candidate = copy.deepcopy(event)
            if self._wal_file is not None:
                with self._wal_lock:
                    line = json.dumps(
                        canonical_candidate.to_dict(),
                        sort_keys=True,
                        ensure_ascii=False,
                    ) + "\n"
                    self._wal_file.write(line.encode("utf-8"))
                    if self.config.wal_fsync:
                        os.fsync(self._wal_file.fileno())
            self._buffer.append(canonical_candidate)
            self._event_ids.add(canonical_candidate.event_id)
            should_flush = len(self._buffer) >= self.config.batch_size

        if should_flush:
            self.flush()

    def flush(self) -> int:
        self._raise_background_error()
        with self._flush_lock:
            with self._buffer_lock:
                if not self._buffer:
                    return 0
                batch = self._buffer
                self._buffer = []
            for event in batch:
                self._canonical.append(event)
            if self._on_flush is not None:
                self._on_flush(copy.deepcopy(batch))
            self._last_flush = time.monotonic()
            return len(batch)

    def close(self) -> None:
        if self._closed:
            return
        self._stop_event.set()
        if self._background_thread is not None:
            self._background_thread.join(timeout=5.0)
        self._raise_background_error()
        self.flush()
        if self._wal_file is not None:
            self._wal_file.close()
        self._closed = True

    def events(self) -> list[Event]:
        self.flush()
        return self._canonical.events()

    def __iter__(self) -> Iterator[Event]:
        return iter(self.events())

    def __len__(self) -> int:
        with self._buffer_lock:
            return len(self._canonical) + len(self._buffer)

    def last_event_hash(self) -> str | None:
        self._raise_background_error()
        with self._buffer_lock:
            if self._buffer:
                return self._buffer[-1].event_hash
            return self._canonical.last_event_hash()

    def verify(self, key_service: KeyService) -> VerificationReport:
        self.flush()
        verifier = LedgerVerifier(
            key_service,
            parallel_signatures=self.config.parallel_verify,
            max_workers=self.config.verify_workers,
        )
        return verifier.verify(self._canonical)

    def get(self, event_id: str) -> Event | None:
        self.flush()
        return self._canonical.get(event_id)


class BackpressureError(RuntimeError):
    """Raised when the buffer is full and cannot accept more events."""


__all__ = [
    "BatchConfig",
    "BatchedLedger",
    "BackpressureError",
    "BackgroundFlushError",
    "WALRecoveryError",
    "VerificationReport",
]
