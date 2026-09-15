# Registration Service - Visual Reference Guide

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │   Web UI     │  │  Mobile App  │  │   Desktop    │  │  Third-party Apps   │ │
│  │  (React)     │  │  (iOS/Andrd) │  │   (Electron) │  │  (Webhooks/API)     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────────────┘ │
└────────────────────────────────────────────┬──────────────────────────────────────┘
                                             │ HTTP/REST
                    ┌────────────────────────▼────────────────────────┐
                    │     LOAD BALANCER / REVERSE PROXY               │
                    │  (Nginx/HAProxy/Cloud LB)                       │
                    └────────────────────────┬────────────────────────┘
                                             │ HTTP/REST
        ┌────────────────────────────────────┴────────────────────────────────────┐
        │                     FASTAPI APPLICATION TIER                            │
        │                                                                         │
        │  ┌─────────────────────────────────────────────────────────────────┐   │
        │  │                    FastAPI Application                          │   │
        │  │                     (Port 8000)                                 │   │
        │  │  ┌──────────────────────────────────────────────────────────┐  │   │
        │  │  │ HTTP Handlers (Async)                                    │  │   │
        │  │  │ ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │  │   │
        │  │  │ │ POST         │  │ GET          │  │ GET              │ │  │   │
        │  │  │ │ /api/v1/reg  │  │ /api/v1/sse/ │  │ /health          │ │  │   │
        │  │  │ │ istrations   │  │ registrations│  │                  │ │  │   │
        │  │  │ └──────────────┘  └──────────────┘  └──────────────────┘ │  │   │
        │  │  └──────────────┬───────────────────────────────────────────┘  │   │
        │  │                 │ (Request/Response)                           │   │
        │  │  ┌──────────────▼───────────────────────────────────────────┐  │   │
        │  │  │ Middleware Layer                                         │  │   │
        │  │  │ ├─ CORS Middleware                                       │  │   │
        │  │  │ ├─ Error Handling                                        │  │   │
        │  │  │ ├─ Request Logging                                       │  │   │
        │  │  │ └─ Validation                                            │  │   │
        │  │  └──────────────┬───────────────────────────────────────────┘  │   │
        │  │                 │                                               │   │
        │  │  ┌──────────────▼───────────────────────────────────────────┐  │   │
        │  │  │ Service Layer                                            │  │   │
        │  │  │ ├─ RegistrationService                                  │  │   │
        │  │  │ ├─ KafkaProducer                                         │  │   │
        │  │  │ └─ SSEBroadcaster                                        │  │   │
        │  │  └──────────────┬───────────────────────────────────────────┘  │   │
        │  └─────────────────┼─────────────────────────────────────────────┘   │
        │                    │                                                  │
        └────────────────────┼──────────────────────────────────────────────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
         ┌──────▼──────┐  ┌──▼────────┐ ┌▼─────────────┐
         │ PostgreSQL  │  │   Kafka   │ │  In-Memory   │
         │ Database    │  │ Cluster   │ │  SSE Queue   │
         │             │  │           │ │ (Redis Prod) │
         │ ┌─────────┐ │  │ ┌────┬───┐│ │              │
         │ │registr. │ │  │ │Part│Part││ │              │
         │ │table    │ │  │ │0   │ 1  ││ │              │
         │ │         │ │  │ └────┴───┘│ │              │
         │ └─────────┘ │  │ Topics:    │ │              │
         │             │  │ - regs    │ │              │
         │ Connection: │  │ - results  │ │              │
         │ 5432        │  │            │ │              │
         │             │  │ Port: 9092 │ │              │
         └─────────────┘  └────────────┘ └──────────────┘
         (async conn)    (async producer/consumer)
```

---

## 📊 Data Flow Sequence Diagram

### Registration Creation Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│  CLIENT              API              KAFKA              DATABASE            │
│    │                  │                  │                  │               │
│    │ POST /reg        │                  │                  │               │
│    ├─────────────────>│                  │                  │               │
│    │                  │                  │                  │               │
│    │                  │ Validate Input   │                  │               │
│    │                  │ Generate UUID    │                  │               │
│    │                  │ │                  │                  │               │
│    │                  │ Create Kafka Msg  │                  │               │
│    │                  │                  │                  │               │
│    │                  ├─ Send Message ──>│                  │               │
│    │                  │                  │ Persist Message  │               │
│    │                  │                  │ │                │               │
│    │ HTTP 202         │                  │                  │               │
│    │<────────────────┤                  │                  │               │
│    │ {registration_id}│                  │                  │               │
│    │ {status: proc}   │                  │                  │               │
│    │                  │                  │                  │               │
│    │                  │                  │                  │               │
│    │ [External Processor]                │                  │               │
│    │                  │                  │                  │               │
│    │                  │                  │ Consume Message  │               │
│    │                  │                  ├────────────────>│               │
│    │                  │                  │                  │ Validate     │
│    │                  │                  │                  │ Check Event  │
│    │                  │                  │                  │ Save Status  │
│    │                  │                  │                  │ │             │
│    │                  │ Publish Result  │<─────────────────┤               │
│    │                  │<─────────────────┤                  │               │
│    │                  │                  │                  │               │
│    │ SSE Update       │                  │                  │               │
│    │<─────────────────┤                  │                  │               │
│    │ {status: conf}   │                  │                  │               │
│    │                  │                  │                  │               │
│    │                  │                  │                  │               │
│    └──────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Path Detail View

### POST /api/v1/registrations

```
┌─────────────────────────────────────────────────────────────────────┐
│  Client Request                                                     │
│  ─────────────────────────────────────────────────────────────────   │
│  POST /api/v1/registrations                                         │
│  Content-Type: application/json                                     │
│                                                                     │
│  {                                                                  │
│    "event_id": 1,                                                   │
│    "full_name": "John Doe",                                         │
│    "email": "john@example.com",                                     │
│    "phone": "+1234567890"                                           │
│  }                                                                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FastAPI Router                                                     │
│  ─────────────────────────────────────────────────────────────────   │
│  app/api/v1/routes/registrations.py                                 │
│                                                                     │
│  @router.post("/", status_code=202)                                 │
│  async def create_registration(payload: RegistrationCreate)         │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Validation & Processing                                            │
│  ─────────────────────────────────────────────────────────────────   │
│  ✓ Pydantic validation (type, email format)                         │
│  ✓ Generate UUID for registration_id                                │
│  ✓ Create message payload                                           │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Kafka Producer                                                     │
│  ─────────────────────────────────────────────────────────────────   │
│  await kafka_producer.send(                                         │
│    topic="event.registrations",                                     │
│    message={                                                        │
│      "registration_id": "550e8400-...",                             │
│      "event_id": 1,                                                 │
│      "full_name": "John Doe",                                       │
│      "email": "john@example.com",                                   │
│      "phone": "+1234567890"                                         │
│    }                                                                │
│  )                                                                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Kafka Topic Partitions                                             │
│  ─────────────────────────────────────────────────────────────────   │
│  Topic: event.registrations                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ Partition 0 │  │ Partition 1 │  │ Partition 2 │                 │
│  │ (Offset 0-N)│  │ (Offset 0-M)│  │ (Offset 0-K)│                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                     │
│  Message persisted with:                                            │
│  - Key: event_id (for partitioning)                                │
│  - Value: JSON-serialized message                                  │
│  - Timestamp: Broker timestamp                                     │
│  - Offset: Sequential position                                     │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  API Response (Immediate - Async)                                   │
│  ─────────────────────────────────────────────────────────────────   │
│  HTTP 202 ACCEPTED                                                  │
│                                                                     │
│  {                                                                  │
│    "message": "Registration submitted successfully",                │
│    "registration_id": "550e8400-e29b-41d4-a716-446655440000",      │
│    "status": "processing"                                           │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### GET /api/v1/sse/registrations/{registration_id}

```
┌────────────────────────────────────────────────────────────┐
│  Client Request                                            │
│  ─────────────────────────────────────────────────────────  │
│  GET /api/v1/sse/registrations/550e8400-...              │
│  Accept: text/event-stream                                │
│  Connection: keep-alive                                   │
└────────────┬──────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│  SSE Connection Established                                │
│  ─────────────────────────────────────────────────────────  │
│  HTTP 200 OK                                               │
│  Content-Type: text/event-stream                           │
│  Transfer-Encoding: chunked                                │
│                                                            │
│  [Connection kept open for event streaming]               │
└────────────┬──────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│  SSE Client Registration                                   │
│  ─────────────────────────────────────────────────────────  │
│  app/consumers/sse_broadcaster.py                          │
│                                                            │
│  sse_clients[registration_id] = asyncio.Queue()           │
│                                                            │
│  [Queue registered in-memory store]                        │
└────────────┬──────────────────────────────────────────────┘
             │
             ├──────────────────────────────────────┐
             │                                      │
             ▼                                      ▼
┌──────────────────────────┐        ┌──────────────────────────┐
│  Keep-Alive Handler      │        │  Event Listener          │
│  ─────────────────────   │        │  ─────────────────────   │
│  Every 15 seconds:       │        │  Listen for updates:     │
│  event: ping             │        │  - Poll Kafka topic      │
│  data: keepalive         │        │  - Match registration_id │
│                          │        │  - Queue.put(message)    │
└──────────────────────────┘        └──────────────────────────┘
             │                                      │
             └──────────────┬─────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│  SSE Event Stream Response                                 │
│  ─────────────────────────────────────────────────────────  │
│                                                            │
│  event: ping                                               │
│  data: keepalive                                           │
│                                                            │
│  event: registration_update                                │
│  data: {                                                   │
│    "registration_id": "550e8400-...",                      │
│    "status": "confirmed",                                  │
│    "timestamp": "2024-01-15T10:30:00Z"                    │
│  }                                                         │
│                                                            │
│  event: ping                                               │
│  data: keepalive                                           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 📦 Module Dependency Graph

```
app/main.py
    │
    ├─> app/core/config.py
    ├─> app/core/kafka.py (kafka producer)
    ├─> app/core/database.py
    │   └─> sqlalchemy.ext.asyncio
    │
    └─> app/api/router.py
        │
        ├─> app/api/v1/routes/registrations.py
        │   ├─> app/schemas/registration.py
        │   │   └─> pydantic
        │   ├─> app/core/kafka.py
        │   └─> app/core/config.py
        │
        └─> app/api/v1/routes/sse.py
            ├─> app/consumers/sse_broadcaster.py
            ├─> sse_starlette
            └─> asyncio


app/consumers/sse_broadcaster.py (separate process)
    ├─> aiokafka
    ├─> app/core/config.py
    └─> asyncio
```

---

## 🗄️ Database Schema Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    registrations table                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PK │ id              │ SERIAL                              │
│     ├─ INT                                                  │
│     │                                                       │
│ IDX │ event_id        │ INTEGER                             │
│     ├─ References event ID (external system)                │
│     │                                                       │
│     │ full_name       │ VARCHAR(255)                        │
│     ├─ User's full name                                     │
│     │                                                       │
│ IDX │ email           │ VARCHAR(255) UNIQUE                 │
│     ├─ User's email address                                 │
│     │ - Must be unique per registration                     │
│     │                                                       │
│     │ phone           │ VARCHAR(50) [NULLABLE]              │
│     ├─ User's phone number (optional)                       │
│     │                                                       │
│     │ status          │ VARCHAR(50)                         │
│     ├─ Values: pending|confirmed|rejected                   │
│     │ - Default: pending                                    │
│     │                                                       │
│ TS  │ created_at      │ TIMESTAMP WITH TIMEZONE             │
│     ├─ Registration creation time (UTC)                     │
│     │ - Auto-set by database                                │
│     │                                                       │
└─────────────────────────────────────────────────────────────┘

Indexes:
  - event_id: Fast lookups by event
  - email: Prevent duplicates, user lookup
  - created_at: Timeline queries
  - (event_id, status): Common composite query
```

---

## 🔧 Configuration Hierarchy

```
┌──────────────────────────────────────────────────────────────┐
│  System Defaults (in code)                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ DEBUG = False                                          │  │
│  │ DATABASE_URL = postgresql+asyncpg://localhost:5432... │  │
│  │ KAFKA_BOOTSTRAP_SERVERS = localhost:9092              │  │
│  │ KAFKA_TOPIC_REGISTRATIONS = event.registrations       │  │
│  │ KAFKA_TOPIC_RESULTS = event.registration.results      │  │
│  └────────────────────────────────────────────────────────┘  │
│                           ▲                                  │
│                           │ Override with                    │
└──────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌────────────────────────┐          ┌────────────────────────┐
│   .env File            │          │  Environment Variables │
│  ─────────────────────  │          │  ──────────────────── │
│  DEBUG=false           │          │  DEBUG=false          │
│  DATABASE_URL=...      │          │  DATABASE_URL=...     │
│  KAFKA_...=...         │          │  KAFKA_...=...        │
│                        │          │                       │
│  [Local Development]   │          │  [Container/CI/CD]    │
│                        │          │                       │
└────────────────────────┘          └────────────────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │   Runtime Config      │
                │   (pydantic Settings) │
                │                       │
                │ Used in App at        │
                │ startup               │
                └───────────────────────┘
```

---

## ⚡ Performance Characteristics

### Request Processing Timeline

```
Time (ms)    Event
─────────────────────────────────────────────────────────────
0            Client sends POST /registrations
1-2          Network latency
3            Request arrives at FastAPI
4-5          Pydantic validation
6            UUID generation
7-9          Kafka producer.send() call
10-12        Message serialization
13-25        Kafka broker write
26           Kafka acknowledge
27-28        Response serialization
29-30        Network latency
31-33        Total round-trip time (approx 30ms)

Characteristics:
✓ Non-blocking (async/await)
✓ Message persisted before response
✓ No database access in critical path
✓ Scalable to thousands/sec
```

### Kafka Topic Partitioning

```
Registration messages distributed by event_id:

Event 1 ──┐
Event 2 ──┤──> Partition 0 (even events)
Event 4 ──┤
Event 6 ──┘

Event 3 ──┐
Event 5 ──┤──> Partition 1 (odd events)
Event 7 ──┤
Event 9 ──┘

Benefits:
✓ In-order processing per event
✓ Parallel processing across events
✓ Load balanced across broker
```

---

## 🔒 Security Layers

```
┌──────────────────────────────────────────────────────────┐
│                      External Client                    │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │  Load Balancer / TLS        │
        │  (HTTPS termination)        │
        │  (IP Whitelist)             │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  CORS Middleware            │
        │  (Origin validation)        │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  Request Parsing            │
        │  (Size limits)              │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  Pydantic Validation        │
        │  (Type checking)            │
        │  (Email validation)         │
        │  (Field constraints)        │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  API Route Handler          │
        │  (Business logic)           │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  SQLAlchemy ORM             │
        │  (SQL injection prevention) │
        │  (Parameterized queries)    │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  PostgreSQL Database        │
        │  (Connection encryption)    │
        │  (User authentication)      │
        └─────────────────────────────┘
```

---

## 📈 Scaling Architecture

### Horizontal Scaling

```
Load Balancer
    │
    ├─> Registration Service #1 (Port 8001)
    ├─> Registration Service #2 (Port 8002)
    ├─> Registration Service #3 (Port 8003)
    └─> Registration Service #4 (Port 8004)
    
    All sharing:
    ├─> Kafka Cluster (distributed topics)
    ├─> PostgreSQL (shared database)
    └─> Redis (shared SSE queue - future)
    
    Each instance:
    ├─ In-memory request cache
    ├─ Connection pool
    └─ Kafka consumer group
```

---

## 📚 File Organization

```
registration-service/
├── app/
│   ├── __init__.py
│   ├── main.py                  ← FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            ← Settings management
│   │   ├── database.py          ← Database connection
│   │   └── kafka.py             ← Kafka producer
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py            ← Route aggregation
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routes/
│   │           ├── __init__.py
│   │           ├── registrations.py  ← Registration endpoints
│   │           └── sse.py            ← SSE endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── registration.py      ← SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── registration.py      ← Pydantic schemas
│   └── consumers/
│       ├── __init__.py
│       ├── registration_processor.py
│       └── sse_broadcaster.py
├── pyproject.toml               ← Dependencies
├── Dockerfile                   ← Container image
├── docker-compose.yml           ← Full stack
├── .env.example                 ← Environment template
└── alembic/                     ← Database migrations
    └── versions/
```

---

## ✅ Status Checklist

```
Architecture Documentation
  ☑ System architecture diagram
  ☑ Request/response flows
  ☑ Data flow sequences
  ☑ Module dependency graph
  ☑ Database schema

Implementation Files
  ☑ main.py (FastAPI app)
  ☑ database.py (SQLAlchemy)
  ☑ kafka.py (Producer)
  ☑ router.py (Routes)
  ☑ config.py (Settings)

Infrastructure
  ☑ Dockerfile
  ☑ docker-compose.yml
  ☑ .env.example
  
Automation
  ☑ quickstart.sh script
  ☑ Health checks
  ☑ Dependency checks

Documentation
  ☑ Setup guide
  ☑ Architecture guide
  ☑ Analysis document
  ☑ Visual reference
  ☑ API documentation
```

---
