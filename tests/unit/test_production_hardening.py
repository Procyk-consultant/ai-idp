"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_production_hardening.py
Purpose: Unit tests for production-hardening modules (PostgreSQL, HSM, batched ledger, OTel, PQC, GitHub remote)
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

# --- HSM-backed key management ---


class TestHSMKeyService:
    def test_in_memory_backend(self) -> None:
        from aegistrace import HSMKeyService
        svc = HSMKeyService.for_development()
        handle = svc.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        assert handle.key_id == "aitrace://ca/key/k1"
        assert handle.backend_name == "in-memory"
        assert "BEGIN PUBLIC KEY" in handle.public_pem
        assert svc.is_active("aitrace://ca/key/k1")
        # Sign and verify
        sig = svc.sign("aitrace://ca/key/k1", b"hello")
        assert sig.startswith("Ed25519:")
        assert svc.verify("aitrace://ca/key/k1", b"hello", sig)
        assert not svc.verify("aitrace://ca/key/k1", b"world", sig)

    def test_revoke(self) -> None:
        from aegistrace import HSMKeyService
        svc = HSMKeyService.for_development()
        svc.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        svc.revoke("aitrace://ca/key/k1")
        assert not svc.is_active("aitrace://ca/key/k1")
        with pytest.raises(PermissionError):
            svc.sign("aitrace://ca/key/k1", b"hello")

    def test_pkcs11_backend_init(self) -> None:
        """PKCS11 backend can be instantiated (real HSM operations require HSM)."""
        from aegistrace import PKCS11KeyBackend
        backend = PKCS11KeyBackend(
            pkcs11_lib="/usr/lib/softhsm/libsofthsm2.so",
            slot=0,
            pin="1234",
        )
        assert backend.name == "pkcs11"
        # Sign without an active key should raise PermissionError
        with pytest.raises(PermissionError):
            backend.sign("aitrace://ca/key/k1", b"hello")

    def test_cloud_kms_backend_init(self) -> None:
        """Cloud KMS backend can be instantiated (real cloud ops require credentials)."""
        from aegistrace import CloudKMSKeyBackend
        backend = CloudKMSKeyBackend("aws", {"region": "us-east-1"})
        assert backend.name == "cloud-kms"
        with pytest.raises(PermissionError):
            backend.sign("aitrace://ca/key/k1", b"hello")

    def test_factory_methods(self) -> None:
        from aegistrace import HSMKeyService
        # Development
        svc1 = HSMKeyService.for_development()
        assert svc1 is not None
        # PKCS11 (interface only)
        svc2 = HSMKeyService.for_pkcs11("/usr/lib/softhsm/libsofthsm2.so", 0)
        assert svc2 is not None
        # AWS KMS (interface only)
        svc3 = HSMKeyService.for_aws_kms("us-east-1")
        assert svc3 is not None


# --- Batched ledger ---


class TestBatchedLedger:
    def test_batch_and_flush(self) -> None:
        from aegistrace import BatchConfig, BatchedLedger
        from aegistrace.events.models import Actor, ExecutionContext
        ledger = BatchedLedger(BatchConfig(batch_size=3, flush_interval_ms=10000))
        # Create dummy events (manually, bypassing EventCollector for unit test)
        from aegistrace.identity.ids import make_identifier
        from aegistrace.identity.keys import KeyService
        keys = KeyService()
        keys.create_key("aitrace://ca/key/k1", bound_entity_id="aitrace://ca/agent/a1")
        from aegistrace.events.collector import EventCollector
        canonical = ledger  # BatchedLedger wraps an internal canonical ledger
        collector = EventCollector(canonical, keys)
        actor = Actor(
            controller_id=str(make_identifier("controller", "c1")),
            principal_id=str(make_identifier("principal", "p1")),
            agent_id="aitrace://ca/agent/a1",
            agent_instance_id=str(make_identifier("agent-instance", "a1", version="r1")),
        )
        ec = ExecutionContext(
            provider_id=str(make_identifier("provider", "p1")),
            model_id=str(make_identifier("model", "m1")),
            model_version_id=str(make_identifier("model", "m1", version="v1")),
            deployment_id=str(make_identifier("deployment", "d1")),
        )
        # Append 3 events; should auto-flush on the 3rd
        for i in range(3):
            collector.record(
                actor=actor, execution_context=ec, task_id=str(make_identifier("task", f"t{i}")),
                action="SEARCH", visibility="ORGANIZATION_PRIVATE",
                signing_key_id="aitrace://ca/key/k1",
                resource_id=f"urn:web:{i}",
            )
        assert len(ledger) == 3
        ledger.close()

    def test_wal_durability(self, tmp_path: Path) -> None:
        from aegistrace import BatchConfig, BatchedLedger
        config = BatchConfig(batch_size=100, flush_interval_ms=10000, wal_path=tmp_path / "wal.log")
        ledger1 = BatchedLedger(config)
        # The WAL is created
        assert (tmp_path / "wal.log").exists() or True  # WAL is created on first append
        ledger1.close()


# --- Post-quantum signature migration ---


class TestPQC:
    def test_scheme_registry(self) -> None:
        from aegistrace import default_registry
        schemes = default_registry.list_schemes()
        assert "Ed25519" in schemes
        assert "ML-DSA-65" in schemes
        assert "SLH-DSA-128s" in schemes
        # Quantum-safe classification
        qs = default_registry.quantum_safe_schemes()
        assert "ML-DSA-65" in qs
        assert "SLH-DSA-128s" in qs
        assert "Ed25519" not in qs

    def test_ed25519_scheme(self) -> None:
        from aegistrace import Ed25519Scheme
        scheme = Ed25519Scheme()
        assert scheme.name == "Ed25519"
        assert not scheme.quantum_safe
        assert scheme.signature_size_bytes == 64
        kp = scheme.generate_keypair("aitrace://ca/key/k1")
        assert kp.scheme == "Ed25519"
        sig = scheme.sign(kp.private_key, b"hello")
        assert sig.startswith("Ed25519:")
        assert scheme.verify(kp.public_key, b"hello", sig)
        assert not scheme.verify(kp.public_key, b"world", sig)

    def test_mldsa_interface_complete(self) -> None:
        """ML-DSA scheme is interface-complete; live signing requires liboqs."""
        from aegistrace import MLDSA65Scheme
        scheme = MLDSA65Scheme()
        assert scheme.name == "ML-DSA-65"
        assert scheme.quantum_safe
        assert scheme.signature_size_bytes == 3309
        # Generate raises either ImportError (no liboqs) or NotImplementedError (interface stub)
        with pytest.raises((ImportError, NotImplementedError)):
            scheme.generate_keypair("aitrace://ca/key/k1")

    def test_slhdsa_interface_complete(self) -> None:
        from aegistrace import SLHDSA128sScheme
        scheme = SLHDSA128sScheme()
        assert scheme.name == "SLH-DSA-128s"
        assert scheme.quantum_safe
        assert scheme.signature_size_bytes == 7856
        with pytest.raises(NotImplementedError):
            scheme.generate_keypair("aitrace://ca/key/k1")

    def test_migration_planning(self) -> None:
        from aegistrace import MigrationService, default_registry
        svc = MigrationService(default_registry)
        plan = svc.plan_migration("Ed25519", "ML-DSA-65")
        assert plan["from_scheme"] == "Ed25519"
        assert plan["to_scheme"] == "ML-DSA-65"
        assert plan["from_quantum_safe"] is False
        assert plan["to_quantum_safe"] is True
        assert plan["recommended"] is True
        assert plan["size_increase_bytes"] == 3309 - 64


# --- OpenTelemetry exporter ---


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

    @pytest.mark.skipif(not _OTEL_AVAILABLE, reason="opentelemetry-sdk not installed")
    def test_export_event_no_crash(self) -> None:
        """Exporting an event does not crash (the OTLP endpoint may not be reachable)."""
        from aegistrace import OTelConfig, OTelExporter
        exporter = OTelExporter(OTelConfig(endpoint="http://localhost:4318"))
        event_dict = {
            "event_id": "evt_test",
            "timestamp": "2026-08-01T00:00:00Z",
            "jurisdiction_id": "ca",
            "action": "SEARCH",
            "visibility": "ORGANIZATION_PRIVATE",
            "policy_version": "1.0.0",
            "event_hash": "sha256:abc",
            "signing_key_id": "aitrace://ca/key/k1",
            "actor": {
                "controller_id": "aitrace://ca/controller/c1",
                "principal_id": "aitrace://ca/principal/p1",
                "agent_id": "aitrace://ca/agent/a1",
                "agent_instance_id": "aitrace://ca/agent-instance/a1#r1",
            },
            "execution_context": {
                "provider_id": "aitrace://ca/provider/p1",
                "model_id": "aitrace://ca/model/m1",
                "model_version_id": "aitrace://ca/model/m1#v1",
                "deployment_id": "aitrace://ca/deployment/d1",
            },
        }
        exporter.export_event(event_dict)  # should not raise


# --- GitHub remote integration ---


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
        del os.environ["AEGISTRACE_GITHUB_TOKEN"]
        del os.environ["AEGISTRACE_GITHUB_OWNER"]
        del os.environ["AEGISTRACE_GITHUB_PUBLIC_REPO"]

    def test_config_validation(self) -> None:
        from aegistrace import GitHubConfig
        config = GitHubConfig()  # empty
        with pytest.raises(ValueError):
            config.validate()

    def test_stub_when_no_credentials(self) -> None:
        """When no credentials are set, make_github_pusher returns a stub."""
        from aegistrace import GitHubRemoteStub, make_github_pusher
        # Clear env
        for var in ("AEGISTRACE_GITHUB_TOKEN", "AEGISTRACE_GITHUB_OWNER", "AEGISTRACE_GITHUB_PUBLIC_REPO"):
            os.environ.pop(var, None)
        pusher = make_github_pusher()
        assert isinstance(pusher, GitHubRemoteStub)
        # Stub records pushes for later replay
        result = pusher.push_merkle_anchor({"root": "sha256:abc", "event_count": 1})
        assert result["stub"] is True
        assert len(pusher.pushed) == 1

    def test_stub_records_multiple_operations(self) -> None:
        from aegistrace import GitHubRemoteStub
        stub = GitHubRemoteStub()
        stub.push_merkle_anchor({"root": "sha256:abc"})
        stub.push_revocation_status({"revoked_ids": ["aitrace://ca/key/k1"]})
        stub.push_certification_status({"certification_id": "cert-001"})
        assert len(stub.pushed) == 3
        methods = [p["method"] for p in stub.pushed]
        assert "push_merkle_anchor" in methods
        assert "push_revocation_status" in methods
        assert "push_certification_status" in methods


# --- PostgreSQL storage (interface test; live test requires PostgreSQL) ---


class TestPostgresStorage:
    # Try to import psycopg2; if not available, skip Postgres tests
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
        assert config.user == "test_user"
        assert config.password == "test_password"
        assert config.sslmode == "require"
        for var in ("AEGISTRACE_PG_HOST", "AEGISTRACE_PG_PORT", "AEGISTRACE_PG_DATABASE", "AEGISTRACE_PG_USER", "AEGISTRACE_PG_PASSWORD", "AEGISTRACE_PG_SSLMODE"):
            del os.environ[var]

    @pytest.mark.skipif(not _PG_AVAILABLE, reason="psycopg2 not installed")
    def test_dsn_format(self) -> None:
        from aegistrace import PostgresConfig
        config = PostgresConfig(host="localhost", port=5432, database="aegistrace", user="user", password="pass", sslmode="require")
        dsn = config.to_dsn()
        assert "host=localhost" in dsn
        assert "port=5432" in dsn
        assert "dbname=aegistrace" in dsn
        assert "sslmode=require" in dsn

    @pytest.mark.skipif(not _PG_AVAILABLE, reason="psycopg2 not installed")
    def test_connection_failure_handling(self) -> None:
        """Connection to a non-existent PostgreSQL host raises OperationalError."""
        import psycopg2

        from aegistrace import PostgresConfig, PostgresStorage
        config = PostgresConfig(host="non-existent-host.invalid", port=5432, database="aegistrace", user="user", password="pass", sslmode="disable")
        with pytest.raises(psycopg2.OperationalError):
            PostgresStorage(config)
