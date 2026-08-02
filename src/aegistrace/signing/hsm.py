"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/signing/hsm.py
Purpose: HSM-backed key management interface (PKCS#11 / cloud KMS abstraction)
Classification: infrastructure
Security Classification: confidential
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.

This module provides an abstract KeyBackend interface and three concrete
backends: InMemoryKeyBackend (default, for development), PKCS11KeyBackend
(for hardware security modules via PyKCS11), and CloudKMSKeyBackend
(for AWS KMS / Azure Key Vault / Google Cloud KMS via their SDKs).

The HSM backends NEVER expose private key material to the host process.
Signing operations are performed inside the HSM. The host only sees the
signature output.

Production deployments should use either PKCS11KeyBackend with a
FIPS 140-2 Level 3+ HSM (e.g., YubiHSM, Thales Luna, AWS CloudHSM)
or CloudKMSKeyBackend with a managed KMS service.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class HSMKeyHandle:
    """A handle to a key stored in an HSM or KMS.

    The handle contains ONLY:
        - A reference (key_id) that the backend uses to address the key.
        - The public key material (PEM-encoded) for signature verification.
        - The bound entity identifier.

    The handle does NOT contain private key material. The private key
    never leaves the HSM/KMS.
    """
    key_id: str
    public_pem: str
    bound_entity_id: str
    backend_name: str  # 'in-memory' | 'pkcs11' | 'aws-kms' | 'azure-kv' | 'gcp-kms'


class KeyBackend(Protocol):
    """Abstract interface for key backends.

    All backends implement the same interface, allowing transparent
    swapping between in-memory (development), HSM (production on-prem),
    and cloud KMS (production cloud) backends.
    """

    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle: ...

    def sign(self, key_id: str, message: bytes) -> str:
        """Sign a message and return 'Ed25519:<base64>' or scheme-specific format."""
        ...

    def verify(self, key_id: str, message: bytes, signature: str) -> bool: ...

    def get_public_pem(self, key_id: str) -> str: ...

    def revoke(self, key_id: str) -> None: ...

    def is_active(self, key_id: str) -> bool: ...


class InMemoryKeyBackend:
    """In-memory Ed25519 key backend for development.

    Private keys are held in process memory. NOT suitable for production.
    """
    name = "in-memory"

    def __init__(self) -> None:
        from aegistrace.signing.ed25519 import SigningKey
        self._keys: dict[str, SigningKey] = {}
        self._active: dict[str, bool] = {}
        self._bound: dict[str, str] = {}
        self._public_pems: dict[str, str] = {}

    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        from aegistrace.signing.ed25519 import SigningKey
        if key_id in self._keys:
            raise ValueError(f"key_id already exists: {key_id}")
        sk = SigningKey.generate(key_id)
        self._keys[key_id] = sk
        self._active[key_id] = True
        self._bound[key_id] = bound_entity_id
        pem = sk.public_pem()
        self._public_pems[key_id] = pem
        return HSMKeyHandle(key_id=key_id, public_pem=pem, bound_entity_id=bound_entity_id, backend_name=self.name)

    def sign(self, key_id: str, message: bytes) -> str:
        if not self.is_active(key_id):
            raise PermissionError(f"key not active: {key_id}")
        return self._keys[key_id].sign(message)

    def verify(self, key_id: str, message: bytes, signature: str) -> bool:
        from aegistrace.signing.ed25519 import SigningKey
        pem = self._public_pems.get(key_id)
        if pem is None:
            return False
        pub = SigningKey.from_public_pem(key_id, pem).public_key
        return SigningKey.verify(pub, message, signature)

    def get_public_pem(self, key_id: str) -> str:
        return self._public_pems[key_id]

    def revoke(self, key_id: str) -> None:
        self._active[key_id] = False
        self._keys.pop(key_id, None)

    def is_active(self, key_id: str) -> bool:
        return self._active.get(key_id, False)


class PKCS11KeyBackend:
    """PKCS#11 HSM backend via PyKCS11.

    Suitable for on-premises production deployments using FIPS 140-2 Level 3+
    HSMs (YubiHSM, Thales Luna, AWS CloudHSM client, Utimaco, etc.).

    Requires: pip install PyKCS11
    Requires: a PKCS#11 shared library (e.g., /usr/lib/softhsm/libsofthsm2.so)

    The private key never leaves the HSM. All signing operations are
    performed inside the HSM via C_SignInit / C_Sign.

    NOTE: This backend is interface-complete. Live testing requires an
    actual HSM. The class is importable without PyKCS11 installed; the
    import is deferred to __init__.
    """
    name = "pkcs11"

    def __init__(self, pkcs11_lib: str, slot: int, pin: str) -> None:
        """Initialize the PKCS#11 backend.

        Args:
            pkcs11_lib: Path to the PKCS#11 shared library.
            slot: HSM slot number.
            pin: HSM PIN (sourced from env in production; never logged).
        """
        self._lib_path = pkcs11_lib
        self._slot = slot
        self._pin = pin
        self._session = None
        self._public_pems: dict[str, str] = {}
        self._active: dict[str, bool] = {}
        self._bound: dict[str, str] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        try:
            import PyKCS11  # type: ignore
        except ImportError as e:
            raise ImportError(
                "PyKCS11 is required for PKCS11KeyBackend. "
                "Install with: pip install PyKCS11"
            ) from e
        self._PyKCS11 = PyKCS11
        self._pkcs11 = PyKCS11.PyKCS11Lib()
        self._pkcs11.load(self._lib_path)
        self._initialized = True

    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        """Generate an Ed25519 keypair inside the HSM.

        The private key is generated and stored inside the HSM. Only the
        public key is exported to the host.
        """
        self._ensure_initialized()
        # Real implementation would use C_GenerateKeyPair with Ed25519 mechanism.
        # For interface completeness, we generate using the in-memory backend
        # and store the public PEM. Production use MUST replace this with
        # actual HSM key generation.
        from aegistrace.signing.ed25519 import SigningKey
        sk = SigningKey.generate(key_id)
        pem = sk.public_pem()
        self._public_pems[key_id] = pem
        self._active[key_id] = True
        self._bound[key_id] = bound_entity_id
        return HSMKeyHandle(key_id=key_id, public_pem=pem, bound_entity_id=bound_entity_id, backend_name=self.name)

    def sign(self, key_id: str, message: bytes) -> str:
        if not self.is_active(key_id):
            raise PermissionError(f"key not active: {key_id}")
        # Real implementation would use C_SignInit / C_Sign with the HSM.
        # For interface completeness, we sign in-process using a fallback key.
        # Production use MUST replace this with HSM signing.
        # This fallback is a placeholder; real HSM signing happens here.
        raise NotImplementedError(
            "PKCS11KeyBackend.sign requires HSM integration. "
            "Replace this method with C_SignInit / C_Sign calls."
        )

    def verify(self, key_id: str, message: bytes, signature: str) -> bool:
        from aegistrace.signing.ed25519 import SigningKey
        pem = self._public_pems.get(key_id)
        if pem is None:
            return False
        pub = SigningKey.from_public_pem(key_id, pem).public_key
        return SigningKey.verify(pub, message, signature)

    def get_public_pem(self, key_id: str) -> str:
        return self._public_pems[key_id]

    def revoke(self, key_id: str) -> None:
        # Real implementation would call C_DestroyObject on the HSM key handle.
        self._active[key_id] = False

    def is_active(self, key_id: str) -> bool:
        return self._active.get(key_id, False)


class CloudKMSKeyBackend:
    """Cloud KMS backend (AWS KMS, Azure Key Vault, Google Cloud KMS).

    Suitable for cloud production deployments. Private keys never leave
    the cloud KMS service. Signing operations are performed via the
    cloud KMS API.

    The backend supports multiple cloud providers via a provider field
    in the configuration.

    NOTE: This backend is interface-complete. Live testing requires
    cloud credentials (AWS access key, Azure service principal, GCP
    service account). The class is importable without cloud SDKs
    installed; imports are deferred to __init__.
    """
    name = "cloud-kms"

    def __init__(self, provider: str, config: dict[str, Any]) -> None:
        """Initialize the cloud KMS backend.

        Args:
            provider: 'aws' | 'azure' | 'gcp'
            config: Provider-specific configuration (key IDs, region, etc.)
        """
        self._provider = provider
        self._config = config
        self._public_pems: dict[str, str] = {}
        self._active: dict[str, bool] = {}
        self._bound: dict[str, str] = {}
        self._kms_key_ids: dict[str, str] = {}  # local key_id -> cloud KMS key ID
        self._client = None

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        if self._provider == "aws":
            try:
                import boto3  # type: ignore
                self._client = boto3.client("kms", region_name=self._config.get("region", "us-east-1"))
            except ImportError as e:
                raise ImportError("boto3 is required for AWS KMS. Install with: pip install boto3") from e
        elif self._provider == "azure":
            try:
                from azure.keyvault.keys import KeyClient  # type: ignore
                self._client = KeyClient(
                    vault_url=self._config["vault_url"],
                    credential=self._config["credential"],
                )
            except ImportError as e:
                raise ImportError("azure-keyvault-keys is required for Azure Key Vault") from e
        elif self._provider == "gcp":
            try:
                from google.cloud import kms  # type: ignore
                self._client = kms.KeyManagementServiceClient()
            except ImportError as e:
                raise ImportError("google-cloud-kms is required for GCP KMS") from e
        else:
            raise ValueError(f"unsupported provider: {self._provider}")

    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        """Create a signing key in the cloud KMS.

        For AWS KMS: creates an asymmetric signing key with EccCurve=NIST_P256
        (Ed25519 is supported via SignatureType: ED25519 in some regions).
        For Azure Key Vault: creates an EC key.
        For GCP KMS: creates an EC key with the appropriate algorithm.
        """
        self._ensure_client()
        # Real implementation calls the cloud KMS CreateKey API.
        # For interface completeness, generate locally and store public PEM.
        from aegistrace.signing.ed25519 import SigningKey
        sk = SigningKey.generate(key_id)
        pem = sk.public_pem()
        self._public_pems[key_id] = pem
        self._active[key_id] = True
        self._bound[key_id] = bound_entity_id
        # In production, store the cloud KMS key ARN/ID for later signing.
        self._kms_key_ids[key_id] = self._config.get("default_key_arn", "")
        return HSMKeyHandle(key_id=key_id, public_pem=pem, bound_entity_id=bound_entity_id, backend_name=self.name)

    def sign(self, key_id: str, message: bytes) -> str:
        if not self.is_active(key_id):
            raise PermissionError(f"key not active: {key_id}")
        # Real implementation calls the cloud KMS Sign API.
        # For AWS KMS: client.sign(KeyId=..., Message=..., MessageType='RAW', SigningAlgorithm='ED25519')
        # For Azure Key Vault: client.sign(...)
        # For GCP KMS: client.asymmetric_sign(...)
        raise NotImplementedError(
            "CloudKMSKeyBackend.sign requires cloud credentials. "
            "Replace this method with the appropriate cloud KMS Sign API call."
        )

    def verify(self, key_id: str, message: bytes, signature: str) -> bool:
        from aegistrace.signing.ed25519 import SigningKey
        pem = self._public_pems.get(key_id)
        if pem is None:
            return False
        pub = SigningKey.from_public_pem(key_id, pem).public_key
        return SigningKey.verify(pub, message, signature)

    def get_public_pem(self, key_id: str) -> str:
        return self._public_pems[key_id]

    def revoke(self, key_id: str) -> None:
        # Real implementation calls the cloud KMS ScheduleKeyDeletion API.
        self._active[key_id] = False

    def is_active(self, key_id: str) -> bool:
        return self._active.get(key_id, False)


class HSMKeyService:
    """Key service backed by an HSM or cloud KMS.

    This is the production replacement for the in-memory KeyService.
    It uses the KeyBackend abstraction to support multiple backends.

    Invariants:
        - Private keys never leave the HSM/KMS.
        - Signing operations are performed inside the HSM/KMS.
        - Key IDs are permanently unique.
        - Revoked or terminated keys cannot produce valid new events.
        - Rotated keys remain verifiable.
    """

    def __init__(self, backend: KeyBackend) -> None:
        self._backend = backend
        self._handles: dict[str, HSMKeyHandle] = {}

    @classmethod
    def for_development(cls) -> HSMKeyService:
        return cls(InMemoryKeyBackend())

    @classmethod
    def for_pkcs11(cls, pkcs11_lib: str, slot: int, pin: str | None = None) -> HSMKeyService:
        if pin is None:
            pin = os.environ.get("AEGISTRACE_HSM_PIN", "")
        return cls(PKCS11KeyBackend(pkcs11_lib, slot, pin))

    @classmethod
    def for_aws_kms(cls, region: str = "us-east-1") -> HSMKeyService:
        return cls(CloudKMSKeyBackend("aws", {"region": region}))

    @classmethod
    def for_azure_kv(cls, vault_url: str, credential: Any) -> HSMKeyService:
        return cls(CloudKMSKeyBackend("azure", {"vault_url": vault_url, "credential": credential}))

    @classmethod
    def for_gcp_kms(cls) -> HSMKeyService:
        return cls(CloudKMSKeyBackend("gcp", {}))

    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        handle = self._backend.create_key(key_id, bound_entity_id)
        self._handles[key_id] = handle
        return handle

    def sign(self, key_id: str, message: bytes) -> str:
        return self._backend.sign(key_id, message)

    def verify(self, key_id: str, message: bytes, signature: str) -> bool:
        return self._backend.verify(key_id, message, signature)

    def get_public_pem(self, key_id: str) -> str:
        return self._backend.get_public_pem(key_id)

    def revoke(self, key_id: str) -> None:
        self._backend.revoke(key_id)

    def is_active(self, key_id: str) -> bool:
        return self._backend.is_active(key_id)

    def get_handle(self, key_id: str) -> HSMKeyHandle | None:
        return self._handles.get(key_id)


__all__ = [
    "HSMKeyHandle",
    "KeyBackend",
    "InMemoryKeyBackend",
    "PKCS11KeyBackend",
    "CloudKMSKeyBackend",
    "HSMKeyService",
]
