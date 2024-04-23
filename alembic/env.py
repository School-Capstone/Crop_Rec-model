import models
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# My code
import os
import sys
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
sys.path.append(BASE_DIR)


# This is the Alembic Config object, which provides
# Access to the values within the .ini file in use.
config = context.config

DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "35.227.44.19"
# DB_HOST = "croc-db.c50cugi4gdw1.us-west-2.rds.amazonaws.com"


#  Making a connection
config.set_main_option(
    'sqlalchemy.url',
    'postgresql+pg8000://postgres:password@postgres?unix_sock=/cloudsql/premium-valor-418410:us-east1:test-instance/.s.PGSQL.5432')

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = models.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.QueuePool,
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


# curl -X PUT \
# -H "Content-Type: application/json" \
# -H "Authorization: Bearer dop_v1_da7efb2e2a9806b0a8fd08c2c55e79f9cba92fdd585d8287a7912be52d8dbc0e" \
# -d '{"rules": [{"type": "ip_addr","value": "192.168.1.1"},{"type": "droplet","value": "414392895"},{"type": "k8s","value": "ff2a6c52-5a44-4b63-b99c-0e98e7a63d61"},{"type": "tag","value": "backend"}]}' \
# "https://api.digitalocean.com/v2/databases/1ddb6425-4b01-4f8e-877c-951cdd867778/firewall"
