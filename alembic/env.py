# alembic/env.py
import sys
import os
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.db.database import engine
from backend.src.db.base import Base

# Настройка логирования
config = context.config
fileConfig(config.config_file_name)

# Устанавливаем target_metadata
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Run migrations in 'online' mode."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        dialect_name="postgresql",
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' mode with async engine."""
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_migrations_online())