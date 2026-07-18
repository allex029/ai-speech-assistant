"""Chat / coaching conversation routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ConversationRole
from app.database.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llama_service import LlamaService, get_llama_service
from app.services.session_service import SessionService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    llama: LlamaService = Depends(get_llama_service),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Generate an AI coaching response from a speech transcript.

    Uses Llama 3 via Groq. Optionally attaches multi-turn history
    when `session_id` is provided.
    """
    history = None
    session_service = SessionService(db)

    if payload.session_id:
        history = await session_service.get_conversation_history(payload.session_id)
        await session_service.save_conversation_turn(
            role=ConversationRole.USER.value,
            content=payload.transcript,
            session_id=payload.session_id,
        )

    result = await llama.generate_response(
        payload.transcript,
        system_prompt=payload.system_prompt,
        history=history,
    )

    if payload.session_id:
        await session_service.save_conversation_turn(
            role=ConversationRole.ASSISTANT.value,
            content=result.response,
            session_id=payload.session_id,
            model_used=result.model_used,
            latency_ms=result.latency_ms,
        )
        result.session_id = payload.session_id

    return result
