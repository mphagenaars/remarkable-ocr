"""
Email Handler Module voor Remarkable 2 naar Tekst Converter.

Verantwoordelijk voor:
- IMAP mailbox monitoring 
- Afzender whitelist validatie
- PDF/PNG attachment filtering en download
- Background polling met configureerbare intervallen
"""

import ssl
import email
import imaplib
import asyncio
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import OCR processor
from .ocr_processor import OCRProcessor

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuratie voor IMAP/SMTP connecties"""
    email: str
    password: str
    imap_server: str
    imap_port: int
    smtp_server: str
    smtp_port: int
    allowed_senders: List[str]
    openrouter_api_key: Optional[str] = None  # OCR API key


def create_email_config(config_data: Dict[str, Any], allowed_senders: List[str]) -> EmailConfig:
    """Factory function voor EmailConfig"""
    return EmailConfig(
        email=config_data["email"],
        password=config_data["password"],
        imap_server=config_data["imap_server"],
        imap_port=config_data["imap_port"],
        smtp_server=config_data["smtp_server"],
        smtp_port=config_data["smtp_port"],
        allowed_senders=allowed_senders,
        openrouter_api_key=config_data.get("openrouter_api_key")
    )


def validate_email_config(config: EmailConfig) -> tuple[bool, Optional[str]]:
    """Valideer email configuratie"""
    if not config.email or "@" not in config.email:
        return False, "Ongeldig email adres"
    
    if not config.password:
        return False, "Wachtwoord is vereist"
    
    if not config.allowed_senders:
        return False, "Minimaal één toegestane afzender vereist"
    
    return True, None


class EmailHandler:
    """Handles email monitoring en attachment processing"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.is_polling = False
        self.processed_messages: Set[str] = set()
        self._polling_task: Optional[asyncio.Task] = None
        
        # Initialize OCR processor if API key is available
        self.ocr_processor: Optional[OCRProcessor] = None
        if config.openrouter_api_key:
            self.ocr_processor = OCRProcessor(
                api_key=config.openrouter_api_key,
                model="google/gemini-2.5-flash"  # Werkende model
            )
            logger.info(f"OCR processor initialized for {config.email}")
        else:
            logger.warning(f"No OpenRouter API key provided for {config.email}, OCR disabled")
        
    async def start_polling(self, interval_seconds: int = 30):
        """Start background polling van mailbox"""
        if self.is_polling:
            logger.warning(f"Polling already active for {self.config.email}")
            return
            
        self.is_polling = True
        logger.info(f"Starting email polling for {self.config.email} every {interval_seconds}s")
        
        self._polling_task = asyncio.create_task(self._poll_loop(interval_seconds))
        
    async def _poll_loop(self, interval_seconds: int):
        """Main polling loop"""
        while self.is_polling:
            try:
                await self._check_new_emails()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Polling error for {self.config.email}: {e}")
                await asyncio.sleep(interval_seconds)  # Continue polling despite errors
                
    async def _check_new_emails(self):
        """Check for new emails from allowed senders with attachments"""
        try:
            context = ssl.create_default_context()
            
            with imaplib.IMAP4_SSL(self.config.imap_server, self.config.imap_port, ssl_context=context) as imap:
                imap.login(self.config.email, self.config.password)
                imap.select("INBOX")
                
                # Search for unread emails
                status, messages = imap.search(None, "UNSEEN")
                
                if status == "OK" and messages[0]:
                    message_ids = messages[0].split()
                    logger.info(f"Found {len(message_ids)} unread emails for {self.config.email}")
                    
                    for msg_id in message_ids:
                        msg_id_str = msg_id.decode()
                        
                        if msg_id_str in self.processed_messages:
                            continue
                            
                        await self._process_email(imap, msg_id_str)
                        self.processed_messages.add(msg_id_str)
                        
        except Exception as e:
            logger.error(f"Email check failed for {self.config.email}: {e}")
            
    async def _process_email(self, imap: imaplib.IMAP4_SSL, msg_id: str):
        """Process individual email for attachments"""
        try:
            # Fetch email
            status, msg_data = imap.fetch(msg_id, "(RFC822)")
            
            if status != "OK":
                return
                
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Check sender
            sender = email_message.get("From", "")
            sender_email = self._extract_email_address(sender)
            
            if not self._is_allowed_sender(sender_email):
                logger.info(f"Ignoring email from non-whitelisted sender: {sender_email}")
                return
                
            logger.info(f"Processing email from allowed sender: {sender_email}")
            
            # Look for PDF/PNG attachments
            attachments = self._extract_attachments(email_message)
            
            if attachments:
                logger.info(f"Found {len(attachments)} attachments in email from {sender_email}")
                
                # Process attachments with OCR if available
                if self.ocr_processor:
                    await self._process_attachments_with_ocr(attachments, sender_email)
                else:
                    logger.warning("OCR processor not available, skipping text extraction")
                    for attachment in attachments:
                        logger.info(f"Attachment found: {attachment['filename']} ({attachment['content_type']})")
            else:
                logger.info(f"No PDF/PNG attachments found in email from {sender_email}")
                
        except Exception as e:
            logger.error(f"Failed to process email {msg_id}: {e}")
    
    async def _process_attachments_with_ocr(self, attachments: List[Dict[str, Any]], sender_email: str):
        """Process attachments with OCR and log results"""
        for attachment in attachments:
            try:
                filename = attachment['filename']
                file_data = attachment['data']
                
                logger.info(f"Starting OCR processing for: {filename}")
                
                # Process with OCR
                ocr_result = await self.ocr_processor.process_attachment(filename, file_data)
                
                if ocr_result['success']:
                    logger.info(f"OCR successful for {filename}: {len(ocr_result['text'])} characters extracted")
                    logger.info(f"OCR confidence: {ocr_result['confidence']}")
                    
                    # Log first 200 chars of extracted text for debugging
                    preview_text = ocr_result['text'][:200] + "..." if len(ocr_result['text']) > 200 else ocr_result['text']
                    logger.info(f"Extracted text preview: {preview_text}")
                    
                    # Send notification if notification handler is available
                    from app import notification_handlers
                    user_email = self.config.email
                    
                    if user_email in notification_handlers:
                        notification_handler = notification_handlers[user_email]
                        
                        # Try to send notification
                        try:
                            # Include filename in OCR result
                            ocr_result['filename'] = filename
                            
                            # Send notification with original attachment
                            success = await notification_handler.send_ocr_result(
                                ocr_result,
                                original_attachment=file_data
                            )
                            
                            if success:
                                logger.info(f"OCR notification sent successfully for {filename}")
                            else:
                                logger.error(f"Failed to send OCR notification for {filename}")
                                
                        except Exception as e:
                            logger.error(f"Error sending OCR notification: {e}")
                    else:
                        logger.info(f"No notification handler available for {user_email}, skipping notification")
                    
                else:
                    logger.error(f"OCR failed for {filename}: {ocr_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Exception during OCR processing of {attachment['filename']}: {e}")
            
    def _extract_email_address(self, sender: str) -> str:
        """Extract email address from sender field"""
        if "<" in sender and ">" in sender:
            start = sender.find("<") + 1
            end = sender.find(">")
            return sender[start:end].lower().strip()
        return sender.lower().strip()
        
    def _is_allowed_sender(self, sender_email: str) -> bool:
        """Check if sender is in whitelist"""
        return sender_email in [s.lower().strip() for s in self.config.allowed_senders]
        
    def _extract_attachments(self, email_message) -> List[Dict[str, Any]]:
        """Extract PDF/PNG attachments from email"""
        attachments = []
        
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Check for PDF or PNG attachments
            if content_type in ["application/pdf", "image/png"] and "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    attachments.append({
                        "filename": filename,
                        "content_type": content_type,
                        "data": part.get_payload(decode=True)
                    })
                    
        return attachments
        
    def stop_polling(self):
        """Stop polling"""
        self.is_polling = False
        if self._polling_task:
            self._polling_task.cancel()
        logger.info(f"Stopped polling for {self.config.email}")
