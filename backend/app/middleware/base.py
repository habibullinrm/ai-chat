"""Базовые классы для middleware системы."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID


class MiddlewareType(str, Enum):
    """Тип middleware."""

    PRE = "pre"
    POST = "post"
    BOTH = "both"


class MiddlewareAction(str, Enum):
    """Действие middleware."""

    CONTINUE = "continue"
    STOP = "stop"
    BLOCK = "block"


@dataclass
class MiddlewareContext:
    """Контекст для передачи между middleware."""

    user_id: UUID
    conversation_id: UUID | None
    message: str
    provider: str
    model: str
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    system_prompt: str | None = None

    # Флаги состояния
    blocked: bool = False
    block_reason: str | None = None
    modified: bool = False


@dataclass
class MiddlewareResult:
    """Результат выполнения middleware."""

    action: MiddlewareAction = MiddlewareAction.CONTINUE
    context: MiddlewareContext | None = None
    response: str | None = None
    error: str | None = None


class BaseMiddleware(ABC):
    """Абстрактный базовый класс для middleware."""

    name: str = ""
    description: str = ""
    middleware_type: MiddlewareType = MiddlewareType.BOTH

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Инициализация middleware.

        Args:
            config: Конфигурация middleware
        """
        self.config = config or {}

    @abstractmethod
    async def pre_process(self, context: MiddlewareContext) -> MiddlewareResult:
        """Обработка перед отправкой в LLM.

        Args:
            context: Контекст запроса

        Returns:
            Результат обработки
        """
        ...

    @abstractmethod
    async def post_process(
        self,
        context: MiddlewareContext,
        response: str,
    ) -> MiddlewareResult:
        """Обработка после получения ответа от LLM.

        Args:
            context: Контекст запроса
            response: Ответ от LLM

        Returns:
            Результат обработки
        """
        ...

    def validate_config(self) -> list[str]:
        """Валидация конфигурации.

        Returns:
            Список ошибок валидации (пустой если всё OK)
        """
        return []

    def get_info(self) -> dict[str, Any]:
        """Получение информации о middleware.

        Returns:
            Информация о middleware
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": self.middleware_type.value,
            "config": self.config,
        }
