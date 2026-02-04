"""Схемы для работы с чатом."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.message import MessageRole


class ChatMessageInput(BaseModel):
    """Входное сообщение для чата."""

    role: MessageRole
    content: str


class ChatParameters(BaseModel):
    """Параметры генерации ответа."""

    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=16384)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stop: list[str] | None = None


class ChatCompletionRequest(BaseModel):
    """Запрос на генерацию ответа."""

    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=32000)
    provider: str = Field(default="deepseek")
    model: str = Field(default="deepseek-chat")
    parameters: ChatParameters = Field(default_factory=ChatParameters)
    system_prompt: str | None = None


class UsageInfo(BaseModel):
    """Информация об использовании токенов."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """Ответ на запрос чата."""

    conversation_id: UUID
    message_id: UUID
    content: str
    role: MessageRole = MessageRole.ASSISTANT
    usage: UsageInfo
    finish_reason: str = "stop"
    created_at: datetime

    model_config = {"from_attributes": True}


class StreamChunk(BaseModel):
    """Чанк для стриминга."""

    delta: str
    finish_reason: str | None = None


class MessageResponse(BaseModel):
    """Схема ответа с сообщением."""

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    tokens_used: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
