"""Эндпоинты для работы с чатом."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from app.services.chat import ChatService, MiddlewareBlockedError

router = APIRouter()


@router.post(
    "/completions",
    response_model=ChatCompletionResponse,
    summary="Отправка сообщения",
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatCompletionResponse:
    """Отправка сообщения и получение ответа от LLM.

    Args:
        request: Данные запроса (сообщение, провайдер, параметры)
        current_user: Текущий пользователь
        db: Сессия БД

    Returns:
        Ответ от LLM с метаданными

    Raises:
        HTTPException: При ошибке провайдера, диалога или блокировке middleware
    """
    service = ChatService(db)

    try:
        return await service.send_message(current_user.id, request)
    except MiddlewareBlockedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e.message),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка провайдера: {str(e)}",
        )
