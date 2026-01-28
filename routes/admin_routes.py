"""
Admin and debug routes
Handles health checks, debug info and system status
"""

import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from config.app_config import get_stats, active_handlers, get_config_mode
from config.storage import count_processed_messages, check_db
from core.metrics import snapshot
from core.polling_scheduler import get_scheduler

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint voor monitoring"""
    stats = get_stats()
    db_ok, db_detail = check_db()
    scheduler = get_scheduler()
    overall_ok = db_ok
    return {
        "status": "healthy" if overall_ok else "degraded",
        "service": "remarkable-ocr",
        "config_mode": get_config_mode(),
        "configured_users": stats["configured_users"],
        "active_handlers": stats["active_handlers"],
        "notification_handlers": stats["notification_handlers"],
        "processed_messages_total": count_processed_messages(),
        "scheduler_running": scheduler.running,
        "database": {"ok": db_ok, "detail": db_detail},
        "environment": os.getenv("DEBUG", "False"),
    }


@router.get("/debug/polling")
async def debug_polling():
    """Debug endpoint voor polling status"""
    stats = get_stats()
    debug_info = {
        "active_handlers": stats["active_handlers"],
        "configured_users": stats["configured_users"],
        "handlers": {}
    }
    
    for email, handler in active_handlers.items():
        debug_info["handlers"][email] = {
            "is_polling": handler.is_polling,
            "processed_messages": count_processed_messages(email),
            "allowed_senders": handler.config.allowed_senders
        }
    
    return JSONResponse(debug_info)


@router.get("/status")
async def get_status():
    """API endpoint voor huidige systeem status"""
    stats = get_stats()
    return {
        "app_version": "0.1.0",
        "configured_users": stats["configured_users"],
        "users": stats["users"],
        "environment": os.getenv("DEBUG", "False")
    }


@router.get("/metrics")
async def metrics():
    """Basic JSON metrics endpoint."""
    return JSONResponse(snapshot())
