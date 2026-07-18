"""Global exception handlers for meaningful HTTP responses."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.services.groq_service import GroqAPIError
from app.services.session_service import SessionNotFoundError
from app.utils.audio import AudioValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AudioValidationError)
    async def audio_validation_handler(
        request: Request,
        exc: AudioValidationError,
    ) -> JSONResponse:
        logger.warning("Audio validation failed: %s", exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error_code": "audio_validation_error"},
        )

    @app.exception_handler(GroqAPIError)
    async def groq_error_handler(
        request: Request,
        exc: GroqAPIError,
    ) -> JSONResponse:
        logger.error("Groq error: %s | details=%s", exc.message, exc.details)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_code": "groq_api_error",
            },
        )

    @app.exception_handler(SessionNotFoundError)
    async def session_not_found_handler(
        request: Request,
        exc: SessionNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "detail": str(exc),
                "error_code": "session_not_found",
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning("Validation error: %s", exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "error_code": "validation_error",
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(
        request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        logger.exception("Database error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "A database error occurred. Please try again later.",
                "error_code": "database_error",
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": "http_error",
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected error occurred.",
                "error_code": "internal_server_error",
            },
        )
