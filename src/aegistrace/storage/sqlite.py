"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/storage/sqlite.py
Purpose: SQLite persistent storage backend
Classification: infrastructure
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    seq INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,
    event_hash TEXT NOT NULL,
    previous_event_hash TEXT,
    payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS registry (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    state TEXT NOT NULL,
    payload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS keys (
    key_id TEXT PRIMARY KEY,
    public_pem TEXT NOT NULL,
    state TEXT NOT NULL,
    bound_entity_id TEXT,
    payload TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_seq ON events(seq);
CREATE INDEX IF NOT EXISTS idx_events_action ON events(action);
CREATE INDEX IF NOT EXISTS idx_registry_type ON registry(entity_type);
"""


class SQLiteStorage:
    """SQLite-backed persistent storage for AegisTrace.

    The ledger is also persisted to a JSONL file for human readability
    and external verification; the SQLite store provides indexed query
    access.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> SQLiteStorage:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def append_event(self, seq: int, event: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO events (event_id, seq, timestamp, action, event_hash, previous_event_hash, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                event["event_id"],
                seq,
                event["timestamp"],
                event["action"],
                event["event_hash"],
                event.get("previous_event_hash"),
                json.dumps(event, sort_keys=True),
            ),
        )
        self._conn.commit()

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        cur = self._conn.execute("SELECT payload FROM events WHERE event_id = ?", (event_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def list_events(self, limit: int = 1000, offset: int = 0) -> list[dict[str, Any]]:
        cur = self._conn.execute("SELECT payload FROM events ORDER BY seq LIMIT ? OFFSET ?", (limit, offset))
        return [json.loads(r[0]) for r in cur.fetchall()]

    def upsert_registry(self, entity_id: str, entity_type: str, state: str, payload: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO registry (entity_id, entity_type, state, payload) VALUES (?, ?, ?, ?)",
            (entity_id, entity_type, state, json.dumps(payload, sort_keys=True)),
        )
        self._conn.commit()

    def get_registry(self, entity_id: str) -> dict[str, Any] | None:
        cur = self._conn.execute("SELECT payload FROM registry WHERE entity_id = ?", (entity_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def upsert_key(self, key_id: str, public_pem: str, state: str, bound_entity_id: str | None, payload: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO keys (key_id, public_pem, state, bound_entity_id, payload) VALUES (?, ?, ?, ?, ?)",
            (key_id, public_pem, state, bound_entity_id, json.dumps(payload, sort_keys=True)),
        )
        self._conn.commit()

    def get_key(self, key_id: str) -> dict[str, Any] | None:
        cur = self._conn.execute("SELECT payload FROM keys WHERE key_id = ?", (key_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None


__all__ = ["SQLiteStorage", "SCHEMA_SQL"]
