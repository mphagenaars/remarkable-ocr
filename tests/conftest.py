import os

import pytest

from core import metrics


@pytest.fixture(autouse=True)
def reset_metrics():
    metrics._counters.clear()
    metrics._gauges.clear()
    metrics._timers.clear()
    yield


@pytest.fixture
def temp_db_path(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    return db_path
