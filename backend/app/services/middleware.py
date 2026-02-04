"""Сервис для работы с middleware."""

from uuid import UUID

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.middleware import Middleware
from app.schemas.middleware import MiddlewareCreate, MiddlewareUpdate


class MiddlewareService:
    """Сервис для операций с middleware."""

    def __init__(self, db: AsyncSession) -> None:
        """Инициализация сервиса.

        Args:
            db: Асинхронная сессия БД
        """
        self.db = db

    async def create(self, data: MiddlewareCreate) -> Middleware:
        """Создание нового middleware.

        Args:
            data: Данные для создания

        Returns:
            Созданный middleware
        """
        middleware = Middleware(
            name=data.name,
            display_name=data.display_name,
            description=data.description,
            middleware_type=data.middleware_type,
            is_active=data.is_active,
            order=data.order,
            config=data.config,
        )
        self.db.add(middleware)
        await self.db.commit()
        await self.db.refresh(middleware)
        return middleware

    async def get(self, middleware_id: UUID) -> Middleware | None:
        """Получение middleware по ID.

        Args:
            middleware_id: ID middleware

        Returns:
            Middleware или None если не найден
        """
        result = await self.db.execute(
            select(Middleware).where(Middleware.id == middleware_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Middleware | None:
        """Получение middleware по имени.

        Args:
            name: Имя middleware

        Returns:
            Middleware или None если не найден
        """
        result = await self.db.execute(
            select(Middleware).where(Middleware.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Middleware]:
        """Получение всех middleware.

        Returns:
            Список всех middleware
        """
        result = await self.db.execute(
            select(Middleware).order_by(Middleware.order)
        )
        return list(result.scalars().all())

    async def list_active(self) -> list[Middleware]:
        """Получение активных middleware.

        Returns:
            Список активных middleware в порядке выполнения
        """
        result = await self.db.execute(
            select(Middleware)
            .where(Middleware.is_active == True)
            .order_by(Middleware.order)
        )
        return list(result.scalars().all())

    async def update(
        self,
        middleware_id: UUID,
        data: MiddlewareUpdate,
    ) -> Middleware | None:
        """Обновление middleware.

        Args:
            middleware_id: ID middleware
            data: Данные для обновления

        Returns:
            Обновлённый middleware или None если не найден
        """
        middleware = await self.get(middleware_id)
        if middleware is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(middleware, field, value)

        await self.db.commit()
        await self.db.refresh(middleware)
        return middleware

    async def delete(self, middleware_id: UUID) -> bool:
        """Удаление middleware.

        Args:
            middleware_id: ID middleware

        Returns:
            True если удалён, False если не найден
        """
        middleware = await self.get(middleware_id)
        if middleware is None:
            return False

        await self.db.delete(middleware)
        await self.db.commit()
        return True

    async def toggle(self, middleware_id: UUID, is_active: bool) -> Middleware | None:
        """Переключение активности middleware.

        Args:
            middleware_id: ID middleware
            is_active: Новое состояние

        Returns:
            Обновлённый middleware или None если не найден
        """
        middleware = await self.get(middleware_id)
        if middleware is None:
            return None

        middleware.is_active = is_active
        await self.db.commit()
        await self.db.refresh(middleware)
        return middleware

    async def reorder(self, middleware_ids: list[UUID]) -> list[Middleware]:
        """Изменение порядка middleware.

        Args:
            middleware_ids: Список ID в новом порядке

        Returns:
            Список обновлённых middleware
        """
        for order, middleware_id in enumerate(middleware_ids):
            await self.db.execute(
                update(Middleware)
                .where(Middleware.id == middleware_id)
                .values(order=order)
            )

        await self.db.commit()
        return await self.list_all()

    async def name_exists(self, name: str, exclude_id: UUID | None = None) -> bool:
        """Проверка существования middleware с таким именем.

        Args:
            name: Имя для проверки
            exclude_id: ID для исключения (при обновлении)

        Returns:
            True если имя занято
        """
        query = select(func.count(Middleware.id)).where(Middleware.name == name)
        if exclude_id:
            query = query.where(Middleware.id != exclude_id)

        result = await self.db.execute(query)
        count = result.scalar() or 0
        return count > 0
