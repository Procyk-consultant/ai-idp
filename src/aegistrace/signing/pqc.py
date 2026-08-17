"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/signing/pqc.py
Purpose: Post-quantum signature schemes and migration support
Classification: domain
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar


@dataclass
class SignatureResult:
    scheme: str
    value: str
    signing_key_id: str


@dataclass
class KeyPair:
    key_id: str
    scheme: str
    private_key: Any
    public_key: Any
    public_pem: str


class SignatureScheme(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def quantum_safe(self) -> bool: ...

    @property
    @abstractmethod
    def signature_size_bytes(self) -> int: ...

    @abstractmethod
    def generate_keypair(self, key_id: str) -> KeyPair: ...

    @abstractmethod
    def sign(self, private_key: Any, message: bytes) -> str: ...

    @abstractmethod
    def verify(self, public_key: Any, message: bytes, signature: str) -> bool: ...


class Ed25519Scheme(SignatureScheme):
    @property
    def name(self) -> str:
        return "Ed25519"

    @property
    def quantum_safe(self) -> bool:
        return False

    @property
    def signature_size_bytes(self) -> int:
        return 64

    def generate_keypair(self, key_id: str) -> KeyPair:
        from aegistrace.signing.ed25519 import SigningKey

        sk = SigningKey.generate(key_id)
        return KeyPair(
            key_id=key_id,
            scheme=self.name,
            private_key=sk.private_key,
            public_key=sk.public_key,
            public_pem=sk.public_pem(),
        )

    def sign(self, private_key: Any, message: bytes) -> str:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        if not isinstance(private_key, Ed25519PrivateKey):
            raise TypeError("private_key must be Ed25519PrivateKey")
        value = private_key.sign(message)
        return f"Ed25519:{base64.b64encode(value).decode('ascii')}"

    def verify(self, public_key: Any, message: bytes, signature: str) -> bool:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        if not isinstance(public_key, Ed25519PublicKey) or not signature.startswith("Ed25519:"):
            return False
        try:
            public_key.verify(base64.b64decode(signature.split(":", 1)[1], validate=True), message)
            return True
        except Exception:
            return False


class _LibOQSSignatureScheme(SignatureScheme):
    """Shared live liboqs-python implementation for stateless PQ signatures."""

    algorithm_candidates: ClassVar[tuple[str, ...]] = ()
    signature_prefix: ClassVar[str]
    public_key_label: ClassVar[str]

    @property
    def quantum_safe(self) -> bool:
        return True

    def _oqs(self):
        try:
            import oqs  # type: ignore
        except ImportError as exc:
            raise ImportError(
                f"liboqs-python is required for {self.name}. Install the 'pqc' extra."
            ) from exc
        return oqs

    def _algorithm(self) -> str:
        oqs = self._oqs()
        enabled = set(oqs.get_enabled_sig_mechanisms())
        for candidate in self.algorithm_candidates:
            if candidate in enabled:
                return candidate
        raise RuntimeError(
            f"No enabled liboqs mechanism for {self.name}; expected one of {self.algorithm_candidates}."
        )

    def _armor(self, public_key: bytes) -> str:
        body = base64.b64encode(public_key).decode("ascii")
        return (
            f"-----BEGIN AEGISTRACE {self.public_key_label} PUBLIC KEY-----\n"
            f"{body}\n"
            f"-----END AEGISTRACE {self.public_key_label} PUBLIC KEY-----\n"
        )

    def generate_keypair(self, key_id: str) -> KeyPair:
        oqs = self._oqs()
        algorithm = self._algorithm()
        with oqs.Signature(algorithm) as signer:
            public_key = bytes(signer.generate_keypair())
            private_key = bytes(signer.export_secret_key())
        return KeyPair(
            key_id=key_id,
            scheme=self.name,
            private_key=private_key,
            public_key=public_key,
            public_pem=self._armor(public_key),
        )

    def sign(self, private_key: Any, message: bytes) -> str:
        if not isinstance(private_key, (bytes, bytearray, memoryview)):
            raise TypeError(f"private_key for {self.name} must be bytes-like")
        oqs = self._oqs()
        algorithm = self._algorithm()
        with oqs.Signature(algorithm, bytes(private_key)) as signer:
            signature = bytes(signer.sign(message))
        return f"{self.signature_prefix}:{base64.b64encode(signature).decode('ascii')}"

    def verify(self, public_key: Any, message: bytes, signature: str) -> bool:
        if not isinstance(public_key, (bytes, bytearray, memoryview)):
            return False
        expected = f"{self.signature_prefix}:"
        if not signature.startswith(expected):
            return False
        try:
            signature_bytes = base64.b64decode(signature[len(expected):], validate=True)
            oqs = self._oqs()
            algorithm = self._algorithm()
            with oqs.Signature(algorithm) as verifier:
                return bool(verifier.verify(message, signature_bytes, bytes(public_key)))
        except Exception:
            return False


class MLDSA65Scheme(_LibOQSSignatureScheme):
    """Live ML-DSA-65 implementation through liboqs-python."""

    algorithm_candidates = ("ML-DSA-65",)
    signature_prefix = "ML-DSA-65"
    public_key_label = "ML-DSA-65"

    @property
    def name(self) -> str:
        return "ML-DSA-65"

    @property
    def signature_size_bytes(self) -> int:
        return 3309


class SLHDSA128sScheme(_LibOQSSignatureScheme):
    """Live SLH-DSA SHA2-128s implementation through liboqs-python."""

    algorithm_candidates = (
        "SLH_DSA_PURE_SHA2_128S",
        "SPHINCS+-SHA2-128s-simple",
    )
    signature_prefix = "SLH-DSA-128s"
    public_key_label = "SLH-DSA-128S"

    @property
    def name(self) -> str:
        return "SLH-DSA-128s"

    @property
    def signature_size_bytes(self) -> int:
        return 7856


class SchemeRegistry:
    def __init__(self) -> None:
        self._schemes: dict[str, SignatureScheme] = {}
        self.register(Ed25519Scheme())
        self.register(MLDSA65Scheme())
        self.register(SLHDSA128sScheme())

    def register(self, scheme: SignatureScheme) -> None:
        self._schemes[scheme.name] = scheme

    def get(self, name: str) -> SignatureScheme:
        if name not in self._schemes:
            raise KeyError(f"unknown scheme: {name}")
        return self._schemes[name]

    def list_schemes(self) -> list[str]:
        return list(self._schemes)

    def quantum_safe_schemes(self) -> list[str]:
        return [name for name, scheme in self._schemes.items() if scheme.quantum_safe]


@dataclass
class SchemeMigrationRecord:
    migration_id: str
    from_scheme: str
    to_scheme: str
    migrated_event_ids: list[str] = field(default_factory=list)
    migrated_at: str = ""
    migrated_by: str = ""
    signature: str = ""
    signing_key_id: str = ""


class MigrationService:
    """Re-sign events with a new scheme while preserving historical signatures."""

    def __init__(self, registry: SchemeRegistry) -> None:
        self._registry = registry
        self._migrations: list[SchemeMigrationRecord] = []

    def plan_migration(self, from_scheme: str, to_scheme: str) -> dict[str, Any]:
        source = self._registry.get(from_scheme)
        target = self._registry.get(to_scheme)
        return {
            "from_scheme": from_scheme,
            "to_scheme": to_scheme,
            "from_quantum_safe": source.quantum_safe,
            "to_quantum_safe": target.quantum_safe,
            "from_signature_size": source.signature_size_bytes,
            "to_signature_size": target.signature_size_bytes,
            "size_increase_bytes": target.signature_size_bytes - source.signature_size_bytes,
            "size_increase_percent": (
                (target.signature_size_bytes - source.signature_size_bytes)
                / source.signature_size_bytes
            ) * 100,
            "recommended": target.quantum_safe and not source.quantum_safe,
            "risk_assessment": "low" if target.quantum_safe else "high",
        }

    def migrate_events(
        self,
        events: list[Any],
        from_scheme: str,
        to_scheme: str,
        new_signing_key_id: str,
        new_private_key: Any,
    ) -> SchemeMigrationRecord:
        from aegistrace.identity.ids import make_event_id
        from aegistrace.signing.canonical import canonicalize_for_signature

        target = self._registry.get(to_scheme)
        migrated_ids: list[str] = []
        for event in events:
            event_dict = event.to_dict() if hasattr(event, "to_dict") else dict(event)
            new_signature = target.sign(new_private_key, canonicalize_for_signature(event_dict))
            if hasattr(event, "signature"):
                historical = list(getattr(event, "_migration_signatures", []))
                historical.append(
                    {
                        "scheme": event_dict.get("signing_scheme", from_scheme),
                        "signature": event.signature,
                        "signing_key_id": event.signing_key_id,
                    }
                )
                event._migration_signatures = historical
                event.signature = new_signature
                event.signing_key_id = new_signing_key_id
                event.signing_scheme = to_scheme
            migrated_ids.append(event_dict.get("event_id", ""))

        record = SchemeMigrationRecord(
            migration_id="mig_" + make_event_id()[4:],
            from_scheme=from_scheme,
            to_scheme=to_scheme,
            migrated_event_ids=migrated_ids,
            migrated_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            migrated_by=new_signing_key_id,
            signing_key_id=new_signing_key_id,
        )
        self._migrations.append(record)
        return record

    def list_migrations(self) -> list[SchemeMigrationRecord]:
        return list(self._migrations)


default_registry = SchemeRegistry()

__all__ = [
    "SignatureResult",
    "SignatureScheme",
    "KeyPair",
    "Ed25519Scheme",
    "MLDSA65Scheme",
    "SLHDSA128sScheme",
    "SchemeRegistry",
    "SchemeMigrationRecord",
    "MigrationService",
    "default_registry",
]
