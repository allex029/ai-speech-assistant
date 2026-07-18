"""Shared / health schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "running"


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
