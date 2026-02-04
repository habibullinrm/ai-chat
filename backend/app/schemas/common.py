"""Общие схемы."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой."""

    detail: str
    code: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Схема пагинированного ответа."""

    items: list[T]
    total: int
    page: int
    per_page: int

    @property
    def pages(self) -> int:
        """Общее количество страниц."""
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_next(self) -> bool:
        """Есть ли следующая страница."""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Есть ли предыдущая страница."""
        return self.page > 1