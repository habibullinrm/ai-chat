"""Конфигурация окружения Alembic для асинхронных миграций."""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.config import get_settings
from app.db.base import Base

# Импортируем все модели для автогенерации миграций
from app.models import user, conversation, message  # noqa: F401

# Объект конфигурации Alembic
config = context.config

# Настройка логирования из конфигурационного файла
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Получаем URL базы данных из настроек приложения
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# Метаданные моделей для автогенерации
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в offline режиме.

    Конфигурирует контекст только с URL, без создания Engine.
    Используется для генерации SQL скриптов без подключения к БД.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполнение миграций с переданным подключением."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Запуск асинхронных миграций."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в online режиме с асинхронным движком."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()