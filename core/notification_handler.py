"""
Notification Handler Module voor Remarkable 2 naar Tekst Converter.

Verantwoordelijk voor:
- Formatteren van OCR resultaten
- Genereren van email notificaties
- Verzenden via SMTP
- Error handling en retries
"""

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, Any, Optional
import asyncio
from pathlib import Path
import os
import jinja2

logger = logging.getLogger(__name__)

# Set up Jinja2 environment for email templates
template_loader = jinja2.FileSystemLoader(searchpath=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))
template_env = jinja2.Environment(loader=template_loader)


class NotificationHandler:
    """Handles formatting and sending OCR result notifications."""
    
    def __init__(self, smtp_config: Dict[str, Any], notification_email: Optional[str] = None):
        """Initialize notification handler.
        
        Args:
            smtp_config (dict): SMTP server configuration
            notification_email (str, optional): Default notification email address
        """
        self.smtp_config = smtp_config
        self.notification_email = notification_email
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
    def set_notification_email(self, email: str):
        """Set or update the notification email address.
        
        Args:
            email (str): Email address for notifications
        """
        self.notification_email = email
        logger.info(f"Notification email updated to: {email}")
        

    async def format_ocr_result(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format OCR result text for better readability.
        
        Args:
            ocr_result (dict): OCR processor output
            
        Returns:
            dict: Formatted result with metadata
        """
        formatted_text = ocr_result.get("text", "")
        
        # Preserve paragraphs and whitespace
        # For now, we keep it simple and preserve the original text structure
        # In future iterations, we could add smart paragraph detection and cleanup
        
        # Add metadata to the formatted result
        formatted_result = {
            "text": formatted_text,
            "confidence": ocr_result.get("confidence", "Unknown"),
            "processing_time": ocr_result.get("processing_time", "Unknown"),
            "timestamp": ocr_result.get("timestamp", "Unknown"),
            "model": ocr_result.get("model", "Unknown"),
            "success": ocr_result.get("success", False)
        }
        
        return formatted_result
        
    async def prepare_email(self, recipient: str, formatted_result: Dict[str, Any], original_filename: str) -> MIMEMultipart:
        """Prepare email content with OCR results.
        
        Args:
            recipient (str): Recipient email
            formatted_result (dict): Formatted OCR result
            original_filename (str): Original attachment filename
            
        Returns:
            MIMEMultipart: Prepared email message
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = f"OCR Resultaat: {original_filename}"
        message["From"] = self.smtp_config["email"]
        message["To"] = recipient
        
        # Create plain text version
        text_content = f"""OCR Resultaat voor: {original_filename}
        
Vertrouwen: {formatted_result.get('confidence', 'Unknown')}
Model: {formatted_result.get('model', 'Unknown')}

-------- TEKST --------

{formatted_result.get('text', 'Geen tekst gevonden.')}

------------------------

Automatisch verwerkt door Remarkable 2 naar Tekst Converter.
        """
        
        # Create HTML version using template
        try:
            template = template_env.get_template("email_response.html")
            html_content = template.render(
                filename=original_filename,
                result=formatted_result
            )
        except jinja2.exceptions.TemplateNotFound:
            # Fallback to basic HTML if template not found
            logger.warning("Email template niet gevonden, fallback naar basis HTML")
            html_content = f"""
            <html>
              <body>
                <h2>OCR Resultaat: {original_filename}</h2>
                <p><strong>Vertrouwen:</strong> {formatted_result.get('confidence', 'Unknown')}</p>
                <p><strong>Model:</strong> {formatted_result.get('model', 'Unknown')}</p>
                <hr>
                <pre style="white-space: pre-wrap; font-family: monospace;">{formatted_result.get('text', 'Geen tekst gevonden.')}</pre>
                <hr>
                <p><em>Automatisch verwerkt door Remarkable 2 naar Tekst Converter.</em></p>
              </body>
            </html>
            """
            
        # Attach parts to message
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)
        
        return message
        
    async def send_ocr_result(self, ocr_result: Dict[str, Any], original_attachment: Optional[bytes] = None, 
                              recipient: Optional[str] = None) -> bool:
        """Send OCR results via email.
        
        Args:
            ocr_result (dict): OCR processor result
            original_attachment (bytes, optional): Original file
            recipient (str, optional): Custom recipient (overrides default notification_email)
            
        Returns:
            bool: Success status
        """
        # Use default notification_email if recipient not specified
        target_email = recipient or self.notification_email
        
        if not target_email:
            logger.error("Geen notificatie email adres ingesteld")
            return False
            
        if not ocr_result.get("success", False):
            logger.warning(f"Poging om mislukt OCR resultaat te versturen: {ocr_result.get('error', 'Unknown error')}")
        
        try:
            # Format OCR result
            formatted_result = await self.format_ocr_result(ocr_result)
            
            # Get original filename or use default
            original_filename = ocr_result.get("filename", "document.pdf")
            
            # Prepare email message
            message = await self.prepare_email(target_email, formatted_result, original_filename)
            
            # Attach original file if provided
            if original_attachment:
                attachment = MIMEApplication(original_attachment)
                attachment.add_header(
                    "Content-Disposition", 
                    f"attachment; filename={original_filename}"
                )
                message.attach(attachment)
            
            # Send email with retry mechanism
            return await self._send_with_retry(message, target_email)
            
        except Exception as e:
            logger.error(f"Fout bij voorbereiden notificatie email: {e}")
            return False
    
    async def _send_with_retry(self, message: MIMEMultipart, recipient: str) -> bool:
        """Send email with retry mechanism.
        
        Args:
            message: Prepared email message
            recipient: Target email address
            
        Returns:
            bool: Success status
        """
        retries = 0
        
        while retries < self.max_retries:
            try:
                context = ssl.create_default_context()
                
                with smtplib.SMTP(self.smtp_config["smtp_server"], self.smtp_config["smtp_port"]) as server:
                    server.starttls(context=context)
                    server.login(self.smtp_config["email"], self.smtp_config["password"])
                    server.sendmail(
                        self.smtp_config["email"],
                        recipient,
                        message.as_string()
                    )
                
                logger.info(f"OCR notificatie succesvol verzonden naar {recipient}")
                return True
                
            except Exception as e:
                retries += 1
                logger.error(f"Poging {retries}/{self.max_retries} om email te verzenden mislukt: {e}")
                
                if retries < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                    # Increase delay for next retry (exponential backoff)
                    self.retry_delay *= 2
        
        logger.error(f"OCR notificatie kon niet worden verzonden na {self.max_retries} pogingen")
        return False
