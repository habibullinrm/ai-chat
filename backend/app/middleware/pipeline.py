"""Pipeline для обработки сообщений через middleware."""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.base import (
    BaseMiddleware,
    MiddlewareAction,
    MiddlewareContext,
    MiddlewareResult,
    MiddlewareType,
)

logger = logging.getLogger(__name__)


class MiddlewarePipeline:
    """Pipeline для последовательной обработки через middleware."""

    def __init__(self, db: AsyncSession) -> None:
        """Инициализация pipeline.

        Args:
            db: Сессия БД
        """
        self.db = db
        self._middlewares: list[BaseMiddleware] = []
        self._loaded = False

    async def load_middlewares(self) -> None:
        """Загрузка активных middleware из БД."""
        from app.models.middleware import Middleware as MiddlewareModel
        from app.middleware import get_middleware_class

        result = await self.db.execute(
            select(MiddlewareModel)
            .where(MiddlewareModel.is_active == True)
            .order_by(MiddlewareModel.order)
        )
        middleware_records = result.scalars().all()

        self._middlewares = []
        for record in middleware_records:
            try:
                middleware_class = get_middleware_class(record.name)
                if middleware_class:
                    instance = middleware_class(config=record.config or {})
                    self._middlewares.append(instance)
            except Exception as e:
                logger.error(f"Ошибка загрузки middleware '{record.name}': {e}")

        self._loaded = True

    async def run_pre_process(
        self,
        context: MiddlewareContext,
    ) -> MiddlewareResult:
        """Выполнение pre-process цепочки.

        Args:
            context: Контекст запроса

        Returns:
            Финальный результат обработки
        """
        if not self._loaded:
            await self.load_middlewares()

        current_context = context

        for middleware in self._middlewares:
            if middleware.middleware_type not in (MiddlewareType.PRE, MiddlewareType.BOTH):
                continue

            try:
                result = await middleware.pre_process(current_context)

                if result.action == MiddlewareAction.BLOCK:
                    logger.info(
                        f"Middleware '{middleware.name}' заблокировал запрос: {result.error}"
                    )
                    return MiddlewareResult(
                        action=MiddlewareAction.BLOCK,
                        context=current_context,
                        error=result.error or "Запрос заблокирован",
                    )

                if result.action == MiddlewareAction.STOP:
                    logger.info(f"Middleware '{middleware.name}' остановил цепочку")
                    return MiddlewareResult(
                        action=MiddlewareAction.CONTINUE,
                        context=result.context or current_context,
                    )

                if result.context:
                    current_context = result.context

            except Exception as e:
                logger.error(f"Ошибка в middleware '{middleware.name}' pre_process: {e}")
                # Продолжаем выполнение при ошибке

        return MiddlewareResult(
            action=MiddlewareAction.CONTINUE,
            context=current_context,
        )

    async def run_post_process(
        self,
        context: MiddlewareContext,
        response: str,
    ) -> MiddlewareResult:
        """Выполнение post-process цепочки.

        Args:
            context: Контекст запроса
            response: Ответ от LLM

        Returns:
            Финальный результат обработки
        """
        if not self._loaded:
            await self.load_middlewares()

        current_response = response

        # Post-process в обратном порядке
        for middleware in reversed(self._middlewares):
            if middleware.middleware_type not in (MiddlewareType.POST, MiddlewareType.BOTH):
                continue

            try:
                result = await middleware.post_process(context, current_response)

                if result.action == MiddlewareAction.BLOCK:
                    logger.info(
                        f"Middleware '{middleware.name}' заблокировал ответ: {result.error}"
                    )
                    return MiddlewareResult(
                        action=MiddlewareAction.BLOCK,
                        response=current_response,
                        error=result.error or "Ответ заблокирован",
                    )

                if result.action == MiddlewareAction.STOP:
                    logger.info(f"Middleware '{middleware.name}' остановил цепочку")
                    return MiddlewareResult(
                        action=MiddlewareAction.CONTINUE,
                        response=result.response or current_response,
                    )

                if result.response:
                    current_response = result.response

            except Exception as e:
                logger.error(f"Ошибка в middleware '{middleware.name}' post_process: {e}")
                # Продолжаем выполнение при ошибке

        return MiddlewareResult(
            action=MiddlewareAction.CONTINUE,
            response=current_response,
        )

    def create_context(
        self,
        user_id: UUID,
        message: str,
        provider: str,
        model: str,
        conversation_id: UUID | None = None,
        parameters: dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> MiddlewareContext:
        """Создание контекста для pipeline.

        Args:
            user_id: ID пользователя
            message: Сообщение пользователя
            provider: ID провайдера
            model: ID модели
            conversation_id: ID диалога
            parameters: Параметры генерации
            system_prompt: Системный промпт

        Returns:
            Контекст middleware
        """
        return MiddlewareContext(
            user_id=user_id,
            conversation_id=conversation_id,
            message=message,
            provider=provider,
            model=model,
            parameters=parameters or {},
            system_prompt=system_prompt,
        )
