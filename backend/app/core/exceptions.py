"""Кастомные исключения приложения."""

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Базовое исключение приложения."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code


class CredentialsException(AppException):
    """Исключение при ошибке аутентификации (401)."""

    def __init__(
        self,
        detail: str = "Невалидные учётные данные",
        code: str = "INVALID_CREDENTIALS",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code=code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedException(AppException):
    """Исключение при отсутствии прав (403)."""

    def __init__(
        self,
        detail: str = "Недостаточно прав для выполнения операции",
        code: str = "PERMISSION_DENIED",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code=code,
        )


class NotFoundException(AppException):
    """Исключение когда ресурс не найден (404)."""

    def __init__(
        self,
        detail: str = "Ресурс не найден",
        code: str = "NOT_FOUND",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code=code,
        )


class ValidationException(AppException):
    """Исключение при ошибке валидации (422)."""

    def __init__(
        self,
        detail: str = "Ошибка валидации данных",
        code: str = "VALIDATION_ERROR",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code=code,
        )


class ConflictException(AppException):
    """Исключение при конфликте данных (409)."""

    def __init__(
        self,
        detail: str = "Конфликт данных",
        code: str = "CONFLICT",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            code=code,
        )


class RateLimitException(AppException):
    """Исключение при превышении лимита запросов (429)."""

    def __init__(
        self,
        detail: str = "Превышен лимит запросов",
        code: str = "RATE_LIMIT_EXCEEDED",
        retry_after: int = 60,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            code=code,
            headers={"Retry-After": str(retry_after)},
        )