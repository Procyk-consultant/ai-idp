"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/signing/canonical.py
Purpose: Canonical serialization for AI-IDP events (RFC 8785-inspired deterministic JSON)
Classification: domain
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from typing import Any


def canonicalize(obj: Any) -> bytes:
    """Canonical JSON serialization: sorted keys, no whitespace, UTF-8, non-ASCII allowed.

    Rules (deterministic, stable across implementations):
        1. Sort object keys lexicographically (UTF-8 byte order).
        2. No insignificant whitespace.
        3. No non-ASCII escapes (ensure_ascii=False).
        4. UTF-8 encoded bytes.
        5. Numbers formatted minimally.
        6. No trailing newline.

    This is sufficient for cryptographic signature stability.
    For full RFC 8785 compliance, a more sophisticated serializer
    would be required (number normalization, etc.); AI-IDP events
    use only integers and strings, so the simple form is sufficient.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonicalize_for_hash(event: dict) -> bytes:
    """Canonicalize an event for hash computation.

    Excludes the 'event_hash' and 'signature' fields, which are
    computed after canonicalization.
    """
    obj = {k: v for k, v in event.items() if k not in ("event_hash", "signature")}
    return canonicalize(obj)


def canonicalize_for_signature(event: dict) -> bytes:
    """Canonicalize an event for signature computation.

    Includes the 'event_hash' field (so the signature covers the hash)
    but excludes the 'signature' field.
    """
    obj = {k: v for k, v in event.items() if k != "signature"}
    return canonicalize(obj)


__all__ = [
    "canonicalize",
    "canonicalize_for_hash",
    "canonicalize_for_signature",
]
