"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/ledger/merkle.py
Purpose: Merkle root computation for periodic anchoring
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import hashlib

from aegistrace.events.models import Event


def _sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def merkle_root(events: list[Event]) -> str:
    """Compute the Merkle root over a list of events.

    Returns 'sha256:<64 hex chars>' of the root. For an empty list,
    returns 'sha256:' + sha256(b'').hexdigest().
    """
    if not events:
        return "sha256:" + _sha256_bytes(b"").hex()
    # Leaves: sha256 of each event's event_hash field (which is itself sha256:hex)
    leaves = [_sha256_bytes(e.event_hash.encode("ascii")) for e in events]
    while len(leaves) > 1:
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])  # duplicate last
        leaves = [_sha256_bytes(leaves[i] + leaves[i + 1]) for i in range(0, len(leaves), 2)]
    return "sha256:" + leaves[0].hex()


def merkle_proof(events: list[Event], index: int) -> list[str]:
    """Compute the Merkle proof for the event at `index`.

    Returns a list of sibling hashes (as 'sha256:hex') from leaf to root.
    """
    if not events or index < 0 or index >= len(events):
        raise IndexError("index out of range")
    leaves = [_sha256_bytes(e.event_hash.encode("ascii")) for e in events]
    proof: list[str] = []
    i = index
    while len(leaves) > 1:
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])
        if i % 2 == 0:
            sibling = leaves[i + 1] if i + 1 < len(leaves) else leaves[i]
        else:
            sibling = leaves[i - 1]
        proof.append("sha256:" + sibling.hex())
        leaves = [_sha256_bytes(leaves[j] + leaves[j + 1]) for j in range(0, len(leaves), 2)]
        i //= 2
    return proof


__all__ = ["merkle_root", "merkle_proof"]
