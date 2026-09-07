"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_ledger.py
Purpose: Unit tests for ledger module
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from pathlib import Path

from aegistrace.events.collector import EventCollector
from aegistrace.events.models import Actor, ExecutionContext
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier
from aegistrace.ledger.merkle import merkle_proof, merkle_root


def make_actor():
    return Actor(
        controller_id=str(make_identifier("controller", "org-001")),
        principal_id=str(make_identifier("principal", "user-012")),
        agent_id=str(make_identifier("agent", "research-agent", version="v3")),
        agent_instance_id=str(make_identifier("agent-instance", "research-agent", version="run-0042")),
    )


def make_ec():
    return ExecutionContext(
        provider_id=str(make_identifier("provider", "prov-001")),
        model_id=str(make_identifier("model", "llm")),
        model_version_id=str(make_identifier("model", "llm", version="v1")),
        deployment_id=str(make_identifier("deployment", "dep-001")),
    )


def make_collector():
    ledger = AppendOnlyLedger()
    keys = KeyService()
    _registry = Registry()
    collector = EventCollector(ledger, keys)
    # Register entities and create signing key
    actor = make_actor()
    keys.create_key("aitrace://ca/key/k1", bound_entity_id=actor.agent_id)
    return ledger, keys, collector, actor


class TestLedger:
    def test_append_and_verify(self) -> None:
        ledger, keys, collector, actor = make_collector()
        ec = make_ec()
        e = collector.record(
            actor=actor, execution_context=ec, task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:example",
        )
        assert e.event_id.startswith("evt_")
        assert e.event_hash.startswith("sha256:")
        assert e.signature.startswith("Ed25519:")
        assert len(ledger) == 1
        verifier = LedgerVerifier(keys)
        report = verifier.verify(ledger)
        assert report.ok, report.failures

    def test_hash_chain(self) -> None:
        ledger, keys, collector, actor = make_collector()
        ec = make_ec()
        tid = str(make_identifier("task", "t1"))
        for action in ["SEARCH", "READ", "MODIFY"]:
            collector.record(
                actor=actor, execution_context=ec, task_id=tid,
                action=action, visibility="ORGANIZATION_PRIVATE",
                signing_key_id="aitrace://ca/key/k1",
                resource_id="urn:file:f",
            )
        assert len(ledger) == 3
        events = ledger.events()
        assert events[0].previous_event_hash is None
        assert events[1].previous_event_hash == events[0].event_hash
        assert events[2].previous_event_hash == events[1].event_hash
        verifier = LedgerVerifier(keys)
        report = verifier.verify(ledger)
        assert report.ok, report.failures

    def test_jsonl_roundtrip(self, tmp_path: Path) -> None:
        ledger, keys, collector, actor = make_collector()
        ec = make_ec()
        collector.record(
            actor=actor, execution_context=ec, task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
        )
        path = tmp_path / "ledger.jsonl"
        ledger.save(path)
        ledger2 = AppendOnlyLedger.load(path)
        assert len(ledger2) == 1
        assert ledger2.events()[0].event_id == ledger.events()[0].event_id

    def test_merkle_root_empty(self) -> None:
        root = merkle_root([])
        assert root.startswith("sha256:")

    def test_merkle_root_single(self) -> None:
        ledger, keys, collector, actor = make_collector()
        ec = make_ec()
        collector.record(
            actor=actor, execution_context=ec, task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
        )
        root = merkle_root(ledger.events())
        assert root.startswith("sha256:")
        assert len(root) == len("sha256:") + 64

    def test_merkle_proof(self) -> None:
        ledger, keys, collector, actor = make_collector()
        ec = make_ec()
        for i in range(4):
            collector.record(
                actor=actor, execution_context=ec, task_id=str(make_identifier("task", f"t{i}")),
                action="SEARCH", visibility="ORGANIZATION_PRIVATE",
                signing_key_id="aitrace://ca/key/k1",
            )
        proof = merkle_proof(ledger.events(), 0)
        assert len(proof) == 2  # 4 leaves -> 2 levels
