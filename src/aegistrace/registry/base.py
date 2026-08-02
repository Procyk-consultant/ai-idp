"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/registry/base.py
Purpose: Registry interface
Classification: domain
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from aegistrace.identity.lifecycle import EntityRecord


class RegistryBackend(ABC):
    """Storage backend for the registry.

    Implementations: MemoryRegistry, SQLiteRegistry (pluggable).
    """

    @abstractmethod
    def put(self, entity_id: str, record: EntityRecord) -> None: ...

    @abstractmethod
    def get(self, entity_id: str) -> EntityRecord | None: ...

    @abstractmethod
    def list_all(self) -> dict[str, EntityRecord]: ...


class MemoryRegistry(RegistryBackend):
    def __init__(self) -> None:
        self._store: dict[str, EntityRecord] = {}

    def put(self, entity_id: str, record: EntityRecord) -> None:
        self._store[entity_id] = record

    def get(self, entity_id: str) -> EntityRecord | None:
        return self._store.get(entity_id)

    def list_all(self) -> dict[str, EntityRecord]:
        return dict(self._store)


__all__ = ["RegistryBackend", "MemoryRegistry"]
