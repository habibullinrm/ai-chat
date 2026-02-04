"""Реестр LLM провайдеров."""

from typing import Type

from app.config import get_settings
from app.providers.base import BaseLLMProvider
from app.providers.deepseek import DeepSeekProvider
from app.schemas.provider import ProviderInfo, ProviderStatus


# Реестр доступных провайдеров
_PROVIDERS: dict[str, Type[BaseLLMProvider]] = {
    "deepseek": DeepSeekProvider,
}

# Кэш инициализированных провайдеров
_provider_instances: dict[str, BaseLLMProvider] = {}


def get_provider(provider_id: str) -> BaseLLMProvider:
    """Получение экземпляра провайдера по ID.

    Args:
        provider_id: Идентификатор провайдера (deepseek, openai, anthropic)

    Returns:
        Инициализированный провайдер

    Raises:
        ValueError: Если провайдер не найден или не настроен
    """
    if provider_id in _provider_instances:
        return _provider_instances[provider_id]

    if provider_id not in _PROVIDERS:
        raise ValueError(f"Провайдер '{provider_id}' не найден")

    settings = get_settings()

    # Получаем API ключ для провайдера
    api_key_map = {
        "deepseek": settings.deepseek_api_key,
        "openai": settings.openai_api_key,
        "anthropic": settings.anthropic_api_key,
    }

    api_key = api_key_map.get(provider_id, "")
    if not api_key:
        raise ValueError(f"API ключ для провайдера '{provider_id}' не настроен")

    provider_class = _PROVIDERS[provider_id]
    provider = provider_class(api_key=api_key)

    _provider_instances[provider_id] = provider
    return provider


def list_providers() -> list[ProviderInfo]:
    """Получение списка всех доступных провайдеров.

    Returns:
        Список информации о провайдерах
    """
    settings = get_settings()
    providers = []

    api_key_map = {
        "deepseek": settings.deepseek_api_key,
        "openai": settings.openai_api_key,
        "anthropic": settings.anthropic_api_key,
    }

    for provider_id, provider_class in _PROVIDERS.items():
        api_key = api_key_map.get(provider_id, "")

        # Создаём временный экземпляр для получения метаданных
        temp_provider = provider_class(api_key=api_key or "dummy")
        info = temp_provider.get_provider_info()
        info.is_available = bool(api_key)

        providers.append(info)

    return providers


async def check_provider_status(provider_id: str) -> ProviderStatus:
    """Проверка статуса провайдера.

    Args:
        provider_id: Идентификатор провайдера

    Returns:
        Статус провайдера
    """
    try:
        provider = get_provider(provider_id)
        is_available, latency_ms, error = await provider.health_check()

        return ProviderStatus(
            provider_id=provider_id,
            is_available=is_available,
            latency_ms=latency_ms,
            error=error,
        )
    except ValueError as e:
        return ProviderStatus(
            provider_id=provider_id,
            is_available=False,
            error=str(e),
        )


def register_provider(provider_id: str, provider_class: Type[BaseLLMProvider]) -> None:
    """Регистрация нового провайдера.

    Args:
        provider_id: Уникальный идентификатор провайдера
        provider_class: Класс провайдера
    """
    _PROVIDERS[provider_id] = provider_class


async def close_all_providers() -> None:
    """Закрытие всех инициализированных провайдеров."""
    for provider in _provider_instances.values():
        await provider.close()
    _provider_instances.clear()
