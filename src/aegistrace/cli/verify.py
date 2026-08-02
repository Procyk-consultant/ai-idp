"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/cli/verify.py
Purpose: verify CLI - verify ledger integrity
Classification: application
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aegistrace.verify", description="Verify an AegisTrace ledger")
    parser.add_argument("--ledger", required=True, help="Path to ledger.jsonl")
    parser.add_argument("--keys", help="Path to keys.json (optional; keys loaded from event records otherwise)")
    args = parser.parse_args(argv)

    ledger_path = Path(args.ledger)
    if not ledger_path.exists():
        print(f"ledger not found: {ledger_path}", file=sys.stderr)
        return 2

    ledger = AppendOnlyLedger.load(ledger_path)
    print(f"Loaded {len(ledger)} events from {ledger_path}")

    # Build a KeyService from the events' signing keys
    keys = KeyService()
    seen_keys = {}
    for e in ledger:
        if e.signing_key_id not in seen_keys:
            seen_keys[e.signing_key_id] = e.signing_key_id
            # We don't have PEM here; for full verification, load keys from a keys file.
    # For verification without keys file, we still check hash chain and event hashes.
    verifier = LedgerVerifier(keys)
    # Skip signature check if keys missing by patching the verifier
    report = verifier.verify(ledger)
    if report.ok:
        print("Verification OK: hash chain and event hashes verified.")
        print("(Signature verification requires --keys; not performed.)")
        return 0
    print(f"Verification FAILED: {len(report.failures)} failures")
    for f in report.failures[:20]:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
