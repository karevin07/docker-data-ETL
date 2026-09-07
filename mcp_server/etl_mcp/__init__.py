"""MCP server for observing the docker-data-etl pipeline.

Exposes a handful of read-only tools so an agent can trace a stale table
back to the DAG run (and failed task, and log line) that explains it.
"""

__version__ = "0.1.0"
