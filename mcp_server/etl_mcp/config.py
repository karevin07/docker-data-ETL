"""Runtime configuration, resolved from environment variables.

Defaults assume you are running this server on the Docker host with the
stack up (``make up``): Postgres is published on ``localhost:5432`` and the
Airflow task logs are bind-mounted to ``./logs`` in the repo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# mcp_server/etl_mcp/config.py -> repo root is two parents up.
REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DSN = "postgresql://airflow:airflow@localhost:5432/airflow"


@dataclass(frozen=True)
class Config:
    airflow_db_dsn: str
    """DSN for the Airflow metadata database (dag / dag_run / task_instance)."""

    data_db_dsn: str
    """DSN for the warehouse that holds the ETL output tables (title / content)."""

    logs_dir: Path
    """Host path to the Airflow ``base_log_folder`` bind mount."""

    lineage_file: Path
    """YAML file mapping warehouse tables to the DAG/tasks that produce them."""

    log_tail_lines: int
    """How many trailing log lines to return for a failed task."""


def load_config() -> Config:
    airflow_dsn = os.environ.get("AIRFLOW_DB_DSN", DEFAULT_DSN)
    return Config(
        airflow_db_dsn=airflow_dsn,
        data_db_dsn=os.environ.get("DATA_DB_DSN", airflow_dsn),
        logs_dir=Path(os.environ.get("AIRFLOW_LOGS_DIR", REPO_ROOT / "logs")).expanduser(),
        lineage_file=Path(
            os.environ.get("LINEAGE_FILE", Path(__file__).resolve().parents[1] / "lineage.yaml")
        ).expanduser(),
        log_tail_lines=int(os.environ.get("MCP_LOG_TAIL_LINES", "60")),
    )
