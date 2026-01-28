"""Logging configuration utilities."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging() -> None:
    """Configure root logger based on environment variables."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_to_file = os.getenv("LOG_TO_FILE", "false").lower() == "true"
    log_file = os.getenv("LOG_FILE", "./data/remarkable.log")
    log_format = os.getenv("LOG_FORMAT", "text").lower()

    level = getattr(logging, log_level, logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    # Clear existing handlers to avoid duplicates
    for handler in list(root.handlers):
        root.removeHandler(handler)

    formatter: logging.Formatter
    if log_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )

    handlers = [logging.StreamHandler()]
    if log_to_file:
        handlers.append(logging.FileHandler(log_file))

    for handler in handlers:
        handler.setFormatter(formatter)
        root.addHandler(handler)

    logging.captureWarnings(True)
