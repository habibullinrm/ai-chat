"""Реестр middleware."""

from typing import Any, Type

from app.middleware.base import BaseMiddleware, MiddlewareType
from app.middleware.builtin import (
    LoggerMiddleware,
    SystemPromptMiddleware,
    ContentFilterMiddleware,
)


# Реестр встроенных middleware
_BUILTIN_MIDDLEWARES: dict[str, Type[BaseMiddleware]] = {
    "logger": LoggerMiddleware,
    "system_prompt": SystemPromptMiddleware,
    "content_filter": ContentFilterMiddleware,
}


def get_middleware_class(name: str) -> Type[BaseMiddleware] | None:
    """Получение класса middleware по имени.

    Args:
        name: Имя middleware

    Returns:
        Класс middleware или None если не найден
    """
    return _BUILTIN_MIDDLEWARES.get(name)


def create_middleware_instance(
    name: str,
    config: dict[str, Any] | None = None,
) -> BaseMiddleware | None:
    """Создание экземпляра middleware.

    Args:
        name: Имя middleware
        config: Конфигурация

    Returns:
        Экземпляр middleware или None если не найден
    """
    middleware_class = get_middleware_class(name)
    if middleware_class is None:
        return None
    return middleware_class(config=config)


def list_builtin_middlewares() -> list[dict[str, Any]]:
    """Получение списка встроенных middleware.

    Returns:
        Список информации о middleware
    """
    result = []
    for name, cls in _BUILTIN_MIDDLEWARES.items():
        config_schema = getattr(cls, "CONFIG_SCHEMA", None)
        result.append({
            "name": name,
            "description": cls.description,
            "middleware_type": cls.middleware_type.value,
            "config_schema": config_schema,
        })
    return result


def register_middleware(name: str, middleware_class: Type[BaseMiddleware]) -> None:
    """Регистрация нового middleware.

    Args:
        name: Уникальное имя middleware
        middleware_class: Класс middleware
    """
    _BUILTIN_MIDDLEWARES[name] = middleware_class
