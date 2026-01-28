"""Retry helpers with exponential backoff."""

from __future__ import annotations

import random


def compute_backoff(
    attempt: int,
    base_delay: float,
    max_delay: float,
    multiplier: float = 2.0,
    jitter: float = 0.1,
) -> float:
    """Compute exponential backoff delay with optional jitter.

    attempt is 1-based (first retry => attempt=1).
    """
    delay = min(base_delay * (multiplier ** (attempt - 1)), max_delay)
    if jitter > 0:
        delay *= random.uniform(1 - jitter, 1 + jitter)
    return delay
