"""Make DB rows JSON-friendly for the MCP transport."""

from __future__ import annotations

import datetime as _dt
from decimal import Decimal
from typing import Any


def jsonify(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: jsonify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonify(v) for v in value]
    if isinstance(value, (_dt.datetime, _dt.date, _dt.time)):
        return value.isoformat()
    if isinstance(value, _dt.timedelta):
        return value.total_seconds()
    if isinstance(value, Decimal):
        return float(value)
    return value
