"""
Notification configuration routes
Handles notification email settings
"""

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from core.notification_handler import NotificationHandler
from config.app_config import (
    get_user_config, is_user_configured, set_user_config,
    get_notification_handler, set_notification_handler
)

router = APIRouter()


@router.post("/set-notification-email")
async def set_notification_email(
    email: str = Form(...),
    notification_email: str = Form(...)
):
    """Stel notificatie-emailadres in voor gebruiker"""
    if not is_user_configured(email):
        return JSONResponse({
            "status": "error",
            "message": "❌ Email niet geconfigureerd",
            "details": "Configureer eerst je email-instellingen"
        }, status_code=400)
    
    try:
        # Update config
        config = get_user_config(email)
        config["notification_email"] = notification_email
        set_user_config(email, config)
        
        # Update notification handler if it exists
        notification_handler = get_notification_handler(email)
        if notification_handler:
            notification_handler.set_notification_email(notification_email)
        else:
            # Create notification handler with SMTP config
            smtp_config = {
                "email": config["email"],
                "password": config["password"],
                "smtp_server": config["smtp_server"],
                "smtp_port": config["smtp_port"],
            }
            new_handler = NotificationHandler(smtp_config, notification_email)
            set_notification_handler(email, new_handler)
        
        return JSONResponse({
            "status": "success",
            "message": f"✅ Notificatie-emailadres ingesteld: {notification_email}",
            "details": "OCR resultaten worden naar dit adres gestuurd"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"❌ Fout bij instellen notificatie-email: {str(e)}"
        }, status_code=500)



