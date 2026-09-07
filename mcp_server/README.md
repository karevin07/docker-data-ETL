# ETL Observability MCP Server

An [MCP](https://modelcontextprotocol.io) server that lets an agent answer one
recurring question about this pipeline:

> **"This table didn't update today. Why?"**

It is the machine-readable version of a data dictionary: instead of a human
opening the Airflow UI, tailing logs, and cross-referencing which DAG writes
which table, the agent does it with five read-only tools.

## The five tools

| Tool | Answers |
| --- | --- |
| `list_dags()` | What pipelines exist, are they paused, how did the last run go |
| `get_recent_runs(dag_id, limit=10)` | Did today's run happen, and how did it end |
| `get_task_failures(dag_id, run_id=None)` | Which task failed + a tail of its log |
| `get_table_schema(table, schema="public")` | Columns, exact/estimated row count, size, last (auto)vacuum/analyze |
| `get_lineage(table)` | Which DAG + tasks write this table, and what feeds them |

All queries run in a **read-only, autocommit** Postgres session — the server
cannot modify either database. The agent never passes raw SQL.

## How the agent chains them

```
"the content table is stale today, why?"

  get_lineage("content")          -> produced by dag etl_flow,
                                     task load-data.spark-load-content-data,
                                     upstream transformation-data.spark_job
  get_recent_runs("etl_flow")     -> last run scheduled__… state=failed
  get_task_failures("etl_flow")   -> transformation-data.spark_job FAILED;
                                     load tasks upstream_failed
                                     log tail -> java.lang.OutOfMemoryError
                                                 in reduceByKey stage

  => "Last night's 23:40 run failed: the Spark word-count stage
      (transformation-data.spark_job) OOM'd in reduceByKey, so the
      load task never ran. Check input.json size from the scraper."
```

## Data sources

- **Airflow metadata DB** (`dag`, `dag_run`, `task_instance`) — same Postgres
  the stack already runs (`postgresql://airflow:airflow@postgres/airflow`),
  published on `localhost:5432`.
- **Task logs** — the Airflow `base_log_folder` bind mount (`./logs` in the
  repo), default 2.10 layout
  `dag_id=…/run_id=…/task_id=…/attempt=N.log`.
- **Lineage** — [`lineage.yaml`](lineage.yaml), hand-maintained. Add a table
  entry when a new one appears; keep task ids fully qualified
  (`<taskgroup>.<task_id>`) so they match `task_instance.task_id`.

## Setup

Requires the ETL stack to be up (`make up` from the repo root) so Postgres is
reachable and the scheduler has parsed the DAGs.

```bash
cd mcp_server
uv sync                 # install into ./.venv
uv run pytest           # offline unit tests (no DB needed)
uv run etl-mcp          # start the server on stdio
```

### Register with a client

Claude Desktop / Claude Code (`claude mcp add`), pointing at this directory:

```json
{
  "mcpServers": {
    "data-etl": {
      "command": "uv",
      "args": [
        "run", "--directory",
        "/Users/kelvin.liao/Work/Projects/docker-data-etl/mcp_server",
        "etl-mcp"
      ]
    }
  }
}
```

### Configuration (env vars)

| Var | Default | Purpose |
| --- | --- | --- |
| `AIRFLOW_DB_DSN` | `postgresql://airflow:airflow@localhost:5432/airflow` | Airflow metadata DB |
| `DATA_DB_DSN` | = `AIRFLOW_DB_DSN` | Warehouse holding the output tables |
| `AIRFLOW_LOGS_DIR` | `<repo>/logs` | Host path to `base_log_folder` |
| `LINEAGE_FILE` | `<repo>/mcp_server/lineage.yaml` | Lineage definitions |
| `MCP_LOG_TAIL_LINES` | `60` | Log lines returned per failed task |

## Demo scenario

The scraper rarely fails on cue. To make the "OOM'd last night" story
reproducible, seed a failed run into the running stack:

```bash
uv run python demo/seed_failure.py          # inject failed etl_flow run + OOM log
uv run python demo/seed_failure.py --clear   # remove it
```

Then ask your agent: *"the content table didn't update today — why?"*
