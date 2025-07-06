"""
Email Handler - IMAP polling en message processing
Handles mailbox monitoring, attachment filtering, and sender whitelisting
"""

import imaplib
import email
import ssl
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dataclasses import dataclass
from datetime import datetime
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuration for IMAP/SMTP"""
    email_address: str
    password: str
    imap_server: str
    imap_port: int
    smtp_server: str
    smtp_port: int
    allowed_senders: List[str]  # Whitelist van toegestane afzenders


@dataclass
class EmailMessage:
    """Parsed email message met attachment info"""
    message_id: str
    sender: str
    subject: str
    date: datetime
    attachments: List[Dict[str, any]]
    raw_email: email.message.EmailMessage


class EmailHandler:
    """Handles IMAP polling en email processing"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.is_polling = False
        self.processed_messages = set()  # Track verwerkte message IDs
        
    async def start_polling(self, poll_interval: int = 30) -> None:
        """Start continuous mailbox polling"""
        logger.info(f"Starting email polling every {poll_interval} seconds")
        logger.info(f"Allowed senders: {', '.join(self.config.allowed_senders)}")
        
        self.is_polling = True
        while self.is_polling:
            try:
                await self._check_mailbox()
                await asyncio.sleep(poll_interval)
            except Exception as e:
                logger.error(f"Polling error: {e}")
                await asyncio.sleep(poll_interval * 2)  # Longer wait on error
    
    def stop_polling(self) -> None:
        """Stop mailbox polling"""
        logger.info("Stopping email polling")
        self.is_polling = False
    
    async def _check_mailbox(self) -> List[EmailMessage]:
        """Check for new emails with attachments from allowed senders"""
        try:
            context = ssl.create_default_context()
            
            with imaplib.IMAP4_SSL(self.config.imap_server, self.config.imap_port, 
                                  ssl_context=context) as imap:
                imap.login(self.config.email_address, self.config.password)
                imap.select("INBOX")
                
                # Search for recent unread emails
                status, messages = imap.search(None, "UNSEEN")
                
                if status != "OK" or not messages[0]:
                    logger.debug("No new messages found")
                    return []
                
                message_ids = messages[0].split()
                new_messages = []
                
                for msg_id in message_ids:
                    try:
                        parsed_msg = await self._process_message(imap, msg_id)
                        if parsed_msg:
                            new_messages.append(parsed_msg)
                    except Exception as e:
                        logger.error(f"Error processing message {msg_id}: {e}")
                
                if new_messages:
                    logger.info(f"Found {len(new_messages)} new messages to process")
                
                return new_messages
                
        except Exception as e:
            logger.error(f"Mailbox check error: {e}")
            raise
    
    async def _process_message(self, imap: imaplib.IMAP4_SSL, 
                              msg_id: bytes) -> Optional[EmailMessage]:
        """Process single email message"""
        try:
            # Fetch message
            status, msg_data = imap.fetch(msg_id, "(RFC822)")
            if status != "OK":
                return None
            
            raw_email = email.message_from_bytes(msg_data[0][1])
            
            # Extract basic info
            sender = self._extract_email_address(raw_email.get("From", ""))
            subject = raw_email.get("Subject", "")
            message_id = raw_email.get("Message-ID", "")
            date_str = raw_email.get("Date", "")
            
            # Skip if already processed
            if message_id in self.processed_messages:
                logger.debug(f"Message {message_id} already processed")
                return None
            
            # Check sender whitelist
            if not self._is_sender_allowed(sender):
                logger.warning(f"Email from {sender} blocked - not in whitelist")
                return None
            
            # Extract attachments
            attachments = self._extract_attachments(raw_email)
            
            # Only process emails with PDF/PNG attachments
            if not self._has_valid_attachments(attachments):
                logger.info(f"Email from {sender} has no valid attachments (PDF/PNG)")
                return None
            
            # Parse date
            try:
                msg_date = email.utils.parsedate_to_datetime(date_str)
            except:
                msg_date = datetime.now()
            
            # Mark as processed
            self.processed_messages.add(message_id)
            
            logger.info(f"Processing email from {sender}: {subject}")
            logger.info(f"Found {len(attachments)} valid attachments")
            
            return EmailMessage(
                message_id=message_id,
                sender=sender,
                subject=subject,
                date=msg_date,
                attachments=attachments,
                raw_email=raw_email
            )
            
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            return None
    
    def _is_sender_allowed(self, sender: str) -> bool:
        """Check if sender is in whitelist"""
        sender_clean = sender.lower().strip()
        
        for allowed in self.config.allowed_senders:
            if allowed.lower().strip() in sender_clean:
                return True
        
        return False
    
    def _extract_email_address(self, from_header: str) -> str:
        """Extract clean email address from From header"""
        try:
            # Handle formats like: "Name <email@domain.com>" or "email@domain.com"
            if "<" in from_header and ">" in from_header:
                return from_header.split("<")[1].split(">")[0].strip()
            else:
                return from_header.strip()
        except:
            return from_header.strip()
    
    def _extract_attachments(self, msg: email.message.EmailMessage) -> List[Dict]:
        """Extract PDF/PNG attachments from email"""
        attachments = []
        
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                
                if filename and self._is_valid_file_type(filename):
                    attachments.append({
                        "filename": filename,
                        "content_type": part.get_content_type(),
                        "size": len(part.get_payload(decode=True) or b""),
                        "data": part.get_payload(decode=True)
                    })
        
        return attachments
    
    def _is_valid_file_type(self, filename: str) -> bool:
        """Check if file is PDF or PNG"""
        filename_lower = filename.lower()
        return filename_lower.endswith(('.pdf', '.png', '.jpg', '.jpeg'))
    
    def _has_valid_attachments(self, attachments: List[Dict]) -> bool:
        """Check if email has at least one valid attachment"""
        return len(attachments) > 0
    
    async def mark_as_processed(self, message_id: str) -> None:
        """Mark message as processed to avoid reprocessing"""
        self.processed_messages.add(message_id)
        logger.debug(f"Marked message {message_id} as processed")


# Helper functions for email config management
def create_email_config(email_data: Dict, allowed_senders: List[str]) -> EmailConfig:
    """Create EmailConfig from form data"""
    return EmailConfig(
        email_address=email_data["email"],
        password=email_data["password"],
        imap_server=email_data["imap_server"],
        imap_port=int(email_data["imap_port"]),
        smtp_server=email_data["smtp_server"],
        smtp_port=int(email_data["smtp_port"]),
        allowed_senders=allowed_senders
    )


def validate_email_config(config: EmailConfig) -> Tuple[bool, str]:
    """Validate email configuration"""
    if not config.email_address or "@" not in config.email_address:
        return False, "Invalid email address"
    
    if not config.password:
        return False, "Password is required"
    
    if not config.allowed_senders:
        return False, "At least one allowed sender must be specified"
    
    if not (1 <= config.imap_port <= 65535):
        return False, "Invalid IMAP port"
    
    if not (1 <= config.smtp_port <= 65535):
        return False, "Invalid SMTP port"
    
    return True, "Configuration valid"
