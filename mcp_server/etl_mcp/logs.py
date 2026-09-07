"""Locate and tail Airflow task-instance log files on the host.

The Airflow image in this repo uses the default 2.10 layout
(``docker/docker-airflow/config/airflow.cfg``)::

    dag_id={dag_id}/run_id={run_id}/task_id={task_id}/[map_index={n}/]attempt={try_number}.log

and ``base_log_folder = /opt/airflow/logs``, bind-mounted to ``./logs``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .config import Config


def _task_dir(cfg: Config, dag_id: str, run_id: str, task_id: str, map_index: int | None) -> Path:
    d = cfg.logs_dir / f"dag_id={dag_id}" / f"run_id={run_id}" / f"task_id={task_id}"
    if map_index is not None and map_index >= 0:
        d = d / f"map_index={map_index}"
    return d


def _tail(path: Path, n: int) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return "\n".join(lines[-n:])


def get_task_log_tail(
    cfg: Config,
    dag_id: str,
    run_id: str,
    task_id: str,
    try_number: int | None,
    map_index: int | None = None,
    n: int | None = None,
) -> dict[str, Any]:
    """Return the last ``n`` lines of the newest attempt log for a task instance."""
    n = n or cfg.log_tail_lines
    task_dir = _task_dir(cfg, dag_id, run_id, task_id, map_index)

    if not task_dir.exists():
        return {
            "found": False,
            "searched": str(task_dir),
            "hint": (
                "No log directory for this task instance. If the stack runs "
                "elsewhere, point AIRFLOW_LOGS_DIR at its base_log_folder."
            ),
        }

    attempts = sorted(
        task_dir.glob("attempt=*.log"),
        key=lambda p: int(re.search(r"attempt=(\d+)", p.name).group(1)),
    )
    chosen: Path | None = None
    if try_number is not None:
        exact = task_dir / f"attempt={try_number}.log"
        if exact.exists():
            chosen = exact
    if chosen is None and attempts:
        chosen = attempts[-1]

    if chosen is None:
        return {"found": False, "searched": str(task_dir), "hint": "Directory exists but holds no attempt=*.log files."}

    return {
        "found": True,
        "file": str(chosen),
        "attempts_available": [p.name for p in attempts],
        "tail_lines": n,
        "tail": _tail(chosen, n),
    }
