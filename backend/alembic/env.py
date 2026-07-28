"""Alembic env.py configured for async SQLAlchemy."""

import asyncio
import re
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.base import Base

# Import all models so Alembic can see them for autogenerate
from app.models import *

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

VERSIONS_DIR = Path(__file__).resolve().parent / "versions"
SEQUENCE_PREFIX = re.compile(r"^(\d{4})")
MAX_SEQUENCE = 9999


def next_revision_id() -> str:
    """Return the next free 4-digit revision id, scanning existing version files."""
    used = [
        int(match.group(1))
        for path in VERSIONS_DIR.glob("*.py")
        if (match := SEQUENCE_PREFIX.match(path.name))
    ]
    candidate = max(used, default=0) + 1
    if candidate > MAX_SEQUENCE:
        raise RuntimeError(f"Migration sequence exhausted (max {MAX_SEQUENCE}).")
    return f"{candidate:04d}"


def process_revision_directives(_context, _revision, directives) -> None:
    """Name revisions 0001, 0002, ... instead of Alembic's random hex ids.

    Combined with `file_template` in alembic.ini this yields `<NNNN>_<reason>.py`
    and a `down_revision` chain that reads in order. An explicit `--rev-id` wins.
    """
    if getattr(config, "cmd_opts", None) is not None and config.cmd_opts.rev_id:
        return
    for directive in directives:
        directive.rev_id = next_revision_id()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode (async)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
