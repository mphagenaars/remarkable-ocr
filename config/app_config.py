"""
Application configuration and storage management
Centralized storage voor user configs en active handlers
"""

from typing import Dict, Any
import os
from core.email_handler import EmailHandler
from core.notification_handler import NotificationHandler
from config.storage import (
    init_db,
    get_user_config as storage_get_user_config,
    set_user_config as storage_set_user_config,
    list_users as storage_list_users,
    has_users as storage_has_users,
)

# Initialize persistent storage
init_db()

# Active email handlers (runtime-only)
active_handlers: Dict[str, EmailHandler] = {}

# Active notification handlers (runtime-only)
notification_handlers: Dict[str, NotificationHandler] = {}


def get_config_mode() -> str:
    """Get configuration mode from environment"""
    return os.getenv("CONFIG_MODE", "gui").lower()


def is_env_mode() -> bool:
    """Check if running in env-only mode"""
    return get_config_mode() == "env"


def is_hybrid_mode() -> bool:
    """Check if running in hybrid mode"""
    return get_config_mode() == "hybrid"


def is_gui_mode() -> bool:
    """Check if running in GUI mode"""
    return get_config_mode() == "gui"


def validate_env_config() -> tuple[bool, str]:
    """Validate environment configuration"""
    if not is_env_mode():
        return True, ""

    required_vars = ["EMAIL", "EMAIL_PASSWORD", "ALLOWED_SENDERS"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        return False, f"Missing required ENV variables: {', '.join(missing)}"
    
    # Validate email format
    email = os.getenv("EMAIL")
    if "@" not in email:
        return False, f"Invalid email format for EMAIL: {email}"
    
    # Validate allowed senders
    senders = os.getenv("ALLOWED_SENDERS")
    if not senders or not any("@" in s.strip() for s in senders.split(",")):
        return False, "ALLOWED_SENDERS must contain at least one valid email address"
    
    return True, "Configuration valid"




async def auto_start_polling():
    """Auto-start polling if configured in ENV mode"""
    if not is_env_mode():
        return
        
    if not os.getenv("AUTO_START_POLLING", "false").lower() == "true":
        return
        
    email = os.getenv("EMAIL")
    if not email or not is_user_configured(email):
        print("Cannot auto-start polling: user not configured")
        return
        
    # Start polling via existing route logic
    from routes.polling_routes import start_polling_internal
    try:
        await start_polling_internal(email)
        print(f"Auto-started polling for {email}")
    except Exception as e:
        print(f"Auto-start polling failed: {e}")


def load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    if not is_env_mode():
        return {}
    
    is_valid, message = validate_env_config()
    if not is_valid:
        raise ValueError(message)
    
    email = os.getenv("EMAIL")
    password = os.getenv("EMAIL_PASSWORD") 
    allowed_senders = os.getenv("ALLOWED_SENDERS")
    
    return {
        "email": email,
        "password": password,
        "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
        "imap_port": int(os.getenv("IMAP_PORT", "993")),
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "allowed_senders": [s.strip() for s in allowed_senders.split(",")],
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
        "notification_email": os.getenv("NOTIFICATION_EMAIL"),
        "status": "env_configured"
    }

def auto_configure_env_user():
    """Auto-configure user from ENV if in env mode"""
    if is_env_mode():
        try:
            env_config = load_env_config()
            if not storage_has_users() or not is_user_configured(env_config["email"]):
                set_user_config(env_config["email"], env_config)
            print(f"Auto-configured user: {env_config['email']}")
        except ValueError as e:
            print(f"ENV configuration error: {e}")


def get_user_config(email: str) -> Dict[str, Any]:
    """Get user configuration by email"""
    config = storage_get_user_config(email)
    return config or {}


def set_user_config(email: str, config: Dict[str, Any]) -> None:
    """Set user configuration"""
    storage_set_user_config(email, config)


def is_user_configured(email: str) -> bool:
    """Check if user is configured"""
    return storage_get_user_config(email) is not None


def get_active_handler(email: str) -> EmailHandler:
    """Get active email handler by email"""
    return active_handlers.get(email)


def set_active_handler(email: str, handler: EmailHandler) -> None:
    """Set active email handler"""
    active_handlers[email] = handler


def remove_active_handler(email: str) -> None:
    """Remove active email handler"""
    if email in active_handlers:
        del active_handlers[email]


def is_polling_active(email: str) -> bool:
    """Check if polling is active for email"""
    return email in active_handlers


def get_notification_handler(email: str) -> NotificationHandler:
    """Get notification handler by email"""
    return notification_handlers.get(email)


def set_notification_handler(email: str, handler: NotificationHandler) -> None:
    """Set notification handler"""
    notification_handlers[email] = handler


def get_stats() -> Dict[str, Any]:
    """Get application statistics"""
    users = storage_list_users()
    return {
        "configured_users": len(users),
        "active_handlers": len(active_handlers),
        "notification_handlers": len(notification_handlers),
        "users": list(users)
    }
