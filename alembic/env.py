import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from backend.src.db.database import Base  # Импорт твоих моделей
from backend.src.core.config import settings  # Импорт настроек

# Чтение конфигурации из alembic.ini
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Настройка логгирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей
target_metadata = Base.metadata

# Создание асинхронного движка
connectable = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

def run_migrations_offline() -> None:
    """Запуск миграций в оффлайн-режиме (без подключения к базе)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме (асинхронно)"""
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    """Функция для выполнения миграций в синхронном контексте"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations():
    """Обёртка для запуска миграций"""
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())

# Запуск миграций
run_migrations()