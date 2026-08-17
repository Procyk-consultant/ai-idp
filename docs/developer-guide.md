# AegisTrace Developer Guide

Last Material Revision: 2026-08-17

## Architecture Overview

AegisTrace separates identity, authority, governance, evidence, disclosure, federation, storage, cryptographic backends, and external adapters.

The critical operational distinction is:

- `EventCollector` is the low-level **evidence collection/import** primitive.
- `GovernedEventService` is the **authorization/delegation/approval boundary** for governed operational evidence.
- `create_app()` exposes the authenticated HTTP boundary and combines proof-of-possession, replay resistance, policy evaluation, and governed append.

Production/high-assurance deployments should not bypass the governed boundary merely because the low-level collector remains available for evidence import, fixtures, verification, or explicitly evidence-only workflows.

See `spec/AI-IDP-CORE.md`, `spec/AUTHORIZATION_PROTOCOL.md`, `spec/APPROVAL_PROTOCOL.md`, `spec/DELEGATION_PROTOCOL.md`, `spec/FEDERATION_PROTOCOL.md`, and `technical/AEGISTRACE_TECHNICAL_ARCHITECTURE.md`.

## 1. Build the Identity / Registry Chain

```python
from aegistrace import Registry, KeyService, make_identifier

registry = Registry()
keys = KeyService()

controller_id = str(make_identifier("controller", "org-001"))
principal_id = str(make_identifier("principal", "user-001"))
agent_id = str(make_identifier("agent", "my-agent", version="v1"))
instance_id = str(make_identifier("agent-instance", "my-agent", version="run-1"))
provider_id = str(make_identifier("provider", "provider-001"))
model_id = str(make_identifier("model", "model-001"))
model_version_id = str(make_identifier("model", "model-001", version="v1"))
deployment_id = str(make_identifier("deployment", "deployment-001"))
task_id = str(make_identifier("task", "task-001"))

registry.register(controller_id, "controller")
registry.register(principal_id, "principal")
registry.register(agent_id, "agent", {"controller_id": controller_id})
registry.register(instance_id, "agent-instance", {"agent_id": agent_id})
registry.register(provider_id, "provider")
registry.register(model_id, "model")
registry.register(model_version_id, "model")
registry.register(deployment_id, "deployment")
registry.register(task_id, "task")

controller_key_id = str(make_identifier("key", "controller-key"))
principal_key_id = str(make_identifier("key", "principal-key"))
agent_key_id = str(make_identifier("key", "agent-key"))

keys.create_key(controller_key_id, bound_entity_id=controller_id)
keys.create_key(principal_key_id, bound_entity_id=principal_id)
keys.create_key(agent_key_id, bound_entity_id=agent_id)
```

## 2. Create the Governed Runtime Boundary

```python
from aegistrace import (
    Actor,
    AppendOnlyLedger,
    DelegationBroker,
    EventCollector,
    ExecutionContext,
    GovernedEventService,
    PolicyEngine,
)

ledger = AppendOnlyLedger()
collector = EventCollector(ledger, keys)
policy = PolicyEngine(keys)
delegations = DelegationBroker(keys)
governed = GovernedEventService(
    collector=collector,
    policy_engine=policy,
    delegation_broker=delegations,
    registry=registry,
)

actor = Actor(
    controller_id=controller_id,
    principal_id=principal_id,
    agent_id=agent_id,
    agent_instance_id=instance_id,
)
execution_context = ExecutionContext(
    provider_id=provider_id,
    model_id=model_id,
    model_version_id=model_version_id,
    deployment_id=deployment_id,
)
```

## 3. Issue Bounded Authorization

```python
authorization = policy.issue_authorization(
    principal_id=principal_id,
    controller_id=controller_id,
    agent_id=agent_id,
    task_id=task_id,
    scope={
        "action_classes": ["SEARCH", "READ", "PUBLISH"],
        "resource_classes": ["document"],
        "provider_classes": ["approved-provider"],
    },
    signing_key_id=controller_key_id,
)
```

If a scope dimension is constrained, the corresponding evaluated context is required. Missing context fails closed.

## 4. Exact-Action Approval

Approval-gated actions use `ActionIntent`. The digest binds the approver to the exact material action, including visibility.

```python
from aegistrace import ActionIntent, ScopeContext

scope_context = ScopeContext(
    resource_class="document",
    provider_class="approved-provider",
)

intent = ActionIntent(
    controller_id=controller_id,
    principal_id=principal_id,
    agent_id=agent_id,
    agent_instance_id=instance_id,
    provider_id=provider_id,
    model_id=model_id,
    model_version_id=model_version_id,
    deployment_id=deployment_id,
    task_id=task_id,
    action="PUBLISH",
    visibility="ORGANIZATION_PRIVATE",
    jurisdiction_id="ca",
    resource_id="urn:artifact:report",
    scope_context=scope_context,
)

approval = policy.issue_approval(
    action="PUBLISH",
    action_digest=intent.digest(),
    approver_id=principal_id,
    authorization_id=authorization.authorization_id,
    signing_key_id=principal_key_id,
)
```

Changing the resource, actor, task, execution context, scope context, jurisdiction, action, or visibility changes the digest and invalidates that approval for the modified intent.

## 5. Record the Governed Action

```python
event = governed.record(
    actor=actor,
    execution_context=execution_context,
    task_id=task_id,
    action="PUBLISH",
    visibility="ORGANIZATION_PRIVATE",
    signing_key_id=agent_key_id,
    authorization_id=authorization.authorization_id,
    approval_id=approval.approval_id,
    scope_context=scope_context,
    resource_id="urn:artifact:report",
)

assert event.action_intent_digest == intent.digest()
```

For denied actions, `GovernedEventService` can create signed `DENY` evidence. A denial record is evidence of rejection; it never becomes permission.

## 6. Durable Replay and Single-Use Approval State

Both `SQLiteStorage` and `PostgresStorage` implement:

- the API replay-reservation contract;
- the approval-consumption contract.

SQLite provides durable single-host/process coordination. PostgreSQL provides a shared database mechanism appropriate for multi-process/multi-node coordination of nonce reservation and approval consumption.*

```python
from pathlib import Path
from aegistrace import SQLiteStorage, PolicyEngine
from aegistrace.api.authentication import ActionRequestAuthenticator

security_state = SQLiteStorage(Path("aegistrace.db"))
policy = PolicyEngine(
    keys,
    approval_consumption_store=security_state,
)
authenticator = ActionRequestAuthenticator(
    keys,
    replay_store=security_state,
)
```

With PostgreSQL, the same `PostgresStorage` instance can implement both contracts.

## 7. Approver Entitlements

The default policy is fail-closed: only the authorization principal is entitled to approve.

Explicit additional approvers can be configured through the entitlement contract:

```python
from aegistrace import (
    CompositeApproverEntitlementProvider,
    PrincipalApproverEntitlementProvider,
    StaticApproverEntitlementProvider,
)

second_approver = str(make_identifier("principal", "approver-002"))
entitlements = CompositeApproverEntitlementProvider(
    PrincipalApproverEntitlementProvider(),
    StaticApproverEntitlementProvider(
        {second_approver: ["DESTROY_KEY", "MODIFY_PRODUCTION"]}
    ),
)

policy = PolicyEngine(keys, approver_entitlements=entitlements)
```

A production organization may implement `ApproverEntitlementProvider` against its approved IAM/directory/role source.*

## 8. FastAPI High-Assurance Wiring

```python
from aegistrace.api.server import create_app
from aegistrace import PostgresConfig, PostgresStorage

storage = PostgresStorage(PostgresConfig.from_env())
app = create_app(
    registry=registry,
    key_service=keys,
    ledger=ledger,
    replay_store=storage,
    approval_consumption_store=storage,
    approver_entitlements=entitlements,
)
```

If a preconfigured `PolicyEngine` or `ActionRequestAuthenticator` is passed, configure its stores/providers directly rather than passing duplicate store arguments to `create_app()`.

The HTTP `POST /events` request must carry:

- the acting agent's signing key ID;
- signed request timestamp;
- sufficiently long nonce;
- agent proof-of-possession signature over the canonical request;
- valid authorization/delegation/approval evidence.

A replay-store failure is fail-closed.

## 9. Delegation

```python
from aegistrace import DelegationBroker, DelegationScope

broker = DelegationBroker(keys)
child_agent_id = str(make_identifier("agent", "child-agent"))

delegation = broker.create(
    parent_agent_id=agent_id,
    parent_instance_id=instance_id,
    child_agent_id=child_agent_id,
    principal_id=principal_id,
    controller_id=controller_id,
    scope=DelegationScope(
        action_classes=["SEARCH", "READ"],
        resource_classes=["document"],
        provider_classes=["approved-provider"],
        delegation_depth=0,
    ),
    signing_key_id=agent_key_id,
)
```

Nested delegation must be a subset of the complete parent scope and remain within allowed delegation depth. Broken, revoked, expired, widened, cyclic, or incorrectly bound lineage fails verification.

## 10. Ledger Verification

```python
from aegistrace import LedgerVerifier

report = LedgerVerifier(keys).verify(ledger)
assert report.ok, report.failures
```

Independent verification can use a verify-only public key registry; private signing material is not required.

The CLI provides full signature verification and an explicit hash-only mode:

```text
python -m aegistrace.cli verify --ledger ledger.jsonl --keys public_keys.json
python -m aegistrace.cli verify --ledger ledger.jsonl --hash-only
```

Hash-only mode is intentionally labelled as integrity-only and must not be presented as full cryptographic signature verification.

## 11. Signed Federation

```python
from dataclasses import replace
from aegistrace import FederationAgreement, FederationGateway

local_authority_id = str(make_identifier("registry-authority", "local"))
remote_authority_id = str(make_identifier("registry-authority", "remote"))

# Local and remote public verification keys must already be registered/bound.
unsigned = FederationAgreement(
    agreement_id=str(make_identifier("federation-agreement", "agreement-001")),
    local_authority_id=local_authority_id,
    remote_authority_id=remote_authority_id,
    effective_at="2026-08-17T00:00:00Z",
    local_signing_key_id="aitrace://ca/key/federation-local",
    remote_signing_key_id="aitrace://ca/key/federation-remote",
    local_signature="",
    remote_signature="",
)

message = unsigned.signable_bytes()
agreement = replace(
    unsigned,
    local_signature=keys.get_signing_key(unsigned.local_signing_key_id).sign(message),
    # A real remote authority supplies this second signature.
    remote_signature="Ed25519:<REMOTE_SIGNATURE>",
)
```

`FederationGateway.register_authority()` verifies both authority/key bindings and signatures before trusting a remote client. Public responses are allow-listed and cached for a bounded TTL. Remote failures are recorded as federation breaks.

The reference gateway also verifies fully disclosed cross-registry event chains. A redacted public event projection is an integrity/reference surface; full canonical event signature verification requires the authorized disclosed record or a separately defined public anchor/proof.

## 12. Cryptographic Backends

### Development Ed25519

```python
from aegistrace import HSMKeyService

service = HSMKeyService.for_development()
```

### PKCS#11*

```python
service = HSMKeyService.for_pkcs11(
    "/path/to/vendor-pkcs11-library",
    slot=0,
)
```

Private key generation/signing occur in the token when the device exposes the required EdDSA mechanisms.

### AWS KMS*

```python
service = HSMKeyService.for_aws_kms("ca-central-1")
```

The default key spec is the AWS Ed25519 asymmetric signing key path; alternate supported key specs can be configured.

### Azure Key Vault / Google Cloud KMS*

Factory paths are provided by `HSMKeyService.for_azure_kv()` and `for_gcp_kms()`.

### ML-DSA / SLH-DSA*

```python
from aegistrace import MLDSA65Scheme, SLHDSA128sScheme

mldsa = MLDSA65Scheme()
slhdsa = SLHDSA128sScheme()
```

These paths use the optional `liboqs-python` runtime for live key generation, signing, and verification.

## 13. Adapters and Evidence

Low-level adapters return resource/digest/evidence data. The caller is responsible for crossing the governed boundary before an external effect where policy requires pre-authorization, then recording the resulting evidence according to the action protocol.

Examples include:

- `FilesystemAdapter`
- `GitAdapter`
- `GitHubEvidenceAdapter`
- database adapter
- MCP adapter
- GitHub remote integration*
- OpenTelemetry exporter*

## 14. Validation Status

The historical v2.0.0 baseline recorded **113/113 tests passing on 2026-08-02**. The 2026-08-17 reconciliation branch contains material source changes described above and has not been rerun or recompiled in this reconciliation session.

Do not represent the changed branch as newly validated until the controlled validation gate is executed and recorded.

> `*` External databases, HSM/KMS devices/accounts, cloud credentials, IAM systems, collectors, remote registry operators, liboqs runtime, regulator-operated infrastructure, and certification/adoption processes require their corresponding target environment and evidence. Their external status is distinct from the source implementation path.
