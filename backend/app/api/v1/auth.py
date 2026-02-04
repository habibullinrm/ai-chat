"""Эндпоинты аутентификации."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Регистрация нового пользователя.

    Args:
        user_data: Данные для регистрации
        db: Сессия БД

    Returns:
        Созданный пользователь

    Raises:
        HTTPException: Если email уже занят
    """
    auth_service = AuthService(db)

    if await auth_service.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    return await auth_service.create_user(user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="Авторизация",
)
async def login(
    credentials: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Авторизация пользователя.

    Args:
        credentials: Учётные данные
        db: Сессия БД

    Returns:
        Access и refresh токены

    Raises:
        HTTPException: Если учётные данные неверны
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        credentials.email,
        credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход",
)
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Выход из системы.

    Note:
        В текущей реализации JWT токены stateless,
        поэтому logout просто подтверждает валидность токена.
        Для полноценного logout нужно добавить blacklist токенов в Redis.
    """
    # TODO: Добавить токен в blacklist в Redis
    pass


@router.post(
    "/refresh",
    response_model=Token,
    summary="Обновление токена",
)
async def refresh_token(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Обновление access токена с помощью refresh токена.

    Args:
        refresh_token: Refresh токен
        db: Сессия БД

    Returns:
        Новая пара токенов

    Raises:
        HTTPException: Если refresh токен невалидный
    """
    token_data = decode_token(refresh_token)

    if token_data is None or token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from app.services.user import UserService

    user_service = UserService(db)
    user = await user_service.get_user(token_data.sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Текущий пользователь",
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Получение информации о текущем пользователе.

    Args:
        current_user: Текущий авторизованный пользователь

    Returns:
        Данные пользователя
    """
    return current_user