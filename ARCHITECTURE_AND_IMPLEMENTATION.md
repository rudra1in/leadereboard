# Registration Service - Architecture & Implementation Guide

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT TIER                                 │
│  ┌──────────────┬──────────────┬──────────────┬──────────────────┐  │
│  │   Web UI     │  Mobile App  │   Desktop    │   Third-party    │  │
│  │  (React)     │  (iOS/Andrd) │   Client     │    Services      │  │
│  └──────────────┴──────────────┴──────────────┴──────────────────┘  │
│                               ↓                                      │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY / LB                                │
│                (Nginx / HAProxy / Cloud LB)                          │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION TIER                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │           FastAPI Application (Port 8000)                   │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │  HTTP Request Handler                              │   │   │
│  │  │  ┌──────────┐    ┌──────────┐    ┌──────────────┐ │   │   │
│  │  │  │POST /api/│    │GET /api/ │    │GET /health  │ │   │   │
│  │  │  │Registrat│    │sse/regis │    │             │ │   │   │
│  │  │  └──────────┘    └──────────┘    └──────────────┘ │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  │                       ↓                                     │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │  Middleware                                         │   │   │
│  │  │  ├─ CORS (Cross-Origin)                            │   │   │
│  │  │  ├─ Error Handling                                 │   │   │
│  │  │  ├─ Request Validation                             │   │   │
│  │  │  └─ Logging                                        │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  │                       ↓                                     │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │  Service Layer                                      │   │   │
│  │  │  ├─ Registration Service                            │   │   │
│  │  │  ├─ Kafka Producer                                 │   │   │
│  │  │  └─ SSE Broadcaster                                │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
         ↓                            ↓                        ↓
┌──────────────────┐     ┌──────────────────┐    ┌──────────────────┐
│   PostgreSQL     │     │  Kafka Cluster   │    │  In-Memory Store │
│   Database       │     │                  │    │  (SSE clients)   │
│ ┌──────────────┐ │     │┌────┬────┬────┐ │    │ (Redis in Prod)  │
│ │Registration  │ │     ││Prod││Prod││Prod
│ │Table         │ │     │└────┴────┴────┘ │    └──────────────────┘
│ │              │ │     │Topics:           │
│ │id: INT (PK)  │ │     │- registrations   │
│ │event_id      │ │     │- results         │
│ │full_name     │ │     └──────────────────┘
│ │email         │ │
│ │phone         │ │
│ │status        │ │
│ │created_at    │ │
│ └──────────────┘ │
└──────────────────┘
```

---

## 🔄 Request/Response Flow Sequences

### Registration Creation Flow (Async Processing)

```
Client                     Service                  Kafka               Database
  │                           │                       │                    │
  ├─POST /registrations──────>│                       │                    │
  │ {event_id, email, ...}    │                       │                    │
  │                           │                       │                    │
  │                           ├─Validate Input        │                    │
  │                           ├─Generate UUID         │                    │
  │                           │                       │                    │
  │                           ├─Send to Kafka──────────>                   │
  │                           │ {registration_id...}  │                    │
  │                           │                       ├─Store Message      │
  │                           │                       │                    │
  │<──202 Accepted────────────┤                       │                    │
  │ {registration_id, status} │                       │                    │
  │                           │                       │                    │
  │                           │                       │                    │
  │  SSE Connection           │                       │                    │
  │  (keeps open)             │                       │                    │
  │                           │                       │                    │
  │                           │   [Background Processor]                   │
  │                           │   Consumer reads Kafka                     │
  │                           │                       ├─Process Event      │
  │                           │                       │                    │
  │                           │                       │   Database Ops:    │
  │                           │                       │   - Save reg       │
  │                           │                       │   - Validate event │
  │                           │                       │   - Check conflicts│
  │                           │                       │                    │
  │                           │    Publish Result     │                    │
  │                           │<──result.registered──┤                    │
  │                           │                       │                    │
  │<──SSE Update──────────────┤                       │                    │
  │  {status: confirmed}      │                       │                    │
  │                           │                       │                    │
  └──Close Connection─────────>                       │                    │
```

### Real-Time Update Flow (SSE)

```
Client                  Service              SSE Broadcaster         Kafka
  │                       │                        │                   │
  ├──GET /sse/:id────────>│                        │                   │
  │ (HTTP persistent)     │                        │                   │
  │                       ├──Register Queue        │                   │
  │                       │                        │                   │
  │                       │<──Keepalive (15s)──────┤                   │
  │<──event: ping─────────┤                        │                   │
  │   data: keepalive     │                        │                   │
  │                       │                        │                   │
  │                       │                        │   [Consumer Loop] │
  │                       │                        │<──Poll Messages───┤
  │                       │                        │                   │
  │                       │<──registration_update──┤                   │
  │<──event: update───────┤                        │                   │
  │   data: {status...}   │                        │                   │
  │                       │                        │                   │
  │<──keepalive (15s)─────┤                        │                   │
  │                       │                        │                   │
  │──Close────────────────>                        │                   │
  │                       ├──Cleanup queue         │                   │
  │                       │                        │                   │
```

---

## 🛠️ Implementation Patterns

### 1. FastAPI Application Factory

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await kafka_producer.start()
    yield
    # Shutdown
    await kafka_producer.stop()

app = FastAPI(lifespan=lifespan)
```

**Benefits:**
- Clean startup/shutdown lifecycle
- Resource management
- Error handling in initialization
- Async support

---

### 2. Async Database Session Management

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Usage in routes
@router.get("/registrations/{id}")
async def get_registration(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Registration).where(Registration.id == id)
    )
    return result.scalars().first()
```

**Benefits:**
- Automatic session cleanup
- Transaction handling
- Error recovery
- Connection pooling

---

### 3. Kafka Producer with Retry Logic

```python
# app/core/kafka.py
class KafkaProducerManager:
    async def send(self, topic: str, message: dict):
        try:
            await self.producer.send_and_wait(
                topic, 
                message,
                timeout_ms=30000
            )
            logger.info(f"Message sent: {message}")
        except Exception as e:
            logger.error(f"Send failed: {e}")
            raise
```

**Benefits:**
- Explicit error handling
- Timeout configuration
- Logging for debugging
- Exception propagation

---

### 4. SSE with Queue-Based Broadcasting

```python
# app/api/v1/routes/sse.py
@router.get("/registrations/{registration_id}")
async def registration_events(registration_id: str):
    queue = asyncio.Queue()
    sse_clients[registration_id] = queue
    
    async def event_generator():
        try:
            while True:
                try:
                    data = await asyncio.wait_for(
                        queue.get(), 
                        timeout=15.0
                    )
                    yield {"event": "registration_update", "data": data}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keepalive"}
        finally:
            sse_clients.pop(registration_id, None)
    
    return EventSourceResponse(event_generator())
```

**Benefits:**
- Automatic keepalive
- Memory cleanup
- Scalable with Redis
- Client disconnection handling

---

### 5. Pydantic Validation with Email

```python
# app/schemas/registration.py
from pydantic import BaseModel, EmailStr

class RegistrationCreate(BaseModel):
    event_id: int
    full_name: str
    email: EmailStr  # Built-in email validation
    phone: str | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": 1,
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890"
            }
        }
```

**Benefits:**
- Automatic validation
- Email format checking
- Type safety
- Documentation generation

---

## 📊 Database Schema Design

### Registration Table

```sql
CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL INDEX,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE INDEX,
    phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes Strategy

```
- event_id: Fast lookup by event
- email: Prevent duplicates, quick user lookup
- created_at: Timeline queries, archival operations
```

### Future Optimizations

```sql
-- Composite index for common queries
CREATE INDEX idx_event_status 
ON registrations(event_id, status);

-- For time-range queries
CREATE INDEX idx_created_at 
ON registrations(created_at DESC);

-- Partitioning by date (for large datasets)
CREATE TABLE registrations_2024_q1 PARTITION OF registrations
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

---

## 🔐 Security Considerations

### Input Validation

```python
class RegistrationCreate(BaseModel):
    event_id: int = Field(..., gt=0)  # Must be positive
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr  # RFC 5322 validation
    phone: str | None = Field(None, max_length=50)
```

### SQL Injection Prevention

```python
# ✅ SAFE - Using ORM
result = await db.execute(
    select(Registration).where(
        Registration.email == email  # Parameterized
    )
)

# ❌ UNSAFE - Raw SQL (never do this)
result = await db.execute(f"SELECT * FROM registrations WHERE email = '{email}'")
```

### CORS Configuration

```python
# Development
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://example.com",
        "https://app.example.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"]
)
```

### Rate Limiting (Add to production)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/registrations")
@limiter.limit("10/minute")
async def create_registration(request: Request, ...):
    ...
```

---

## 🚀 Performance Optimization

### Database Query Optimization

```python
# ✅ Good - Indexed column
@router.get("/registrations/event/{event_id}")
async def get_event_registrations(event_id: int, db: AsyncSession):
    return await db.execute(
        select(Registration)
        .where(Registration.event_id == event_id)
        .order_by(Registration.created_at.desc())
    )

# Connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,  # Connection pool size
    max_overflow=0,  # Wait for connection instead of creating new
    pool_pre_ping=True,  # Verify connections before use
)
```

### Async Concurrency

```python
# ✅ Parallel processing with gather
from asyncio import gather

async def bulk_process_registrations(registrations: List):
    tasks = [
        process_registration(reg) 
        for reg in registrations
    ]
    results = await gather(*tasks)
    return results
```

### Kafka Batching

```python
# Producer batch configuration
producer = AIOKafkaProducer(
    bootstrap_servers="localhost:9092",
    batch_size=32768,  # 32KB batches
    linger_ms=10,  # Wait up to 10ms for batch
    compression_type="snappy"
)
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/test_schemas.py
import pytest
from app.schemas.registration import RegistrationCreate

def test_valid_registration():
    data = {
        "event_id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
    }
    reg = RegistrationCreate(**data)
    assert reg.event_id == 1

def test_invalid_email():
    with pytest.raises(ValidationError):
        RegistrationCreate(
            event_id=1,
            full_name="John",
            email="invalid-email",
            phone=None
        )
```

### Integration Tests

```python
# tests/test_api.py
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_create_registration():
    client = TestClient(app)
    response = client.post(
        "/api/v1/registrations",
        json={
            "event_id": 1,
            "full_name": "Test User",
            "email": "test@example.com"
        }
    )
    assert response.status_code == 202
    assert "registration_id" in response.json()
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/health

# Using locust
locust -f tests/locustfile.py --host=http://localhost:8000
```

---

## 📈 Monitoring & Observability

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, generate_latest

registrations_total = Counter(
    'registrations_total',
    'Total registrations',
    ['event_id', 'status']
)

registration_latency = Histogram(
    'registration_latency_seconds',
    'Registration processing latency'
)

@router.post("/registrations")
async def create_registration(payload: RegistrationCreate):
    with registration_latency.time():
        # Process registration
        registrations_total.labels(
            event_id=payload.event_id,
            status="submitted"
        ).inc()
```

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "registration_created",
    registration_id=registration_id,
    event_id=event_id,
    email=email,
    timestamp=datetime.utcnow()
)
```

### Health Check Endpoints

```python
@app.get("/health/live")
async def liveness():
    """Is the service running?"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Is the service ready for traffic?"""
    kafka_ok = kafka_producer.producer is not None
    db_ok = await check_db_connection()
    
    if kafka_ok and db_ok:
        return {"status": "ready"}
    
    raise HTTPException(status_code=503, detail="Service not ready")
```

---

## 🔄 Scaling Strategies

### Horizontal Scaling

```yaml
# kubernetes deployment
replicas: 3

strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

### Database Connection Pooling

```python
# Multiple connections for concurrent requests
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### Kafka Consumer Groups

```python
# Multiple consumers for parallel processing
consumer = AIOKafkaConsumer(
    'event.registrations',
    group_id='registration-processors',  # Shared group
    bootstrap_servers=['kafka:9092'],
    max_poll_records=100  # Batch processing
)
```

---

## 📝 Deployment Checklist

### Pre-Deployment

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Kafka topics created
- [ ] SSL certificates installed
- [ ] API keys generated
- [ ] Monitoring configured
- [ ] Backup strategy in place

### Post-Deployment

- [ ] Health checks passing
- [ ] Load tests successful
- [ ] Logs monitored
- [ ] Alerts configured
- [ ] Runbooks created
- [ ] Team trained

---
