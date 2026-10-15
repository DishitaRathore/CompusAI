from pydantic import BaseModel, Field
from typing import Literal

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=500,
        description="The user's question"
    )

    student_id: int = Field(
        default=1,
        ge=1,
        description="The student's ID"
    )

class SecurityEventStatusRequest(BaseModel):
    status: Literal[
        "open",
        "investigating",
        "resolved"
    ]

class ChatResponse(BaseModel):
    answer: str
    mode: str

