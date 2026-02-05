"""Сервис для работы с диалогами."""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class ConversationService:
    """Сервис для операций с диалогами."""

    def __init__(self, db: AsyncSession) -> None:
        """Инициализация сервиса.

        Args:
            db: Асинхронная сессия БД
        """
        self.db = db

    async def create(
        self,
        user_id: UUID,
        data: ConversationCreate,
    ) -> Conversation:
        """Создание нового диалога.

        Args:
            user_id: ID пользователя
            data: Данные для создания

        Returns:
            Созданный диалог
        """
        conversation = Conversation(
            user_id=user_id,
            title=data.title,
            provider=data.provider,
            model=data.model,
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get(self, conversation_id: UUID) -> Conversation | None:
        """Получение диалога по ID.

        Args:
            conversation_id: ID диалога

        Returns:
            Диалог или None если не найден
        """
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_with_messages(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        """Получение диалога с сообщениями.

        Args:
            conversation_id: ID диалога

        Returns:
            Диалог с загруженными сообщениями или None
        """
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()

    async def get_user_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Conversation | None:
        """Получение диалога пользователя по ID.

        Args:
            conversation_id: ID диалога
            user_id: ID пользователя

        Returns:
            Диалог или None если не найден/не принадлежит пользователю
        """
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_user_conversations(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Conversation], int]:
        """Получение списка диалогов пользователя.

        Args:
            user_id: ID пользователя
            page: Номер страницы
            per_page: Количество на странице

        Returns:
            Кортеж (список диалогов, общее количество)
        """
        # Подсчёт общего количества
        count_result = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.user_id == user_id
            )
        )
        total = count_result.scalar() or 0

        # Получение страницы
        offset = (page - 1) * per_page
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        conversations = list(result.scalars().all())

        return conversations, total

    async def update(
        self,
        conversation_id: UUID,
        user_id: UUID,
        data: ConversationUpdate,
    ) -> Conversation | None:
        """Обновление диалога.

        Args:
            conversation_id: ID диалога
            user_id: ID пользователя
            data: Данные для обновления

        Returns:
            Обновлённый диалог или None если не найден
        """
        conversation = await self.get_user_conversation(conversation_id, user_id)
        if conversation is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(conversation, field, value)

        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def delete(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Удаление диалога.

        Args:
            conversation_id: ID диалога
            user_id: ID пользователя

        Returns:
            True если диалог удалён, False если не найден
        """
        conversation = await self.get_user_conversation(conversation_id, user_id)
        if conversation is None:
            return False

        await self.db.delete(conversation)
        await self.db.commit()
        return True

    async def get_messages(
        self,
        conversation_id: UUID,
        limit: int | None = None,
    ) -> list[Message]:
        """Получение сообщений диалога.

        Args:
            conversation_id: ID диалога
            limit: Максимальное количество сообщений

        Returns:
            Список сообщений в хронологическом порядке
        """
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )

        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def clear_messages(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Удаление всех сообщений диалога.

        Args:
            conversation_id: ID диалога
            user_id: ID пользователя (для проверки прав)

        Returns:
            True если сообщения удалены, False если диалог не найден
        """
        # Проверяем права на диалог
        conversation = await self.get_user_conversation(conversation_id, user_id)
        if conversation is None:
            return False

        # Удаляем все сообщения
        messages = await self.get_messages(conversation_id)
        for message in messages:
            await self.db.delete(message)

        await self.db.commit()
        return True
