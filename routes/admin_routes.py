"""
Admin and debug routes
Handles health checks, debug info and system status
"""

import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from config.app_config import get_stats, active_handlers

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint voor monitoring"""
    return {"status": "healthy", "service": "remarkable-ocr"}


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
            "processed_messages": len(handler.processed_messages),
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
