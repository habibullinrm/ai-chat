"""Сервис для работы с чатом."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.base import MiddlewareAction
from app.middleware.pipeline import MiddlewarePipeline
from app.models.message import Message, MessageRole
from app.providers import get_provider
from app.providers.base import ChatCompletionResult
from app.schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessageInput,
)
from app.schemas.conversation import ConversationCreate
from app.services.conversation import ConversationService


class MiddlewareBlockedError(Exception):
    """Исключение при блокировке middleware."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ChatService:
    """Сервис для операций чата."""

    def __init__(self, db: AsyncSession) -> None:
        """Инициализация сервиса.

        Args:
            db: Асинхронная сессия БД
        """
        self.db = db
        self.conversation_service = ConversationService(db)
        self.pipeline = MiddlewarePipeline(db)

    async def send_message(
        self,
        user_id: UUID,
        request: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        """Отправка сообщения и получение ответа от LLM.

        Args:
            user_id: ID пользователя
            request: Запрос на генерацию

        Returns:
            Ответ от LLM

        Raises:
            ValueError: Если диалог не найден или не принадлежит пользователю
            MiddlewareBlockedError: Если сообщение заблокировано middleware
        """
        # 1. Получаем или создаём диалог
        if request.conversation_id:
            conversation = await self.conversation_service.get_user_conversation(
                request.conversation_id,
                user_id,
            )
            if conversation is None:
                raise ValueError("Диалог не найден")
        else:
            # Создаём новый диалог
            conversation = await self.conversation_service.create(
                user_id,
                ConversationCreate(
                    title=self._generate_title(request.message),
                    provider=request.provider,
                    model=request.model,
                ),
            )

        # 2. Создаём контекст middleware
        context = self.pipeline.create_context(
            user_id=user_id,
            message=request.message,
            provider=request.provider,
            model=request.model,
            conversation_id=conversation.id,
            parameters=request.parameters.model_dump(),
            system_prompt=request.system_prompt,
        )

        # 3. Выполняем pre-process middleware
        pre_result = await self.pipeline.run_pre_process(context)

        if pre_result.action == MiddlewareAction.BLOCK:
            raise MiddlewareBlockedError(pre_result.error or "Запрос заблокирован")

        # Обновляем контекст после middleware
        if pre_result.context:
            context = pre_result.context

        # 4. Загружаем историю сообщений
        history = await self.conversation_service.get_messages(
            conversation.id,
            limit=50,
        )

        # 5. Формируем список сообщений для LLM
        messages: list[ChatMessageInput] = []

        # Добавляем системный промпт (может быть изменён middleware)
        if context.system_prompt:
            messages.append(ChatMessageInput(
                role=MessageRole.SYSTEM,
                content=context.system_prompt,
            ))

        # Добавляем историю
        for msg in history:
            messages.append(ChatMessageInput(
                role=msg.role,
                content=msg.content,
            ))

        # Добавляем текущее сообщение (может быть изменено middleware)
        messages.append(ChatMessageInput(
            role=MessageRole.USER,
            content=context.message,
        ))

        # 6. Сохраняем сообщение пользователя
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=context.message,
        )
        self.db.add(user_message)

        # 7. Получаем ответ от провайдера
        provider = get_provider(context.provider)
        result: ChatCompletionResult = await provider.chat_completion(
            messages=messages,
            model=context.model,
            parameters=request.parameters,
        )

        # 8. Выполняем post-process middleware
        post_result = await self.pipeline.run_post_process(context, result.content)

        if post_result.action == MiddlewareAction.BLOCK:
            raise MiddlewareBlockedError(post_result.error or "Ответ заблокирован")

        # Используем обработанный ответ
        final_content = post_result.response or result.content

        # 9. Сохраняем ответ ассистента
        assistant_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=final_content,
            tokens_used=result.usage.total_tokens,
        )
        self.db.add(assistant_message)

        # 10. Коммитим изменения
        await self.db.commit()
        await self.db.refresh(assistant_message)

        return ChatCompletionResponse(
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            content=final_content,
            role=MessageRole.ASSISTANT,
            usage=result.usage,
            finish_reason=result.finish_reason,
            created_at=assistant_message.created_at,
        )

    def _generate_title(self, message: str, max_length: int = 50) -> str:
        """Генерация заголовка диалога из первого сообщения.

        Args:
            message: Первое сообщение
            max_length: Максимальная длина заголовка

        Returns:
            Заголовок диалога
        """
        title = message.strip()

        # Ищем конец первого предложения
        for sep in [". ", "? ", "! ", "\n"]:
            if sep in title:
                title = title.split(sep)[0] + sep.strip()
                break

        if len(title) > max_length:
            title = title[:max_length - 3] + "..."

        return title or "Новый диалог"
