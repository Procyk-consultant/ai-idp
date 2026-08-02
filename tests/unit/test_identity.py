"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_identity.py
Purpose: Unit tests for identity module
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import pytest

from aegistrace.identity.ids import ID_PATTERN, Identifier, make_event_id, make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry


class TestIdentifier:
    def test_parse_simple(self) -> None:
        i = Identifier.parse("aitrace://ca/controller/org-001")
        assert i.jurisdiction == "ca"
        assert i.entity_type == "controller"
        assert i.slug == "org-001"
        assert i.version is None

    def test_parse_versioned(self) -> None:
        i = Identifier.parse("aitrace://ca/agent/research-agent#v3")
        assert i.entity_type == "agent"
        assert i.slug == "research-agent"
        assert i.version == "v3"

    def test_parse_provincial(self) -> None:
        i = Identifier.parse("aitrace://ca-qc/provider/provider-001")
        assert i.jurisdiction == "ca-qc"

    def test_parse_invalid(self) -> None:
        with pytest.raises(ValueError):
            Identifier.parse("not-an-identifier")

    def test_str_roundtrip(self) -> None:
        s = "aitrace://ca/agent/research-agent#v3"
        assert str(Identifier.parse(s)) == s

    def test_pattern_matches(self) -> None:
        assert ID_PATTERN.match("aitrace://ca/controller/org-001")
        assert ID_PATTERN.match("aitrace://ca-qc/agent/foo#v1")
        assert not ID_PATTERN.match("aitrace://us/controller/foo")

    def test_make_identifier(self) -> None:
        i = make_identifier("provider", "prov-001")
        assert str(i) == "aitrace://ca/provider/prov-001"

    def test_make_event_id_format(self) -> None:
        eid = make_event_id()
        assert eid.startswith("evt_")
        assert len(eid) == 4 + 26


class TestKeyService:
    def test_create_key(self) -> None:
        ks = KeyService()
        sk = ks.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        assert sk.key_id == "aitrace://ca/key/k1"
        assert ks.is_active("aitrace://ca/key/k1")

    def test_key_uniqueness(self) -> None:
        ks = KeyService()
        ks.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        with pytest.raises(ValueError):
            ks.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")

    def test_sign_and_verify(self) -> None:
        ks = KeyService()
        sk = ks.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        sig = sk.sign(b"hello")
        assert sig.startswith("Ed25519:")
        from aegistrace.signing.ed25519 import SigningKey
        assert SigningKey.verify(sk.public_key, b"hello", sig)
        assert not SigningKey.verify(sk.public_key, b"world", sig)

    def test_revoke_key_blocks_signing(self) -> None:
        ks = KeyService()
        ks.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        ks.revoke("aitrace://ca/key/k1")
        with pytest.raises(PermissionError):
            ks.get_signing_key("aitrace://ca/key/k1")

    def test_rotate_key(self) -> None:
        ks = KeyService()
        ks.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        new_sk = ks.rotate("aitrace://ca/key/k1", "aitrace://ca/key/k2")
        assert new_sk.key_id == "aitrace://ca/key/k2"
        assert ks.get_record("aitrace://ca/key/k1").state == "rotated"
        assert ks.is_active("aitrace://ca/key/k2")
        assert not ks.is_active("aitrace://ca/key/k1")

    def test_suspend_and_reactivate(self) -> None:
        ks = KeyService()
        ks.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        ks.suspend("aitrace://ca/key/k1")
        assert not ks.is_active("aitrace://ca/key/k1")
        with pytest.raises(PermissionError):
            ks.get_signing_key("aitrace://ca/key/k1")
        ks.reactivate("aitrace://ca/key/k1")
        assert ks.is_active("aitrace://ca/key/k1")


class TestRegistry:
    def test_register_and_resolve(self) -> None:
        r = Registry()
        eid = "aitrace://ca/agent/a1"
        r.register(eid, "agent", {"name": "agent-1"})
        rec = r.resolve(eid)
        assert rec.entity_type == "agent"
        assert rec.is_active()
        assert rec.attributes["name"] == "agent-1"

    def test_register_uniqueness(self) -> None:
        r = Registry()
        eid = "aitrace://ca/agent/a1"
        r.register(eid, "agent")
        with pytest.raises(ValueError):
            r.register(eid, "agent")

    def test_permanent_resolvability(self) -> None:
        r = Registry()
        eid = "aitrace://ca/agent/a1"
        r.register(eid, "agent")
        r.revoke(eid, "for cause")
        # Identifier remains resolvable after revocation
        rec = r.resolve(eid)
        assert rec.state == "revoked"
        assert rec.is_resolvable()

    def test_terminate_then_archive(self) -> None:
        r = Registry()
        eid = "aitrace://ca/agent/a1"
        r.register(eid, "agent")
        r.terminate(eid, "end of life")
        assert r.resolve(eid).state == "terminated"
        r.archive(eid, "retention expired")
        assert r.resolve(eid).state == "archived"

    def test_invalid_transition(self) -> None:
        r = Registry()
        eid = "aitrace://ca/agent/a1"
        r.register(eid, "agent")
        r.revoke(eid)
        with pytest.raises(ValueError):
            r.reactivate(eid)  # cannot reactivate revoked

    def test_state_history_preserved(self) -> None:
        r = Registry()
        eid = "aitrace://ca/agent/a1"
        r.register(eid, "agent")
        r.suspend(eid, "investigation")
        r.reactivate(eid)
        rec = r.resolve(eid)
        assert len(rec.state_history) == 2
