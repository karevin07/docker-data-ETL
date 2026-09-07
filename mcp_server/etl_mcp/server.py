"""MCP server: trace a stale warehouse table back to the run that explains it.

Tools
-----
- list_dags()                         : what pipelines exist
- get_recent_runs(dag_id)             : recent run states / timing
- get_task_failures(dag_id, run_id?)  : failed tasks + log tails for a run
- get_table_schema(table)             : columns, row count, freshness stats
- get_lineage(table)                  : which DAG/tasks write this table

Typical chain for "table X didn't update today, why?":
    get_lineage(X) -> get_recent_runs(dag) -> get_task_failures(dag, run) -> read log tail
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from psycopg2 import sql

from . import lineage as lineage_mod
from . import logs as logs_mod
from .config import load_config
from .db import DBError, query
from .serialize import jsonify

cfg = load_config()
mcp = MCPServer(
    "etl-observability",
    instructions=(
        "Read-only observability for the docker-data-etl pipeline. To explain a "
        "stale table: get_lineage(table) -> get_recent_runs(dag_id) -> "
        "get_task_failures(dag_id, run_id) -> read the log tail."
    ),
)


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def _dag_ids() -> list[str]:
    return [r["dag_id"] for r in query(cfg.airflow_db_dsn, "SELECT dag_id FROM dag ORDER BY dag_id")]


def _require_dag(dag_id: str) -> None:
    ids = _dag_ids()
    if dag_id not in ids:
        raise ValueError(f"Unknown dag_id '{dag_id}'. Known DAGs: {', '.join(ids) or '(none)'}.")


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #
@mcp.tool()
def list_dags() -> list[dict[str, Any]]:
    """List every Airflow DAG with its pause state, schedule, owners, and the
    state of its most recent run. Start here to see what pipelines exist."""
    rows = query(
        cfg.airflow_db_dsn,
        """
        SELECT d.dag_id,
               d.is_paused,
               d.is_active,
               d.schedule_interval,
               d.owners,
               d.description,
               d.fileloc,
               d.last_parsed_time,
               lr.run_id        AS last_run_id,
               lr.state         AS last_run_state,
               lr.run_type      AS last_run_type,
               lr.execution_date AS last_run_execution_date,
               lr.start_date    AS last_run_start,
               lr.end_date      AS last_run_end
        FROM dag d
        LEFT JOIN LATERAL (
            SELECT run_id, state, run_type, execution_date, start_date, end_date
            FROM dag_run r
            WHERE r.dag_id = d.dag_id
            ORDER BY r.execution_date DESC
            LIMIT 1
        ) lr ON TRUE
        ORDER BY d.dag_id
        """,
    )
    return jsonify(rows)


@mcp.tool()
def get_recent_runs(dag_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Recent DagRuns for one DAG, newest first: state, run type, the data
    interval covered, queue/start/end timestamps and wall-clock duration.
    Use this to see whether today's run happened at all and how it ended."""
    _require_dag(dag_id)
    rows = query(
        cfg.airflow_db_dsn,
        """
        SELECT run_id,
               state,
               run_type,
               external_trigger,
               execution_date,
               data_interval_start,
               data_interval_end,
               queued_at,
               start_date,
               end_date,
               EXTRACT(EPOCH FROM (end_date - start_date)) AS duration_seconds
        FROM dag_run
        WHERE dag_id = %s
        ORDER BY execution_date DESC
        LIMIT %s
        """,
        (dag_id, _clamp(limit, 1, 50)),
    )
    return jsonify(rows)


@mcp.tool()
def get_task_failures(dag_id: str, run_id: str | None = None) -> dict[str, Any]:
    """For one DAG run, list the failed / upstream_failed task instances and,
    for each genuinely failed task, a tail of its log.

    If run_id is omitted, the most recent run that did not succeed is used."""
    _require_dag(dag_id)

    if run_id is None:
        latest = query(
            cfg.airflow_db_dsn,
            """
            SELECT run_id
            FROM dag_run
            WHERE dag_id = %s AND state IS DISTINCT FROM 'success'
            ORDER BY execution_date DESC
            LIMIT 1
            """,
            (dag_id,),
        )
        if not latest:
            return {
                "dag_id": dag_id,
                "message": "Every recorded run of this DAG succeeded (or no runs exist).",
                "tasks": [],
            }
        run_id = latest[0]["run_id"]

    run = query(
        cfg.airflow_db_dsn,
        "SELECT run_id, state, run_type, execution_date, start_date, end_date "
        "FROM dag_run WHERE dag_id = %s AND run_id = %s",
        (dag_id, run_id),
    )
    if not run:
        raise ValueError(f"No run '{run_id}' for dag '{dag_id}'. Call get_recent_runs first.")

    failed = query(
        cfg.airflow_db_dsn,
        """
        SELECT task_id,
               state,
               try_number,
               max_tries,
               map_index,
               operator,
               pool,
               hostname,
               start_date,
               end_date,
               EXTRACT(EPOCH FROM (end_date - start_date)) AS duration_seconds
        FROM task_instance
        WHERE dag_id = %s AND run_id = %s
          AND state IN ('failed', 'upstream_failed')
        ORDER BY end_date NULLS LAST, task_id
        """,
        (dag_id, run_id),
    )

    tasks: list[dict[str, Any]] = []
    for row in failed:
        entry = dict(row)
        if row["state"] == "failed":
            entry["log"] = logs_mod.get_task_log_tail(
                cfg,
                dag_id=dag_id,
                run_id=run_id,
                task_id=row["task_id"],
                try_number=row["try_number"],
                map_index=row["map_index"],
            )
        tasks.append(entry)

    return jsonify(
        {
            "dag_id": dag_id,
            "run": run[0],
            "failed_task_count": len(tasks),
            "tasks": tasks,
            "note": (
                "upstream_failed tasks were skipped because an earlier task failed; "
                "look at the 'failed' one for the root cause."
            ),
        }
    )


@mcp.tool()
def get_table_schema(table: str, schema: str = "public") -> dict[str, Any]:
    """Describe a warehouse table: column definitions plus freshness signals
    (exact and estimated row counts, total size, last (auto)vacuum/analyze,
    rows inserted/updated/deleted since stats reset).

    The ETL output tables have no updated_at column, so 'is it fresh?' is
    answered by combining this with get_lineage + get_recent_runs."""
    columns = query(
        cfg.data_db_dsn,
        """
        SELECT column_name, data_type, is_nullable, column_default, ordinal_position
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """,
        (schema, table),
    )
    if not columns:
        available = query(
            cfg.data_db_dsn,
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_type = 'BASE TABLE' AND table_schema NOT IN "
            "('pg_catalog', 'information_schema') ORDER BY table_schema, table_name",
        )
        listing = ", ".join(f"{r['table_schema']}.{r['table_name']}" for r in available) or "(none)"
        raise ValueError(f"Table {schema}.{table} not found. Available tables: {listing}.")

    stats = query(
        cfg.data_db_dsn,
        """
        SELECT n_live_tup   AS estimated_row_count,
               n_dead_tup   AS dead_tuples,
               n_tup_ins    AS inserts_since_stats_reset,
               n_tup_upd    AS updates_since_stats_reset,
               n_tup_del    AS deletes_since_stats_reset,
               last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
        FROM pg_stat_user_tables
        WHERE schemaname = %s AND relname = %s
        """,
        (schema, table),
    )

    size = query(
        cfg.data_db_dsn,
        "SELECT pg_size_pretty(pg_total_relation_size(%s)) AS total_size",
        (f'"{schema}"."{table}"',),
    )

    exact = query(
        cfg.data_db_dsn,
        sql.SQL("SELECT count(*) AS exact_row_count FROM {}.{}").format(
            sql.Identifier(schema), sql.Identifier(table)
        ),
    )

    return jsonify(
        {
            "table": f"{schema}.{table}",
            "columns": columns,
            "exact_row_count": exact[0]["exact_row_count"] if exact else None,
            "total_size": size[0]["total_size"] if size else None,
            "stats": stats[0] if stats else {"note": "no row in pg_stat_user_tables yet"},
        }
    )


@mcp.tool()
def get_lineage(table: str) -> dict[str, Any]:
    """Which DAG and tasks write this table, and what feeds them upstream,
    from lineage.yaml. This is the entry point for 'why is table X stale?':
    it tells you which DAG to inspect next."""
    entry = lineage_mod.lookup(cfg, table)
    if entry is None:
        raise ValueError(
            f"No lineage registered for '{table}'. Known tables: "
            f"{', '.join(lineage_mod.known_tables(cfg))}. Add it to lineage.yaml."
        )
    return jsonify({"table": table, **entry})


def main() -> None:
    """Console-script entry point; serves over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
