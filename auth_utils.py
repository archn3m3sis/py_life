"""
Authentication utilities for magic-link based authentication.

This module provides utility functions for creating and sending magic links,
validating tokens, and managing user authentication flow.

Environment Variables:
    BASE_URL: Base URL for the application (default: http://localhost:3000)
    SMTP_SERVER: SMTP server for sending emails
    SMTP_PORT: SMTP port (default: 587)
    SMTP_USER: SMTP username
    SMTP_PASS: SMTP password

Example Usage:
    # Create and send a magic link
    success = create_and_send_magic_link("user@example.com")
    
    # Validate a token
    is_valid, user, magic_link = validate_token("some-token")
    
    # Consume a token (mark as used)
    success, user = consume_token("some-token")
"""

import os
import logging
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText

# Base configuration
from rxconfig import config
from py_life.models.core.models import User, MagicLink

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy session setup
engine = create_engine(config.db_url)
Session = sessionmaker(bind=engine)

# Exported functions
__all__ = [
    'generate_token',
    'create_magic_link',
    'send_magic_link',
    'create_and_send_magic_link',
    'validate_token',
    'consume_token'
]


def generate_token():
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def create_magic_link(email):
    """Create a magic link for an email address.
    
    Args:
        email (str): The email address to create a magic link for
        
    Returns:
        str: The full URL for the magic link, or None if creation failed
    """
    session = Session()
    try:
        # Fetch user or create if doesn't exist
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email, name=email.split('@')[0])  # Example name as local part
            session.add(user)
            session.flush()  # Flush to get the user ID
            logger.info(f"Created new user for email: {email}")
        else:
            logger.info(f"Found existing user for email: {email}")

        # Create and store magic link
        token = generate_token()
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Create MagicLink directly instead of using user method
        magic_link = MagicLink(
            token=token,
            expires_at=expires_at,
            user_id=user.id
        )
        session.add(magic_link)
        session.commit()

        # Get base URL from environment variable or use default
        base_url = os.getenv('BASE_URL', 'http://localhost:3000')
        url = f"{base_url}/verify?token={token}"
        logger.info(f"Magic link created for {email}: {url}")
        return url
    except Exception as e:
        logger.error(f"Error creating magic link for {email}: {str(e)}", exc_info=True)
        session.rollback()
        return None
    finally:
        session.close()


def send_magic_link(email, url):
    """Send magic link to the user via email or log to console.
    
    Args:
        email (str): The recipient's email address
        url (str): The magic link URL to send
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not email or not url:
        logger.error("Email or URL is missing")
        return False
        
    try:
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASS')

        if smtp_server and smtp_user and smtp_pass:
            # Send email via SMTP
            logger.info(f"Sending magic link to {email} via SMTP")
            with SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                
                # Create email message
                msg = MIMEText(
                    f"Hello,\n\n"
                    f"Click the link below to verify your email and log in:\n\n"
                    f"{url}\n\n"
                    f"This link will expire in 15 minutes.\n\n"
                    f"If you didn't request this, please ignore this email."
                )
                msg['Subject'] = "Your Magic Link - PyLife"
                msg['From'] = smtp_user
                msg['To'] = email
                
                server.send_message(msg)
                logger.info(f"Magic link sent successfully to {email}")
                return True
        else:
            # Fallback: log to console
            logger.warning("SMTP not configured. Logging magic link to console.")
            logger.info(f"=== MAGIC LINK FOR {email} ===")
            logger.info(f"URL: {url}")
            logger.info(f"=============================")
            return True
            
    except SMTPException as e:
        logger.error(f"SMTP error sending magic link to {email}: {str(e)}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending magic link to {email}: {str(e)}", exc_info=True)
        return False


def create_and_send_magic_link(email):
    """Create and send a magic link in one step.
    
    Args:
        email (str): The email address to create and send magic link for
        
    Returns:
        bool: True if both creation and sending succeeded, False otherwise
    """
    url = create_magic_link(email)
    if url:
        return send_magic_link(email, url)
    return False


def validate_token(token):
    """Validate a magic link token.
    
    Args:
        token (str): The token to validate
        
    Returns:
        tuple: (is_valid, user, magic_link) where:
            - is_valid (bool): True if token is valid
            - user (User): The user associated with the token (if valid)
            - magic_link (MagicLink): The magic link object (if valid)
    """
    session = Session()
    try:
        # Find the magic link by token
        magic_link = session.query(MagicLink).filter_by(token=token).first()
        
        if not magic_link:
            logger.warning(f"Token not found: {token}")
            return False, None, None
            
        # Check if token is still valid
        if not magic_link.is_valid():
            logger.warning(f"Token is expired or already used: {token}")
            return False, None, None
            
        # Get the associated user
        user = session.query(User).filter_by(id=magic_link.user_id).first()
        
        if not user:
            logger.error(f"User not found for magic link: {token}")
            return False, None, None
            
        logger.info(f"Valid token for user: {user.email}")
        return True, user, magic_link
        
    except Exception as e:
        logger.error(f"Error validating token {token}: {str(e)}", exc_info=True)
        return False, None, None
    finally:
        session.close()


def consume_token(token):
    """Consume (mark as used) a magic link token.
    
    Args:
        token (str): The token to consume
        
    Returns:
        tuple: (success, user) where:
            - success (bool): True if token was successfully consumed
            - user (User): The user associated with the token (if successful)
    """
    session = Session()
    try:
        # Validate the token first
        is_valid, user, magic_link = validate_token(token)
        
        if not is_valid:
            return False, None
            
        # Mark the magic link as used
        magic_link_obj = session.query(MagicLink).filter_by(token=token).first()
        magic_link_obj.mark_as_used()
        session.commit()
        
        logger.info(f"Token consumed successfully for user: {user.email}")
        return True, user
        
    except Exception as e:
        logger.error(f"Error consuming token {token}: {str(e)}", exc_info=True)
        session.rollback()
        return False, None
    finally:
        session.close()

