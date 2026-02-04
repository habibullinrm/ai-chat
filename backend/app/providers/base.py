"""Базовый класс для LLM провайдеров."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from app.schemas.chat import ChatMessageInput, ChatParameters, UsageInfo, StreamChunk
from app.schemas.provider import ModelInfo, ProviderInfo


@dataclass
class ChatCompletionResult:
    """Результат генерации ответа."""

    content: str
    usage: UsageInfo
    finish_reason: str = "stop"
    raw_response: dict[str, Any] | None = None


class BaseLLMProvider(ABC):
    """Абстрактный базовый класс для LLM провайдеров."""

    provider_id: str = ""
    provider_name: str = ""
    provider_description: str | None = None

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        """Инициализация провайдера.

        Args:
            api_key: API ключ для провайдера
            base_url: Базовый URL API (опционально)
        """
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[ChatMessageInput],
        model: str,
        parameters: ChatParameters,
    ) -> ChatCompletionResult:
        """Генерация ответа на сообщения.

        Args:
            messages: Список сообщений диалога
            model: ID модели
            parameters: Параметры генерации

        Returns:
            Результат генерации
        """
        ...

    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: list[ChatMessageInput],
        model: str,
        parameters: ChatParameters,
    ) -> AsyncIterator[StreamChunk]:
        """Потоковая генерация ответа.

        Args:
            messages: Список сообщений диалога
            model: ID модели
            parameters: Параметры генерации

        Yields:
            Чанки ответа
        """
        ...

    @abstractmethod
    def get_models(self) -> list[ModelInfo]:
        """Получение списка доступных моделей.

        Returns:
            Список моделей провайдера
        """
        ...

    def get_provider_info(self) -> ProviderInfo:
        """Получение информации о провайдере.

        Returns:
            Метаданные провайдера
        """
        return ProviderInfo(
            id=self.provider_id,
            name=self.provider_name,
            description=self.provider_description,
            models=self.get_models(),
            is_available=bool(self.api_key),
        )

    async def health_check(self) -> tuple[bool, int | None, str | None]:
        """Проверка доступности провайдера.

        Returns:
            Кортеж (доступен, latency_ms, ошибка)
        """
        return (bool(self.api_key), None, None if self.api_key else "API ключ не настроен")

    async def close(self) -> None:
        """Закрытие соединений (переопределить при необходимости)."""
        pass
