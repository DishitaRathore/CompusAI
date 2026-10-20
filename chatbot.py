from email.mime import message

from sqlalchemy import select
from sqlalchemy.orm import Session

from text_normalizer import normalize_query
from intent_classifier import classify_intent
from llm import generate_answer
from models import Attendance, ChatMessage, Fee
from rag import get_relevant_context
from tools import (
    create_support_ticket,
    record_audit_log,
    record_security_event
)

import re


def get_small_talk_response(message: str):
    text = re.sub(
        r"\s+",
        " ",
        message.lower().strip()
    )

    if re.fullmatch(
        r"(hi|hello|hey|hii|helo|good morning|good afternoon|good evening)",
        text
    ):
        return "Hello! How can I help you today?"

    if text in {
        "how are you",
        "how are you doing",
        "how is it going"
    }:
        return "I'm doing well! I can help with attendance, fees, policies, support tickets, cybersecurity, and chat history."

    if text in {
        "who are you",
        "what are you",
        "what is your name"
    }:
        return "I am CampusFlow AI, a student support and cybersecurity assistant."

    if text in {
        "what can you do",
        "how can you help",
        "help"
    }:
        return (
            "I can help you with attendance, fee status, college policies, "
            "support tickets, cybersecurity guidance, security reports, "
            "and previous chat messages."
        )

    if text in {
        "thanks",
        "thank you",
        "thankyou",
        "thx"
    }:
        return "You're welcome! Let me know if you need anything else."

    if text in {
        "bye",
        "goodbye",
        "see you",
        "see you later"
    }:
        return "Goodbye! Have a great day."

    return None

def read_attendance(db: Session, student_id: int) -> str:
    records = db.scalars(
        select(Attendance).where(
            Attendance.student_id == student_id
        )
    ).all()

    if not records:
        answer = "No attendance records were found."
    else:
        lines = []

        for record in records:
            percentage = 0

            if record.total != 0:
                percentage = (
                    record.attended / record.total
                ) * 100

            lines.append(
                f"- {record.subject}: "
                f"{record.attended}/{record.total} classes "
                f"({percentage:.1f}%)"
            )

        answer = "Your attendance:\n" + "\n".join(lines)

    record_audit_log(
        db=db,
        student_id=student_id,
        action="read_attendance",
        message="Student attendance was requested"
    )

    return answer


def read_fee_status(db: Session, student_id: int) -> str:
    fee = db.scalar(
        select(Fee).where(
            Fee.student_id == student_id
        )
    )

    if fee is None:
        answer = "No fee record was found."
    else:
        answer = (
            f"Total fee: ₹{fee.total_fee:.2f}\n"
            f"Paid: ₹{fee.paid:.2f}\n"
            f"Remaining: ₹{fee.remaining:.2f}"
        )

    record_audit_log(
        db=db,
        student_id=student_id,
        action="read_fee_status",
        message="Student fee status was requested"
    )

    return answer

def read_chat_history(
    db: Session,
    student_id: int,
    limit: int = 10
) -> str:
    messages = db.scalars(
        select(ChatMessage)
        .where(
            ChatMessage.student_id == student_id
        )
        .order_by(
            ChatMessage.created_at.desc()
        )
        .limit(limit)
    ).all()

    messages = list(reversed(messages))

    if not messages:
        answer = "No conversation history was found."
    else:
        lines = []

        for message in messages:
            role = message.role.capitalize()

            lines.append(
                f"{role}: {message.content}"
            )

        answer = (
            "Recent conversation:\n"
            + "\n".join(lines)
        )

    record_audit_log(
        db=db,
        student_id=student_id,
        action="read_chat_history",
        message="Student conversation history was requested"
    )

    return answer

def create_ticket_from_message(
    db: Session,
    student_id: int,
    message: str
) -> str:
    if ":" in message:
        description = message.split(":", 1)[1].strip()
    else:
        description = message

    ticket = create_support_ticket(
        db=db,
        student_id=student_id,
        description=description
    )

    record_audit_log(
        db=db,
        student_id=student_id,
        action="create_ticket",
        message=f"Support ticket #{ticket.id} was created"
    )

    return (
        f"Your support ticket was created successfully. "
        f"Ticket ID: {ticket.id}"
    )


def answer_from_knowledge_base(
    db: Session,
    student_id: int,
    message: str
) -> str:
    context = get_relevant_context(
        query=message,
        top_k=1
    )

    source = context.split("\n", 1)[0]

    try:
        answer = generate_answer(
            question=message,
            context=context
        )

        action = "rag_llm_answer"

    except Exception as error:
        answer = (
            "The language model is temporarily unavailable. "
            "Here is the relevant information:\n\n"
            f"{context}"
        )

        action = "llm_fallback"

        print(
            f"LLM error: {type(error).__name__}"
        )

    record_audit_log(
        db=db,
        student_id=student_id,
        action=action,
        message="The chatbot processed a knowledge-base question"
    )

    return f"{answer}\n\n{source}"

def generate_reply(
    
    message: str,
    student_id: int,
    db: Session
) -> dict:
    text = message.lower().strip()

    small_talk_response = get_small_talk_response(message)

    if small_talk_response:
        record_audit_log(
            db=db,
            student_id=student_id,
            action="small_talk",
            message="Small-talk response generated"
        )

        return {
            "answer": small_talk_response,
            "mode": "small_talk"
        }

    routing_message = normalize_query(message)

    # Use the corrected text for keyword fallback conditions
    text = routing_message.lower().strip()

    intent, confidence = classify_intent(
        routing_message,
        threshold=0.60
    )
    classifier_active = confidence >= 0.60

    print(
        f"Intent: {intent}, "
        f"Confidence: {confidence:.2f}"
    )

    record_audit_log(
        db=db,
        student_id=student_id,
        action="intent_classification",
        message=(
            f"Predicted intent={intent}; "
            f"confidence={confidence:.3f}; "
            f"classifier_active={classifier_active}"
        )
    )

    ticket_keywords = (
        "create ticket",
        "raise ticket",
        "open ticket",
        "report issue",
        "complaint",
        "support ticket",
        "support request",
        "help desk",
        "student support",
        "service request",
        "technical help",
        "contact support"
    )

    if (
        intent == "create_ticket"
        or (
            not classifier_active
            and any(
                keyword in text
                for keyword in ticket_keywords
            )
        )
    ):
        answer = create_ticket_from_message(
            db=db,
            student_id=student_id,
            message=message
        )

        return {
            "answer": answer,
            "mode": "ticket"
        }

    security_terms = (
        "phishing",
        "suspicious link",
        "suspicious email",
        "hacked",
        "malware",
        "scam",
        "unauthorized access"
    )

    incident_terms = (
        "i received",
        "i got",
        "i clicked",
        "report",
        "hacked",
        "unauthorized access",
        "malware",
        "scam"
    )

    is_security_incident = (
        intent == "security_report"
        or (
            any(term in text for term in security_terms)
            and any(term in text for term in incident_terms)
        )
    )

    if is_security_incident:
        if (
            "phishing" in text
            or "suspicious link" in text
        ):
            event_type = "phishing_report"
            severity = "high"
        else:
            event_type = "security_report"
            severity = "medium"

        event = record_security_event(
            db=db,
            student_id=student_id,
            event_type=event_type,
            description=message,
            severity=severity
        )

        record_audit_log(
            db=db,
            student_id=student_id,
            action="security_event_created",
            message=f"Security event #{event.id} was created"
        )

        answer = (
            f"Your security report has been recorded. "
            f"Event ID: {event.id}. "
            f"Please contact your institution's IT support team."
        )

        return {
            "answer": answer,
            "mode": "security_event"
        }

    rag_keywords = (
        "policy",
        "policies",
        "guideline",
        "guidelines",
        "requirement",
        "minimum",
        "rule",
        "phishing",
        "suspicious link",
        "password",
        "one-time password",
        "otp"
    )

    if (
        intent == "policy_question"
        or (
            not classifier_active
            and any(
                keyword in text
                for keyword in rag_keywords
            )
        )
    ):
        answer = answer_from_knowledge_base(
            db=db,
            student_id=student_id,
            message=message
        )

        return {
            "answer": answer,
            "mode": "rag_llm"
        }

    if (
        intent == "attendance_query"
        or (
            not classifier_active
            and "attendance" in text
        )
    ):
        answer = read_attendance(
            db=db,
            student_id=student_id
        )

        return {
            "answer": answer,
            "mode": "attendance"
        }

    if (
        intent == "fee_query"
        or (
            not classifier_active
            and (
                "fee" in text
                or "fees" in text
            )
        )
    ):
        answer = read_fee_status(
            db=db,
            student_id=student_id
        )

        return {
            "answer": answer,
            "mode": "fees"
        }

    if (
        intent == "security_guidance"
        or (
            not classifier_active
            and (
                "security" in text
                or "password" in text
            )
        )
    ):
        answer = (
            "Never share your password or click unknown links. "
            "If you received a suspicious message, report it immediately."
        )

        record_audit_log(
            db=db,
            student_id=student_id,
            action="security_guidance",
            message="General security guidance was requested"
        )

        return {
            "answer": answer,
            "mode": "security_guidance"
        }

    chat_history_keywords = (
        "chat history",
        "conversation history",
        "previous messages",
        "previous chat",
        "past chats",
        "earlier messages",
        "previous conversation",
        "old messages"
    )

    if (
        intent == "chat_history"
        or any(
            keyword in text
            for keyword in chat_history_keywords
        )
    ):
        answer = read_chat_history(
            db=db,
            student_id=student_id
        )

        return {
            "answer": answer,
            "mode": "chat_history"
        }

    answer = (
        "I can currently help with attendance, fee status, "
        "security guidance, support tickets, and college policies."
    )

    record_audit_log(
        db=db,
        student_id=student_id,
        action="unknown_question",
        message="The chatbot received an unsupported question"
    )

    return {
        "answer": answer,
        "mode": "fallback"
    }