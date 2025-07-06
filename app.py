"""
Remarkable 2 naar Tekst Converter - Main Application
FastAPI web interface voor email configuratie en connectiviteit testing
"""

import os
import ssl
import imaplib
import smtplib
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

# Import our email handler
from core.email_handler import EmailHandler, EmailConfig, create_email_config, validate_email_config

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Remarkable 2 naar Tekst Converter",
    description="Automatische conversie van handgeschreven notities naar tekst",
    version="0.1.0"
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage voor MVP (later vervangen door SQLite in Stap 4)
user_configs: Dict[str, Dict[str, Any]] = {}

# Active email handlers
active_handlers: Dict[str, EmailHandler] = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Hoofdpagina met email configuratie formulier"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/test-connection")
async def test_connection(
    email: str = Form(...),
    password: str = Form(...),
    imap_server: str = Form(...),
    imap_port: int = Form(993),
    smtp_server: str = Form(...),
    smtp_port: int = Form(587),
    allowed_senders: str = Form(...)
):
    """Test IMAP en SMTP connectiviteit volgens MVP spec"""
    try:
        # Parse allowed senders
        sender_list = [s.strip() for s in allowed_senders.split(",") if s.strip()]
        
        if not sender_list:
            return JSONResponse({
                "status": "error",
                "message": "❌ Minimaal één toegestane afzender vereist",
                "details": "Vul minimaal één email adres in bij toegestane afzenders"
            }, status_code=400)
        
        # Test IMAP verbinding
        context = ssl.create_default_context()
        
        with imaplib.IMAP4_SSL(imap_server, imap_port, ssl_context=context) as imap:
            imap.login(email, password)
            imap.select("INBOX")
            # Test basic functionality
            status, messages = imap.search(None, "ALL")
            
        # Test SMTP verbinding
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls(context=context)
            smtp.login(email, password)
        
        # Sla configuratie tijdelijk op (in-memory voor MVP)
        user_configs[email] = {
            "email": email,
            "password": password,  # TODO: encrypt in Stap 4
            "imap_server": imap_server,
            "imap_port": imap_port,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "allowed_senders": sender_list,
            "status": "connected"
        }
        
        return JSONResponse({
            "status": "success",
            "message": f"✅ Verbinding succesvol! IMAP en SMTP werken correct.",
            "details": f"Inbox toegang: OK, SMTP authenticatie: OK, {len(sender_list)} toegestane afzender(s)"
        })
    
    except imaplib.IMAP4.error as e:
        return JSONResponse({
            "status": "error",
            "message": f"❌ IMAP fout: {str(e)}",
            "details": "Controleer IMAP server, poort en inloggegevens"
        }, status_code=400)
    
    except smtplib.SMTPException as e:
        return JSONResponse({
            "status": "error", 
            "message": f"❌ SMTP fout: {str(e)}",
            "details": "Controleer SMTP server, poort en inloggegevens"
        }, status_code=400)
    
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"❌ Onbekende fout: {str(e)}",
            "details": "Controleer alle instellingen en probeer opnieuw"
        }, status_code=500)


@app.post("/start-polling")
async def start_polling(
    background_tasks: BackgroundTasks,
    email: str = Form(...)
):
    """Start mailbox polling voor geconfigureerde gebruiker"""
    if email not in user_configs:
        return JSONResponse({
            "status": "error",
            "message": "❌ Email niet geconfigureerd",
            "details": "Test eerst de verbinding voordat je polling start"
        }, status_code=400)
    
    if email in active_handlers:
        return JSONResponse({
            "status": "warning",
            "message": "⚠️ Polling al actief",
            "details": f"Mailbox polling voor {email} is al gestart"
        })
    
    try:
        # Create email config
        config_data = user_configs[email]
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
        active_handlers[email] = handler
        
        # Start polling in background
        background_tasks.add_task(handler.start_polling, 30)  # Poll every 30 seconds
        
        # Update status
        user_configs[email]["status"] = "polling"
        
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


@app.post("/stop-polling")
async def stop_polling(email: str = Form(...)):
    """Stop mailbox polling"""
    if email not in active_handlers:
        return JSONResponse({
            "status": "warning",
            "message": "⚠️ Geen actieve polling",
            "details": f"Er is geen actieve polling voor {email}"
        })
    
    try:
        # Stop handler
        handler = active_handlers[email]
        handler.stop_polling()
        del active_handlers[email]
        
        # Update status
        if email in user_configs:
            user_configs[email]["status"] = "connected"
        
        return JSONResponse({
            "status": "success",
            "message": f"⏹️ Polling gestopt voor {email}"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"❌ Stop polling fout: {str(e)}"
        }, status_code=500)


@app.get("/polling-status/{email}")
async def get_polling_status(email: str):
    """Get polling status voor specifieke email"""
    if email not in user_configs:
        return JSONResponse({
            "configured": False,
            "polling": False,
            "message": "Email niet geconfigureerd"
        })
    
    is_polling = email in active_handlers
    config = user_configs[email]
    
    return JSONResponse({
        "configured": True,
        "polling": is_polling,
        "status": config.get("status", "unknown"),
        "allowed_senders": config.get("allowed_senders", []),
        "message": f"Polling {'actief' if is_polling else 'gestopt'}"
    })
    """API endpoint voor huidige systeem status"""
    return {
        "app_version": "0.1.0",
        "configured_users": len(user_configs),
        "users": list(user_configs.keys()),
        "environment": os.getenv("DEBUG", "False")
    }


@app.get("/debug/polling")
async def debug_polling():
    """Debug endpoint voor polling status"""
    debug_info = {
        "active_handlers": len(active_handlers),
        "configured_users": len(user_configs),
        "handlers": {}
    }
    
    for email, handler in active_handlers.items():
        debug_info["handlers"][email] = {
            "is_polling": handler.is_polling,
            "processed_messages": len(handler.processed_messages),
            "allowed_senders": handler.config.allowed_senders
        }
    
    return JSONResponse(debug_info)


@app.get("/health")
async def health_check():
    """Health check endpoint voor monitoring"""
    return {"status": "healthy", "service": "remarkable-ocr"}


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
