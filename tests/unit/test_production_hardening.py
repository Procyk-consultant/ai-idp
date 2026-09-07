"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_production_hardening.py
Purpose: Unit tests for production-hardening modules
Version: 2.1.0
Last Material Revision: 2026-09-07
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest


class TestHSMKeyService:
    def test_in_memory_backend_roundtrip_and_revoke(self) -> None:
        from aegistrace import HSMKeyService

        service = HSMKeyService.for_development()
        handle = service.create_key(
            "aitrace://ca/key/k1",
            bound_entity_id="aitrace://ca/agent/a1",
        )
        assert handle.backend_name == "in-memory"
        assert handle.signing_algorithm == "Ed25519"
        signature = service.sign(handle.key_id, b"hello")
        assert service.verify(handle.key_id, b"hello", signature)
        assert not service.verify(handle.key_id, b"world", signature)
        service.revoke(handle.key_id)
        assert not service.is_active(handle.key_id)
        with pytest.raises(PermissionError):
            service.sign(handle.key_id, b"hello")

    def test_pkcs11_backend_constructs_without_loading_token(self) -> None:
        from aegistrace import PKCS11KeyBackend

        backend = PKCS11KeyBackend(
            pkcs11_lib="/usr/lib/softhsm/libsofthsm2.so",
            slot=0,
            pin="1234",
        )
        assert backend.name == "pkcs11"

    def test_cloud_kms_backend_rejects_unknown_provider(self) -> None:
        from aegistrace import CloudKMSKeyBackend

        with pytest.raises(ValueError, match="unsupported provider"):
            CloudKMSKeyBackend("unknown", {})

    def test_factory_methods_do_not_contact_external_services(self) -> None:
        from aegistrace import HSMKeyService

        assert HSMKeyService.for_development() is not None
        assert HSMKeyService.for_pkcs11("/usr/lib/softhsm/libsofthsm2.so", 0) is not None
        assert HSMKeyService.for_aws_kms("us-east-1") is not None
        assert HSMKeyService.for_azure_kv("https://example.vault.azure.net", object()) is not None
        assert HSMKeyService.for_gcp_kms(
            project_id="project",
            location_id="ca",
            key_ring_id="aegistrace",
        ) is not None

    def test_aws_kms_backend_roundtrip_with_fake_client(self) -> None:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        from aegistrace import CloudKMSKeyBackend

        class FakeKMS:
            def __init__(self) -> None:
                self.private_key = Ed25519PrivateKey.generate()
                self.enabled = True
                self.arn = "arn:aws:kms:ca-central-1:000000000000:key/test"

            def create_key(self, **kwargs):
                assert kwargs["KeyUsage"] == "SIGN_VERIFY"
                assert kwargs["KeySpec"] == "ECC_NIST_EDWARDS25519"
                return {
                    "KeyMetadata": {
                        "Arn": self.arn,
                        "KeyId": "test",
                        "Enabled": True,
                        "KeyState": "Enabled",
                        "SigningAlgorithms": ["ED25519_SHA_512"],
                    }
                }

            def get_public_key(self, **kwargs):
                assert kwargs["KeyId"] == self.arn
                return {
                    "PublicKey": self.private_key.public_key().public_bytes(
                        serialization.Encoding.DER,
                        serialization.PublicFormat.SubjectPublicKeyInfo,
                    )
                }

            def sign(self, **kwargs):
                assert kwargs["SigningAlgorithm"] == "ED25519_SHA_512"
                return {"Signature": self.private_key.sign(kwargs["Message"])}

            def verify(self, **kwargs):
                try:
                    self.private_key.public_key().verify(
                        kwargs["Signature"],
                        kwargs["Message"],
                    )
                    return {"SignatureValid": True}
                except Exception:
                    return {"SignatureValid": False}

            def describe_key(self, **kwargs):
                return {
                    "KeyMetadata": {
                        "Enabled": self.enabled,
                        "KeyState": "Enabled" if self.enabled else "Disabled",
                    }
                }

            def disable_key(self, **kwargs):
                self.enabled = False

        backend = CloudKMSKeyBackend(
            "aws",
            {"region": "ca-central-1", "key_spec": "ECC_NIST_EDWARDS25519"},
        )
        backend._client = FakeKMS()
        handle = backend.create_key(
            "aitrace://ca/key/aws-k1",
            "aitrace://ca/agent/a1",
        )
        assert handle.backend_name == "aws-kms"
        assert handle.signing_algorithm == "ED25519_SHA_512"
        signature = backend.sign(handle.key_id, b"canonical-event")
        assert signature.startswith("Ed25519:")
        assert backend.verify(handle.key_id, b"canonical-event", signature)
        assert not backend.verify(handle.key_id, b"different", signature)
        backend.revoke(handle.key_id)
        assert not backend.is_active(handle.key_id)


class TestBatchedLedger:
    def test_batch_and_flush(self) -> None:
        from aegistrace import BatchConfig, BatchedLedger
        from aegistrace.events.collector import EventCollector
        from aegistrace.events.models import Actor, ExecutionContext
        from aegistrace.identity.ids import make_identifier
        from aegistrace.identity.keys import KeyService

        ledger = BatchedLedger(BatchConfig(batch_size=3, flush_interval_ms=10000))
        keys = KeyService()
        keys.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        collector = EventCollector(ledger, keys)
        actor = Actor(
            controller_id=str(make_identifier("controller", "c1")),
            principal_id=str(make_identifier("principal", "p1")),
            agent_id="aitrace://ca/agent/a1",
            agent_instance_id=str(make_identifier("agent-instance", "a1", version="r1")),
        )
        context = ExecutionContext(
            provider_id=str(make_identifier("provider", "p1")),
            model_id=str(make_identifier("model", "m1")),
            model_version_id=str(make_identifier("model", "m1", version="v1")),
            deployment_id=str(make_identifier("deployment", "d1")),
        )
        for index in range(3):
            collector.record(
                actor=actor,
                execution_context=context,
                task_id=str(make_identifier("task", f"t{index}")),
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id="aitrace://ca/key/k1",
                resource_id=f"urn:web:{index}",
            )
        assert len(ledger) == 3
        ledger.close()

    def test_wal_file_is_created_on_first_append_contract(self, tmp_path: Path) -> None:
        from aegistrace import BatchConfig, BatchedLedger

        path = tmp_path / "wal.log"
        ledger = BatchedLedger(BatchConfig(batch_size=100, flush_interval_ms=10000, wal_path=path))
        ledger.close()


class TestPQC:
    @staticmethod
    def _oqs():
        if os.environ.get("AEGISTRACE_RUN_LIBOQS_TESTS") != "1":
            pytest.skip(
                "live liboqs tests are opt-in because importing liboqs-python may build native code"
            )
        return pytest.importorskip("oqs", reason="liboqs-python not installed")

    def test_scheme_registry(self) -> None:
        from aegistrace import default_registry

        assert default_registry.list_schemes() == ["Ed25519", "ML-DSA-65", "SLH-DSA-128s"]
        assert default_registry.quantum_safe_schemes() == ["ML-DSA-65", "SLH-DSA-128s"]

    def test_ed25519_roundtrip(self) -> None:
        from aegistrace import Ed25519Scheme

        scheme = Ed25519Scheme()
        pair = scheme.generate_keypair("aitrace://ca/key/ed25519")
        signature = scheme.sign(pair.private_key, b"hello")
        assert scheme.verify(pair.public_key, b"hello", signature)
        assert not scheme.verify(pair.public_key, b"world", signature)

    def test_mldsa65_live_roundtrip_when_liboqs_available(self) -> None:
        oqs = self._oqs()
        assert "ML-DSA-65" in oqs.get_enabled_sig_mechanisms()
        from aegistrace import MLDSA65Scheme

        scheme = MLDSA65Scheme()
        pair = scheme.generate_keypair("aitrace://ca/key/mldsa")
        signature = scheme.sign(pair.private_key, b"hello quantum-safe world")
        assert signature.startswith("ML-DSA-65:")
        assert scheme.verify(pair.public_key, b"hello quantum-safe world", signature)
        assert not scheme.verify(pair.public_key, b"different", signature)

    def test_slhdsa128s_live_roundtrip_when_liboqs_available(self) -> None:
        oqs = self._oqs()
        enabled = set(oqs.get_enabled_sig_mechanisms())
        assert {"SLH_DSA_PURE_SHA2_128S", "SPHINCS+-SHA2-128s-simple"} & enabled
        from aegistrace import SLHDSA128sScheme

        scheme = SLHDSA128sScheme()
        pair = scheme.generate_keypair("aitrace://ca/key/slhdsa")
        signature = scheme.sign(pair.private_key, b"hello hash-based world")
        assert signature.startswith("SLH-DSA-128s:")
        assert scheme.verify(pair.public_key, b"hello hash-based world", signature)
        assert not scheme.verify(pair.public_key, b"different", signature)

    def test_migration_planning(self) -> None:
        from aegistrace import MigrationService, default_registry

        plan = MigrationService(default_registry).plan_migration("Ed25519", "ML-DSA-65")
        assert plan["recommended"] is True
        assert plan["size_increase_bytes"] == 3309 - 64


class TestOTelExporter:
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # noqa: F401
        from opentelemetry.sdk.trace import TracerProvider  # noqa: F401

        _OTEL_AVAILABLE = True
    except ImportError:
        _OTEL_AVAILABLE = False

    @pytest.mark.skipif(not _OTEL_AVAILABLE, reason="opentelemetry-sdk not installed")
    def test_config_from_env(self) -> None:
        from aegistrace import OTelConfig

        os.environ["OTEL_SERVICE_NAME"] = "test-aegistrace"
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:4318"
        config = OTelConfig.from_env()
        assert config.service_name == "test-aegistrace"
        assert config.endpoint == "http://localhost:4318"
        del os.environ["OTEL_SERVICE_NAME"]
        del os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]

    @pytest.mark.skipif(not _OTEL_AVAILABLE, reason="opentelemetry-sdk not installed")
    def test_exporter_initialization(self) -> None:
        from aegistrace import OTelConfig, OTelExporter

        exporter = OTelExporter(OTelConfig())
        assert exporter.available


class TestGitHubRemote:
    def test_config_from_env(self) -> None:
        from aegistrace import GitHubConfig

        os.environ["AEGISTRACE_GITHUB_TOKEN"] = "ghp_test_token"
        os.environ["AEGISTRACE_GITHUB_OWNER"] = "test-owner"
        os.environ["AEGISTRACE_GITHUB_PUBLIC_REPO"] = "test-public-repo"
        config = GitHubConfig.from_env()
        assert config.token == "ghp_test_token"
        assert config.owner == "test-owner"
        assert config.public_repo == "test-public-repo"
        for variable in (
            "AEGISTRACE_GITHUB_TOKEN",
            "AEGISTRACE_GITHUB_OWNER",
            "AEGISTRACE_GITHUB_PUBLIC_REPO",
        ):
            os.environ.pop(variable, None)

    def test_stub_without_credentials(self) -> None:
        from aegistrace import GitHubRemoteStub, make_github_pusher

        for variable in (
            "AEGISTRACE_GITHUB_TOKEN",
            "AEGISTRACE_GITHUB_OWNER",
            "AEGISTRACE_GITHUB_PUBLIC_REPO",
        ):
            os.environ.pop(variable, None)
        pusher = make_github_pusher()
        assert isinstance(pusher, GitHubRemoteStub)
        assert pusher.push_merkle_anchor({"root": "sha256:abc"})["stub"] is True


class TestPostgresStorage:
    try:
        import psycopg2  # noqa: F401

        _PG_AVAILABLE = True
    except ImportError:
        _PG_AVAILABLE = False

    @pytest.mark.skipif(not _PG_AVAILABLE, reason="psycopg2 not installed")
    def test_config_from_env(self) -> None:
        from aegistrace import PostgresConfig

        os.environ["AEGISTRACE_PG_HOST"] = "db.example.com"
        os.environ["AEGISTRACE_PG_PORT"] = "5433"
        os.environ["AEGISTRACE_PG_DATABASE"] = "test_aegistrace"
        os.environ["AEGISTRACE_PG_USER"] = "test_user"
        os.environ["AEGISTRACE_PG_PASSWORD"] = "test_password"
        os.environ["AEGISTRACE_PG_SSLMODE"] = "require"
        config = PostgresConfig.from_env()
        assert config.host == "db.example.com"
        assert config.port == 5433
        assert config.database == "test_aegistrace"
        assert config.sslmode == "require"
        for variable in (
            "AEGISTRACE_PG_HOST",
            "AEGISTRACE_PG_PORT",
            "AEGISTRACE_PG_DATABASE",
            "AEGISTRACE_PG_USER",
            "AEGISTRACE_PG_PASSWORD",
            "AEGISTRACE_PG_SSLMODE",
        ):
            os.environ.pop(variable, None)

    @pytest.mark.skipif(not _PG_AVAILABLE, reason="psycopg2 not installed")
    def test_dsn_format(self) -> None:
        from aegistrace import PostgresConfig

        config = PostgresConfig(
            host="localhost",
            port=5432,
            database="aegistrace",
            user="user",
            password="pass",
            sslmode="require",
        )
        dsn = config.to_dsn()
        assert "host=localhost" in dsn
        assert "port=5432" in dsn
        assert "dbname=aegistrace" in dsn
        assert "sslmode=require" in dsn
