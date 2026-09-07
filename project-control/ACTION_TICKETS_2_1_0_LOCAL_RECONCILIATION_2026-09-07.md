# GIFT-X++ Action Tickets — Local 2.1.0 Reconciliation

```yaml
action_ticket:
  id: AT-20260907-01
  plan_node: P1-version-authority
  description: Establish 2.1.0 as the current local runtime/package state while preserving historical 2.0.0 release evidence.
  preconditions:
    - role_is_single: true
    - deps_declared: true
    - tests_written: true
  acceptance_tests:
    unit: python -m pytest tests/unit/test_project_metadata.py
    integration: python -c "import importlib.metadata as m, aegistrace; assert m.version('aegistrace') == aegistrace.__version__ == '2.1.0'"
    container: blocked in current environment because Docker Desktop Linux engine is unavailable
  risks:
    - R-version-history: Preserve v2.0.0 publication and release records as historical evidence.
  outputs: [IP_HEADER_BLOCK, CODE, TEST, RATIONALE]
  owner: Codex
  due: 2026-09-07
  status: done
```

```yaml
action_ticket:
  id: AT-20260907-02
  plan_node: P2-runtime-boundaries
  description: Repair API ledger injection, ledger typing, KMS verification narrowing, and leaf-delegation failure ordering.
  preconditions:
    - role_is_single: true
    - deps_declared: true
    - tests_written: true
  acceptance_tests:
    unit: python -m pytest tests/unit
    integration: python -m pytest tests/integration tests/security tests/privacy tests/permanence tests/conformance
    container: blocked in current environment because Docker Desktop Linux engine is unavailable
  risks:
    - R-governance-regression: Run the complete 164-test collection plus independent governed-demo verification.
  outputs: [IP_HEADER_BLOCK, CODE, TEST, RATIONALE]
  owner: Codex
  due: 2026-09-07
  status: done
```

```yaml
action_ticket:
  id: AT-20260907-03
  plan_node: P3-native-pqc-validation
  description: Prevent an ordinary validation run from silently downloading and compiling native liboqs while retaining an explicit live-PQC test path.
  preconditions:
    - role_is_single: true
    - deps_declared: true
    - tests_written: true
  acceptance_tests:
    unit: python -m pytest tests/unit/test_production_hardening.py
    integration: python -m pytest -q
    container: blocked in current environment because Docker Desktop Linux engine is unavailable
  risks:
    - R-pqc-overclaim: Mark native ML-DSA and SLH-DSA round trips as skipped unless explicitly provisioned and enabled.
  outputs: [IP_HEADER_BLOCK, CODE, TEST, RATIONALE]
  owner: Codex
  due: 2026-09-07
  status: done
```

```yaml
action_ticket:
  id: AT-20260907-04
  plan_node: P6-governance-continuity
  description: Reconcile context-specific Indigenous engagement language and persist evidence-separated current status.
  preconditions:
    - role_is_single: true
    - deps_declared: true
    - tests_written: true
  acceptance_tests:
    unit: repository text scan for stale universal-precondition wording outside historical snapshots
    integration: cross-check README, privacy, specification, project status, and D-drive 2.1.0 synthesis
    container: not applicable to documentation/evidence reconciliation
  risks:
    - R-rights-erasure: Preserve engagement duties where a material Indigenous rights/data/governance nexus exists.
    - R-fabricated-communications: Record sent-email status as user-confirmed unless receipt evidence is available.
  outputs: [IP_HEADER_BLOCK, CODE, TEST, RATIONALE]
  owner: Codex
  due: 2026-09-07
  status: done
```
