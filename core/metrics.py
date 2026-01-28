"""Simple in-memory metrics for observability endpoints."""

from __future__ import annotations

import time
from threading import Lock
from typing import Dict, Any, Tuple

_lock = Lock()
_start_time = time.time()

_counters: Dict[str, float] = {}
_gauges: Dict[str, float] = {}
_timers: Dict[str, Dict[str, float]] = {}


def _make_key(name: str, labels: Dict[str, str] | None = None) -> str:
    if not labels:
        return name
    label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
    return f"{name}|{label_str}"


def inc_counter(name: str, value: float = 1, **labels: str) -> None:
    key = _make_key(name, labels or None)
    with _lock:
        _counters[key] = _counters.get(key, 0) + value


def set_gauge(name: str, value: float, **labels: str) -> None:
    key = _make_key(name, labels or None)
    with _lock:
        _gauges[key] = value


def observe_duration(name: str, seconds: float, **labels: str) -> None:
    key = _make_key(name, labels or None)
    with _lock:
        entry = _timers.setdefault(key, {"count": 0.0, "sum": 0.0})
        entry["count"] += 1
        entry["sum"] += seconds


def get_uptime_seconds() -> float:
    return time.time() - _start_time


def snapshot() -> Dict[str, Any]:
    with _lock:
        counters = dict(_counters)
        gauges = dict(_gauges)
        timers = {k: dict(v) for k, v in _timers.items()}
    return {
        "uptime_seconds": get_uptime_seconds(),
        "counters": counters,
        "gauges": gauges,
        "timers": timers,
    }
