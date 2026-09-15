# user-service

Complete FastAPI service with:
- Async SQLAlchemy + PostgreSQL
- Alembic migrations
- Kafka producer
- Server-Sent Events (SSE)

### Quick start
```bash
uv pip install -r pyproject.toml
alembic revision --autogenerate -m "create users"
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```
