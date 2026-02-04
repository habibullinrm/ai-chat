"""Сервис аутентификации."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    """Сервис для операций аутентификации."""

    def __init__(self, db: AsyncSession) -> None:
        """Инициализация сервиса.

        Args:
            db: Асинхронная сессия БД
        """
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя.

        Args:
            user_data: Данные для создания пользователя

        Returns:
            Созданный пользователь
        """
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User | None:
        """Аутентификация пользователя.

        Args:
            email: Email пользователя
            password: Пароль

        Returns:
            Пользователь или None если аутентификация не удалась
        """
        user = await self.get_user_by_email(email)
        if user is None:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Получение пользователя по email.

        Args:
            email: Email пользователя

        Returns:
            Пользователь или None если не найден
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Проверка существования email.

        Args:
            email: Email для проверки

        Returns:
            True если email уже занят
        """
        user = await self.get_user_by_email(email)
        return user is not None