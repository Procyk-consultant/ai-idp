"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/cli/reconstruct.py
Purpose: reconstruct CLI - reconstruct an incident timeline
Classification: application
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aegistrace.ledger.append_only import AppendOnlyLedger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aegistrace.reconstruct", description="Reconstruct an incident timeline from an AegisTrace ledger")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--task", help="Filter by task_id")
    parser.add_argument("--agent", help="Filter by agent_id")
    parser.add_argument("--resource", help="Filter by resource_id")
    parser.add_argument("--since", help="ISO 8601 timestamp; include events after this")
    parser.add_argument("--until", help="ISO 8601 timestamp; include events before this")
    parser.add_argument("--output", help="Write JSON timeline to this path")
    args = parser.parse_args(argv)

    ledger = AppendOnlyLedger.load(Path(args.ledger))
    events = ledger.events()
    filtered = []
    for e in events:
        if args.task and e.task_id != args.task:
            continue
        if args.agent and e.actor.agent_id != args.agent:
            continue
        if args.resource and e.resource_id != args.resource:
            continue
        if args.since and e.timestamp < args.since:
            continue
        if args.until and e.timestamp > args.until:
            continue
        filtered.append(e)

    timeline = []
    for e in filtered:
        timeline.append({
            "seq": e.event_id,
            "timestamp": e.timestamp,
            "action": e.action,
            "agent": e.actor.agent_id,
            "instance": e.actor.agent_instance_id,
            "principal": e.actor.principal_id,
            "task": e.task_id,
            "resource": e.resource_id,
            "before_digest": e.before_digest,
            "after_digest": e.after_digest,
            "event_hash": e.event_hash,
        })

    report = {
        "filter": {"task": args.task, "agent": args.agent, "resource": args.resource, "since": args.since, "until": args.until},
        "matched_events": len(timeline),
        "timeline": timeline,
    }
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Timeline written to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
