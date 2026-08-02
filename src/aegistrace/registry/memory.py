"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/registry/memory.py
Purpose: In-memory registry implementation
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from aegistrace.identity.lifecycle import Registry


class InMemoryRegistry(Registry):
    """Concrete in-memory Registry.

    Used by the reference implementation and by tests. Production
    deployments should use a persistent backend (SQLite or PostgreSQL).
    """

    pass


__all__ = ["InMemoryRegistry"]
