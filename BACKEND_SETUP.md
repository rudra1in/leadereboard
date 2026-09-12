# GameX Leaderboard Backend - Setup & Development Guide

## Quick Start (5 Minutes)

### 1. Prerequisites
- Python 3.9+
- PostgreSQL 12+ (or SQLite for development)
- pip or conda

### 2. Setup Database

**Option A: PostgreSQL (Production)**
```bash
# Create database
createdb gamex_leaderboard

# Create user
createuser gamex -P
# Enter password: gamex_password
```

**Option B: SQLite (Development)**
```bash
# No setup needed, uses file-based database
# Update .env: DATABASE_URL=sqlite:///./gamex_leaderboard.db
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your database settings
```

### 5. Initialize Database
```bash
python -c "from database import create_all_tables; create_all_tables()"
```

### 6. Run Server
```bash
python main.py
# Server starts on http://localhost:8000
```

### 7. Verify Installation
```bash
# Health check
curl http://localhost:8000/health

# Readiness check
curl http://localhost:8000/ready

# API docs
open http://localhost:8000/docs
```

## Development Setup

### Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### Install Development Dependencies
```bash
pip install -r requirements.txt
# Also install dev tools
pip install pytest pytest-asyncio black flake8 mypy
```

### Code Quality Tools
```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .

# Import sorting
isort .
```

## File Structure

```
backend/
├── models/
│   └── ranking_model.py         # ORM models
├── schemas/
│   └── ranking_schema.py        # Pydantic schemas
├── repositories/
│   └── ranking_repository.py    # Data access layer
├── services/
│   └── ranking_service.py       # Business logic layer
├── routers/
│   └── ranking_router.py        # API endpoints
├── database.py                  # Database configuration
├── main.py                      # FastAPI application
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── BACKEND_ARCHITECTURE.md      # Architecture docs
├── BACKEND_SETUP.md            # This file
└── tests/
    ├── test_repositories.py     # Repository tests
    ├── test_services.py         # Service tests
    └── test_routers.py          # API tests
```

## Database Operations

### Create All Tables
```python
from database import create_all_tables
create_all_tables()
```

### Drop All Tables
```python
from database import drop_all_tables
drop_all_tables()
```

### Reset Database
```python
from database import reset_database
reset_database()
```

### Run Migrations (with Alembic)
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_repositories.py
```

### Run with Coverage
```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
```

### Test with Different Database
```bash
DATABASE_URL=sqlite:///./test.db pytest
```

## API Testing

### Using cURL

#### Get Rankings
```bash
curl "http://localhost:8000/api/rankings?category=CAT001&limit=10"
```

#### Get Specific Ranking
```bash
curl "http://localhost:8000/api/rankings/RANK001"
```

#### Get Ranking Detail
```bash
curl "http://localhost:8000/api/rankings/RANK001/detail"
```

#### Get Explainability
```bash
curl "http://localhost:8000/api/rankings/ATH001/explainability?category_id=CAT001"
```

#### Get Scenarios
```bash
curl "http://localhost:8000/api/rankings/ATH001/qualification-scenarios?category_id=CAT001"
```

#### Trigger Recompute
```bash
curl -X POST http://localhost:8000/api/admin/rankings/recompute \
  -H "Content-Type: application/json" \
  -d '{"event_id":"EVT001","triggered_by":"admin"}'
```

### Using Postman
1. Import OpenAPI schema: http://localhost:8000/openapi.json
2. All endpoints with request examples are available

### Using Python Client
```python
import httpx

client = httpx.Client(base_url="http://localhost:8000")

# Get rankings
response = client.get("/api/rankings", params={"category": "CAT001"})
rankings = response.json()

# Get explainability
response = client.get(
    "/api/rankings/ATH001/explainability",
    params={"category_id": "CAT001"}
)
explainability = response.json()
```

## Common Development Tasks

### Add a New Endpoint

1. **Define Schema** (`schemas/ranking_schema.py`):
```python
class NewRequestSchema(BaseModel):
    field: str
    value: int
```

2. **Implement Service Method** (`services/ranking_service.py`):
```python
def new_operation(self, param: str) -> Any:
    # business logic
    return result
```

3. **Add Repository Method** (`repositories/ranking_repository.py`):
```python
def query_new_data(self, param: str):
    # query logic
    return results
```

4. **Add Router Method** (`routers/ranking_router.py`):
```python
@router.post("/new-endpoint")
async def new_endpoint(request: NewRequestSchema, db: Session = Depends(get_db)):
    service = RankingService(db)
    result = service.new_operation(request.field)
    return result
```

### Modify Database Schema

1. **Update Model** (`models/ranking_model.py`):
```python
class MyModel(Base):
    __tablename__ = "my_table"
    new_field = Column(String(255), nullable=True)
```

2. **Create Migration** (with Alembic):
```bash
alembic revision --autogenerate -m "Add new_field to my_table"
alembic upgrade head
```

3. **Or Recreate** (development only):
```python
from database import reset_database
reset_database()
```

### Add Business Logic

1. **Implement in Service** (`services/ranking_service.py`):
```python
def complex_calculation(self, input_data: Dict) -> float:
    # Step 1: fetch data
    # Step 2: process
    # Step 3: validate
    return result
```

2. **Use in Endpoint** (`routers/ranking_router.py`):
```python
result = service.complex_calculation(request.dict())
return {"result": result}
```

## Debugging

### Enable SQL Logging
```bash
# In .env
DB_ECHO_SQL=true
```

### Verbose Logging
```bash
# In .env
LOG_LEVEL=DEBUG
```

### Print Debugging
```python
# In code
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Variable value: {variable}")
```

### Use Python Debugger
```python
# In code
import pdb; pdb.set_trace()

# In terminal
(Pdb) p variable_name  # print variable
(Pdb) c               # continue
```

## Deployment

### Local Development
```bash
python main.py
# Uses default settings: localhost:8000
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Docker Container
```bash
# Build
docker build -t gamex-leaderboard .

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  gamex-leaderboard
```

### Environment Variables for Production
```bash
export ENVIRONMENT=production
export DEBUG=false
export DATABASE_URL=postgresql://user:pass@host:5432/db
export CORS_ORIGINS=https://example.com
export ADMIN_TOKEN=strong-secret-token
```

## Troubleshooting

### Database Connection Error
```
ERROR: could not connect to server
```

**Solution:**
- Check PostgreSQL is running: `pg_isready`
- Check connection string in .env
- Check credentials are correct

### Module Import Error
```
ModuleNotFoundError: No module named 'sqlalchemy'
```

**Solution:**
- Install requirements: `pip install -r requirements.txt`
- Check virtual environment is activated

### Port Already in Use
```
OSError: [Errno 48] Address already in use
```

**Solution:**
- Use different port: `PORT=8001 python main.py`
- Kill process on port: `lsof -i :8000` then `kill -9 <PID>`

### Database Locked (SQLite)
```
database is locked
```

**Solution:**
- Close other connections to database
- Delete `.db-journal` file
- Use PostgreSQL for development

### Schema Mismatch
```
ERROR: column "new_column" does not exist
```

**Solution:**
- Run database migrations: `alembic upgrade head`
- Or reset: `python -c "from database import reset_database; reset_database()"`

## Performance Tips

### Index Management
- Indexes are automatically created (see models)
- For custom queries, add indexes in model `__table_args__`

### Query Optimization
- Use `limit` and `offset` for pagination
- Filter at database level (not in Python)
- Use `select()` for specific columns only

### Connection Pooling
- Configured in `DatabaseConfig`
- Increase `POOL_SIZE` for high concurrency
- Increase `MAX_OVERFLOW` for spike handling

### Caching
- Add Redis for ranking results
- Cache config lookups
- Invalidate on updates

## References

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/14/orm/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/usage/validators/)
- [PostgreSQL Setup](https://www.postgresql.org/docs/)

## Support

For issues or questions:
1. Check this guide first
2. Review BACKEND_ARCHITECTURE.md
3. Check error messages in logs
4. Review code comments in source files

## Next Steps

1. ✅ Complete setup following this guide
2. ✅ Understand architecture (read BACKEND_ARCHITECTURE.md)
3. ✅ Run tests to verify installation
4. ✅ Explore API endpoints (visit /docs)
5. ✅ Make modifications for your use case
6. ✅ Deploy to production
