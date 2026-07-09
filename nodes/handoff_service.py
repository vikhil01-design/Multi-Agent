import os
import logging
import smtplib
import datetime
import secrets
from email.mime.text import MIMEText
from typing import Optional
from dotenv import load_dotenv
from state import InvestmentState

load_dotenv()

logger = logging.getLogger(__name__)


def get_email_config() -> dict:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_from = os.getenv("EMAIL_FROM") or os.getenv("APPLICATION_EMAIL")
    email_to = os.getenv("EMAIL_TO") or os.getenv("SUPPORT_EMAIL")
    return {
        "smtp_host": smtp_host,
        "smtp_port": smtp_port,
        "smtp_username": smtp_username,
        "smtp_password": smtp_password,
        "email_from": email_from,
        "email_to": email_to,
    }


def generate_handoff_reference_id(now: Optional[datetime.datetime] = None) -> str:
    """Generate a unique handoff reference ID."""
    now = now or datetime.datetime.now(datetime.UTC)
    return f"HO-{now.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(3).upper()}"


def send_handoff_email(state: InvestmentState):
    """Send a human handoff email when the workflow needs review."""

    config = get_email_config()
    smtp_host = config["smtp_host"]
    smtp_port = config["smtp_port"]
    smtp_username = config["smtp_username"]
    smtp_password = config["smtp_password"]
    email_from = config["email_from"]
    email_to = config["email_to"]

    if not all([smtp_host, smtp_username, smtp_password, email_from, email_to]):
        logger.warning("Email settings missing. Cannot send handoff email.")
        return

    subject = f"[HUMAN HANDOFF] Ref {state.get('humanHandOffRef', 'N/A')}"
    body = f"""
A human handoff has been triggered.
user_prompt: {state.get('user_prompt', '')}
crew_response: {state.get('crew_response', '')}
retries: {state.get('retries', 0)}
"""

    msg = MIMEText(body)
    msg["From"] = email_from
    msg["To"] = email_to
    msg["Subject"] = subject

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(email_from, email_to, msg.as_string())
        logger.info("Human handoff email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send handoff email: {e}")
