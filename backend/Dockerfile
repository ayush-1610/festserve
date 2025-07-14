FROM python:3.11-slim
WORKDIR /app

# 1) install your app (including dev dependencies for testing)
COPY poetry.lock pyproject.toml ./
RUN pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --with dev

# 2) bring in Alembic config + migrations
COPY alembic.ini ./
COPY alembic/ ./alembic/

# bring in the script to drop the alembic version table 
COPY drop_alembic_version.py ./

# 3) bring in your FastAPI source
COPY src/ ./src/

# bring in the script to create test users
COPY tests/ ./tests/

# 4) static assets
COPY static/ ./static

# so python can import festserve_api:
ENV PYTHONPATH=/app/src

EXPOSE 8000
CMD ["uvicorn", "src.festserve_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
