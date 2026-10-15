import os
import re

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from models import AuditLog, SecurityEvent, Ticket

load_dotenv()


_EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE
)

_PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"
)

_SECRET_PATTERN = re.compile(
    r"(?i)\b(api[_ -]?key|password|secret|token)"
    r"\b\s*[:=]\s*[^\s,;]+"
)


def sanitize_sensitive_text(text: str) -> str:
    sanitized = text

    for variable_name in (
        "APP_API_KEY",
        "ADMIN_API_KEY",
        "DATABASE_URL",
        "DB_PASSWORD",
        "MYSQL_PASSWORD"
    ):
        secret_value = os.getenv(variable_name)

        if secret_value:
            sanitized = sanitized.replace(
                secret_value,
                "[REDACTED]"
            )

    sanitized = _SECRET_PATTERN.sub(
        "[REDACTED]",
        sanitized
    )

    sanitized = _EMAIL_PATTERN.sub(
        "[EMAIL_REDACTED]",
        sanitized
    )

    sanitized = _PHONE_PATTERN.sub(
        "[PHONE_REDACTED]",
        sanitized
    )

    return sanitized

def create_support_ticket(
    db: Session,
    student_id: int,
    description: str
) -> Ticket:
    ticket = Ticket(
        student_id=student_id,
        title="Student support request",
        description=description,
        status="open"
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def record_audit_log(
    db: Session,
    student_id: int,
    action: str,
    message: str
) -> None:
    audit_log = AuditLog(
        student_id=student_id,
        action=action,
        message=sanitize_sensitive_text(message)
    )

    db.add(audit_log)
    db.commit()
    

def record_security_event(
    db: Session,
    student_id: int,
    event_type: str,
    description: str,
    severity: str = "medium"
) -> SecurityEvent:
    security_event = SecurityEvent(
        student_id=student_id,
        event_type=event_type,
        description=sanitize_sensitive_text(
            description
        ),
        severity=severity,
        status="open"
    )

    db.add(security_event)
    db.commit()
    db.refresh(security_event)

    return security_event