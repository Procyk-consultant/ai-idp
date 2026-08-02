# AegisTrace Quickstart

Last Material Revision: 2026-08-01

## Prerequisites

- Python 3.12 or later
- pip

## Install

```bash
cd /path/to/ai-idp-aegistrace/
pip install -e . --break-system-packages
```

## Run the Demo

```bash
python3 -m aegistrace.cli admin demo --out .aitrace-demo
```

This produces a `.aitrace-demo/` directory containing `ledger.jsonl` and `demo_summary.json`. The demo registers entities, creates signing keys, issues authorizations and approvals, creates a delegation, records events, verifies the ledger, and computes the Merkle root.

## Verify a Ledger

```bash
python3 -m aegistrace.cli verify --ledger .aitrace-demo/ledger.jsonl
```

## Audit a Ledger

```bash
python3 -m aegistrace.cli audit --ledger .aitrace-demo/ledger.jsonl
```

## Reconstruct an Incident Timeline

```bash
python3 -m aegistrace.cli reconstruct --ledger .aitrace-demo/ledger.jsonl --agent aitrace://ca/agent/research-agent#v3
```

## Start the API Server

```bash
uvicorn aegistrace.api.server:app --host 127.0.0.1 --port 8765
```

Then visit http://127.0.0.1:8765/docs for the interactive API documentation.

## Run Tests

```bash
PYTHONPATH=src python3 -m pytest tests/ -v
```

## Next Steps

- Read `docs/developer-guide.md` for the developer guide.
- Read `docs/architecture-guide.md` for the architecture guide.
- Read `spec/AI-IDP-CORE.md` for the formal specification.
- Read `technical/AEGISTRACE_TECHNICAL_ARCHITECTURE.md` for the technical architecture.

# AegisTrace Quickstart
