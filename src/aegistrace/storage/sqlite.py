"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/storage/sqlite.py
Purpose: SQLite persistent storage backend
Classification: infrastructure
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    seq INTEGER NOT NULL UNIQUE,
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

CREATE TABLE IF NOT EXISTS replay_nonces (
    key_id TEXT NOT NULL,
    nonce TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    PRIMARY KEY (key_id, nonce)
);
CREATE INDEX IF NOT EXISTS idx_replay_nonces_expiry ON replay_nonces(expires_at);

CREATE TABLE IF NOT EXISTS approval_consumption (
    approval_id TEXT PRIMARY KEY,
    used_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_events_seq ON events(seq);
CREATE INDEX IF NOT EXISTS idx_events_action ON events(action);
CREATE INDEX IF NOT EXISTS idx_registry_type ON registry(entity_type);
"""


class SQLiteStorage:
    """SQLite-backed local persistent storage.

    Besides query persistence, this backend implements the replay-reservation
    and approval-consumption contracts. Security-state methods open their own
    short transactions so they remain safe across request-handler threads and
    persist across process restarts.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def _security_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=5.0)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> SQLiteStorage:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def append_event(self, seq: int, event: dict[str, Any]) -> None:
        """Append one immutable event; duplicate IDs or sequences fail visibly."""
        try:
            self._conn.execute(
                "INSERT INTO events (event_id, seq, timestamp, action, event_hash, previous_event_hash, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
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
        except sqlite3.IntegrityError as exc:
            self._conn.rollback()
            raise ValueError(
                f"event_id or sequence already exists: {event['event_id']} / {seq}"
            ) from exc

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        cur = self._conn.execute("SELECT payload FROM events WHERE event_id = ?", (event_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def list_events(self, limit: int = 1000, offset: int = 0) -> list[dict[str, Any]]:
        cur = self._conn.execute(
            "SELECT payload FROM events ORDER BY seq LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [json.loads(row[0]) for row in cur.fetchall()]

    def upsert_registry(
        self,
        entity_id: str,
        entity_type: str,
        state: str,
        payload: dict[str, Any],
    ) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO registry (entity_id, entity_type, state, payload) VALUES (?, ?, ?, ?)",
            (entity_id, entity_type, state, json.dumps(payload, sort_keys=True)),
        )
        self._conn.commit()

    def get_registry(self, entity_id: str) -> dict[str, Any] | None:
        cur = self._conn.execute("SELECT payload FROM registry WHERE entity_id = ?", (entity_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def upsert_key(
        self,
        key_id: str,
        public_pem: str,
        state: str,
        bound_entity_id: str | None,
        payload: dict[str, Any],
    ) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO keys (key_id, public_pem, state, bound_entity_id, payload) VALUES (?, ?, ?, ?, ?)",
            (key_id, public_pem, state, bound_entity_id, json.dumps(payload, sort_keys=True)),
        )
        self._conn.commit()

    def get_key(self, key_id: str) -> dict[str, Any] | None:
        cur = self._conn.execute("SELECT payload FROM keys WHERE key_id = ?", (key_id,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def reserve_nonce(self, key_id: str, nonce: str, *, expires_at: str) -> bool:
        """Atomically reserve a replay nonce across process restarts."""
        now = _now()
        connection = self._security_connection()
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM replay_nonces WHERE expires_at <= ?", (now,))
            cursor = connection.execute(
                "INSERT OR IGNORE INTO replay_nonces (key_id, nonce, expires_at) VALUES (?, ?, ?)",
                (key_id, nonce, expires_at),
            )
            reserved = cursor.rowcount == 1
            connection.commit()
            return reserved
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def prune_expired_nonces(self, *, before: str | None = None) -> int:
        cutoff = before or _now()
        connection = self._security_connection()
        try:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "DELETE FROM replay_nonces WHERE expires_at <= ?",
                (cutoff,),
            )
            removed = cursor.rowcount
            connection.commit()
            return int(removed)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def approvals_available(self, approval_ids: tuple[str, ...]) -> bool:
        unique_ids = tuple(dict.fromkeys(approval_ids))
        if not unique_ids:
            return True
        placeholders = ",".join("?" for _ in unique_ids)
        connection = self._security_connection()
        try:
            cursor = connection.execute(
                f"SELECT COUNT(*) FROM approval_consumption WHERE approval_id IN ({placeholders})",
                unique_ids,
            )
            row = cursor.fetchone()
            return row is not None and int(row[0]) == 0
        finally:
            connection.close()

    def consume_approvals(self, approval_ids: tuple[str, ...], *, used_at: str) -> bool:
        """Atomically consume all approval IDs or none of them."""
        unique_ids = tuple(dict.fromkeys(approval_ids))
        if not unique_ids:
            return True
        placeholders = ",".join("?" for _ in unique_ids)
        connection = self._security_connection()
        try:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                f"SELECT COUNT(*) FROM approval_consumption WHERE approval_id IN ({placeholders})",
                unique_ids,
            )
            row = cursor.fetchone()
            if row is None or int(row[0]) != 0:
                connection.rollback()
                return False
            connection.executemany(
                "INSERT INTO approval_consumption (approval_id, used_at) VALUES (?, ?)",
                [(approval_id, used_at) for approval_id in unique_ids],
            )
            connection.commit()
            return True
        except sqlite3.IntegrityError:
            connection.rollback()
            return False
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


__all__ = ["SQLiteStorage", "SCHEMA_SQL"]
