"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_ledger_hardening.py
Purpose: Unit tests for WAL, mutation isolation, and parallel verification hardening
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from aegistrace.events.collector import EventCollector
from aegistrace.events.models import Actor, ExecutionContext
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger
from aegistrace.ledger.batched import BatchConfig, BatchedLedger, WALRecoveryError


def _event_stack(ledger):
    keys = KeyService()
    agent = str(make_identifier("agent", "a1"))
    key_id = str(make_identifier("key", "k1"))
    keys.create_key(key_id, bound_entity_id=agent)
    actor = Actor(
        controller_id=str(make_identifier("controller", "c1")),
        principal_id=str(make_identifier("principal", "p1")),
        agent_id=agent,
        agent_instance_id=str(make_identifier("agent-instance", "a1", version="r1")),
    )
    execution_context = ExecutionContext(
        provider_id=str(make_identifier("provider", "p1")),
        model_id=str(make_identifier("model", "m1")),
        model_version_id=str(make_identifier("model", "m1", version="v1")),
        deployment_id=str(make_identifier("deployment", "d1")),
    )
    return keys, EventCollector(ledger, keys), actor, execution_context, key_id


def _record(collector, actor, execution_context, key_id, index: int = 0):
    return collector.record(
        actor=actor,
        execution_context=execution_context,
        task_id=str(make_identifier("task", f"t{index}")),
        action="SEARCH",
        visibility="ORGANIZATION_PRIVATE",
        signing_key_id=key_id,
        resource_id=f"urn:web:{index}",
    )


class TestLedgerHardening:
    def test_batch_config_rejects_invalid_limits(self) -> None:
        with pytest.raises(ValueError):
            BatchConfig(batch_size=0)
        with pytest.raises(ValueError):
            BatchConfig(batch_size=10, max_buffer_size=9)
        with pytest.raises(ValueError):
            BatchConfig(verify_workers=0)

    def test_wal_is_real_file_without_tautological_assertion(self, tmp_path: Path) -> None:
        wal_path = tmp_path / "wal.log"
        ledger = BatchedLedger(
            BatchConfig(batch_size=100, flush_interval_ms=10_000, wal_path=wal_path)
        )
        assert wal_path.exists()
        keys, collector, actor, execution_context, key_id = _event_stack(ledger)
        _record(collector, actor, execution_context, key_id)
        assert wal_path.stat().st_size > 0
        ledger.close()

    def test_invalid_candidate_is_rejected_before_wal_persistence(self, tmp_path: Path) -> None:
        source = AppendOnlyLedger()
        keys, collector, actor, execution_context, key_id = _event_stack(source)
        event = _record(collector, actor, execution_context, key_id)
        event.action = "DELETE"

        wal_path = tmp_path / "wal.log"
        ledger = BatchedLedger(
            BatchConfig(batch_size=100, flush_interval_ms=10_000, wal_path=wal_path)
        )
        with pytest.raises(ValueError, match="event_hash mismatch"):
            ledger.append(event)
        assert wal_path.read_bytes() == b""
        ledger.close()

    def test_caller_mutation_after_append_cannot_change_buffered_event(self, tmp_path: Path) -> None:
        ledger = BatchedLedger(
            BatchConfig(
                batch_size=100,
                flush_interval_ms=10_000,
                wal_path=tmp_path / "wal.log",
            )
        )
        keys, collector, actor, execution_context, key_id = _event_stack(ledger)
        event = _record(collector, actor, execution_context, key_id)
        event.action = "DELETE"
        event.resource_id = "urn:attacker:mutated"
        stored = ledger.events()[0]
        assert stored.action == "SEARCH"
        assert stored.resource_id == "urn:web:0"
        assert ledger.verify(keys).ok
        ledger.close()

    def test_corrupt_wal_fails_closed_and_is_quarantined(self, tmp_path: Path) -> None:
        wal_path = tmp_path / "wal.log"
        wal_path.write_text('{"not":"a complete event"}\nthis-is-not-json\n', encoding="utf-8")
        with pytest.raises(WALRecoveryError) as exc_info:
            BatchedLedger(
                BatchConfig(batch_size=100, flush_interval_ms=10_000, wal_path=wal_path)
            )
        assert exc_info.value.quarantine_path is not None
        assert exc_info.value.quarantine_path.exists()
        assert exc_info.value.quarantine_path.read_bytes() == wal_path.read_bytes()

    def test_valid_wal_replays_without_silent_truncation(self, tmp_path: Path) -> None:
        source = AppendOnlyLedger()
        keys, collector, actor, execution_context, key_id = _event_stack(source)
        event = _record(collector, actor, execution_context, key_id)
        wal_path = tmp_path / "wal.log"
        wal_path.write_text(json.dumps(event.to_dict(), sort_keys=True) + "\n", encoding="utf-8")
        original_bytes = wal_path.read_bytes()

        recovered = BatchedLedger(
            BatchConfig(batch_size=100, flush_interval_ms=10_000, wal_path=wal_path)
        )
        assert len(recovered) == 1
        assert recovered.events()[0].event_id == event.event_id
        assert wal_path.read_bytes().startswith(original_bytes)
        recovered.close()

    def test_batched_verifier_uses_parallel_signature_mode(self) -> None:
        ledger = BatchedLedger(
            BatchConfig(
                batch_size=100,
                flush_interval_ms=10_000,
                parallel_verify=True,
                verify_workers=4,
            )
        )
        keys, collector, actor, execution_context, key_id = _event_stack(ledger)
        for index in range(8):
            _record(collector, actor, execution_context, key_id, index=index)
        report = ledger.verify(keys)
        assert report.ok
        assert report.verified_signature_count == 8
        assert report.verification_mode == "hash-chain+parallel-signatures"
        ledger.close()
