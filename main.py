from collections import defaultdict, deque
from math import ceil
from time import monotonic

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request
)
from sqlalchemy.orm import Session

from chatbot import generate_reply
from database import check_database_connection, get_db
from schemas import (
    ChatRequest,
    ChatResponse,
    SecurityEventStatusRequest
)
from models import AuditLog ,ChatMessage, SecurityEvent
from sqlalchemy import select
from auth import get_current_user, require_admin



app = FastAPI(
    title="CampusFlow AI",
    description="A secure education ERP assistant",
    version="0.1.0"
)
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60

request_history = defaultdict(deque)


def enforce_rate_limit(request: Request):
    api_key = request.headers.get(
        "x-api-key",
        ""
    )

    client_host = (
        request.client.host
        if request.client
        else "unknown"
    )

    rate_limit_key = api_key or client_host
    now = monotonic()

    timestamps = request_history[
        rate_limit_key
    ]

    while timestamps and (
        now - timestamps[0]
        >= RATE_LIMIT_WINDOW_SECONDS
    ):
        timestamps.popleft()

    if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
        retry_after = ceil(
            RATE_LIMIT_WINDOW_SECONDS
            - (now - timestamps[0])
        )

        raise HTTPException(
            status_code=429,
            detail=(
                "Too many requests. "
                "Please try again later."
            ),
            headers={
                "Retry-After": str(retry_after)
            }
        )

    timestamps.append(now)


@app.get("/")
def home():
    return {
        "message": "CampusFlow AI is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/database-health")
def database_health():
    try:
        check_database_connection()

        return {
            "status": "healthy",
            "database": "MySQL"
        }

    except Exception as error:
        return {
            "status": "unhealthy",
            "error": str(error)
        }


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(enforce_rate_limit)
):
    if (
        current_user["role"] == "student"
        and current_user["student_id"] != request.student_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Students can access only their own records"
        )
    user_message = ChatMessage(
        student_id=request.student_id,
        role="user",
        content=request.message
    )

    db.add(user_message)
    db.commit()

    result = generate_reply(
        message=request.message,
        student_id=request.student_id,
        db=db
    )

    answer = result["answer"]
    mode = result["mode"]

    assistant_message = ChatMessage(
        student_id=request.student_id,
        role="assistant",
        content=answer
    )

    db.add(assistant_message)
    db.commit()

    return {
        "answer": answer,
        "mode": mode
    }

@app.get("/chat-history/{student_id}")
def get_chat_history(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(enforce_rate_limit)
):
    if (
        current_user["role"] == "student"
        and current_user["student_id"] != student_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Students can access only their own history"
        )
    messages = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.student_id == student_id)
        .order_by(ChatMessage.created_at.asc())
    ).all()

    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at
        }
        for message in messages
    ]

@app.get("/security-events")
def get_security_events(
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    events = db.scalars(
        select(SecurityEvent)
        .order_by(SecurityEvent.created_at.desc())
    ).all()

    return [
        {
            "id": event.id,
            "student_id": event.student_id,
            "event_type": event.event_type,
            "description": event.description,
            "severity": event.severity,
            "status": event.status,
            "created_at": event.created_at
        }
        for event in events
    ]

@app.patch("/security-events/{event_id}/status")
def update_security_event_status(
    event_id: int,
    request: SecurityEventStatusRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    event = db.get(
        SecurityEvent,
        event_id
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Security event not found"
        )

    event.status = request.status

    db.commit()
    db.refresh(event)

    return {
        "message": "Security event status updated",
        "event_id": event.id,
        "status": event.status
    }

@app.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    _: bool = Depends(require_admin)
):
    logs = db.scalars(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
    ).all()

    return [
        {
            "id": log.id,
            "student_id": log.student_id,
            "action": log.action,
            "message": log.message,
            "created_at": log.created_at
        }
        for log in logs
    ]