"""
Polling management routes
Handles mailbox polling start/stop/status
"""

from fastapi import APIRouter, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio
from core.email_handler import EmailHandler, create_email_config, validate_email_config
from core.notification_handler import NotificationHandler
from config.app_config import (
    get_user_config, is_user_configured, get_active_handler, 
    set_active_handler, remove_active_handler, is_polling_active,
    set_notification_handler, set_user_config
)
import os

router = APIRouter()


async def start_polling_internal(email: str, background_tasks: BackgroundTasks = None):
    """Internal logic to start polling."""
    if not is_user_configured(email):
        raise ValueError("Email niet geconfigureerd")

    if is_polling_active(email):
        # This is not an error, just already active.
        print(f"Polling is al actief voor {email}")
        return

    # Create email config
    config_data = get_user_config(email)
    email_config = create_email_config(config_data, config_data["allowed_senders"])
    
    # Validate config
    is_valid, error_msg = validate_email_config(email_config)
    if not is_valid:
        raise ValueError(f"Configuratie fout: {error_msg}")
    
    # Create and start handler
    handler = EmailHandler(email_config)
    set_active_handler(email, handler)
    
    # Initialize notification handler if notification email is set
    notification_email = config_data.get("notification_email")
    if notification_email:
        smtp_config = {
            "email": email,
            "password": config_data["password"],
            "smtp_server": config_data["smtp_server"],
            "smtp_port": config_data["smtp_port"]
        }
        notification_handler = NotificationHandler(smtp_config, notification_email)
        set_notification_handler(email, notification_handler)
        print(f"Notification handler initialized for {email} with target: {notification_email}")
    
    # Start polling in background
    polling_interval = int(os.getenv("POLLING_INTERVAL", 300))
    if background_tasks:
        background_tasks.add_task(handler.start_polling, polling_interval)
    else:
        # When called from startup, no background_tasks object is available.
        # We run it in a separate thread.
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, handler.start_polling, polling_interval)

    # Update status
    config_data["status"] = "polling"
    set_user_config(email, config_data)
    print(f"Mailbox polling gestart voor {email}")


@router.post("/start-polling")
async def start_polling(
    background_tasks: BackgroundTasks,
    email: str = Form(...)
):
    """Start mailbox polling voor geconfigureerde gebruiker"""
    try:
        await start_polling_internal(email, background_tasks)
        config_data = get_user_config(email)
        return JSONResponse({
            "status": "success",
            "message": f"📧 Mailbox polling gestart voor {email}",
            "details": f"Monitoring inbox. Toegestane afzenders: {', '.join(config_data['allowed_senders'])}"
        })
    except ValueError as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"❌ Polling start fout: {str(e)}"}, status_code=500)


@router.post("/stop-polling")
async def stop_polling(email: str = Form(...)):
    """Stop mailbox polling"""
    if not is_polling_active(email):
        return JSONResponse({
            "status": "warning",
            "message": "⚠️ Geen actieve polling",
            "details": f"Er is geen actieve polling voor {email}"
        })
    
    try:
        # Stop handler
        handler = get_active_handler(email)
        handler.stop_polling()
        remove_active_handler(email)
        
        # Update status
        if is_user_configured(email):
            config = get_user_config(email)
            config["status"] = "connected"
            set_user_config(email, config)
        
        return JSONResponse({
            "status": "success",
            "message": f"⏹️ Polling gestopt voor {email}"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"❌ Stop polling fout: {str(e)}"
        }, status_code=500)


@router.get("/polling-status/{email}")
async def get_polling_status(email: str):
    """Get polling status voor specifieke email"""
    if not is_user_configured(email):
        return JSONResponse({
            "configured": False,
            "polling": False,
            "message": "Email niet geconfigureerd"
        })
    
    is_polling = is_polling_active(email)
    config = get_user_config(email)
    
    return JSONResponse({
        "configured": True,
        "polling": is_polling,
        "status": config.get("status", "unknown"),
        "allowed_senders": config.get("allowed_senders", []),
        "message": f"Polling {'actief' if is_polling else 'gestopt'}"
    })
