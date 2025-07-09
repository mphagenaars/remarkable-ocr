"""
Application configuration and storage management
Centralized storage voor user configs en active handlers
"""

from typing import Dict, Any
from core.email_handler import EmailHandler
from core.notification_handler import NotificationHandler

# In-memory storage voor MVP (later vervangen door SQLite in Stap 4)
user_configs: Dict[str, Dict[str, Any]] = {}

# Active email handlers
active_handlers: Dict[str, EmailHandler] = {}

# Active notification handlers
notification_handlers: Dict[str, NotificationHandler] = {}


def get_user_config(email: str) -> Dict[str, Any]:
    """Get user configuration by email"""
    return user_configs.get(email, {})


def set_user_config(email: str, config: Dict[str, Any]) -> None:
    """Set user configuration"""
    user_configs[email] = config


def is_user_configured(email: str) -> bool:
    """Check if user is configured"""
    return email in user_configs


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
    return {
        "configured_users": len(user_configs),
        "active_handlers": len(active_handlers),
        "notification_handlers": len(notification_handlers),
        "users": list(user_configs.keys())
    }
