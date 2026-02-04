"""Content Filter middleware — фильтрация контента."""

import re
from typing import Any

from app.middleware.base import (
    BaseMiddleware,
    MiddlewareAction,
    MiddlewareContext,
    MiddlewareResult,
    MiddlewareType,
)


class ContentFilterMiddleware(BaseMiddleware):
    """Middleware для фильтрации контента по ключевым словам."""

    name = "content_filter"
    description = "Фильтрация сообщений по запрещённым словам и паттернам"
    middleware_type = MiddlewareType.BOTH

    CONFIG_SCHEMA = {
        "blocked_words": {
            "type": "array",
            "items": {"type": "string"},
            "default": [],
            "description": "Список запрещённых слов",
        },
        "blocked_patterns": {
            "type": "array",
            "items": {"type": "string"},
            "default": [],
            "description": "Список запрещённых regex паттернов",
        },
        "action": {
            "type": "string",
            "enum": ["block", "warn", "replace"],
            "default": "block",
            "description": "Действие при обнаружении: block, warn, replace",
        },
        "replacement": {
            "type": "string",
            "default": "[FILTERED]",
            "description": "Текст замены (для action=replace)",
        },
        "case_sensitive": {
            "type": "boolean",
            "default": False,
            "description": "Учитывать регистр",
        },
        "check_response": {
            "type": "boolean",
            "default": True,
            "description": "Проверять ответы LLM",
        },
    }

    def _check_content(self, content: str) -> tuple[bool, str | None]:
        """Проверка контента на запрещённые слова/паттерны.

        Args:
            content: Текст для проверки

        Returns:
            Кортеж (найдено_совпадение, найденное_слово)
        """
        blocked_words = self.config.get("blocked_words", [])
        blocked_patterns = self.config.get("blocked_patterns", [])
        case_sensitive = self.config.get("case_sensitive", False)

        check_content = content if case_sensitive else content.lower()

        # Проверка слов
        for word in blocked_words:
            check_word = word if case_sensitive else word.lower()
            if check_word in check_content:
                return True, word

        # Проверка паттернов
        flags = 0 if case_sensitive else re.IGNORECASE
        for pattern in blocked_patterns:
            try:
                if re.search(pattern, content, flags):
                    return True, pattern
            except re.error:
                continue

        return False, None

    def _replace_content(self, content: str) -> str:
        """Замена запрещённого контента.

        Args:
            content: Исходный текст

        Returns:
            Текст с заменами
        """
        blocked_words = self.config.get("blocked_words", [])
        blocked_patterns = self.config.get("blocked_patterns", [])
        replacement = self.config.get("replacement", "[FILTERED]")
        case_sensitive = self.config.get("case_sensitive", False)

        result = content
        flags = 0 if case_sensitive else re.IGNORECASE

        # Замена слов
        for word in blocked_words:
            pattern = re.escape(word)
            result = re.sub(pattern, replacement, result, flags=flags)

        # Замена по паттернам
        for pattern in blocked_patterns:
            try:
                result = re.sub(pattern, replacement, result, flags=flags)
            except re.error:
                continue

        return result

    async def pre_process(self, context: MiddlewareContext) -> MiddlewareResult:
        """Фильтрация входящего сообщения."""
        action = self.config.get("action", "block")
        found, matched = self._check_content(context.message)

        if not found:
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, context=context)

        if action == "block":
            return MiddlewareResult(
                action=MiddlewareAction.BLOCK,
                context=context,
                error=f"Сообщение содержит запрещённый контент: {matched}",
            )

        if action == "replace":
            context.message = self._replace_content(context.message)
            context.modified = True
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, context=context)

        # action == "warn" — продолжаем, но добавляем метаданные
        context.metadata["content_filter_warning"] = f"Обнаружено: {matched}"
        return MiddlewareResult(action=MiddlewareAction.CONTINUE, context=context)

    async def post_process(
        self,
        context: MiddlewareContext,
        response: str,
    ) -> MiddlewareResult:
        """Фильтрация ответа LLM."""
        check_response = self.config.get("check_response", True)
        if not check_response:
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, response=response)

        action = self.config.get("action", "block")
        found, matched = self._check_content(response)

        if not found:
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, response=response)

        if action == "block":
            return MiddlewareResult(
                action=MiddlewareAction.BLOCK,
                response=response,
                error=f"Ответ содержит запрещённый контент: {matched}",
            )

        if action == "replace":
            filtered_response = self._replace_content(response)
            return MiddlewareResult(
                action=MiddlewareAction.CONTINUE,
                response=filtered_response,
            )

        # action == "warn" — продолжаем
        return MiddlewareResult(action=MiddlewareAction.CONTINUE, response=response)
