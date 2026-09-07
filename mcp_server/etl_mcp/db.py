"""Thin, read-only Postgres access.

Every connection opened here is put into a read-only, autocommit session so
the tools physically cannot mutate either database. Callers never pass raw
SQL from the model; queries are defined in this package and parameterised.
"""

from __future__ import annotations

import contextlib
import re
from typing import Any, Iterator, Sequence

import psycopg2
import psycopg2.extras


class DBError(RuntimeError):
    """Raised when a database is unreachable or a query fails."""


def redact_dsn(dsn: str) -> str:
    """Strip the password from a DSN so it is safe to show in an error."""
    return re.sub(r"(://[^:/@]+:)[^@/]+@", r"\1***@", dsn)


@contextlib.contextmanager
def connect(dsn: str) -> Iterator["psycopg2.extensions.connection"]:
    try:
        conn = psycopg2.connect(dsn, connect_timeout=5)
    except psycopg2.OperationalError as exc:
        raise DBError(
            f"Could not connect to Postgres at {redact_dsn(dsn)}. "
            "Is the ETL stack running? Try `make up` from the repo root. "
            f"({str(exc).strip()})"
        ) from exc
    try:
        conn.set_session(readonly=True, autocommit=True)
        yield conn
    finally:
        conn.close()


def query(dsn: str, sql: Any, params: Sequence[Any] | None = None) -> list[dict]:
    """Run a SELECT and return rows as a list of plain dicts."""
    try:
        with connect(dsn) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params or ())
                return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error as exc:
        raise DBError(f"Query failed: {str(exc).strip()}") from exc
