"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/signing/pqc.py
Purpose: Post-quantum signature migration interface (ML-DSA / CRYSTALS-Dilithium)
Classification: domain
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.

This module provides:
1. An abstract SignatureScheme interface that abstracts over signature schemes.
2. A registry of schemes (Ed25519, ML-DSA-65, future schemes).
3. A MigrationService that re-signs existing events with a new scheme while
   preserving the original signatures (per spec/PERMANENT_RECORD_PROTOCOL.md).
4. A SchemeVersioning record that tracks which scheme was used for each event.

The module is interface-complete. Live use of ML-DSA requires either:
- liboqs-python (https://github.com/open-quantum-safe/liboqs-python) with
  NIST PQC standardized algorithms (ML-DSA, SLH-DSA), OR
- A cloud KMS that supports PQC signing (when available).

The cryptography library (PyCA) is expected to add PQC support in a future
release (tracked at https://github.com/pyca/cryptography/issues/10845).

Until PQC libraries are available, the PQCSignatureScheme classes raise
NotImplementedError on sign/verify. The migration interface is ready;
the algorithms will be plugged in when standardized libraries are available.
"""
from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC
from typing import Any


@dataclass
class SignatureResult:
    """A signature with its scheme identifier.

    The scheme field allows mixed-scheme ledgers: events signed with
    different schemes can coexist, and verifiers select the appropriate
    scheme based on the scheme field.
    """
    scheme: str  # 'Ed25519' | 'ML-DSA-65' | 'SLH-DSA-128s' | ...
    value: str  # '<scheme>:<base64>'
    signing_key_id: str


class SignatureScheme(ABC):
    """Abstract interface for signature schemes.

    All schemes implement the same interface, allowing transparent
    migration between schemes (e.g., Ed25519 -> ML-DSA-65).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Scheme name (e.g., 'Ed25519', 'ML-DSA-65')."""
        ...

    @property
    @abstractmethod
    def quantum_safe(self) -> bool:
        """Whether this scheme is resistant to quantum attacks."""
        ...

    @property
    @abstractmethod
    def signature_size_bytes(self) -> int:
        """Expected signature size in bytes."""
        ...

    @abstractmethod
    def generate_keypair(self, key_id: str) -> KeyPair:
        """Generate a new keypair."""
        ...

    @abstractmethod
    def sign(self, private_key: Any, message: bytes) -> str:
        """Sign a message and return '<scheme>:<base64>'."""
        ...

    @abstractmethod
    def verify(self, public_key: Any, message: bytes, signature: str) -> bool:
        """Verify a signature."""
        ...


@dataclass
class KeyPair:
    """A keypair for a specific signature scheme."""
    key_id: str
    scheme: str
    private_key: Any
    public_key: Any
    public_pem: str  # PEM-encoded public key for verification


class Ed25519Scheme(SignatureScheme):
    """Ed25519 signature scheme (current default).

    Quantum-safe: NO (vulnerable to Shor's algorithm on sufficiently
    large quantum computers).
    """

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
        sig = private_key.sign(message)
        return f"Ed25519:{base64.b64encode(sig).decode('ascii')}"

    def verify(self, public_key: Any, message: bytes, signature: str) -> bool:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        if not isinstance(public_key, Ed25519PublicKey):
            return False
        if not signature.startswith("Ed25519:"):
            return False
        try:
            sig_bytes = base64.b64decode(signature[len("Ed25519:"):])
            public_key.verify(sig_bytes, message)
            return True
        except Exception:
            return False


class MLDSA65Scheme(SignatureScheme):
    """ML-DSA-65 (CRYSTALS-Dilithium, security level 3) signature scheme.

    NIST PQC standardization: FIPS 204 (August 2024).
    Quantum-safe: YES.

    This class is interface-complete. Live signing requires liboqs-python
    or a cloud KMS that supports ML-DSA. Install with:
        pip install liboqs-python
    (requires liboqs system library: https://github.com/open-quantum-safe/liboqs)
    """

    @property
    def name(self) -> str:
        return "ML-DSA-65"

    @property
    def quantum_safe(self) -> bool:
        return True

    @property
    def signature_size_bytes(self) -> int:
        return 3309  # ML-DSA-65 signature size per FIPS 204

    def _ensure_liboqs(self) -> None:
        try:
            import oqs  # type: ignore
            return oqs
        except ImportError as e:
            raise ImportError(
                "liboqs-python is required for ML-DSA signing. "
                "Install with: pip install liboqs-python "
                "(requires liboqs system library)"
            ) from e

    def generate_keypair(self, key_id: str) -> KeyPair:
        oqs = self._ensure_liboqs()
        # Real implementation:
        # with oqs.Signature("ML-DSA-65") as signer:
        #     public_key = signer.generate_keypair()
        #     private_key = signer.export_secret_key()
        # For interface completeness, raise NotImplementedError
        raise NotImplementedError(
            "ML-DSA key generation requires liboqs-python. "
            "Implement using oqs.Signature('ML-DSA-65')."
        )

    def sign(self, private_key: Any, message: bytes) -> str:
        oqs = self._ensure_liboqs()
        # Real implementation:
        # with oqs.Signature("ML-DSA-65", secret_key=private_key) as signer:
        #     sig = signer.sign(message)
        # return f"ML-DSA-65:{base64.b64encode(sig).decode('ascii')}"
        raise NotImplementedError(
            "ML-DSA signing requires liboqs-python. "
            "Implement using oqs.Signature('ML-DSA-65', secret_key=...).sign(message)."
        )

    def verify(self, public_key: Any, message: bytes, signature: str) -> bool:
        oqs = self._ensure_liboqs()
        if not signature.startswith("ML-DSA-65:"):
            return False
        # Real implementation:
        # with oqs.Signature("ML-DSA-65") as verifier:
        #     return verifier.verify(message, sig_bytes, public_key)
        raise NotImplementedError(
            "ML-DSA verification requires liboqs-python. "
            "Implement using oqs.Signature('ML-DSA-65').verify(message, sig, public_key)."
        )


class SLHDSA128sScheme(SignatureScheme):
    """SLH-DSA-128s (SPHINCS+-128s) signature scheme.

    NIST PQC standardization: FIPS 205 (August 2024).
    Quantum-safe: YES (hash-based, conservative security).

    Smaller signatures would use SLH-DSA-128f (fast variant) but larger
    signature size. SLH-DSA-128s has smaller signatures but slower signing.

    This class is interface-complete. Live signing requires liboqs-python.
    """

    @property
    def name(self) -> str:
        return "SLH-DSA-128s"

    @property
    def quantum_safe(self) -> bool:
        return True

    @property
    def signature_size_bytes(self) -> int:
        return 7856  # SLH-DSA-128s signature size per FIPS 205

    def _ensure_liboqs(self) -> None:
        try:
            import oqs  # type: ignore
            return oqs
        except ImportError as e:
            raise ImportError(
                "liboqs-python is required for SLH-DSA signing."
            ) from e

    def generate_keypair(self, key_id: str) -> KeyPair:
        raise NotImplementedError(
            "SLH-DSA key generation requires liboqs-python."
        )

    def sign(self, private_key: Any, message: bytes) -> str:
        raise NotImplementedError(
            "SLH-DSA signing requires liboqs-python."
        )

    def verify(self, public_key: Any, message: bytes, signature: str) -> bool:
        raise NotImplementedError(
            "SLH-DSA verification requires liboqs-python."
        )


class SchemeRegistry:
    """Registry of available signature schemes.

    The registry allows the system to look up a scheme by name and to
    enumerate available schemes (e.g., for migration planning).
    """

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
        return list(self._schemes.keys())

    def quantum_safe_schemes(self) -> list[str]:
        return [name for name, scheme in self._schemes.items() if scheme.quantum_safe]


@dataclass
class SchemeMigrationRecord:
    """Record of a signature migration.

    Per spec/PERMANENT_RECORD_PROTOCOL.md, migration:
    1. Adopts a new signature scheme.
    2. Re-signs existing events with the new scheme.
    3. Records the re-signing as a new signed event.
    4. Preserves the original signatures.
    """
    migration_id: str
    from_scheme: str
    to_scheme: str
    migrated_event_ids: list[str] = field(default_factory=list)
    migrated_at: str = ""
    migrated_by: str = ""
    signature: str = ""
    signing_key_id: str = ""


class MigrationService:
    """Service for migrating events from one signature scheme to another.

    The migration preserves original signatures (per the permanent-record
    protocol). Each migrated event receives a NEW signature in the new
    scheme, recorded as a new migration event. The original event and
    signature are preserved.

    Migration is irreversible: once migrated, the new scheme is canonical.
    However, the original signatures remain verifiable for audit purposes.
    """

    def __init__(self, registry: SchemeRegistry) -> None:
        self._registry = registry
        self._migrations: list[SchemeMigrationRecord] = []

    def plan_migration(self, from_scheme: str, to_scheme: str) -> dict[str, Any]:
        """Plan a migration from one scheme to another.

        Returns a migration plan with:
        - scheme details
        - estimated effort
        - risk assessment
        - recommended timeline
        """
        from_s = self._registry.get(from_scheme)
        to_s = self._registry.get(to_scheme)
        return {
            "from_scheme": from_scheme,
            "to_scheme": to_scheme,
            "from_quantum_safe": from_s.quantum_safe,
            "to_quantum_safe": to_s.quantum_safe,
            "from_signature_size": from_s.signature_size_bytes,
            "to_signature_size": to_s.signature_size_bytes,
            "size_increase_bytes": to_s.signature_size_bytes - from_s.signature_size_bytes,
            "size_increase_percent": ((to_s.signature_size_bytes - from_s.signature_size_bytes) / from_s.signature_size_bytes) * 100,
            "recommended": to_s.quantum_safe and not from_s.quantum_safe,
            "risk_assessment": "low" if to_s.quantum_safe else "high",
            "notes": (
                f"Migration from {from_scheme} (quantum_safe={from_s.quantum_safe}) "
                f"to {to_scheme} (quantum_safe={to_s.quantum_safe}). "
                f"Signature size changes from {from_s.signature_size_bytes} bytes "
                f"to {to_s.signature_size_bytes} bytes."
            ),
        }

    def migrate_events(
        self,
        events: list[Any],
        from_scheme: str,
        to_scheme: str,
        new_signing_key_id: str,
        new_private_key: Any,
    ) -> SchemeMigrationRecord:
        """Migrate a list of events from one scheme to another.

        For each event:
        1. Compute the canonical form (excluding signature).
        2. Sign with the new scheme.
        3. Attach the new signature (the original signature is preserved in
           a 'signatures' field for audit).

        Returns a migration record.
        """
        from datetime import datetime

        from aegistrace.identity.ids import make_event_id
        from aegistrace.signing.canonical import canonicalize_for_signature

        to_scheme_obj = self._registry.get(to_scheme)
        migrated_ids: list[str] = []
        for event in events:
            if hasattr(event, "to_dict"):
                event_dict = event.to_dict()
            else:
                event_dict = event
            # Compute canonical form for re-signing
            canon = canonicalize_for_signature(event_dict)
            # Sign with new scheme
            try:
                new_sig = to_scheme_obj.sign(new_private_key, canon)
            except NotImplementedError as e:
                raise NotImplementedError(
                    f"Cannot migrate to {to_scheme}: {e}. "
                    "Install the required PQC library."
                ) from e
            # Attach new signature (preserving original)
            if hasattr(event, "signature"):
                # Preserve original signature in a signatures list
                if not hasattr(event, "_migration_signatures"):
                    event._migration_signatures = []
                event._migration_signatures.append({
                    "scheme": event_dict.get("signing_scheme", from_scheme),
                    "signature": event.signature,
                    "signing_key_id": event.signing_key_id,
                })
                event.signature = new_sig
                event.signing_key_id = new_signing_key_id
                # Add a scheme field if not present
                if not hasattr(event, "signing_scheme"):
                    event.signing_scheme = to_scheme
            migrated_ids.append(event_dict.get("event_id", ""))
        # Create migration record
        migration = SchemeMigrationRecord(
            migration_id="mig_" + make_event_id()[4:],
            from_scheme=from_scheme,
            to_scheme=to_scheme,
            migrated_event_ids=migrated_ids,
            migrated_at=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            migrated_by=new_signing_key_id,
            signing_key_id=new_signing_key_id,
        )
        self._migrations.append(migration)
        return migration

    def list_migrations(self) -> list[SchemeMigrationRecord]:
        return list(self._migrations)


# Module-level singleton registry
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
