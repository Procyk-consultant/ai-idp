"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/identity/ids.py
Purpose: AI-IDP identifier model
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import re
import secrets
import time
from dataclasses import dataclass

# aitrace://ca/<entity-type>/<slug>[#<version-or-instance>]
ID_PATTERN = re.compile(
    r"^aitrace://(ca(?:-[a-z]{2})?)/([a-z-]+)/([a-zA-Z0-9._-]+)(?:#([a-zA-Z0-9._-]+))?$"
)

# ULID-like: 26-char Crockford base32
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _ulid() -> str:
    """Generate a 26-character Crockford-base32 ULID-like identifier."""
    ms = int(time.time() * 1000)
    rand = secrets.randbits(80)
    # 48-bit time + 80-bit random = 128 bits
    combined = (ms << 80) | rand
    chars = []
    for _ in range(26):
        chars.append(_CROCKFORD[combined & 0x1F])
        combined >>= 5
    return "".join(reversed(chars))


@dataclass(frozen=True)
class Identifier:
    """An AI-IDP identifier.

    Invariants:
        - jurisdiction is a valid Canadian jurisdiction code.
        - entity_type is one of the canonical entity types.
        - slug is non-empty.
        - version is optional; if present, identifies a version or instance.
    """

    jurisdiction: str
    entity_type: str
    slug: str
    version: str | None = None

    @classmethod
    def parse(cls, s: str) -> Identifier:
        m = ID_PATTERN.match(s)
        if not m:
            raise ValueError(f"invalid AI-IDP identifier: {s!r}")
        jur, etype, slug, ver = m.group(1), m.group(2), m.group(3), m.group(4)
        return cls(jurisdiction=jur, entity_type=etype, slug=slug, version=ver)

    def __str__(self) -> str:
        if self.version:
            return f"aitrace://{self.jurisdiction}/{self.entity_type}/{self.slug}#{self.version}"
        return f"aitrace://{self.jurisdiction}/{self.entity_type}/{self.slug}"

    def to_uri(self) -> str:
        return str(self)


def make_identifier(entity_type: str, slug: str, jurisdiction: str = "ca", version: str | None = None) -> Identifier:
    return Identifier(jurisdiction=jurisdiction, entity_type=entity_type, slug=slug, version=version)


def make_event_id() -> str:
    """Generate an event identifier of the form evt_<ULID>."""
    return "evt_" + _ulid()


def make_slug(prefix: str = "") -> str:
    """Generate an opaque slug, optionally with a prefix."""
    s = _ulid().lower()
    return f"{prefix}-{s}" if prefix else s


__all__ = [
    "Identifier",
    "ID_PATTERN",
    "make_identifier",
    "make_event_id",
    "make_slug",
]
