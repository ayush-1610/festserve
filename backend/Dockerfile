FROM python:3.11-slim
WORKDIR /app

# 1) install your app
COPY poetry.lock pyproject.toml ./
RUN pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --without dev

# 2) bring in Alembic config + migrations
COPY alembic.ini ./
# COPY alembic ./alembic
COPY alembic/ ./alembic/           
# ← include your migration scripts
COPY src/ ./src/                   
# ← include all your FastAPI source


# 3) bring in your code + static assets
# COPY src/ ./src
COPY static/ ./static

# so python can import festserve_api:
ENV PYTHONPATH=/app/src

EXPOSE 8000
CMD ["uvicorn", "src.festserve_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
