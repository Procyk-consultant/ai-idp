"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/__init__.py
Purpose: Top-level package
Classification: domain
Version: 2.1.0
Last Material Revision: 2026-09-07
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from aegistrace.adapters.database import DatabaseAdapter, DatabaseOperation
from aegistrace.adapters.filesystem import FilesystemAdapter, file_digest
from aegistrace.adapters.git import GitAdapter
from aegistrace.adapters.github import CommitAttestation, GitHubEvidenceAdapter
from aegistrace.adapters.mcp import MCPAdapter, MCPCall
from aegistrace.api.replay import InMemoryReplayReservationStore, ReplayReservationStore
from aegistrace.authorization.consumption import (
    ApprovalConsumptionStore,
    InMemoryApprovalConsumptionStore,
)
from aegistrace.authorization.engine import Approval, Authorization, PolicyDecision, PolicyEngine
from aegistrace.authorization.entitlements import (
    ApproverEntitlementProvider,
    CompositeApproverEntitlementProvider,
    PrincipalApproverEntitlementProvider,
    StaticApproverEntitlementProvider,
)
from aegistrace.authorization.intent import ActionIntent
from aegistrace.authorization.scope import ScopeContext, ScopeDecision, evaluate_child_scope, evaluate_scope
from aegistrace.delegation.broker import Delegation, DelegationBroker, DelegationScope
from aegistrace.disclosure.public import PublicEventProjector, PublicProjectionError
from aegistrace.events.collector import EventCollector
from aegistrace.events.models import ACTIONS, GOVERNANCE_MODES, VISIBILITY_TIERS, Actor, Event, ExecutionContext
from aegistrace.federation.gateway import (
    FederatedRegistryClient,
    FederationAgreement,
    FederationBreak,
    FederationGateway,
    FederationResolutionError,
    HTTPFederatedRegistryClient,
)
from aegistrace.governance.service import GovernanceDenied, GovernedEventService
from aegistrace.identity.ids import Identifier, make_event_id, make_identifier
from aegistrace.identity.keys import KeyRecord, KeyService, SigningKey
from aegistrace.identity.lifecycle import EntityRecord, Registry
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier, VerificationReport
from aegistrace.ledger.batched import (
    BackgroundFlushError,
    BackpressureError,
    BatchConfig,
    BatchedLedger,
    WALRecoveryError,
)
from aegistrace.ledger.merkle import merkle_proof, merkle_root
from aegistrace.manifests.resource import ResourceManifest, compute_directory_digest, write_aitrace_directory
from aegistrace.signing.canonical import canonicalize, canonicalize_for_hash, canonicalize_for_signature
from aegistrace.signing.ed25519 import blake2b_hex, sha256_hex, sha256_raw
from aegistrace.storage.sqlite import SQLiteStorage
from aegistrace.version import __version__

try:
    from aegistrace.storage.postgres import PostgresConfig, PostgresStorage
except ImportError:
    PostgresConfig = None  # type: ignore
    PostgresStorage = None  # type: ignore

from aegistrace.signing.hsm import (
    CloudKMSKeyBackend,
    HSMKeyHandle,
    HSMKeyService,
    InMemoryKeyBackend,
    KeyBackend,
    PKCS11KeyBackend,
)
from aegistrace.signing.pqc import (
    Ed25519Scheme,
    KeyPair,
    MigrationService,
    MLDSA65Scheme,
    SchemeMigrationRecord,
    SchemeRegistry,
    SignatureScheme,
    SLHDSA128sScheme,
    default_registry,
)

try:
    from aegistrace.adapters.otel import OTelConfig, OTelEventHook, OTelExporter
except ImportError:
    OTelConfig = None  # type: ignore
    OTelExporter = None  # type: ignore
    OTelEventHook = None  # type: ignore

try:
    from aegistrace.adapters.github_remote import (
        GitHubConfig,
        GitHubRemotePusher,
        GitHubRemoteStub,
        make_github_pusher,
    )
except ImportError:
    GitHubConfig = None  # type: ignore
    GitHubRemotePusher = None  # type: ignore
    GitHubRemoteStub = None  # type: ignore
    make_github_pusher = None  # type: ignore

__all__ = [
    "__version__",
    "Event", "Actor", "ExecutionContext", "ACTIONS", "VISIBILITY_TIERS", "GOVERNANCE_MODES",
    "Identifier", "make_identifier", "make_event_id",
    "KeyService", "KeyRecord", "SigningKey",
    "Registry", "EntityRecord",
    "AppendOnlyLedger", "LedgerVerifier", "VerificationReport",
    "merkle_root", "merkle_proof",
    "EventCollector",
    "Delegation", "DelegationBroker", "DelegationScope",
    "Authorization", "Approval", "PolicyEngine", "PolicyDecision", "ActionIntent",
    "ScopeContext", "ScopeDecision", "evaluate_scope", "evaluate_child_scope",
    "ApprovalConsumptionStore", "InMemoryApprovalConsumptionStore",
    "ApproverEntitlementProvider", "PrincipalApproverEntitlementProvider",
    "StaticApproverEntitlementProvider", "CompositeApproverEntitlementProvider",
    "ReplayReservationStore", "InMemoryReplayReservationStore",
    "GovernanceDenied", "GovernedEventService",
    "PublicEventProjector", "PublicProjectionError",
    "FederatedRegistryClient", "FederationAgreement", "FederationBreak",
    "FederationGateway", "FederationResolutionError", "HTTPFederatedRegistryClient",
    "sha256_hex", "sha256_raw", "blake2b_hex",
    "canonicalize", "canonicalize_for_hash", "canonicalize_for_signature",
    "ResourceManifest", "compute_directory_digest", "write_aitrace_directory",
    "FilesystemAdapter", "file_digest",
    "GitAdapter",
    "GitHubEvidenceAdapter", "CommitAttestation",
    "DatabaseAdapter", "DatabaseOperation",
    "MCPAdapter", "MCPCall",
    "SQLiteStorage",
    "PostgresConfig", "PostgresStorage",
    "HSMKeyHandle", "KeyBackend", "InMemoryKeyBackend", "PKCS11KeyBackend",
    "CloudKMSKeyBackend", "HSMKeyService",
    "BatchConfig", "BatchedLedger", "BackpressureError", "BackgroundFlushError", "WALRecoveryError",
    "SignatureScheme", "KeyPair", "Ed25519Scheme", "MLDSA65Scheme",
    "SLHDSA128sScheme", "SchemeRegistry", "SchemeMigrationRecord",
    "MigrationService", "default_registry",
    "OTelConfig", "OTelExporter", "OTelEventHook",
    "GitHubConfig", "GitHubRemotePusher", "GitHubRemoteStub", "make_github_pusher",
]
