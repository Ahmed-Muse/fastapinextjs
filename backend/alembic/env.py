import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Import your settings and Base
# (Adjust these imports if your folder structure is different)
from app.core.config import settings 
from app.db.base import Base 
from app.models.departments import DepartmentsModel  # Import all your models here
from app.db.sessions import engine  # Import your SQLAlchemy engine
from app.models.database import *  # Import all your models here
# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Set target_metadata for autogenerate support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    # 3. Use settings from your .env
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # 4. Inject the DATABASE_URL into the alembic config section
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()