"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/cli/verify.py
Purpose: verify CLI - verify ledger integrity and signatures
Classification: application
Version: 2.0.0
Last Material Revision: 2026-08-16
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier


def _load_public_keys(path: Path) -> KeyService:
    """Load a verify-only public-key registry exported by KeyService."""
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "aegistrace.public_keys.v1":
        raise ValueError("unsupported public-key registry schema")
    records = data.get("keys")
    if not isinstance(records, list):
        raise ValueError("public-key registry must contain a 'keys' list")

    keys = KeyService()
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("public-key registry contains a non-object key record")
        key_id = item.get("key_id")
        public_pem = item.get("public_pem")
        if not isinstance(key_id, str) or not isinstance(public_pem, str):
            raise ValueError("key record requires string key_id and public_pem")
        keys.register_public_key(
            key_id=key_id,
            public_pem=public_pem,
            bound_entity_id=item.get("bound_entity_id"),
            state=str(item.get("state", "active")),
            created_at=str(item.get("created_at", "")),
            rotated_at=item.get("rotated_at"),
            revoked_at=item.get("revoked_at"),
            terminated_at=item.get("terminated_at"),
            successor_key_id=item.get("successor_key_id"),
        )
    return keys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aegistrace.verify", description="Verify an AegisTrace ledger")
    parser.add_argument("--ledger", required=True, help="Path to ledger.jsonl")
    parser.add_argument(
        "--keys",
        help="Path to an AegisTrace verify-only public-key registry for full cryptographic verification.",
    )
    parser.add_argument(
        "--hash-only",
        action="store_true",
        help="Verify event hashes and the hash chain without cryptographic signature verification.",
    )
    args = parser.parse_args(argv)

    ledger_path = Path(args.ledger)
    if not ledger_path.exists():
        print(f"ledger not found: {ledger_path}", file=sys.stderr)
        return 2

    if args.hash_only and args.keys:
        print("choose either --keys for full verification or --hash-only; do not use both", file=sys.stderr)
        return 2

    try:
        ledger = AppendOnlyLedger.load(ledger_path)
    except Exception as exc:
        print(f"ledger load failed: {exc}", file=sys.stderr)
        return 1

    print(f"Loaded {len(ledger)} events from {ledger_path}")

    full_verification = bool(args.keys)
    if full_verification:
        keys_path = Path(args.keys)
        if not keys_path.exists():
            print(f"public-key registry not found: {keys_path}", file=sys.stderr)
            return 2
        try:
            keys = _load_public_keys(keys_path)
        except Exception as exc:
            print(f"public-key registry load failed: {exc}", file=sys.stderr)
            return 2
        verifier = LedgerVerifier(keys, verify_signatures=True)
    else:
        if not args.hash_only:
            print(
                "WARNING: no --keys registry supplied; running HASH-CHAIN-ONLY verification. "
                "Use --keys for full cryptographic signature verification.",
                file=sys.stderr,
            )
        keys = KeyService()
        verifier = LedgerVerifier(keys, verify_signatures=False)

    report = verifier.verify(ledger)
    if report.ok:
        if full_verification:
            print(
                f"Verification OK: event hashes, hash chain, and {report.verified_signature_count} signatures verified."
            )
        else:
            print("Verification OK (HASH-CHAIN-ONLY): event hashes and hash chain verified; signatures NOT verified.")
        return 0

    print(f"Verification FAILED: {len(report.failures)} failures")
    for failure in report.failures[:20]:
        print(f"  - {failure}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
