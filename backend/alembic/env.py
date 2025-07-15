"""Alembic environment for the FestServe backend."""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context
# from festserve_api.database import DATABASE_URL
from src.festserve_api.database import DATABASE_URL

# Add backend/src to the path so ``from festserve_api.models import Base`` works
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
# Make sure all models are registered on Base.metadata:
import festserve_api.models  # noqa

# from festserve_api.models import Base
from festserve_api.database import Base

# Alembic Config object, provides access to values within the .ini file.
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)


# Configure Python logging via the .ini file.
fileConfig(config.config_file_name)

# Metadata for 'autogenerate' support.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
