"""
Remarkable 2 naar Tekst Converter - Main Application
FastAPI web interface voor email configuratie en connectiviteit testing
"""

import os
import ssl
import imaplib
import smtplib
from typing import Dict, Any
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

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
    smtp_port: int = Form(587)
):
    """Test IMAP en SMTP connectiviteit volgens MVP spec"""
    try:
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
            "status": "connected"
        }
        
        return JSONResponse({
            "status": "success",
            "message": f"✅ Verbinding succesvol! IMAP en SMTP werken correct.",
            "details": f"Inbox toegang: OK, SMTP authenticatie: OK"
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


@app.get("/status")
async def get_status():
    """API endpoint voor huidige systeem status"""
    return {
        "app_version": "0.1.0",
        "configured_users": len(user_configs),
        "users": list(user_configs.keys()),
        "environment": os.getenv("DEBUG", "False")
    }


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
