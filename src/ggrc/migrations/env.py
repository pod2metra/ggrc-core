# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import re
from alembic import context
from logging.config import fileConfig

# Ensure all models are imported so they can be used
# with --autogenerate
from ggrc.app import db
from ggrc.models import all_models  # noqa

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

target_metadata = db.metadata


def include_symbol(tablename, schema=None):
    """Exclude some tables from consideration by alembic's 'autogenerate'.
  """
    # Exclude `*_alembic_version` tables
    if re.match(r'.*_alembic_version$', tablename):
        return False

    # If the tablename didn't match any exclusion cases, return True
    return True


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, include_symbol=include_symbol)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    engine = db.engine

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_symbol=include_symbol)

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
