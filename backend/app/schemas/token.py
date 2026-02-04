"""Схемы для JWT токенов."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.user import UserRole


class Token(BaseModel):
    """Схема ответа с токенами."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Полезная нагрузка JWT токена."""

    sub: UUID  # ID пользователя
    role: UserRole
    exp: datetime
    type: str  # "access" или "refresh"