"""Сервис для работы с пользователями."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserUpdate


class UserService:
    """Сервис для операций с пользователями."""

    def __init__(self, db: AsyncSession) -> None:
        """Инициализация сервиса.

        Args:
            db: Асинхронная сессия БД
        """
        self.db = db

    async def get_user(self, user_id: UUID) -> User | None:
        """Получение пользователя по ID.

        Args:
            user_id: ID пользователя

        Returns:
            Пользователь или None если не найден
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate,
    ) -> User | None:
        """Обновление данных пользователя.

        Args:
            user_id: ID пользователя
            user_data: Данные для обновления

        Returns:
            Обновлённый пользователь или None если не найден
        """
        user = await self.get_user(user_id)
        if user is None:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        """Удаление пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            True если пользователь удалён, False если не найден
        """
        user = await self.get_user(user_id)
        if user is None:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True