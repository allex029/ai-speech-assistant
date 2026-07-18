"""Request logging middleware — method, path, status, duration."""

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logger import get_logger

logger = get_logger("speakflow.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        started = time.perf_counter()
        path = request.url.path
        method = request.method

        logger.info("→ %s %s", method, path)

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.exception(
                "✗ %s %s failed after %.1fms",
                method,
                path,
                elapsed_ms,
            )
            raise

        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "← %s %s %s %.1fms",
            method,
            path,
            response.status_code,
            elapsed_ms,
        )
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
        return response
