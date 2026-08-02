"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_signing.py
Purpose: Unit tests for signing module
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json

import pytest

from aegistrace.signing.canonical import canonicalize, canonicalize_for_hash, canonicalize_for_signature
from aegistrace.signing.ed25519 import SigningKey, blake2b_hex, sha256_hex, sha256_raw


class TestSigning:
    def test_generate_and_sign(self) -> None:
        sk = SigningKey.generate("aitrace://ca/key/k1")
        sig = sk.sign(b"message")
        assert sig.startswith("Ed25519:")
        assert SigningKey.verify(sk.public_key, b"message", sig)

    def test_verify_wrong_message(self) -> None:
        sk = SigningKey.generate("aitrace://ca/key/k1")
        sig = sk.sign(b"message")
        assert not SigningKey.verify(sk.public_key, b"different", sig)

    def test_verify_bad_signature(self) -> None:
        sk = SigningKey.generate("aitrace://ca/key/k1")
        assert not SigningKey.verify(sk.public_key, b"message", "Ed25519:invalidbase64==")

    def test_public_pem_roundtrip(self) -> None:
        sk = SigningKey.generate("aitrace://ca/key/k1")
        pem = sk.public_pem()
        sk2 = SigningKey.from_public_pem("aitrace://ca/key/k1", pem)
        sig = sk.sign(b"message")
        assert SigningKey.verify(sk2.public_key, b"message", sig)

    def test_verify_only_cannot_sign(self) -> None:
        sk = SigningKey.generate("aitrace://ca/key/k1")
        pem = sk.public_pem()
        sk2 = SigningKey.from_public_pem("aitrace://ca/key/k1", pem)
        with pytest.raises(PermissionError):
            sk2.sign(b"message")


class TestHashing:
    def test_sha256_hex(self) -> None:
        h = sha256_hex(b"hello")
        assert h == "sha256:" + "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    def test_sha256_raw(self) -> None:
        d = sha256_raw(b"hello")
        assert len(d) == 32

    def test_blake2b_hex(self) -> None:
        h = blake2b_hex(b"hello")
        assert h.startswith("blake2b:")


class TestCanonicalization:
    def test_canonicalize_sorted(self) -> None:
        obj = {"b": 1, "a": 2, "c": 3}
        c = canonicalize(obj)
        assert c == b'{"a":2,"b":1,"c":3}'

    def test_canonicalize_nested(self) -> None:
        obj = {"outer": {"z": 1, "a": 2}}
        c = canonicalize(obj)
        assert c == b'{"outer":{"a":2,"z":1}}'

    def test_canonicalize_deterministic(self) -> None:
        obj1 = {"a": 1, "b": 2}
        obj2 = {"b": 2, "a": 1}
        assert canonicalize(obj1) == canonicalize(obj2)

    def test_canonicalize_for_hash_excludes_event_hash_and_signature(self) -> None:
        event = {"event_id": "e1", "event_hash": "sha256:abc", "signature": "Ed25519:sig", "action": "READ"}
        c = canonicalize_for_hash(event)
        d = json.loads(c)
        assert "event_hash" not in d
        assert "signature" not in d
        assert d["action"] == "READ"

    def test_canonicalize_for_signature_includes_event_hash_excludes_signature(self) -> None:
        event = {"event_id": "e1", "event_hash": "sha256:abc", "signature": "Ed25519:sig", "action": "READ"}
        c = canonicalize_for_signature(event)
        d = json.loads(c)
        assert "event_hash" in d
        assert "signature" not in d
