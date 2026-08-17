"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/identity/ids.py
Purpose: AI-IDP identifier model
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import re
import secrets
import time
from dataclasses import dataclass

VALID_JURISDICTIONS = frozenset(
    {
        "ca",
        "ca-qc",
        "ca-on",
        "ca-bc",
        "ca-ab",
        "ca-mb",
        "ca-sk",
        "ca-ns",
        "ca-nb",
        "ca-nl",
        "ca-pe",
        "ca-nt",
        "ca-nu",
        "ca-yt",
    }
)

ID_PATTERN = re.compile(
    r"^aitrace://(ca(?:-[a-z]{2})?)/([a-z-]+)/([a-zA-Z0-9._-]+)(?:#([a-zA-Z0-9._-]+))?$"
)

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _ulid() -> str:
    """Generate a 26-character Crockford-base32 ULID-like identifier."""
    ms = int(time.time() * 1000)
    rand = secrets.randbits(80)
    combined = (ms << 80) | rand
    chars = []
    for _ in range(26):
        chars.append(_CROCKFORD[combined & 0x1F])
        combined >>= 5
    return "".join(reversed(chars))


@dataclass(frozen=True)
class Identifier:
    """An AI-IDP identifier with a canonical Canadian jurisdiction."""

    jurisdiction: str
    entity_type: str
    slug: str
    version: str | None = None

    @classmethod
    def parse(cls, value: str) -> Identifier:
        match = ID_PATTERN.match(value)
        if not match:
            raise ValueError(f"invalid AI-IDP identifier: {value!r}")
        jurisdiction, entity_type, slug, version = (
            match.group(1),
            match.group(2),
            match.group(3),
            match.group(4),
        )
        if jurisdiction not in VALID_JURISDICTIONS:
            raise ValueError(f"unsupported AI-IDP jurisdiction: {jurisdiction!r}")
        return cls(
            jurisdiction=jurisdiction,
            entity_type=entity_type,
            slug=slug,
            version=version,
        )

    def __str__(self) -> str:
        if self.version:
            return f"aitrace://{self.jurisdiction}/{self.entity_type}/{self.slug}#{self.version}"
        return f"aitrace://{self.jurisdiction}/{self.entity_type}/{self.slug}"

    def to_uri(self) -> str:
        return str(self)


def make_identifier(
    entity_type: str,
    slug: str,
    jurisdiction: str = "ca",
    version: str | None = None,
) -> Identifier:
    if jurisdiction not in VALID_JURISDICTIONS:
        raise ValueError(f"unsupported AI-IDP jurisdiction: {jurisdiction!r}")
    if not re.fullmatch(r"[a-z-]+", entity_type):
        raise ValueError(f"invalid entity_type: {entity_type!r}")
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", slug):
        raise ValueError(f"invalid slug: {slug!r}")
    if version is not None and not re.fullmatch(r"[a-zA-Z0-9._-]+", version):
        raise ValueError(f"invalid version: {version!r}")
    return Identifier(
        jurisdiction=jurisdiction,
        entity_type=entity_type,
        slug=slug,
        version=version,
    )


def require_identifier_type(value: str, expected_types: str | set[str] | frozenset[str]) -> Identifier:
    """Parse an identifier and require one of the expected entity types."""
    identifier = Identifier.parse(value)
    allowed = {expected_types} if isinstance(expected_types, str) else set(expected_types)
    if identifier.entity_type not in allowed:
        raise ValueError(
            f"identifier {value!r} has entity_type={identifier.entity_type!r}; expected {sorted(allowed)}"
        )
    return identifier


def make_event_id() -> str:
    """Generate an event identifier of the form evt_<ULID>."""
    return "evt_" + _ulid()


def make_slug(prefix: str = "") -> str:
    """Generate an opaque slug, optionally with a prefix."""
    slug = _ulid().lower()
    return f"{prefix}-{slug}" if prefix else slug


__all__ = [
    "Identifier",
    "ID_PATTERN",
    "VALID_JURISDICTIONS",
    "make_identifier",
    "make_event_id",
    "make_slug",
    "require_identifier_type",
]
