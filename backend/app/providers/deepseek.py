"""DeepSeek LLM провайдер."""

import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.providers.base import BaseLLMProvider, ChatCompletionResult
from app.schemas.chat import (
    ChatMessageInput,
    ChatParameters,
    UsageInfo,
    StreamChunk,
)
from app.schemas.provider import ModelInfo


class DeepSeekError(Exception):
    """Исключение для ошибок DeepSeek API."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DeepSeekProvider(BaseLLMProvider):
    """Провайдер для DeepSeek API.

    DeepSeek API совместим с OpenAI API, поэтому используем
    тот же формат запросов/ответов.
    """

    provider_id = "deepseek"
    provider_name = "DeepSeek"
    provider_description = "DeepSeek AI — мощные языковые модели"

    DEFAULT_BASE_URL = "https://api.deepseek.com"

    MODELS = [
        ModelInfo(
            id="deepseek-chat",
            name="DeepSeek Chat",
            description="Универсальная модель для диалогов",
            max_tokens=8192,
            supports_streaming=True,
        ),
        ModelInfo(
            id="deepseek-coder",
            name="DeepSeek Coder",
            description="Специализированная модель для кода",
            max_tokens=16384,
            supports_streaming=True,
        ),
    ]

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        """Инициализация DeepSeek провайдера.

        Args:
            api_key: API ключ DeepSeek
            base_url: Базовый URL (по умолчанию api.deepseek.com)
            timeout: Таймаут запросов в секундах
            max_retries: Количество повторных попыток при ошибках
        """
        super().__init__(api_key, base_url or self.DEFAULT_BASE_URL)
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Получение HTTP клиента (ленивая инициализация)."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def close(self) -> None:
        """Закрытие HTTP клиента."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _prepare_messages(
        self,
        messages: list[ChatMessageInput],
    ) -> list[dict[str, str]]:
        """Подготовка сообщений для API.

        Args:
            messages: Список сообщений

        Returns:
            Сообщения в формате OpenAI API
        """
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]

    def _prepare_request_body(
        self,
        messages: list[ChatMessageInput],
        model: str,
        parameters: ChatParameters,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Подготовка тела запроса.

        Args:
            messages: Список сообщений
            model: ID модели
            parameters: Параметры генерации
            stream: Флаг стриминга

        Returns:
            Тело запроса
        """
        body: dict[str, Any] = {
            "model": model,
            "messages": self._prepare_messages(messages),
            "temperature": parameters.temperature,
            "max_tokens": parameters.max_tokens,
            "top_p": parameters.top_p,
            "frequency_penalty": parameters.frequency_penalty,
            "presence_penalty": parameters.presence_penalty,
            "stream": stream,
        }

        if parameters.stop:
            body["stop"] = parameters.stop

        return body

    async def _make_request(
        self,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Выполнение HTTP запроса с retry логикой.

        Args:
            body: Тело запроса

        Returns:
            Ответ API

        Raises:
            DeepSeekError: При ошибке API
        """
        client = await self._get_client()
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                response = await client.post("/v1/chat/completions", json=body)

                if response.status_code == 200:
                    return response.json()

                # Retry для 5xx ошибок и 429 (rate limit)
                if response.status_code in (429, 500, 502, 503, 504):
                    last_error = DeepSeekError(
                        f"API error: {response.text}",
                        response.status_code,
                    )
                    continue

                # Не retry для других ошибок
                error_data = response.json()
                raise DeepSeekError(
                    error_data.get("error", {}).get("message", "Unknown error"),
                    response.status_code,
                )

            except httpx.RequestError as e:
                last_error = DeepSeekError(f"Request error: {str(e)}")

        raise last_error or DeepSeekError("Max retries exceeded")

    async def chat_completion(
        self,
        messages: list[ChatMessageInput],
        model: str,
        parameters: ChatParameters,
    ) -> ChatCompletionResult:
        """Генерация ответа на сообщения.

        Args:
            messages: Список сообщений диалога
            model: ID модели
            parameters: Параметры генерации

        Returns:
            Результат генерации
        """
        body = self._prepare_request_body(messages, model, parameters, stream=False)
        response = await self._make_request(body)

        choice = response["choices"][0]
        usage_data = response["usage"]

        return ChatCompletionResult(
            content=choice["message"]["content"],
            usage=UsageInfo(
                prompt_tokens=usage_data["prompt_tokens"],
                completion_tokens=usage_data["completion_tokens"],
                total_tokens=usage_data["total_tokens"],
            ),
            finish_reason=choice.get("finish_reason", "stop"),
            raw_response=response,
        )

    async def chat_completion_stream(
        self,
        messages: list[ChatMessageInput],
        model: str,
        parameters: ChatParameters,
    ) -> AsyncIterator[StreamChunk]:
        """Потоковая генерация ответа.

        Args:
            messages: Список сообщений диалога
            model: ID модели
            parameters: Параметры генерации

        Yields:
            Чанки ответа
        """
        body = self._prepare_request_body(messages, model, parameters, stream=True)
        client = await self._get_client()

        async with client.stream("POST", "/v1/chat/completions", json=body) as response:
            if response.status_code != 200:
                text = await response.aread()
                raise DeepSeekError(f"Stream error: {text}", response.status_code)

            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue

                data = line[6:]  # Убираем "data: "

                if data == "[DONE]":
                    break

                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    finish_reason = chunk["choices"][0].get("finish_reason")

                    if content or finish_reason:
                        yield StreamChunk(delta=content, finish_reason=finish_reason)

                except json.JSONDecodeError:
                    continue

    def get_models(self) -> list[ModelInfo]:
        """Получение списка доступных моделей."""
        return self.MODELS.copy()

    async def health_check(self) -> tuple[bool, int | None, str | None]:
        """Проверка доступности провайдера.

        Returns:
            Кортеж (доступен, latency_ms, ошибка)
        """
        if not self.api_key:
            return (False, None, "API ключ не настроен")

        try:
            client = await self._get_client()
            start = time.monotonic()

            # Минимальный запрос для проверки
            response = await client.post(
                "/v1/chat/completions",
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 1,
                },
            )

            latency = int((time.monotonic() - start) * 1000)

            if response.status_code == 200:
                return (True, latency, None)
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                return (False, latency, error_msg)

        except httpx.RequestError as e:
            return (False, None, str(e))
