"""Схемы для диалогов."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.chat import MessageResponse


class ConversationCreate(BaseModel):
    """Схема создания диалога."""

    title: str = Field(default="Новый диалог", max_length=255)
    provider: str = Field(default="deepseek")
    model: str = Field(default="deepseek-chat")


class ConversationUpdate(BaseModel):
    """Схема обновления диалога."""

    title: str | None = Field(default=None, max_length=255)


class ConversationResponse(BaseModel):
    """Схема ответа с диалогом."""

    id: UUID
    user_id: UUID
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationWithMessages(ConversationResponse):
    """Диалог с сообщениями."""

    messages: list[MessageResponse] = []
