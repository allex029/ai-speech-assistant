"""Aggregate API router."""

from fastapi import APIRouter

from app.api.routes import auth, chat, fluency, health, sessions, speech

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(speech.router)
api_router.include_router(chat.router)
api_router.include_router(fluency.router)
api_router.include_router(sessions.router)
