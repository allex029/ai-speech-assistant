"""Chat / conversation schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    transcript: str = Field(..., min_length=1, description="User speech transcript")
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session to attach conversation history",
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="Override the default speaking-coach system prompt",
    )


class ChatResponse(BaseModel):
    response: str
    model_used: Optional[str] = None
    latency_ms: Optional[float] = None
    session_id: Optional[str] = None


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: Optional[str] = None
    role: str
    content: str
    model_used: Optional[str] = None
    created_at: Optional[datetime] = None
