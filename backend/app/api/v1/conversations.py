"""Эндпоинты для работы с диалогами."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.chat import MessageResponse
from app.schemas.common import PaginatedResponse
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    ConversationWithMessages,
)
from app.services.conversation import ConversationService

router = APIRouter()


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание диалога",
)
async def create_conversation(
    data: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationResponse:
    """Создание нового диалога.

    Args:
        data: Данные для создания
        current_user: Текущий пользователь
        db: Сессия БД

    Returns:
        Созданный диалог
    """
    service = ConversationService(db)
    conversation = await service.create(current_user.id, data)
    return ConversationResponse.model_validate(conversation)


@router.get(
    "",
    response_model=PaginatedResponse[ConversationResponse],
    summary="Список диалогов",
)
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[ConversationResponse]:
    """Получение списка диалогов текущего пользователя.

    Args:
        current_user: Текущий пользователь
        db: Сессия БД
        page: Номер страницы
        per_page: Количество на странице

    Returns:
        Пагинированный список диалогов
    """
    service = ConversationService(db)
    conversations, total = await service.list_user_conversations(
        current_user.id,
        page,
        per_page,
    )

    return PaginatedResponse(
        items=[ConversationResponse.model_validate(c) for c in conversations],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationWithMessages,
    summary="Получение диалога",
)
async def get_conversation(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationWithMessages:
    """Получение диалога с сообщениями.

    Args:
        conversation_id: ID диалога
        current_user: Текущий пользователь
        db: Сессия БД

    Returns:
        Диалог с сообщениями

    Raises:
        HTTPException: Если диалог не найден
    """
    service = ConversationService(db)
    conversation = await service.get_user_conversation(
        conversation_id,
        current_user.id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Диалог не найден",
        )

    # Загружаем сообщения
    messages = await service.get_messages(conversation_id)

    return ConversationWithMessages(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        provider=conversation.provider,
        model=conversation.model,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[MessageResponse.model_validate(m) for m in messages],
    )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    summary="Обновление диалога",
)
async def update_conversation(
    conversation_id: UUID,
    data: ConversationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationResponse:
    """Обновление диалога.

    Args:
        conversation_id: ID диалога
        data: Данные для обновления
        current_user: Текущий пользователь
        db: Сессия БД

    Returns:
        Обновлённый диалог

    Raises:
        HTTPException: Если диалог не найден
    """
    service = ConversationService(db)
    conversation = await service.update(
        conversation_id,
        current_user.id,
        data,
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Диалог не найден",
        )

    return ConversationResponse.model_validate(conversation)


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление диалога",
)
async def delete_conversation(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Удаление диалога.

    Args:
        conversation_id: ID диалога
        current_user: Текущий пользователь
        db: Сессия БД

    Raises:
        HTTPException: Если диалог не найден
    """
    service = ConversationService(db)
    deleted = await service.delete(conversation_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Диалог не найден",
        )


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
    summary="Сообщения диалога",
)
async def get_conversation_messages(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=100),
) -> list[MessageResponse]:
    """Получение сообщений диалога.

    Args:
        conversation_id: ID диалога
        current_user: Текущий пользователь
        db: Сессия БД
        limit: Максимальное количество сообщений

    Returns:
        Список сообщений

    Raises:
        HTTPException: Если диалог не найден
    """
    service = ConversationService(db)

    # Проверяем доступ к диалогу
    conversation = await service.get_user_conversation(
        conversation_id,
        current_user.id,
    )
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Диалог не найден",
        )

    messages = await service.get_messages(conversation_id, limit)
    return [MessageResponse.model_validate(m) for m in messages]
