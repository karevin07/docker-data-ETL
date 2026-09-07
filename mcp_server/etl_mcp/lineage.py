"""Load and query the static table-lineage file (``lineage.yaml``)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .config import Config


class LineageError(RuntimeError):
    pass


@lru_cache(maxsize=8)
def _load(path: str, mtime: float) -> dict[str, Any]:
    # `mtime` is part of the cache key so edits to the file are picked up.
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    tables = data.get("tables")
    if not isinstance(tables, dict):
        raise LineageError(f"{path} has no 'tables:' mapping.")
    return tables


def load_tables(cfg: Config) -> dict[str, Any]:
    path = cfg.lineage_file
    if not path.exists():
        raise LineageError(
            f"Lineage file not found: {path}. Create it (see lineage.yaml in the "
            "mcp_server directory) or set LINEAGE_FILE."
        )
    return _load(str(path), path.stat().st_mtime)


def known_tables(cfg: Config) -> list[str]:
    return sorted(load_tables(cfg))


def lookup(cfg: Config, table: str) -> dict[str, Any] | None:
    """Find a table entry, tolerating ``schema.table`` and case differences."""
    tables = load_tables(cfg)
    bare = table.split(".")[-1]
    for candidate in (table, bare):
        if candidate in tables:
            return tables[candidate]
    lowered = {name.lower(): name for name in tables}
    for candidate in (table.lower(), bare.lower()):
        if candidate in lowered:
            return tables[lowered[candidate]]
    return None
