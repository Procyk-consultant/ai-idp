"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/adapters/database.py
Purpose: Database adapter for AI-IDP trace events
Classification: adapter
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass
class DatabaseOperation:
    op_type: str  # WRITE | DELETE_RECORD | ALTER_SCHEMA
    table: str
    row_id: str | None
    before_digest: str | None
    after_digest: str | None


class DatabaseAdapter:
    """Wraps SQLite operations and produces AegisTrace event fields.

    Records WRITE_DATABASE, DELETE_DATABASE_RECORD, ALTER_DATABASE_SCHEMA
    operations with before/after digests.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> DatabaseAdapter:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _row_digest(self, table: str, row_id: str) -> str | None:
        cur = self._conn.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,))
        row = cur.fetchone()
        if row is None:
            return None
        keys = row.keys()
        h = hashlib.sha256()
        for k in keys:
            h.update(k.encode("utf-8"))
            h.update(b"\x00")
            h.update(str(row[k]).encode("utf-8"))
            h.update(b"\x00")
        return "sha256:" + h.hexdigest()

    def write(self, table: str, row_id: str, values: dict[str, Any]) -> DatabaseOperation:
        before = self._row_digest(table, row_id)
        cols = ", ".join(values.keys())
        placeholders = ", ".join("?" for _ in values)
        sql = f"INSERT OR REPLACE INTO {table} (id, {cols}) VALUES (?, {placeholders})"
        self._conn.execute(sql, (row_id, *values.values()))
        self._conn.commit()
        after = self._row_digest(table, row_id)
        return DatabaseOperation(
            op_type="WRITE_DATABASE",
            table=table,
            row_id=row_id,
            before_digest=before,
            after_digest=after,
        )

    def delete(self, table: str, row_id: str) -> DatabaseOperation:
        before = self._row_digest(table, row_id)
        self._conn.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        self._conn.commit()
        return DatabaseOperation(
            op_type="DELETE_DATABASE_RECORD",
            table=table,
            row_id=row_id,
            before_digest=before,
            after_digest=None,
        )

    def alter_schema(self, sql: str) -> DatabaseOperation:
        self._conn.execute(sql)
        self._conn.commit()
        return DatabaseOperation(
            op_type="ALTER_DATABASE_SCHEMA",
            table="__schema__",
            row_id=None,
            before_digest=None,
            after_digest=sha256_sql(sql),
        )


def sha256_sql(sql: str) -> str:
    return "sha256:" + hashlib.sha256(sql.encode("utf-8")).hexdigest()


__all__ = ["DatabaseAdapter", "DatabaseOperation", "sha256_sql"]
