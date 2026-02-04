"""Схемы для работы с пользователями."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Схема для создания пользователя."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Схема для авторизации."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя."""

    id: UUID
    email: EmailStr
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Схема для обновления пользователя."""

    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=100)