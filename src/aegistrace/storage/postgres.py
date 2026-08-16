"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/storage/postgres.py
Purpose: PostgreSQL-backed persistent storage for production AegisTrace deployments
Classification: infrastructure
Security Classification: internal
Version: 2.0.0
Last Material Revision: 2026-08-16
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_values
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    seq BIGSERIAL NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    action TEXT NOT NULL,
    event_hash TEXT NOT NULL,
    previous_event_hash TEXT,
    signing_key_id TEXT NOT NULL,
    payload JSONB NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_events_seq_unique ON events(seq);
CREATE INDEX IF NOT EXISTS idx_events_action ON events(action);
CREATE INDEX IF NOT EXISTS idx_events_signing_key ON events(signing_key_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);

CREATE TABLE IF NOT EXISTS registry (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    state TEXT NOT NULL,
    payload JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_registry_type ON registry(entity_type);
CREATE INDEX IF NOT EXISTS idx_registry_state ON registry(state);

CREATE TABLE IF NOT EXISTS keys (
    key_id TEXT PRIMARY KEY,
    public_pem TEXT NOT NULL,
    state TEXT NOT NULL,
    bound_entity_id TEXT,
    payload JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS merkle_anchors (
    anchor_id BIGSERIAL PRIMARY KEY,
    root TEXT NOT NULL,
    event_count INTEGER NOT NULL,
    first_event_id TEXT,
    last_event_id TEXT,
    anchored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    signing_key_id TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_anchors_root ON merkle_anchors(root);

CREATE TABLE IF NOT EXISTS legal_holds (
    hold_id BIGSERIAL PRIMARY KEY,
    held_record_ids TEXT[] NOT NULL,
    hold_authority TEXT NOT NULL,
    hold_reason TEXT,
    hold_expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS access_log (
    access_id BIGSERIAL PRIMARY KEY,
    accessor_id TEXT NOT NULL,
    accessed_record_id TEXT NOT NULL,
    access_purpose TEXT,
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_access_log_record ON access_log(accessed_record_id);
CREATE INDEX IF NOT EXISTS idx_access_log_accessor ON access_log(accessor_id);
"""


def _payload_dict(value: Any) -> dict[str, Any]:
    """Normalize psycopg2 JSONB output to a dictionary."""
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        parsed = json.loads(value)
        if not isinstance(parsed, dict):
            raise TypeError("JSONB payload is not an object")
        return parsed
    raise TypeError(f"unsupported JSONB payload type: {type(value).__name__}")


@dataclass
class PostgresConfig:
    """Connection configuration for the PostgreSQL backend."""

    host: str = "localhost"
    port: int = 5432
    database: str = "aegistrace"
    user: str = "aegistrace"
    password: str = ""
    sslmode: str = "require"

    @classmethod
    def from_env(cls) -> PostgresConfig:
        import os
        return cls(
            host=os.environ.get("AEGISTRACE_PG_HOST", "localhost"),
            port=int(os.environ.get("AEGISTRACE_PG_PORT", "5432")),
            database=os.environ.get("AEGISTRACE_PG_DATABASE", "aegistrace"),
            user=os.environ.get("AEGISTRACE_PG_USER", "aegistrace"),
            password=os.environ.get("AEGISTRACE_PG_PASSWORD", ""),
            sslmode=os.environ.get("AEGISTRACE_PG_SSLMODE", "require"),
        )

    def to_dsn(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.database} "
            f"user={self.user} password={self.password} sslmode={self.sslmode}"
        )


class PostgresStorage:
    """PostgreSQL-backed persistent storage for AegisTrace.

    PostgreSQL owns the monotonic ``events.seq`` value through BIGSERIAL.
    Callers provide canonical event content, never a process-local sequence
    number that could restart across batches or workers.
    """

    def __init__(self, config: PostgresConfig) -> None:
        if not _PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2 is required for PostgresStorage. "
                "Install with: pip install psycopg2-binary"
            )
        self.config = config
        self._conn = psycopg2.connect(config.to_dsn())
        self._conn.autocommit = False
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> PostgresStorage:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[Any]:
        try:
            yield self._conn.cursor()
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def append_event(self, event: dict[str, Any]) -> int:
        """Insert one event and return its database-assigned sequence."""
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events (event_id, timestamp, action, event_hash, previous_event_hash, signing_key_id, payload)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (event_id) DO NOTHING
                RETURNING seq
                """,
                (
                    event["event_id"],
                    event["timestamp"],
                    event["action"],
                    event["event_hash"],
                    event.get("previous_event_hash"),
                    event["signing_key_id"],
                    json.dumps(event, sort_keys=True),
                ),
            )
            row = cur.fetchone()
        self._conn.commit()
        if row is None:
            raise ValueError(f"event_id already exists: {event['event_id']}")
        return int(row[0])

    def append_events_batch(self, events: list[dict[str, Any]]) -> int:
        """Batch-insert events using database-assigned global sequence values."""
        if not events:
            return 0
        rows = [
            (
                event["event_id"],
                event["timestamp"],
                event["action"],
                event["event_hash"],
                event.get("previous_event_hash"),
                event["signing_key_id"],
                json.dumps(event, sort_keys=True),
            )
            for event in events
        ]
        with self._conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO events (event_id, timestamp, action, event_hash, previous_event_hash, signing_key_id, payload)
                VALUES %s
                ON CONFLICT (event_id) DO NOTHING
                """,
                rows,
                template="(%s, %s, %s, %s, %s, %s, %s::jsonb)",
                page_size=1000,
            )
            inserted = cur.rowcount
        self._conn.commit()
        return int(inserted)

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT payload FROM events WHERE event_id = %s", (event_id,))
            row = cur.fetchone()
            return _payload_dict(row["payload"]) if row else None

    def list_events(self, limit: int = 1000, offset: int = 0) -> list[dict[str, Any]]:
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT payload FROM events ORDER BY seq LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return [_payload_dict(row["payload"]) for row in cur.fetchall()]

    def list_events_by_action(self, action: str, limit: int = 1000) -> list[dict[str, Any]]:
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT payload FROM events WHERE action = %s ORDER BY seq LIMIT %s",
                (action, limit),
            )
            return [_payload_dict(row["payload"]) for row in cur.fetchall()]

    def list_events_by_signing_key(self, key_id: str, limit: int = 1000) -> list[dict[str, Any]]:
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT payload FROM events WHERE signing_key_id = %s ORDER BY seq LIMIT %s",
                (key_id, limit),
            )
            return [_payload_dict(row["payload"]) for row in cur.fetchall()]

    def count_events(self) -> int:
        with self._conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM events")
            row = cur.fetchone()
            return int(row[0])

    def upsert_registry(self, entity_id: str, entity_type: str, state: str, payload: dict[str, Any]) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO registry (entity_id, entity_type, state, payload, updated_at)
                VALUES (%s, %s, %s, %s::jsonb, NOW())
                ON CONFLICT (entity_id) DO UPDATE SET
                    entity_type = EXCLUDED.entity_type,
                    state = EXCLUDED.state,
                    payload = EXCLUDED.payload,
                    updated_at = NOW()
                """,
                (entity_id, entity_type, state, json.dumps(payload, sort_keys=True)),
            )
        self._conn.commit()

    def get_registry(self, entity_id: str) -> dict[str, Any] | None:
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT payload FROM registry WHERE entity_id = %s", (entity_id,))
            row = cur.fetchone()
            return _payload_dict(row["payload"]) if row else None

    def list_registry_by_type(self, entity_type: str) -> list[dict[str, Any]]:
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT payload FROM registry WHERE entity_type = %s", (entity_type,))
            return [_payload_dict(row["payload"]) for row in cur.fetchall()]

    def upsert_key(self, key_id: str, public_pem: str, state: str, bound_entity_id: str | None, payload: dict[str, Any]) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO keys (key_id, public_pem, state, bound_entity_id, payload, updated_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, NOW())
                ON CONFLICT (key_id) DO UPDATE SET
                    public_pem = EXCLUDED.public_pem,
                    state = EXCLUDED.state,
                    bound_entity_id = EXCLUDED.bound_entity_id,
                    payload = EXCLUDED.payload,
                    updated_at = NOW()
                """,
                (key_id, public_pem, state, bound_entity_id, json.dumps(payload, sort_keys=True)),
            )
        self._conn.commit()

    def get_key(self, key_id: str) -> dict[str, Any] | None:
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT payload FROM keys WHERE key_id = %s", (key_id,))
            row = cur.fetchone()
            return _payload_dict(row["payload"]) if row else None

    def record_merkle_anchor(self, root: str, event_count: int, first_event_id: str | None, last_event_id: str | None, signing_key_id: str) -> int:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO merkle_anchors (root, event_count, first_event_id, last_event_id, signing_key_id)
                VALUES (%s, %s, %s, %s, %s) RETURNING anchor_id
                """,
                (root, event_count, first_event_id, last_event_id, signing_key_id),
            )
            anchor_id = cur.fetchone()[0]
        self._conn.commit()
        return int(anchor_id)

    def list_merkle_anchors(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT anchor_id, root, event_count, first_event_id, last_event_id, anchored_at, signing_key_id "
                "FROM merkle_anchors ORDER BY anchor_id DESC LIMIT %s",
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]

    def place_legal_hold(self, held_record_ids: list[str], hold_authority: str, hold_reason: str = "", hold_expires_at: str | None = None) -> int:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO legal_holds (held_record_ids, hold_authority, hold_reason, hold_expires_at)
                VALUES (%s, %s, %s, %s) RETURNING hold_id
                """,
                (held_record_ids, hold_authority, hold_reason, hold_expires_at),
            )
            hold_id = cur.fetchone()[0]
        self._conn.commit()
        return int(hold_id)

    def log_access(self, accessor_id: str, accessed_record_id: str, access_purpose: str = "") -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO access_log (accessor_id, accessed_record_id, access_purpose)
                VALUES (%s, %s, %s)
                """,
                (accessor_id, accessed_record_id, access_purpose),
            )
        self._conn.commit()

    def list_access_log(self, record_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            if record_id:
                cur.execute(
                    "SELECT * FROM access_log WHERE accessed_record_id = %s ORDER BY accessed_at DESC LIMIT %s",
                    (record_id, limit),
                )
            else:
                cur.execute(
                    "SELECT * FROM access_log ORDER BY accessed_at DESC LIMIT %s",
                    (limit,),
                )
            return [dict(row) for row in cur.fetchall()]


__all__ = ["PostgresConfig", "PostgresStorage", "SCHEMA_SQL"]
