"""
Polling management routes
Handles mailbox polling start/stop/status
"""

from fastapi import APIRouter, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from core.email_handler import EmailHandler, create_email_config, validate_email_config
from core.notification_handler import NotificationHandler
from config.app_config import (
    get_user_config, is_user_configured, get_active_handler, 
    set_active_handler, remove_active_handler, is_polling_active,
    set_notification_handler, set_user_config
)

router = APIRouter()


@router.post("/start-polling")
async def start_polling(
    background_tasks: BackgroundTasks,
    email: str = Form(...)
):
    """Start mailbox polling voor geconfigureerde gebruiker"""
    if not is_user_configured(email):
        return JSONResponse({
            "status": "error",
            "message": "❌ Email niet geconfigureerd",
            "details": "Test eerst de verbinding voordat je polling start"
        }, status_code=400)
    
    if is_polling_active(email):
        return JSONResponse({
            "status": "warning",
            "message": "⚠️ Polling al actief",
            "details": f"Mailbox polling voor {email} is al gestart"
        })
    
    try:
        # Create email config
        config_data = get_user_config(email)
        email_config = create_email_config(config_data, config_data["allowed_senders"])
        
        # Validate config
        is_valid, error_msg = validate_email_config(email_config)
        if not is_valid:
            return JSONResponse({
                "status": "error",
                "message": f"❌ Configuratie fout: {error_msg}"
            }, status_code=400)
        
        # Create and start handler
        handler = EmailHandler(email_config)
        set_active_handler(email, handler)
        
        # Initialize notification handler if notification email is set
        notification_email = config_data.get("notification_email")
        sender_email = config_data.get("sender_email")
        if notification_email:
            # Create SMTP config for notification handler
            smtp_config = {
                "email": email,
                "password": config_data["password"],
                "smtp_server": config_data["smtp_server"],
                "smtp_port": config_data["smtp_port"]
            }
            
            # Create notification handler
            notification_handler = NotificationHandler(
                smtp_config, 
                notification_email, 
                sender_email
            )
            set_notification_handler(email, notification_handler)
            
            target_info = f"target: {notification_email}"
            if sender_email:
                target_info += f", sender: {sender_email}"
            print(f"Notification handler initialized for {email} with {target_info}")
        
        # Start polling in background
        background_tasks.add_task(handler.start_polling, 30)  # Poll every 30 seconds
        
        # Update status
        config_data["status"] = "polling"
        set_user_config(email, config_data)
        
        return JSONResponse({
            "status": "success",
            "message": f"📧 Mailbox polling gestart voor {email}",
            "details": f"Monitoring inbox elke 30 seconden. Toegestane afzenders: {', '.join(config_data['allowed_senders'])}"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"❌ Polling start fout: {str(e)}"
        }, status_code=500)


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
