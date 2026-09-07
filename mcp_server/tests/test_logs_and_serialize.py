import datetime as dt
from decimal import Decimal
from pathlib import Path

from etl_mcp.config import Config
from etl_mcp.logs import get_task_log_tail
from etl_mcp.serialize import jsonify


def _cfg(logs_dir: Path) -> Config:
    return Config(
        airflow_db_dsn="postgresql://x/y",
        data_db_dsn="postgresql://x/y",
        logs_dir=logs_dir,
        lineage_file=Path("/nonexistent.yaml"),
        log_tail_lines=3,
    )


def test_jsonify_handles_db_types():
    out = jsonify(
        {
            "ts": dt.datetime(2026, 9, 7, 23, 40),
            "dur": dt.timedelta(seconds=90),
            "n": Decimal("12.5"),
            "nested": [{"d": dt.date(2026, 1, 1)}],
        }
    )
    assert out == {
        "ts": "2026-09-07T23:40:00",
        "dur": 90.0,
        "n": 12.5,
        "nested": [{"d": "2026-01-01"}],
    }


def _make_log(logs_dir: Path, dag, run, task, attempt, body):
    d = logs_dir / f"dag_id={dag}" / f"run_id={run}" / f"task_id={task}"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"attempt={attempt}.log").write_text(body)


def test_log_tail_picks_requested_attempt(tmp_path):
    _make_log(tmp_path, "etl_flow", "scheduled__2026-09-07", "transformation-data.spark_job", 1, "l1\nl2\nl3\nl4\nl5\n")
    cfg = _cfg(tmp_path)
    res = get_task_log_tail(
        cfg,
        dag_id="etl_flow",
        run_id="scheduled__2026-09-07",
        task_id="transformation-data.spark_job",
        try_number=1,
        map_index=-1,
    )
    assert res["found"] is True
    assert res["tail"] == "l3\nl4\nl5"
    assert res["attempts_available"] == ["attempt=1.log"]


def test_log_tail_falls_back_to_newest_attempt(tmp_path):
    _make_log(tmp_path, "etl_flow", "r1", "t", 1, "old\n")
    _make_log(tmp_path, "etl_flow", "r1", "t", 2, "new1\nnew2\n")
    cfg = _cfg(tmp_path)
    res = get_task_log_tail(cfg, dag_id="etl_flow", run_id="r1", task_id="t", try_number=9)
    assert res["file"].endswith("attempt=2.log")
    assert res["tail"] == "new1\nnew2"


def test_log_tail_missing_dir_is_soft_failure(tmp_path):
    cfg = _cfg(tmp_path)
    res = get_task_log_tail(cfg, dag_id="etl_flow", run_id="r1", task_id="t", try_number=1)
    assert res["found"] is False
    assert "searched" in res
