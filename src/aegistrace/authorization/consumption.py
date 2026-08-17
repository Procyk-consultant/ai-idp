"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/authorization/consumption.py
Purpose: Atomic approval-consumption contract for single-use governance
Classification: service
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from threading import RLock
from typing import Protocol


class ApprovalConsumptionStore(Protocol):
    """Coordinate single-use approvals across the intended trust boundary."""

    def approvals_available(self, approval_ids: tuple[str, ...]) -> bool:
        """Return True only when none of the approvals have been consumed."""
        ...

    def consume_approvals(self, approval_ids: tuple[str, ...], *, used_at: str) -> bool:
        """Atomically consume all IDs or consume none of them."""
        ...


class InMemoryApprovalConsumptionStore:
    """Thread-safe process-local approval consumption state."""

    def __init__(self) -> None:
        self._consumed: dict[str, str] = {}
        self._lock = RLock()

    def approvals_available(self, approval_ids: tuple[str, ...]) -> bool:
        unique_ids = tuple(dict.fromkeys(approval_ids))
        with self._lock:
            return all(approval_id not in self._consumed for approval_id in unique_ids)

    def consume_approvals(self, approval_ids: tuple[str, ...], *, used_at: str) -> bool:
        unique_ids = tuple(dict.fromkeys(approval_ids))
        if not unique_ids:
            return True
        with self._lock:
            if any(approval_id in self._consumed for approval_id in unique_ids):
                return False
            for approval_id in unique_ids:
                self._consumed[approval_id] = used_at
            return True


__all__ = ["ApprovalConsumptionStore", "InMemoryApprovalConsumptionStore"]
