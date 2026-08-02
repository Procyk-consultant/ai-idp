"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/signing/ed25519.py
Purpose: Ed25519 signature operations for AI-IDP events
Classification: domain
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


@dataclass(frozen=True)
class SigningKey:
    """A bound Ed25519 signing key with an identifier.

    Invariants:
        - The key_id is permanently unique.
        - The public_key is the Ed25519 public counterpart of private_key.
        - The key_id is bound to a single entity (controller/agent/principal).
    """

    key_id: str
    private_key: Ed25519PrivateKey | None  # None for verify-only contexts
    public_key: Ed25519PublicKey

    @classmethod
    def generate(cls, key_id: str) -> SigningKey:
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        return cls(key_id=key_id, private_key=priv, public_key=pub)

    def sign(self, message: bytes) -> str:
        if self.private_key is None:
            raise PermissionError(f"key {self.key_id} is verify-only")
        sig = self.private_key.sign(message)
        return "Ed25519:" + base64.b64encode(sig).decode("ascii")

    @staticmethod
    def verify(public_key: Ed25519PublicKey, message: bytes, signature_str: str) -> bool:
        if not signature_str.startswith("Ed25519:"):
            return False
        try:
            sig_bytes = base64.b64decode(signature_str[len("Ed25519:"):])
            public_key.verify(sig_bytes, message)
            return True
        except (InvalidSignature, ValueError, Exception):
            return False

    def public_pem(self) -> str:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")

    @classmethod
    def from_public_pem(cls, key_id: str, pem: str) -> SigningKey:
        pub = serialization.load_pem_public_key(pem.encode("ascii"))
        if not isinstance(pub, Ed25519PublicKey):
            raise TypeError("not an Ed25519 public key")
        return cls(key_id=key_id, private_key=None, public_key=pub)


def sha256_hex(data: bytes) -> str:
    """Return 'sha256:<64 hex chars>'."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_raw(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def blake2b_hex(data: bytes) -> str:
    return "blake2b:" + hashlib.blake2b(data, digest_size=32).hexdigest()


__all__ = [
    "SigningKey",
    "sha256_hex",
    "sha256_raw",
    "blake2b_hex",
]
