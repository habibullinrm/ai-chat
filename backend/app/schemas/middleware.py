"""Схемы для middleware."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class MiddlewareCreate(BaseModel):
    """Схема создания middleware."""

    name: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    middleware_type: str = Field(default="both", pattern="^(pre|post|both)$")
    is_active: bool = False
    order: int = Field(default=0, ge=0)
    config: dict[str, Any] | None = None


class MiddlewareUpdate(BaseModel):
    """Схема обновления middleware."""

    display_name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    middleware_type: str | None = Field(default=None, pattern="^(pre|post|both)$")
    is_active: bool | None = None
    order: int | None = Field(default=None, ge=0)
    config: dict[str, Any] | None = None


class MiddlewareResponse(BaseModel):
    """Схема ответа с middleware."""

    id: UUID
    name: str
    display_name: str
    description: str | None
    middleware_type: str
    is_active: bool
    order: int
    config: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MiddlewareToggle(BaseModel):
    """Схема переключения активности."""

    is_active: bool


class MiddlewareReorder(BaseModel):
    """Схема изменения порядка."""

    middleware_ids: list[UUID] = Field(min_length=1)


class MiddlewareInfo(BaseModel):
    """Информация о встроенном middleware."""

    name: str
    description: str
    middleware_type: str
    config_schema: dict[str, Any] | None = None
