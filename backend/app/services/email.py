from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


@dataclass
class SentEmail:
    recipient: str
    subject: str
    body: str
    reset_token: str
    sent_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class EmailService:
    def send_password_reset_email(self, to_email: str, reset_token: str) -> None:
        raise NotImplementedError


class StubEmailService(EmailService):
    """Stub email service that logs and retains sent emails in memory for verification."""

    def __init__(self) -> None:
        self.sent_emails: list[SentEmail] = []

    def send_password_reset_email(self, to_email: str, reset_token: str) -> None:
        subject = "Reset your password - Dzielenie rachunków"
        body = f"Use this token to reset your password: {reset_token}"
        record = SentEmail(
            recipient=to_email,
            subject=subject,
            body=body,
            reset_token=reset_token,
        )
        self.sent_emails.append(record)
        logger.info("Stub email dispatched to %s with token: %s", to_email, reset_token)

    def clear(self) -> None:
        self.sent_emails.clear()


email_service = StubEmailService()