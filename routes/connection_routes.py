"""
Connection testing routes
Handles IMAP/SMTP connectivity testing
"""

import ssl
import imaplib
import smtplib
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from config.app_config import set_user_config

router = APIRouter()


@router.post("/test-connection")
async def test_connection(
    email: str = Form(...),
    password: str = Form(...),
    imap_server: str = Form(...),
    imap_port: int = Form(993),
    smtp_server: str = Form(...),
    smtp_port: int = Form(587),
    allowed_senders: str = Form(...),
    openrouter_api_key: str = Form(""),  # Optional OCR API key
    notification_email: str = Form("")  # Optional notification email
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
        config = {
            "email": email,
            "password": password,  # TODO: encrypt in Stap 4
            "imap_server": imap_server,
            "imap_port": imap_port,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "allowed_senders": sender_list,
            "openrouter_api_key": openrouter_api_key.strip() if openrouter_api_key else None,
            "status": "connected",
            "notification_email": notification_email.strip() if notification_email else None
        }
        set_user_config(email, config)
        
        # Create status message with OCR info
        ocr_status = "OCR enabled" if openrouter_api_key.strip() else "OCR disabled (no API key)"
        
        return JSONResponse({
            "status": "success",
            "message": f"✅ Verbinding succesvol! IMAP en SMTP werken correct.",
            "details": f"Inbox toegang: OK, SMTP authenticatie: OK, {len(sender_list)} toegestane afzender(s), {ocr_status}"
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
