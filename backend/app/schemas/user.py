"""User-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=150)


class UserCreate(UserBase):
    password: Optional[str] = Field(default=None, min_length=8)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    is_anonymous: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
