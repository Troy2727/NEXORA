import smtplib
from email.message import EmailMessage

from settings import smtp_settings


def send_email(email: str, html_content: str, subject: str) -> None:
    """Send one HTML email through the configured SMTP server."""
    message = EmailMessage()
    message["From"] = smtp_settings.username
    message["To"] = email
    message["Subject"] = subject
    message.set_content(html_content, subtype="html")

    if smtp_settings.ssl:
        with smtplib.SMTP_SSL(smtp_settings.host, smtp_settings.port) as server:
            server.login(smtp_settings.username, smtp_settings.password)
            server.send_message(message)
    else:
        with smtplib.SMTP(smtp_settings.host, smtp_settings.port) as server:
            server.send_message(message)
