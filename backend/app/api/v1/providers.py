"""Эндпоинты для работы с провайдерами LLM."""

from fastapi import APIRouter, HTTPException, status

from app.providers import get_provider, list_providers, check_provider_status
from app.schemas.provider import ProvidersListResponse, ProviderInfo, ModelInfo, ProviderStatus

router = APIRouter()


@router.get(
    "",
    response_model=ProvidersListResponse,
    summary="Список провайдеров",
)
async def get_providers() -> ProvidersListResponse:
    """Получение списка доступных LLM провайдеров.

    Returns:
        Список провайдеров с информацией о доступности
    """
    providers = list_providers()
    return ProvidersListResponse(providers=providers)


@router.get(
    "/{provider_id}",
    response_model=ProviderInfo,
    summary="Информация о провайдере",
)
async def get_provider_info(provider_id: str) -> ProviderInfo:
    """Получение информации о конкретном провайдере.

    Args:
        provider_id: Идентификатор провайдера

    Returns:
        Информация о провайдере и его моделях

    Raises:
        HTTPException: Если провайдер не найден
    """
    try:
        provider = get_provider(provider_id)
        return provider.get_provider_info()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{provider_id}/models",
    response_model=list[ModelInfo],
    summary="Модели провайдера",
)
async def get_provider_models(provider_id: str) -> list[ModelInfo]:
    """Получение списка моделей провайдера.

    Args:
        provider_id: Идентификатор провайдера

    Returns:
        Список доступных моделей

    Raises:
        HTTPException: Если провайдер не найден
    """
    try:
        provider = get_provider(provider_id)
        return provider.get_models()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{provider_id}/status",
    response_model=ProviderStatus,
    summary="Статус провайдера",
)
async def get_provider_status(provider_id: str) -> ProviderStatus:
    """Проверка статуса доступности провайдера.

    Args:
        provider_id: Идентификатор провайдера

    Returns:
        Статус провайдера с latency и ошибками
    """
    return await check_provider_status(provider_id)
