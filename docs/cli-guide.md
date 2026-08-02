# AegisTrace CLI Guide

Last Material Revision: 2026-08-01

## Commands

AegisTrace provides four CLIs:

### verify

Verify a ledger's hash chain, event hashes, and signatures (with a keys file).

```bash
python3 -m aegistrace.cli verify --ledger path/to/ledger.jsonl
```

Exit code 0 = OK; 1 = verification failed; 2 = ledger not found.

### audit

Produce an audit summary.

```bash
python3 -m aegistrace.cli audit --ledger path/to/ledger.jsonl --output audit.json
```

The audit summary includes: event count, first/last event timestamps, action counts, agent counts, principal counts, visibility tier distribution, resource counts.

### reconstruct

Reconstruct an incident timeline.

```bash
python3 -m aegistrace.cli reconstruct --ledger path/to/ledger.jsonl --task aitrace://ca/task/task-001 --output timeline.json
```

Filters: `--task`, `--agent`, `--resource`, `--since`, `--until`.

### admin demo

Run the complete demo scenario.

```bash
python3 -m aegistrace.cli admin demo --out .aitrace-demo
```

The demo registers entities, creates signing keys, issues authorizations and approvals, creates a delegation, records events, verifies the ledger, computes the Merkle root, and persists to JSONL.

## Examples

```bash
# Verify a ledger
python3 -m aegistrace.cli verify --ledger .aitrace-demo/ledger.jsonl

# Audit a ledger
python3 -m aegistrace.cli audit --ledger .aitrace-demo/ledger.jsonl

# Reconstruct an incident by task
python3 -m aegistrace.cli reconstruct --ledger .aitrace-demo/ledger.jsonl --task aitrace://ca/task/task-00104

# Reconstruct an incident by agent
python3 -m aegistrace.cli reconstruct --ledger .aitrace-demo/ledger.jsonl --agent aitrace://ca/agent/research-agent#v3

# Reconstruct an incident by time range
python3 -m aegistrace.cli reconstruct --ledger .aitrace-demo/ledger.jsonl --since 2026-08-01T00:00:00Z --until 2026-08-01T23:59:59Z
```

# AegisTrace CLI Guide
