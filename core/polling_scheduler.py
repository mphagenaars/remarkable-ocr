"""
Central polling scheduler using APScheduler.
"""

from __future__ import annotations

import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


def start_scheduler() -> None:
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("Polling scheduler started")


def shutdown_scheduler() -> None:
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Polling scheduler stopped")


def schedule_polling(job_id: str, handler, interval_seconds: int) -> None:
    scheduler = get_scheduler()
    if scheduler.get_job(job_id):
        return
    scheduler.add_job(
        handler.poll_once,
        trigger=IntervalTrigger(seconds=interval_seconds),
        id=job_id,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=interval_seconds,
    )
    logger.info("Scheduled polling for %s every %ss", job_id, interval_seconds)


def unschedule_polling(job_id: str) -> None:
    scheduler = get_scheduler()
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info("Unscheduled polling for %s", job_id)
