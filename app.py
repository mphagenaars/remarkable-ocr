"""
Remarkable 2 naar Tekst Converter - Main Application
FastAPI web interface voor email configuratie en connectiviteit testing
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv

# Import route modules
from routes.connection_routes import router as connection_router
from routes.polling_routes import router as polling_router
from routes.notification_routes import router as notification_router
from routes.admin_routes import router as admin_router
from config.app_config import (
    auto_configure_env_user, auto_start_polling, 
    get_config_mode, is_env_mode, validate_env_config
)

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Remarkable 2 naar Tekst Converter",
    description="Automatische conversie van handgeschreven notities naar tekst",
    version="0.1.0"
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include route modules
app.include_router(connection_router)
app.include_router(polling_router)
app.include_router(notification_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup_event():
    """Configure application on startup"""
    is_valid, message = validate_env_config()
    if not is_valid:
        logger.error("="*50)
        logger.error("FATAL: Invalid environment configuration.")
        logger.error(message)
        logger.error("Application will not start with invalid ENV config.")
        logger.error("="*50)
        # In a real scenario, you might want to exit here.
        # For development, we'll log and continue.
        # import sys
        # sys.exit(1)
        return

    auto_configure_env_user()
    await auto_start_polling()
    logger.info("Application startup complete")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Hoofdpagina met email configuratie formulier"""
    env_defaults = {
        "email": os.getenv("EMAIL", ""),
        "imap_server": os.getenv("IMAP_SERVER", "imap.gmail.com"),
        "imap_port": os.getenv("IMAP_PORT", "993"),
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": os.getenv("SMTP_PORT", "587"),
        "allowed_senders": os.getenv("ALLOWED_SENDERS", ""),
        "notification_email": os.getenv("NOTIFICATION_EMAIL", "")
    }
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "defaults": env_defaults,
        "config_mode": get_config_mode(),
        "is_env_mode": is_env_mode()
    })


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon from static directory"""
    return FileResponse("static/favicon.ico")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
