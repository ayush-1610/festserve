# FestServe

This repository contains the FestServe backend (FastAPI) and frontend (React) applications.

## Prerequisites
- **Docker** and **Docker Compose** for running the services
- **Python 3.11** with [Poetry](https://python-poetry.org/) for local development and testing

## Running the services
1. Start the database and backend:
   ```bash
   docker-compose up --build
   ```
   The backend will be available on `http://localhost:8000`.

2. Apply database migrations:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. (Optional) Seed test data:
   ```bash
   docker-compose exec backend python src/festserve_api/create_users.py
   ```

## Running tests
Run the following inside the `backend/` directory:
```bash
poetry install --no-root
poetry run pytest
```
