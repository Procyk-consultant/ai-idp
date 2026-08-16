"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/ledger/batched.py
Purpose: Higher-throughput batched ledger with evidence-preserving write-ahead log
Classification: infrastructure
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-16
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

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


@dataclass
class BatchConfig:
    """Configuration for the batched ledger."""

    batch_size: int = 100
    flush_interval_ms: int = 100
    wal_path: Path | None = None
    wal_fsync: bool = True
    max_buffer_size: int = 100_000
    parallel_verify: bool = True


class WALRecoveryError(RuntimeError):
    """Raised when a WAL cannot be recovered without losing evidence."""

    def __init__(self, message: str, *, wal_path: Path, quarantine_path: Path | None = None) -> None:
        super().__init__(message)
        self.wal_path = wal_path
        self.quarantine_path = quarantine_path


class BatchedLedger:
    """Higher-throughput batched ledger with optional durable WAL.

    When a WAL is configured, each event is appended and optionally fsync'd
    before the caller is notified. Recovery is fail-closed: malformed or
    chain-invalid WAL content is preserved for investigation and startup
    fails rather than silently discarding evidence.
    """

    def __init__(self, config: BatchConfig | None = None) -> None:
        self.config = config or BatchConfig()
        self._buffer: list[Event] = []
        self._buffer_lock = threading.Lock()
        self._last_flush = time.monotonic()
        self._flush_lock = threading.Lock()
        self._closed = False
        self._wal_file: IO[bytes] | None = None
        self._wal_lock = threading.Lock()
        self._on_flush: Callable[[list[Event]], None] | None = None
        self._background_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._canonical = AppendOnlyLedger()
        if self.config.wal_path is not None:
            self._init_wal(self.config.wal_path)

    def _init_wal(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > 0:
            self._replay_wal(path)
        self._wal_file = open(path, "ab", buffering=0)

    def _quarantine_wal(self, path: Path) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        quarantine = path.with_name(f"{path.name}.corrupt.{timestamp}")
        shutil.copy2(path, quarantine)
        return quarantine

    def _replay_wal(self, path: Path) -> None:
        """Reconstruct the canonical ledger from the complete WAL.

        The WAL is intentionally retained after successful recovery. It is
        the durable recovery evidence for this in-process ledger unless an
        external durable backend/checkpoint mechanism explicitly supersedes
        it. Corruption never causes silent skipping or truncation.
        """
        recovered = AppendOnlyLedger()
        try:
            with open(path, "rb") as file_handle:
                for line_number, raw_line in enumerate(file_handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        event_dict = json.loads(line.decode("utf-8"))
                        recovered.append(Event.from_dict(event_dict))
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
            quarantine = self._quarantine_wal(path) if path.exists() else None
            raise WALRecoveryError(
                f"WAL recovery failed: {exc}",
                wal_path=path,
                quarantine_path=quarantine,
            ) from exc

        self._canonical = recovered

    def set_on_flush(self, callback: Callable[[list[Event]], None]) -> None:
        self._on_flush = callback

    def start_background_flush(self) -> None:
        if self._background_thread is not None:
            return
        self._background_thread = threading.Thread(target=self._background_flush_loop, daemon=True)
        self._background_thread.start()

    def _background_flush_loop(self) -> None:
        interval_sec = self.config.flush_interval_ms / 1000.0
        while not self._stop_event.wait(interval_sec):
            try:
                self.flush()
            except Exception:
                # The background loop remains alive; callers must surface
                # callback/storage errors through their deployment telemetry.
                continue

    def append(self, event: Event) -> None:
        if self._closed:
            raise RuntimeError("ledger is closed")
        with self._buffer_lock:
            if len(self._buffer) >= self.config.max_buffer_size:
                raise BackpressureError(f"buffer full: {len(self._buffer)} >= {self.config.max_buffer_size}")
            self._buffer.append(event)
            should_flush = len(self._buffer) >= self.config.batch_size

        if self._wal_file is not None:
            with self._wal_lock:
                line = json.dumps(event.to_dict(), sort_keys=True, ensure_ascii=False) + "\n"
                self._wal_file.write(line.encode("utf-8"))
                if self.config.wal_fsync:
                    os.fsync(self._wal_file.fileno())
        if should_flush:
            self.flush()

    def flush(self) -> int:
        with self._flush_lock:
            with self._buffer_lock:
                if not self._buffer:
                    return 0
                batch = self._buffer
                self._buffer = []
            for event in batch:
                self._canonical.append(event)
            if self._on_flush is not None:
                self._on_flush(batch)
            self._last_flush = time.monotonic()
            return len(batch)

    def close(self) -> None:
        if self._closed:
            return
        self._stop_event.set()
        if self._background_thread is not None:
            self._background_thread.join(timeout=5.0)
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
        return len(self._canonical) + len(self._buffer)

    def last_event_hash(self) -> str | None:
        if self._buffer:
            return self._buffer[-1].event_hash
        return self._canonical.last_event_hash()

    def verify(self, key_service: KeyService) -> VerificationReport:
        """Verify the canonical ledger.

        ``parallel_verify`` remains a target optimization flag; correctness
        is currently delegated to the strict canonical LedgerVerifier.
        """
        self.flush()
        verifier = LedgerVerifier(key_service)
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
    "WALRecoveryError",
    "VerificationReport",
]
