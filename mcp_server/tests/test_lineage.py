from pathlib import Path

import pytest

from etl_mcp.config import Config
from etl_mcp.lineage import LineageError, known_tables, lookup


def _cfg(lineage_file: Path) -> Config:
    return Config(
        airflow_db_dsn="postgresql://x/y",
        data_db_dsn="postgresql://x/y",
        logs_dir=Path("/nonexistent"),
        lineage_file=lineage_file,
        log_tail_lines=10,
    )


REPO_LINEAGE = Path(__file__).resolve().parents[1] / "lineage.yaml"


def test_ships_with_lineage_for_both_output_tables():
    cfg = _cfg(REPO_LINEAGE)
    assert known_tables(cfg) == ["content", "title"]


def test_lookup_tolerates_schema_prefix_and_case():
    cfg = _cfg(REPO_LINEAGE)
    assert lookup(cfg, "public.CONTENT")["produced_by"]["dag_id"] == "etl_flow"


def test_lookup_unknown_returns_none():
    cfg = _cfg(REPO_LINEAGE)
    assert lookup(cfg, "does_not_exist") is None


def test_write_tasks_are_fully_qualified_for_taskgroup():
    cfg = _cfg(REPO_LINEAGE)
    tasks = lookup(cfg, "title")["produced_by"]["write_tasks"]
    assert "load-data.spark-load-title-data" in tasks


def test_missing_file_raises(tmp_path):
    cfg = _cfg(tmp_path / "nope.yaml")
    with pytest.raises(LineageError):
        known_tables(cfg)


def test_edit_is_picked_up_via_mtime(tmp_path):
    f = tmp_path / "lineage.yaml"
    f.write_text("tables:\n  a: {}\n")
    cfg = _cfg(f)
    assert known_tables(cfg) == ["a"]
    # bump mtime forward so the cache key changes even on coarse clocks
    import os

    future = f.stat().st_mtime + 10
    f.write_text("tables:\n  a: {}\n  b: {}\n")
    os.utime(f, (future, future))
    assert known_tables(cfg) == ["a", "b"]
