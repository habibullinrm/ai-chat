"""Logger middleware — логирование сообщений и ответов."""

import logging
from typing import Any

from app.middleware.base import (
    BaseMiddleware,
    MiddlewareAction,
    MiddlewareContext,
    MiddlewareResult,
    MiddlewareType,
)


class LoggerMiddleware(BaseMiddleware):
    """Middleware для логирования сообщений и ответов."""

    name = "logger"
    description = "Логирование входящих сообщений и ответов LLM"
    middleware_type = MiddlewareType.BOTH

    CONFIG_SCHEMA = {
        "log_level": {
            "type": "string",
            "enum": ["DEBUG", "INFO", "WARNING"],
            "default": "INFO",
            "description": "Уровень логирования",
        },
        "include_content": {
            "type": "boolean",
            "default": True,
            "description": "Включать содержимое сообщений в лог",
        },
        "max_content_length": {
            "type": "integer",
            "default": 200,
            "description": "Максимальная длина контента в логе",
        },
    }

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        log_level = self.config.get("log_level", "INFO")
        self.logger = logging.getLogger("middleware.logger")
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))

    async def pre_process(self, context: MiddlewareContext) -> MiddlewareResult:
        """Логирование входящего сообщения."""
        include_content = self.config.get("include_content", True)
        max_length = self.config.get("max_content_length", 200)

        log_data = {
            "user_id": str(context.user_id),
            "conversation_id": str(context.conversation_id) if context.conversation_id else None,
            "provider": context.provider,
            "model": context.model,
        }

        if include_content:
            content = context.message
            if len(content) > max_length:
                content = content[:max_length] + "..."
            log_data["message"] = content

        self.logger.info(f"[PRE] Входящее сообщение: {log_data}")

        return MiddlewareResult(action=MiddlewareAction.CONTINUE, context=context)

    async def post_process(
        self,
        context: MiddlewareContext,
        response: str,
    ) -> MiddlewareResult:
        """Логирование ответа LLM."""
        include_content = self.config.get("include_content", True)
        max_length = self.config.get("max_content_length", 200)

        log_data = {
            "user_id": str(context.user_id),
            "conversation_id": str(context.conversation_id) if context.conversation_id else None,
            "response_length": len(response),
        }

        if include_content:
            content = response
            if len(content) > max_length:
                content = content[:max_length] + "..."
            log_data["response"] = content

        self.logger.info(f"[POST] Ответ LLM: {log_data}")

        return MiddlewareResult(action=MiddlewareAction.CONTINUE, response=response)
