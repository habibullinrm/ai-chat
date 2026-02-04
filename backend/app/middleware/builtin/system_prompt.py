"""System Prompt middleware — добавление системного промпта."""

from typing import Any

from app.middleware.base import (
    BaseMiddleware,
    MiddlewareAction,
    MiddlewareContext,
    MiddlewareResult,
    MiddlewareType,
)


class SystemPromptMiddleware(BaseMiddleware):
    """Middleware для добавления системного промпта к запросам."""

    name = "system_prompt"
    description = "Добавление системного промпта к запросам LLM"
    middleware_type = MiddlewareType.PRE

    CONFIG_SCHEMA = {
        "prompt_template": {
            "type": "string",
            "default": "You are a helpful assistant.",
            "description": "Шаблон системного промпта",
        },
        "override_existing": {
            "type": "boolean",
            "default": False,
            "description": "Заменять существующий системный промпт",
        },
        "append_mode": {
            "type": "boolean",
            "default": False,
            "description": "Добавлять к существующему промпту",
        },
    }

    async def pre_process(self, context: MiddlewareContext) -> MiddlewareResult:
        """Добавление системного промпта."""
        prompt_template = self.config.get(
            "prompt_template",
            "You are a helpful assistant.",
        )
        override_existing = self.config.get("override_existing", False)
        append_mode = self.config.get("append_mode", False)

        # Определяем финальный системный промпт
        if context.system_prompt:
            if override_existing:
                context.system_prompt = prompt_template
            elif append_mode:
                context.system_prompt = f"{prompt_template}\n\n{context.system_prompt}"
            # Иначе оставляем как есть
        else:
            context.system_prompt = prompt_template

        context.modified = True

        return MiddlewareResult(action=MiddlewareAction.CONTINUE, context=context)

    async def post_process(
        self,
        context: MiddlewareContext,
        response: str,
    ) -> MiddlewareResult:
        """Post-process не используется."""
        return MiddlewareResult(action=MiddlewareAction.CONTINUE, response=response)
