"""Схемы для провайдеров LLM."""

from pydantic import BaseModel


class ModelInfo(BaseModel):
    """Информация о модели."""

    id: str
    name: str
    description: str | None = None
    max_tokens: int = 4096
    supports_streaming: bool = True


class ProviderInfo(BaseModel):
    """Информация о провайдере."""

    id: str
    name: str
    description: str | None = None
    models: list[ModelInfo] = []
    is_available: bool = True


class ProviderStatus(BaseModel):
    """Статус доступности провайдера."""

    provider_id: str
    is_available: bool
    latency_ms: int | None = None
    error: str | None = None


class ProvidersListResponse(BaseModel):
    """Список провайдеров."""

    providers: list[ProviderInfo]
