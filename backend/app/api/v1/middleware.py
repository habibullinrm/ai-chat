"""Эндпоинты для работы с middleware."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_admin
from app.models.user import User
from app.middleware import list_builtin_middlewares, get_middleware_class
from app.schemas.middleware import (
    MiddlewareCreate,
    MiddlewareUpdate,
    MiddlewareResponse,
    MiddlewareToggle,
    MiddlewareReorder,
    MiddlewareInfo,
)
from app.services.middleware import MiddlewareService

router = APIRouter()


@router.get(
    "",
    response_model=list[MiddlewareResponse],
    summary="Список всех middleware",
)
async def list_middlewares(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MiddlewareResponse]:
    """Получение списка всех middleware (только для админов).

    Returns:
        Список всех middleware
    """
    service = MiddlewareService(db)
    middlewares = await service.list_all()
    return [MiddlewareResponse.model_validate(m) for m in middlewares]


@router.get(
    "/active",
    response_model=list[MiddlewareResponse],
    summary="Список активных middleware",
)
async def list_active_middlewares(
    _: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MiddlewareResponse]:
    """Получение списка активных middleware.

    Returns:
        Список активных middleware
    """
    service = MiddlewareService(db)
    middlewares = await service.list_active()
    return [MiddlewareResponse.model_validate(m) for m in middlewares]


@router.get(
    "/builtin",
    response_model=list[MiddlewareInfo],
    summary="Список встроенных middleware",
)
async def list_builtin(
    _: Annotated[User, Depends(require_admin)],
) -> list[MiddlewareInfo]:
    """Получение списка встроенных middleware (только для админов).

    Returns:
        Список информации о встроенных middleware
    """
    builtin = list_builtin_middlewares()
    return [MiddlewareInfo(**m) for m in builtin]


@router.post(
    "",
    response_model=MiddlewareResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание middleware",
)
async def create_middleware(
    data: MiddlewareCreate,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MiddlewareResponse:
    """Создание нового middleware (только для админов).

    Args:
        data: Данные для создания

    Returns:
        Созданный middleware
    """
    # Проверяем, что это встроенный middleware
    if get_middleware_class(data.name) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Middleware '{data.name}' не найден в реестре",
        )

    service = MiddlewareService(db)

    # Проверяем уникальность имени
    if await service.name_exists(data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Middleware с именем '{data.name}' уже существует",
        )

    middleware = await service.create(data)
    return MiddlewareResponse.model_validate(middleware)


@router.get(
    "/{middleware_id}",
    response_model=MiddlewareResponse,
    summary="Получение middleware",
)
async def get_middleware(
    middleware_id: UUID,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MiddlewareResponse:
    """Получение middleware по ID (только для админов).

    Args:
        middleware_id: ID middleware

    Returns:
        Middleware

    Raises:
        HTTPException: Если не найден
    """
    service = MiddlewareService(db)
    middleware = await service.get(middleware_id)

    if middleware is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Middleware не найден",
        )

    return MiddlewareResponse.model_validate(middleware)


@router.put(
    "/{middleware_id}",
    response_model=MiddlewareResponse,
    summary="Обновление middleware",
)
async def update_middleware(
    middleware_id: UUID,
    data: MiddlewareUpdate,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MiddlewareResponse:
    """Обновление middleware (только для админов).

    Args:
        middleware_id: ID middleware
        data: Данные для обновления

    Returns:
        Обновлённый middleware

    Raises:
        HTTPException: Если не найден
    """
    service = MiddlewareService(db)
    middleware = await service.update(middleware_id, data)

    if middleware is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Middleware не найден",
        )

    return MiddlewareResponse.model_validate(middleware)


@router.delete(
    "/{middleware_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление middleware",
)
async def delete_middleware(
    middleware_id: UUID,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Удаление middleware (только для админов).

    Args:
        middleware_id: ID middleware

    Raises:
        HTTPException: Если не найден
    """
    service = MiddlewareService(db)
    deleted = await service.delete(middleware_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Middleware не найден",
        )


@router.patch(
    "/{middleware_id}/toggle",
    response_model=MiddlewareResponse,
    summary="Переключение middleware",
)
async def toggle_middleware(
    middleware_id: UUID,
    data: MiddlewareToggle,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MiddlewareResponse:
    """Включение/выключение middleware (только для админов).

    Args:
        middleware_id: ID middleware
        data: Новое состояние

    Returns:
        Обновлённый middleware

    Raises:
        HTTPException: Если не найден
    """
    service = MiddlewareService(db)
    middleware = await service.toggle(middleware_id, data.is_active)

    if middleware is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Middleware не найден",
        )

    return MiddlewareResponse.model_validate(middleware)


@router.put(
    "/order",
    response_model=list[MiddlewareResponse],
    summary="Изменение порядка middleware",
)
async def reorder_middlewares(
    data: MiddlewareReorder,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MiddlewareResponse]:
    """Изменение порядка выполнения middleware (только для админов).

    Args:
        data: Новый порядок ID

    Returns:
        Список middleware в новом порядке
    """
    service = MiddlewareService(db)
    middlewares = await service.reorder(data.middleware_ids)
    return [MiddlewareResponse.model_validate(m) for m in middlewares]
