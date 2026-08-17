"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/signing/hsm.py
Purpose: Hardware and managed-KMS signing backends
Classification: infrastructure
Security Classification: confidential
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class HSMKeyHandle:
    key_id: str
    public_pem: str
    bound_entity_id: str
    backend_name: str
    remote_key_id: str | None = None
    signing_algorithm: str | None = None


class KeyBackend(Protocol):
    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle: ...
    def sign(self, key_id: str, message: bytes) -> str: ...
    def verify(self, key_id: str, message: bytes, signature: str) -> bool: ...
    def get_public_pem(self, key_id: str) -> str: ...
    def revoke(self, key_id: str) -> None: ...
    def is_active(self, key_id: str) -> bool: ...


class InMemoryKeyBackend:
    """Development-only Ed25519 backend."""

    name = "in-memory"

    def __init__(self) -> None:
        from aegistrace.signing.ed25519 import SigningKey

        self._keys: dict[str, SigningKey] = {}
        self._active: dict[str, bool] = {}
        self._bound: dict[str, str] = {}
        self._public_pems: dict[str, str] = {}

    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        from aegistrace.signing.ed25519 import SigningKey

        if key_id in self._public_pems:
            raise ValueError(f"key_id already exists: {key_id}")
        key = SigningKey.generate(key_id)
        public_pem = key.public_pem()
        self._keys[key_id] = key
        self._active[key_id] = True
        self._bound[key_id] = bound_entity_id
        self._public_pems[key_id] = public_pem
        return HSMKeyHandle(key_id, public_pem, bound_entity_id, self.name, signing_algorithm="Ed25519")

    def sign(self, key_id: str, message: bytes) -> str:
        if not self.is_active(key_id):
            raise PermissionError(f"key not active: {key_id}")
        return self._keys[key_id].sign(message)

    def verify(self, key_id: str, message: bytes, signature: str) -> bool:
        from aegistrace.signing.ed25519 import SigningKey

        public_pem = self._public_pems.get(key_id)
        if public_pem is None:
            return False
        public_key = SigningKey.from_public_pem(key_id, public_pem).public_key
        return SigningKey.verify(public_key, message, signature)

    def get_public_pem(self, key_id: str) -> str:
        return self._public_pems[key_id]

    def revoke(self, key_id: str) -> None:
        if key_id not in self._public_pems:
            raise KeyError(key_id)
        self._active[key_id] = False
        self._keys.pop(key_id, None)

    def is_active(self, key_id: str) -> bool:
        return self._active.get(key_id, False)


class PKCS11KeyBackend:
    """Ed25519 PKCS#11 backend.

    Key generation and signing occur inside the token. Only the public key and
    deterministic PKCS#11 object identifier are exposed to the host process.
    The implementation requires a PKCS#11 v3-capable token exposing Edwards
    curve key generation and CKM_EDDSA.
    """

    name = "pkcs11"
    _ED25519_OID_DER = bytes.fromhex("06032b6570")  # RFC 8410 id-Ed25519

    def __init__(self, pkcs11_lib: str, slot: int, pin: str) -> None:
        self._lib_path = pkcs11_lib
        self._slot = slot
        self._pin = pin
        self._module: Any = None
        self._session: Any = None
        self._public_pems: dict[str, str] = {}
        self._bound: dict[str, str] = {}

    @staticmethod
    def _object_id(key_id: str) -> bytes:
        return hashlib.sha256(key_id.encode("utf-8")).digest()[:20]

    def _ensure_session(self) -> None:
        if self._session is not None:
            return
        try:
            import PyKCS11  # type: ignore
        except ImportError as exc:
            raise ImportError("PyKCS11 is required for the hsm-pkcs11 backend") from exc

        required = (
            "CKK_EC_EDWARDS",
            "CKM_EC_EDWARDS_KEY_PAIR_GEN",
            "CKM_EDDSA",
        )
        missing = [name for name in required if not hasattr(PyKCS11, name)]
        if missing:
            raise RuntimeError(
                "The installed PyKCS11/PKCS#11 headers do not expose required EdDSA constants: "
                + ", ".join(missing)
            )

        module = PyKCS11.PyKCS11Lib()
        module.load(self._lib_path)
        flags = PyKCS11.CKF_SERIAL_SESSION | PyKCS11.CKF_RW_SESSION
        session = module.openSession(self._slot, flags)
        if self._pin:
            session.login(self._pin)
        self._module = PyKCS11
        self._session = session

    def _find(self, key_id: str, object_class: int) -> Any | None:
        self._ensure_session()
        module = self._module
        template = [
            (module.CKA_CLASS, object_class),
            (module.CKA_ID, list(self._object_id(key_id))),
        ]
        objects = self._session.findObjects(template)
        return objects[0] if objects else None

    @staticmethod
    def _decode_ec_point(value: bytes) -> bytes:
        raw = bytes(value)
        if len(raw) == 32:
            return raw
        if len(raw) == 34 and raw[:2] == b"\x04\x20":
            return raw[2:]
        if len(raw) > 2 and raw[0] == 0x04:
            length = raw[1]
            if length == len(raw) - 2:
                return raw[2:]
        raise ValueError("PKCS#11 token returned an unsupported Ed25519 CKA_EC_POINT encoding")

    def _public_pem(self, public_object: Any) -> str:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        module = self._module
        value = self._session.getAttributeValue(
            public_object,
            [module.CKA_EC_POINT],
            allAsBinary=True,
        )[0]
        raw = self._decode_ec_point(bytes(value))
        public_key = Ed25519PublicKey.from_public_bytes(raw)
        return public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")

    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        self._ensure_session()
        module = self._module
        if self._find(key_id, module.CKO_PRIVATE_KEY) is not None or self._find(key_id, module.CKO_PUBLIC_KEY) is not None:
            raise ValueError(f"key_id already exists in PKCS#11 token: {key_id}")

        object_id = list(self._object_id(key_id))
        label = f"aegistrace-{hashlib.sha256(key_id.encode()).hexdigest()[:16]}"
        public_template = [
            (module.CKA_CLASS, module.CKO_PUBLIC_KEY),
            (module.CKA_KEY_TYPE, module.CKK_EC_EDWARDS),
            (module.CKA_TOKEN, True),
            (module.CKA_PRIVATE, False),
            (module.CKA_VERIFY, True),
            (module.CKA_LABEL, label),
            (module.CKA_ID, object_id),
            (module.CKA_EC_PARAMS, list(self._ED25519_OID_DER)),
        ]
        private_template = [
            (module.CKA_CLASS, module.CKO_PRIVATE_KEY),
            (module.CKA_KEY_TYPE, module.CKK_EC_EDWARDS),
            (module.CKA_TOKEN, True),
            (module.CKA_PRIVATE, True),
            (module.CKA_SENSITIVE, True),
            (module.CKA_EXTRACTABLE, False),
            (module.CKA_SIGN, True),
            (module.CKA_LABEL, label),
            (module.CKA_ID, object_id),
        ]
        mechanism = module.Mechanism(module.CKM_EC_EDWARDS_KEY_PAIR_GEN, None)
        public_object, _private_object = self._session.generateKeyPair(
            public_template,
            private_template,
            mechanism,
        )
        public_pem = self._public_pem(public_object)
        self._public_pems[key_id] = public_pem
        self._bound[key_id] = bound_entity_id
        return HSMKeyHandle(
            key_id,
            public_pem,
            bound_entity_id,
            self.name,
            remote_key_id=self._object_id(key_id).hex(),
            signing_algorithm="Ed25519",
        )

    def sign(self, key_id: str, message: bytes) -> str:
        self._ensure_session()
        private_object = self._find(key_id, self._module.CKO_PRIVATE_KEY)
        if private_object is None:
            raise PermissionError(f"PKCS#11 private key unavailable or revoked: {key_id}")
        mechanism = self._module.Mechanism(self._module.CKM_EDDSA, None)
        signature = bytes(self._session.sign(private_object, message, mechanism))
        return f"Ed25519:{base64.b64encode(signature).decode('ascii')}"

    def verify(self, key_id: str, message: bytes, signature: str) -> bool:
        from aegistrace.signing.ed25519 import SigningKey

        if not signature.startswith("Ed25519:"):
            return False
        try:
            public_pem = self.get_public_pem(key_id)
            public_key = SigningKey.from_public_pem(key_id, public_pem).public_key
            return SigningKey.verify(public_key, message, signature)
        except Exception:
            return False

    def get_public_pem(self, key_id: str) -> str:
        cached = self._public_pems.get(key_id)
        if cached is not None:
            return cached
        self._ensure_session()
        public_object = self._find(key_id, self._module.CKO_PUBLIC_KEY)
        if public_object is None:
            raise KeyError(key_id)
        public_pem = self._public_pem(public_object)
        self._public_pems[key_id] = public_pem
        return public_pem

    def revoke(self, key_id: str) -> None:
        self._ensure_session()
        private_object = self._find(key_id, self._module.CKO_PRIVATE_KEY)
        if private_object is None:
            raise KeyError(key_id)
        self._session.destroyObject(private_object)

    def is_active(self, key_id: str) -> bool:
        self._ensure_session()
        return self._find(key_id, self._module.CKO_PRIVATE_KEY) is not None


class CloudKMSKeyBackend:
    """Managed signing backend for AWS KMS, Azure Key Vault, or Google Cloud KMS."""

    name = "cloud-kms"

    def __init__(self, provider: str, config: dict[str, Any]) -> None:
        if provider not in {"aws", "azure", "gcp"}:
            raise ValueError(f"unsupported provider: {provider}")
        self._provider = provider
        self._config = dict(config)
        self._client: Any = None
        self._crypto_clients: dict[str, Any] = {}
        self._public_pems: dict[str, str] = {}
        self._bound: dict[str, str] = {}
        self._remote_ids: dict[str, str] = {}
        self._algorithms: dict[str, str] = {}
        self._active: dict[str, bool] = {}

    @staticmethod
    def _remote_name(key_id: str) -> str:
        return "aegistrace-" + hashlib.sha256(key_id.encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def _pem_from_der(public_der: bytes) -> str:
        from cryptography.hazmat.primitives import serialization

        key = serialization.load_der_public_key(public_der)
        return key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        if self._provider == "aws":
            try:
                import boto3  # type: ignore
            except ImportError as exc:
                raise ImportError("boto3 is required for the hsm-aws backend") from exc
            self._client = boto3.client("kms", region_name=self._config.get("region", "us-east-1"))
            return
        if self._provider == "azure":
            try:
                from azure.keyvault.keys import KeyClient  # type: ignore
            except ImportError as exc:
                raise ImportError("azure-keyvault-keys is required for the hsm-azure backend") from exc
            self._client = KeyClient(
                vault_url=self._config["vault_url"],
                credential=self._config["credential"],
            )
            return
        try:
            from google.cloud import kms_v1  # type: ignore
        except ImportError as exc:
            raise ImportError("google-cloud-kms is required for the hsm-gcp backend") from exc
        self._client = kms_v1.KeyManagementServiceClient()

    def _remember(
        self,
        *,
        key_id: str,
        bound_entity_id: str,
        remote_id: str,
        public_pem: str,
        algorithm: str,
    ) -> HSMKeyHandle:
        self._remote_ids[key_id] = remote_id
        self._public_pems[key_id] = public_pem
        self._bound[key_id] = bound_entity_id
        self._algorithms[key_id] = algorithm
        self._active[key_id] = True
        return HSMKeyHandle(
            key_id=key_id,
            public_pem=public_pem,
            bound_entity_id=bound_entity_id,
            backend_name=f"{self._provider}-kms",
            remote_key_id=remote_id,
            signing_algorithm=algorithm,
        )

    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        if key_id in self._remote_ids:
            raise ValueError(f"key_id already exists: {key_id}")
        self._ensure_client()
        if self._provider == "aws":
            return self._create_aws(key_id, bound_entity_id)
        if self._provider == "azure":
            return self._create_azure(key_id, bound_entity_id)
        return self._create_gcp(key_id, bound_entity_id)

    def _create_aws(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        key_spec = self._config.get("key_spec", "ECC_NIST_EDWARDS25519")
        response = self._client.create_key(
            KeyUsage="SIGN_VERIFY",
            KeySpec=key_spec,
            Description=f"AegisTrace signing key for {key_id}",
        )
        metadata = response["KeyMetadata"]
        remote_id = metadata.get("Arn") or metadata["KeyId"]
        algorithms = metadata.get("SigningAlgorithms") or []
        preferred = {
            "ECC_NIST_EDWARDS25519": "ED25519_SHA_512",
            "ECC_NIST_P256": "ECDSA_SHA_256",
            "ML_DSA_65": "ML_DSA_SHAKE_256",
        }.get(key_spec)
        algorithm = preferred if preferred in algorithms or not algorithms else algorithms[0]
        if algorithm is None:
            raise RuntimeError(f"AWS KMS key {remote_id} exposes no signing algorithm")
        public_der = bytes(self._client.get_public_key(KeyId=remote_id)["PublicKey"])
        public_pem = self._pem_from_der(public_der)
        return self._remember(
            key_id=key_id,
            bound_entity_id=bound_entity_id,
            remote_id=remote_id,
            public_pem=public_pem,
            algorithm=algorithm,
        )

    def _create_azure(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        from azure.keyvault.keys import KeyCurveName, KeyOperation  # type: ignore
        from azure.keyvault.keys.crypto import CryptographyClient  # type: ignore
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec

        name = self._remote_name(key_id)
        key = self._client.create_ec_key(
            name,
            curve=KeyCurveName.p_256,
            key_operations=[KeyOperation.sign, KeyOperation.verify],
            hardware_protected=bool(self._config.get("hardware_protected", True)),
            enabled=True,
        )
        jwk = key.key
        if jwk.x is None or jwk.y is None:
            raise RuntimeError("Azure Key Vault did not return EC public coordinates")
        public_key = ec.EllipticCurvePublicNumbers(
            int.from_bytes(bytes(jwk.x), "big"),
            int.from_bytes(bytes(jwk.y), "big"),
            ec.SECP256R1(),
        ).public_key()
        public_pem = public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")
        remote_id = key.id
        self._crypto_clients[key_id] = CryptographyClient(key, credential=self._config["credential"])
        return self._remember(
            key_id=key_id,
            bound_entity_id=bound_entity_id,
            remote_id=remote_id,
            public_pem=public_pem,
            algorithm="ES256",
        )

    def _create_gcp(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        from google.cloud import kms_v1  # type: ignore

        required = ("project_id", "location_id", "key_ring_id")
        missing = [field for field in required if not self._config.get(field)]
        if missing:
            raise ValueError("GCP KMS requires config fields: " + ", ".join(missing))
        project = self._config["project_id"]
        location = self._config["location_id"]
        key_ring = self._config["key_ring_id"]
        name = self._remote_name(key_id)
        parent = self._client.key_ring_path(project, location, key_ring)
        protection = (
            kms_v1.ProtectionLevel.HSM
            if self._config.get("hardware_protected", True)
            else kms_v1.ProtectionLevel.SOFTWARE
        )
        crypto_key = self._client.create_crypto_key(
            request={
                "parent": parent,
                "crypto_key_id": name,
                "crypto_key": {
                    "purpose": kms_v1.CryptoKey.CryptoKeyPurpose.ASYMMETRIC_SIGN,
                    "version_template": {
                        "algorithm": kms_v1.CryptoKeyVersion.CryptoKeyVersionAlgorithm.EC_SIGN_P256_SHA256,
                        "protection_level": protection,
                    },
                },
            }
        )
        version_name = self._client.crypto_key_version_path(project, location, key_ring, name, "1")
        public = self._client.get_public_key(request={"name": version_name})
        return self._remember(
            key_id=key_id,
            bound_entity_id=bound_entity_id,
            remote_id=version_name,
            public_pem=public.pem,
            algorithm="EC_SIGN_P256_SHA256",
        )

    def sign(self, key_id: str, message: bytes) -> str:
        if not self.is_active(key_id):
            raise PermissionError(f"key not active: {key_id}")
        if self._provider == "aws":
            algorithm = self._algorithms[key_id]
            if len(message) > 4096:
                raise ValueError("AWS KMS RAW signing accepts messages up to 4096 bytes for this backend")
            result = self._client.sign(
                KeyId=self._remote_ids[key_id],
                Message=message,
                MessageType="RAW",
                SigningAlgorithm=algorithm,
            )
            prefix = {
                "ED25519_SHA_512": "Ed25519",
                "ML_DSA_SHAKE_256": "ML-DSA-65",
                "ECDSA_SHA_256": "ECDSA-SHA256",
            }.get(algorithm, algorithm)
            return f"{prefix}:{base64.b64encode(bytes(result['Signature'])).decode('ascii')}"

        if self._provider == "azure":
            from azure.keyvault.keys.crypto import SignatureAlgorithm  # type: ignore

            digest = hashlib.sha256(message).digest()
            result = self._crypto_clients[key_id].sign(SignatureAlgorithm.es256, digest)
            return f"ECDSA-SHA256:{base64.b64encode(bytes(result.signature)).decode('ascii')}"

        digest = hashlib.sha256(message).digest()
        result = self._client.asymmetric_sign(
            request={
                "name": self._remote_ids[key_id],
                "digest": {"sha256": digest},
            }
        )
        return f"ECDSA-SHA256:{base64.b64encode(bytes(result.signature)).decode('ascii')}"

    def verify(self, key_id: str, message: bytes, signature: str) -> bool:
        if key_id not in self._remote_ids:
            return False
        try:
            prefix, encoded = signature.split(":", 1)
            signature_bytes = base64.b64decode(encoded, validate=True)
        except Exception:
            return False

        if self._provider == "aws":
            algorithm = self._algorithms[key_id]
            expected_prefix = {
                "ED25519_SHA_512": "Ed25519",
                "ML_DSA_SHAKE_256": "ML-DSA-65",
                "ECDSA_SHA_256": "ECDSA-SHA256",
            }.get(algorithm, algorithm)
            if prefix != expected_prefix or len(message) > 4096:
                return False
            try:
                result = self._client.verify(
                    KeyId=self._remote_ids[key_id],
                    Message=message,
                    MessageType="RAW",
                    Signature=signature_bytes,
                    SigningAlgorithm=algorithm,
                )
                return bool(result.get("SignatureValid"))
            except Exception:
                return False

        if prefix != "ECDSA-SHA256":
            return False
        digest = hashlib.sha256(message).digest()
        if self._provider == "azure":
            from azure.keyvault.keys.crypto import SignatureAlgorithm  # type: ignore

            try:
                result = self._crypto_clients[key_id].verify(
                    SignatureAlgorithm.es256,
                    digest,
                    signature_bytes,
                )
                return bool(result.is_valid)
            except Exception:
                return False

        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec, utils

        try:
            public_key = serialization.load_pem_public_key(self._public_pems[key_id].encode("ascii"))
            public_key.verify(
                signature_bytes,
                digest,
                ec.ECDSA(utils.Prehashed(hashes.SHA256())),
            )
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False

    def get_public_pem(self, key_id: str) -> str:
        return self._public_pems[key_id]

    def revoke(self, key_id: str) -> None:
        if key_id not in self._remote_ids:
            raise KeyError(key_id)
        self._ensure_client()
        if self._provider == "aws":
            self._client.disable_key(KeyId=self._remote_ids[key_id])
        elif self._provider == "azure":
            key = self._client.get_key(self._remote_name(key_id))
            self._client.update_key_properties(
                key.name,
                version=key.properties.version,
                enabled=False,
            )
        else:
            from google.cloud import kms_v1  # type: ignore
            from google.protobuf.field_mask_pb2 import FieldMask  # type: ignore

            version = self._client.get_crypto_key_version(request={"name": self._remote_ids[key_id]})
            version.state = kms_v1.CryptoKeyVersion.CryptoKeyVersionState.DISABLED
            self._client.update_crypto_key_version(
                request={
                    "crypto_key_version": version,
                    "update_mask": FieldMask(paths=["state"]),
                }
            )
        self._active[key_id] = False

    def is_active(self, key_id: str) -> bool:
        if not self._active.get(key_id, False):
            return False
        try:
            self._ensure_client()
            if self._provider == "aws":
                metadata = self._client.describe_key(KeyId=self._remote_ids[key_id])["KeyMetadata"]
                return bool(metadata.get("Enabled")) and metadata.get("KeyState") == "Enabled"
            if self._provider == "azure":
                key = self._client.get_key(self._remote_name(key_id))
                return key.properties.enabled is not False
            from google.cloud import kms_v1  # type: ignore
            version = self._client.get_crypto_key_version(request={"name": self._remote_ids[key_id]})
            return version.state == kms_v1.CryptoKeyVersion.CryptoKeyVersionState.ENABLED
        except Exception:
            return False


class HSMKeyService:
    """Backend-neutral signing service for local HSMs and managed KMS services."""

    def __init__(self, backend: KeyBackend) -> None:
        self._backend = backend
        self._handles: dict[str, HSMKeyHandle] = {}

    @classmethod
    def for_development(cls) -> HSMKeyService:
        return cls(InMemoryKeyBackend())

    @classmethod
    def for_pkcs11(cls, pkcs11_lib: str, slot: int, pin: str | None = None) -> HSMKeyService:
        effective_pin = pin if pin is not None else os.environ.get("AEGISTRACE_HSM_PIN", "")
        return cls(PKCS11KeyBackend(pkcs11_lib, slot, effective_pin))

    @classmethod
    def for_aws_kms(
        cls,
        region: str = "us-east-1",
        *,
        key_spec: str = "ECC_NIST_EDWARDS25519",
    ) -> HSMKeyService:
        return cls(CloudKMSKeyBackend("aws", {"region": region, "key_spec": key_spec}))

    @classmethod
    def for_azure_kv(
        cls,
        vault_url: str,
        credential: Any,
        *,
        hardware_protected: bool = True,
    ) -> HSMKeyService:
        return cls(
            CloudKMSKeyBackend(
                "azure",
                {
                    "vault_url": vault_url,
                    "credential": credential,
                    "hardware_protected": hardware_protected,
                },
            )
        )

    @classmethod
    def for_gcp_kms(
        cls,
        *,
        project_id: str,
        location_id: str,
        key_ring_id: str,
        hardware_protected: bool = True,
    ) -> HSMKeyService:
        return cls(
            CloudKMSKeyBackend(
                "gcp",
                {
                    "project_id": project_id,
                    "location_id": location_id,
                    "key_ring_id": key_ring_id,
                    "hardware_protected": hardware_protected,
                },
            )
        )

    def create_key(self, key_id: str, bound_entity_id: str) -> HSMKeyHandle:
        if key_id in self._handles:
            raise ValueError(f"key_id already exists in service: {key_id}")
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
