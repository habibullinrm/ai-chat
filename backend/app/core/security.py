"""Модуль безопасности: JWT токены и хеширование паролей."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings
from app.models.user import UserRole
from app.schemas.token import TokenPayload

settings = get_settings()

# Алгоритм JWT
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля.

    Args:
        plain_password: Открытый пароль
        hashed_password: Хешированный пароль

    Returns:
        True если пароль верный
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """Хеширование пароля.

    Args:
        password: Открытый пароль

    Returns:
        Хешированный пароль
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(user_id: UUID, role: UserRole) -> str:
    """Создание access токена.

    Args:
        user_id: ID пользователя
        role: Роль пользователя

    Returns:
        JWT access токен
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": str(user_id),
        "role": role.value,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(user_id: UUID, role: UserRole) -> str:
    """Создание refresh токена.

    Args:
        user_id: ID пользователя
        role: Роль пользователя

    Returns:
        JWT refresh токен
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload = {
        "sub": str(user_id),
        "role": role.value,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenPayload | None:
    """Декодирование JWT токена.

    Args:
        token: JWT токен

    Returns:
        Полезная нагрузка токена или None при ошибке
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return TokenPayload(
            sub=UUID(payload["sub"]),
            role=UserRole(payload["role"]),
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
            type=payload["type"],
        )
    except (JWTError, ValueError, KeyError):
        return None