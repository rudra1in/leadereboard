# GameX Leaderboard Backend - Architecture Documentation

## Overview

This is a production-ready Python microservice for the GameX leaderboard system. It implements professional object-oriented architecture with proper separation of concerns following SOLID principles.

## Architecture Layers

### 1. Models Layer (`models/ranking_model.py`)
**ORM definitions using SQLAlchemy**

- **AthleteModel**: Represents competitors
- **CategoryModel**: Competitive divisions
- **SportModel**: Sports classification
- **RankingModel**: Current rankings
- **RankingEntryModel**: Contributing events
- **RankingConfigModel**: Versioned ranking configurations
- **RankingHistoryModel**: Audit trail
- **RankingRecomputeModel**: Recomputation tracking
- **QualificationScenarioModel**: Projections

**Key Features:**
- Relationship management
- Automatic timestamps
- Index optimization
- Type safety with enum fields

### 2. Schemas Layer (`schemas/ranking_schema.py`)
**Pydantic models for request/response validation**

- Request schemas (create, filter, recompute)
- Response schemas (single, list, detail, error)
- Automatic validation
- OpenAPI documentation
- JSON serialization

**Key Features:**
- Type hints for IDE support
- Automatic validation
- Error messages
- Example values for documentation

### 3. Repository Layer (`repositories/ranking_repository.py`)
**Data Access Object (DAO) pattern**

Classes:
- `BaseRepository`: Generic CRUD operations
- `AthleteRepository`: Athlete data access
- `RankingRepository`: Ranking data access
- `RankingEntryRepository`: Event data access
- `RankingConfigRepository`: Configuration access
- `RankingHistoryRepository`: History/audit access
- `RankingRecomputeRepository`: Recomputation tracking
- `QualificationScenarioRepository`: Scenario data access

**Key Features:**
- Query abstraction
- Error handling
- Pagination support
- Filtering operations
- Transaction management

### 4. Service Layer (`services/ranking_service.py`)
**Business logic and orchestration**

Classes:
- `RankingService`: Core ranking operations
  - Retrieval operations
  - Explainability computation
  - Scenario generation
  - History recording
  - Ranking computation engine

- `RankingRecomputeService`: Recomputation orchestration
  - Trigger management
  - Progress tracking
  - Error handling

**Key Features:**
- Business rule enforcement
- Data transformation
- Cross-repository orchestration
- Ranking computation engine
- History recording

### 5. Router Layer (`routers/ranking_router.py`)
**FastAPI endpoints**

Classes:
- `RankingRouter`: Public ranking endpoints
  - GET /api/rankings
  - GET /api/rankings/{ranking_id}
  - GET /api/rankings/{ranking_id}/detail
  - GET /api/rankings/{athlete_id}/explainability
  - GET /api/rankings/{athlete_id}/qualification-scenarios
  - GET /api/rankings/{athlete_id}/history
  - POST /api/rankings/search

- `AdminRankingRouter`: Admin operations
  - POST /api/admin/rankings/recompute

**Key Features:**
- Request validation
- Response serialization
- Error handling
- OpenAPI documentation
- Dependency injection

## Data Flow

### Ranking Retrieval Flow

```
Router Handler
    ↓
Service.get_rankings()
    ↓
Repository.get_rankings_by_category()
    ↓
SQLAlchemy Query
    ↓
Database
    ↓ (results)
RankingModel instances
    ↓
Service._to_ranking_response()
    ↓
Schema.RankingResponse
    ↓
Router response (JSON)
```

### Ranking Computation Flow

```
AdminRouter.trigger_recompute()
    ↓
RecomputeService.trigger_recompute()
    ↓
RankingService.compute_rankings()
    ↓
For each athlete:
  - Get existing ranking
  - Fetch contributing events
  - Apply decay factor
  - Calculate rank
  - Update or create ranking
  - Record history
    ↓
Database updates
    ↓
Response with stats
```

## Key Patterns

### 1. Dependency Injection
```python
async def get_rankings(db: Session = Depends(get_db)):
    service = RankingService(db)
    # use service
```

### 2. Repository Pattern
```python
rankings, total = self.ranking_repo.get_rankings_by_category(
    category_id, sport_id, limit, offset
)
```

### 3. Service Layer Orchestration
```python
service = RankingService(db)
response = service.get_ranking_detail(ranking_id)
```

### 4. Error Handling
```python
try:
    # operation
except RepositoryException as e:
    raise ServiceException(f"Failed: {str(e)}")
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

## Class Responsibilities

### BaseRepository
- Generic CRUD operations
- Query execution
- Error handling
- Transaction management

### Specific Repositories (AthleteRepository, etc.)
- Domain-specific queries
- Filtering operations
- Relationship traversal
- Custom business queries

### RankingService
- Business logic
- Data transformation
- Multi-repository orchestration
- Ranking computation
- History tracking

### Routers
- HTTP request handling
- Schema validation
- Error responses
- OpenAPI documentation

## Database Schema

### Key Tables

1. **athletes** - Competitor profiles
2. **categories** - Competitive divisions
3. **sports** - Sport classification
4. **ranking_configs** - Configuration versions
5. **rankings** - Current standings
6. **ranking_entries** - Contributing events
7. **ranking_history** - Audit trail
8. **ranking_recomputes** - Recomputation tracking
9. **qualification_scenarios** - Projections

### Indexes
- `idx_athlete_category_config` - Fast athlete ranking lookup
- `idx_rank_category` - Fast rank filtering
- `idx_sport_category_active` - Active categories by sport
- `idx_athlete_date` - History filtering
- And more optimized for common queries

## Configuration

### AppConfig Class
```python
class AppConfig:
    APP_NAME = "GameX Leaderboard"
    DATABASE_URL = os.getenv("DATABASE_URL")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS").split(",")
    DEBUG = ENVIRONMENT == "development"
```

### DatabaseConfig Class
```python
class DatabaseConfig:
    DATABASE_URL = os.getenv("DATABASE_URL")
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
    ECHO_SQL = os.getenv("DB_ECHO_SQL", "false") == "true"
```

## API Endpoints

### Public Endpoints

```
GET    /api/rankings
       - Get paginated rankings
       - Query params: sport, category, window, limit, offset, search

GET    /api/rankings/{ranking_id}
       - Get single ranking

GET    /api/rankings/{ranking_id}/detail
       - Get ranking with contributing events

GET    /api/rankings/{athlete_id}/explainability?category_id=CAT001
       - Get ranking explanation

GET    /api/rankings/{athlete_id}/qualification-scenarios?category_id=CAT001
       - Get qualification scenarios

GET    /api/rankings/{athlete_id}/history?category_id=CAT001&days=90
       - Get ranking history

POST   /api/rankings/search
       - Advanced ranking search
```

### Admin Endpoints

```
POST   /api/admin/rankings/recompute
       - Trigger ranking recomputation
       - Request: { event_id, sport_id?, category_id?, triggered_by }
```

### Health Endpoints

```
GET    /health
       - Health check

GET    /ready
       - Readiness check
```

## Error Handling

### Exception Hierarchy

```
Exception
├── RepositoryException
│   └── Raised by repositories on data access errors
├── ServiceException
│   └── Raised by services on business logic errors
└── HTTPException (FastAPI)
    └── Raised by routers for HTTP responses
```

### Standard Error Response
```json
{
  "error": "Error Type",
  "detail": "Error description",
  "status_code": 400,
  "timestamp": "2026-09-11T14:30:00Z",
  "path": "/api/rankings/ATH999"
}
```

## Performance Optimizations

### Database
- Connection pooling (QueuePool)
- Query result filtering at DB level
- Indexed columns
- Pagination support
- Pre-ping for stale connections

### API
- GZIP compression
- Response caching ready
- Pagination
- Lazy loading of relationships

### Ranking Computation
- Batch processing
- Incremental updates
- Event decay application
- Efficient sorting

## Testing Strategy

### Unit Tests
```python
def test_athlete_repository_get_by_id():
    repo = AthleteRepository(db)
    athlete = repo.get_by_athlete_id("ATH001")
    assert athlete is not None
```

### Integration Tests
```python
def test_ranking_service_compute():
    service = RankingService(db)
    total, changed = service.compute_rankings("CAT001", "CFG001")
    assert total > 0
```

### API Tests
```python
def test_get_rankings_endpoint(client):
    response = client.get("/api/rankings?category=CAT001")
    assert response.status_code == 200
    assert "data" in response.json()
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
See `.env.example` for all available options.

### Database Migration
```python
# Using Alembic
alembic upgrade head
```

## Monitoring

### Health Checks
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

### Metrics (Optional)
- Prometheus metrics endpoint
- Request count/latency
- Database connection pool stats
- Recomputation statistics

## Security Considerations

- API key authentication support
- JWT token support
- Admin endpoint protection
- Input validation
- SQL injection prevention (SQLAlchemy)
- CORS configuration
- Error message sanitization

## Extending the System

### Add New Repository
1. Extend `BaseRepository`
2. Implement domain-specific queries
3. Add error handling

### Add New Service
1. Create service class
2. Use repositories for data access
3. Implement business logic
4. Add schema transformations

### Add New Endpoint
1. Create router method
2. Define request/response schemas
3. Add validation
4. Implement error handling
5. Register in create_ranking_routers()

## Performance Benchmarks

### Expected Performance
- Single ranking retrieval: <50ms
- Rankings list (paginated): <200ms
- Ranking computation (1000 athletes): <5s
- API response time: <500ms

### Optimization Opportunities
- Add Redis caching layer
- Implement GraphQL for field selection
- Use async database driver
- Implement sharding for scale

## Future Enhancements

1. **Caching Layer** - Redis for rankings cache
2. **Message Queue** - Async ranking computation
3. **Real-time Updates** - WebSocket support
4. **Analytics** - Detailed tracking and reporting
5. **Multi-tenant Support** - Per-tenant data isolation
6. **Audit Logging** - Detailed operation logging
7. **GraphQL API** - Alternative query interface
8. **Rate Limiting** - Per-user request limits

## References

- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Pydantic Docs: https://docs.pydantic.dev
- Python SOLID: https://realpython.com/solid-principles/
