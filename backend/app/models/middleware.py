"""Модель middleware."""

from sqlalchemy import String, Text, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDMixin, TimestampMixin


class Middleware(Base, UUIDMixin, TimestampMixin):
    """Модель middleware в БД."""

    __tablename__ = "middlewares"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    middleware_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="both",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        index=True,
    )
    config: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )

    def __repr__(self) -> str:
        status = "active" if self.is_active else "inactive"
        return f"<Middleware {self.name} [{status}] order={self.order}>"
