"""Rate limiting с использованием Redis."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
import redis.asyncio as redis

from app.config import get_settings
from app.models.user import UserRole

settings = get_settings()

# Лимиты запросов в минуту по ролям
RATE_LIMITS: dict[UserRole, int] = {
    UserRole.GUEST: 10,
    UserRole.USER: 60,
    UserRole.ADMIN: 0,  # 0 = без лимита
}


class RateLimiter:
    """Rate limiter с использованием Redis."""

    def __init__(self) -> None:
        """Инициализация подключения к Redis."""
        self._redis: redis.Redis | None = None

    async def get_redis(self) -> redis.Redis:
        """Получение подключения к Redis."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def close(self) -> None:
        """Закрытие подключения к Redis."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int = 60,
    ) -> tuple[bool, int]:
        """Проверка, разрешён ли запрос.

        Args:
            key: Ключ для идентификации клиента
            limit: Максимальное количество запросов
            window: Временное окно в секундах

        Returns:
            Tuple (разрешено, оставшееся количество запросов)
        """
        if limit == 0:  # Без лимита
            return True, -1

        r = await self.get_redis()
        pipe = r.pipeline()

        # Используем INCR с TTL для простого скользящего окна
        pipe.incr(key)
        pipe.expire(key, window)

        results = await pipe.execute()
        current = results[0]
        remaining = max(0, limit - current)

        return current <= limit, remaining

    async def check_rate_limit(
        self,
        request: Request,
        role: UserRole,
        user_id: str | None = None,
    ) -> None:
        """Проверка rate limit и выброс исключения при превышении.

        Args:
            request: FastAPI request
            role: Роль пользователя
            user_id: ID пользователя (если авторизован)

        Raises:
            HTTPException: При превышении лимита
        """
        limit = RATE_LIMITS.get(role, RATE_LIMITS[UserRole.GUEST])

        if limit == 0:  # Без лимита для админов
            return

        # Ключ: user_id или IP адрес
        identifier = user_id or request.client.host if request.client else "unknown"
        key = f"rate_limit:{role.value}:{identifier}"

        allowed, remaining = await self.is_allowed(key, limit)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Превышен лимит запросов. Попробуйте позже.",
                headers={"Retry-After": "60"},
            )


# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter()


async def get_rate_limiter() -> RateLimiter:
    """Dependency для получения rate limiter."""
    return rate_limiter


def rate_limit(role: UserRole | None = None):
    """Фабрика dependency для rate limiting.

    Args:
        role: Роль для определения лимита (если None, используется роль из токена)

    Returns:
        Dependency функция
    """

    async def rate_limit_checker(
        request: Request,
        limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
    ) -> None:
        # Для неавторизованных запросов используем роль GUEST
        user_role = role or UserRole.GUEST
        await limiter.check_rate_limit(request, user_role)

    return rate_limit_checker