"""Seed a realistic 'stale table' scenario into a running stack, for demos.

Injects one failed ``etl_flow`` DagRun into the Airflow metadata DB:

    extract-data                     success
    transformation-data.spark_job    failed        (simulated OOM)
    load-data.spark-load-content-data  upstream_failed
    load-data.spark-load-title-data    upstream_failed

and writes a matching task log under the logs bind mount, so the MCP
server's get_task_failures() returns a real OOM traceback tail.

Usage (stack must be up, Postgres published on localhost:5432)::

    uv run python demo/seed_failure.py          # add the scenario
    uv run python demo/seed_failure.py --clear  # remove it

Then ask an agent: "word_counts / the content table didn't update today, why?"
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from etl_mcp.config import load_config  # noqa: E402

RUN_ID = "scheduled__demo_oom"
DAG_ID = "etl_flow"

LOG_BODY = """\
[2026-09-07T23:40:11.002+0000] {{spark_submit.py:490}} INFO - Spark job submitted: data-transformation
[2026-09-07T23:40:19.771+0000] {{spark_submit.py:583}} INFO - 25/09/07 23:40:19 INFO DAGScheduler: Got job 0 (toPandas) with 8 output partitions
[2026-09-07T23:41:55.410+0000] {{spark_submit.py:583}} INFO - 25/09/07 23:41:55 WARN TaskSetManager: Lost task 3.0 in stage 2.0 (TID 47): java.lang.OutOfMemoryError: Java heap space
[2026-09-07T23:42:03.918+0000] {{spark_submit.py:583}} INFO - 25/09/07 23:42:03 ERROR Executor: Exception in task 3.1 in stage 2.0 (TID 51)
[2026-09-07T23:42:03.919+0000] {{spark_submit.py:583}} INFO - java.lang.OutOfMemoryError: Java heap space
[2026-09-07T23:42:04.220+0000] {{spark_submit.py:583}} INFO -    at org.apache.spark.rdd.PairRDDFunctions.reduceByKey(PairRDDFunctions.scala:325)
[2026-09-07T23:42:06.774+0000] {{spark_submit.py:583}} INFO - 25/09/07 23:42:06 ERROR TaskSchedulerImpl: Stage 2 was cancelled
[2026-09-07T23:42:07.001+0000] {{spark_submit.py:490}} ERROR - Cannot execute: spark-submit ... transformation.py. Process exited with 1
[2026-09-07T23:42:07.114+0000] {{taskinstance.py:2731}} ERROR - Task failed with exception
airflow.exceptions.AirflowException: SparkSubmitOperator failed (exit code 1). Driver OOM in reduceByKey stage.
[2026-09-07T23:42:07.556+0000] {{taskinstance.py:1206}} INFO - Marking task as FAILED. dag_id=etl_flow, task_id=transformation-data.spark_job
"""

TASKS = [
    ("extract-data", "success", -1, 0, "PythonOperator"),
    ("transformation-data.spark_job", "failed", -1, 1, "SparkSubmitOperator"),
    ("load-data.spark-load-content-data", "upstream_failed", -1, 0, "SparkSubmitOperator"),
    ("load-data.spark-load-title-data", "upstream_failed", -1, 0, "SparkSubmitOperator"),
]


def _connect(dsn: str):
    conn = psycopg2.connect(dsn, connect_timeout=5)
    conn.autocommit = True
    return conn


def clear(cur, logs_dir: Path) -> None:
    cur.execute("DELETE FROM task_instance WHERE dag_id = %s AND run_id = %s", (DAG_ID, RUN_ID))
    cur.execute("DELETE FROM dag_run WHERE dag_id = %s AND run_id = %s", (DAG_ID, RUN_ID))
    log_dir = logs_dir / f"dag_id={DAG_ID}" / f"run_id={RUN_ID}"
    if log_dir.exists():
        for p in sorted(log_dir.rglob("*"), reverse=True):
            p.unlink() if p.is_file() else p.rmdir()
        log_dir.rmdir()
    print("cleared demo scenario")


def seed(cur, logs_dir: Path) -> None:
    now = dt.datetime(2026, 9, 7, 23, 40, tzinfo=dt.timezone.utc)
    exec_date = now
    start = now
    end = now + dt.timedelta(minutes=2, seconds=8)

    cur.execute("SELECT 1 FROM dag WHERE dag_id = %s", (DAG_ID,))
    if cur.fetchone() is None:
        raise SystemExit(
            f"DAG '{DAG_ID}' is not registered yet. Start the stack and let the "
            "scheduler parse the DAGs first (make up), then rerun."
        )

    cur.execute(
        """
        INSERT INTO dag_run
            (dag_id, run_id, state, run_type, execution_date, start_date, end_date,
             data_interval_start, data_interval_end, external_trigger, creating_job_id)
        VALUES (%s, %s, 'failed', 'scheduled', %s, %s, %s, %s, %s, false, NULL)
        """,
        (DAG_ID, RUN_ID, exec_date, start, end,
         exec_date - dt.timedelta(days=1), exec_date),
    )

    for task_id, state, map_index, try_number, operator in TASKS:
        t_end = start + dt.timedelta(minutes=2) if state == "failed" else None
        cur.execute(
            """
            INSERT INTO task_instance
                (task_id, dag_id, run_id, map_index, state, try_number, max_tries,
                 operator, start_date, end_date, pool, queue, priority_weight)
            VALUES (%s, %s, %s, %s, %s, %s, 0, %s, %s, %s, 'default_pool', 'default', 1)
            """,
            (task_id, DAG_ID, RUN_ID, map_index, state, try_number, operator,
             start if state != "upstream_failed" else None, t_end),
        )

    log_dir = logs_dir / f"dag_id={DAG_ID}" / f"run_id={RUN_ID}" / "task_id=transformation-data.spark_job"
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "attempt=1.log").write_text(LOG_BODY, encoding="utf-8")

    print(f"seeded failed run '{RUN_ID}' + OOM log at {log_dir / 'attempt=1.log'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clear", action="store_true", help="remove the demo scenario instead of adding it")
    args = ap.parse_args()

    cfg = load_config()
    cfg.logs_dir.mkdir(parents=True, exist_ok=True)
    with _connect(cfg.airflow_db_dsn) as conn, conn.cursor() as cur:
        clear(cur, cfg.logs_dir)
        if not args.clear:
            seed(cur, cfg.logs_dir)


if __name__ == "__main__":
    main()
