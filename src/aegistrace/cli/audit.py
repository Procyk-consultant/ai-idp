"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/cli/audit.py
Purpose: audit CLI - audit ledger contents
Classification: application
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from aegistrace.ledger.append_only import AppendOnlyLedger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aegistrace.audit", description="Audit an AegisTrace ledger")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--output", help="Write JSON audit report to this path")
    args = parser.parse_args(argv)

    ledger = AppendOnlyLedger.load(Path(args.ledger))
    events = ledger.events()

    actions = Counter(e.action for e in events)
    agents = Counter(e.actor.agent_id for e in events)
    principals = Counter(e.actor.principal_id for e in events)
    visibility = Counter(e.visibility for e in events)
    resources = Counter(e.resource_id for e in events if e.resource_id)

    report = {
        "event_count": len(events),
        "first_event": events[0].timestamp if events else None,
        "last_event": events[-1].timestamp if events else None,
        "actions": dict(actions),
        "agents": dict(agents),
        "principals": dict(principals),
        "visibility_tiers": dict(visibility),
        "resources": dict(resources),
    }
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Audit report written to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
