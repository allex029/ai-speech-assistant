"""SpeakFlow FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.database.database import close_db, connect_db
from app.middleware.exception_handler import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.services.groq_service import get_groq_service
from app.utils.logger import setup_logging

logger = setup_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info(
        "Starting %s v%s [%s]",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    await connect_db()
    yield
    await get_groq_service().close()
    await close_db()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production-ready backend for SpeakFlow — "
            "an AI English Speaking Coach."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(application)

    application.include_router(api_router, prefix=settings.api_prefix)

    return application


app = create_app()
