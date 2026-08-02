"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/cli/__main__.py
Purpose: CLI entry point
Classification: application
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import sys

from aegistrace.cli.admin import main as admin_main
from aegistrace.cli.audit import main as audit_main
from aegistrace.cli.reconstruct import main as reconstruct_main
from aegistrace.cli.verify import main as verify_main

USAGE = """AegisTrace CLI

Usage:
  python -m aegistrace.cli <command> [options]

Commands:
  verify       Verify a ledger
  audit        Audit a ledger
  reconstruct  Reconstruct an incident timeline
  admin        Administrative operations (run 'admin demo' for the demo scenario)
"""


def main() -> int:
    if len(sys.argv) < 2:
        print(USAGE)
        return 2
    cmd = sys.argv[1]
    rest = sys.argv[2:]
    if cmd == "verify":
        return verify_main(rest)
    if cmd == "audit":
        return audit_main(rest)
    if cmd == "reconstruct":
        return reconstruct_main(rest)
    if cmd == "admin":
        return admin_main(rest)
    print(f"unknown command: {cmd}")
    print(USAGE)
    return 2


if __name__ == "__main__":
    sys.exit(main())
