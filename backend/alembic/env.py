import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add backend/src to sys.path so "from festserve_api.models import Base" works
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)

from festserve_api.models import Base
print("Base metadata tables:", Base.metadata.tables)

# Alembic Config object
config = context.config

# Set up Python logging using .ini file
fileConfig(config.config_file_name)

# Set target_metadata for 'autogenerate'
target_metadata = Base.metadata
