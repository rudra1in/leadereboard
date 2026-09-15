# Registration Service - FastAPI Architecture Analysis

## 📋 Executive Summary
The Registration Service is a **FastAPI microservice** designed for event registration handling with asynchronous Kafka-based event processing and Server-Sent Events (SSE) for real-time client updates.

## 🏗️ Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           API Layer (v1)                             │   │
│  │  ├─ POST /registrations        → Create Registration│   │
│  │  └─ SSE /sse/registrations/:id → Real-time Updates │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Core Services                                │   │
│  │  ├─ Kafka Producer (aiokafka)                        │   │
│  │  ├─ Configuration Management                         │   │
│  │  └─ Database Connection                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Data Layer                                   │   │
│  │  ├─ SQLAlchemy ORM (async)                           │   │
│  │  ├─ PostgreSQL Database                              │   │
│  │  └─ Pydantic Schemas                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │       Kafka Cluster                     │
        ├─────────────────────────────────────────┤
        │  Topic: event.registrations             │
        │  Topic: event.registration.results      │
        └─────────────────────────────────────────┘
                      ↓
        ┌─────────────────────────────────────────┐
        │  SSE Broadcaster (Consumer)             │
        │  - Consumes registration results        │
        │  - Broadcasts to connected clients      │
        │  - Uses in-memory queue (Redis in Prod) │
        └─────────────────────────────────────────┘
```

## 🔄 Request Flow

### Registration Creation Flow
```
1. Client: POST /api/v1/registrations
   ↓
2. Handler: create_registration(payload)
   - Generate unique registration_id (UUID)
   - Validate email (Pydantic EmailStr)
   ↓
3. Kafka Producer: Send message to 'event.registrations' topic
   {
     "registration_id": "uuid",
     "event_id": 123,
     "full_name": "John Doe",
     "email": "john@example.com",
     "phone": "+1234567890"
   }
   ↓
4. Response: HTTP 202 ACCEPTED
   {
     "message": "Registration submitted successfully",
     "registration_id": "uuid",
     "status": "processing"
   }
```

### Real-time Update Flow (SSE)
```
1. Client: GET /api/v1/sse/registrations/{registration_id}
   ↓
2. Server: Establish SSE connection
   - Register client queue in sse_clients dict
   - Send keepalive ping every 15 seconds
   ↓
3. SSE Broadcaster Consumer:
   - Listens to 'event.registration.results' topic
   - Receives: {registration_id, status, ...}
   ↓
4. Broadcast: Push update to connected client
   Event: "registration_update"
   Data: {registration_id, status, ...}
   ↓
5. Client: Receives real-time update via EventSource
```

## 📁 Project Structure

```
apps/registration-service/
├── app/
│   ├── __init__.py                          [MISSING]
│   ├── main.py                              [MISSING]
│   ├── api/
│   │   ├── __init__.py                      [MISSING]
│   │   └── v1/
│   │       ├── __init__.py                  [MISSING]
│   │       └── routes/
│   │           ├── __init__.py              [MISSING]
│   │           ├── registrations.py         ✓ (POST)
│   │           └── sse.py                   ✓ (SSE)
│   ├── core/
│   │   ├── __init__.py                      [MISSING]
│   │   ├── config.py                        ✓
│   │   ├── database.py                      [MISSING]
│   │   └── kafka.py                         [MISSING - exists as kafka-producer.py]
│   ├── models/
│   │   ├── __init__.py                      [MISSING]
│   │   └── registration.py                  ✓
│   ├── schemas/
│   │   ├── __init__.py                      [MISSING]
│   │   └── registration.py                  ✓
│   ├── consumers/
│   │   ├── __init__.py                      [MISSING]
│   │   ├── registration_processor.py        ✓
│   │   └── sse_broadcaster.py               ✓
│   └── alembic/                             [MISSING]
│       └── versions/
├── pyproject.toml                           [MISSING]
├── Dockerfile                               [MISSING]
├── docker-compose.yml                       [MISSING]
├── .env                                     [MISSING]
└── alembic.ini                              [MISSING]
```

## 🔧 Current Implementation Details

### 1. **Configuration (core/config.py)**
- Uses Pydantic Settings with `.env` support
- Key settings:
  - `DATABASE_URL`: PostgreSQL async connection
  - `KAFKA_BOOTSTRAP_SERVERS`: Kafka cluster
  - `KAFKA_TOPIC_REGISTRATIONS`: Input topic
  - `KAFKA_TOPIC_RESULTS`: Output topic (for SSE)

### 2. **Database Model (models/registration.py)**
- SQLAlchemy ORM with async support
- Table: `registrations`
- Fields:
  - `id` (PK)
  - `event_id` (indexed)
  - `full_name`
  - `email` (indexed)
  - `phone` (optional)
  - `status` (pending|confirmed|rejected)
  - `created_at` (auto-timestamped)

### 3. **API Routes**
- **POST /registrations**: Async registration submission
  - Input: RegistrationCreate (Pydantic validated)
  - Output: HTTP 202 (fire-and-forget pattern)
  - Side effect: Message published to Kafka

- **GET /sse/registrations/{registration_id}**: SSE endpoint
  - Maintains connection for real-time updates
  - Implements keepalive with 15s timeout
  - Auto-cleanup on disconnect

### 4. **Kafka Integration**
- **Producer** (`core/kafka-producer.py`):
  - Async producer using aiokafka
  - JSON serialization
  - Fire-and-wait pattern
  
- **Broadcaster Consumer** (`consumers/sse_broadcaster.py`):
  - Listens to results topic
  - Routes updates to connected SSE clients
  - In-memory dictionary (TODO: Redis for distributed setup)

## 🚨 Identified Issues & Gaps

### Critical Missing Files
1. **app/main.py** - FastAPI application factory
2. **app/core/database.py** - SQLAlchemy async engine
3. **app/api/router.py** - Route aggregation
4. **pyproject.toml** - Dependency specification
5. **Dockerfile** - Container configuration
6. **alembic.ini + migrations** - Database versioning

### Code Quality Issues
1. **Import paths** - `core/kafka-producer.py` should be `core/kafka.py`
2. **Missing __init__.py** files throughout
3. **No error handling** in API routes
4. **No database integration** - models exist but not used
5. **No validation** - e.g., event_id existence check
6. **Missing get_db()** dependency for database access
7. **Hardcoded values** in registration_processor.py
8. **No logging configuration**
9. **No health check endpoint**

### Architecture Concerns
1. **SSE Broadcaster** runs as separate process - no integration
2. **In-memory SSE client store** - not scalable
3. **No retry logic** for Kafka operations
4. **No database persistence** of registration status
5. **No API authentication/authorization**
6. **No request validation** of event_id existence
7. **Missing transaction handling**

## 📊 Dependency Stack

```
Core Framework:
├── fastapi>=0.115.0          (Web framework)
├── uvicorn[standard]>=0.30.0 (ASGI server)

Database:
├── sqlalchemy[asyncio]>=2.0.36
├── asyncpg>=0.29.0           (PostgreSQL async driver)
├── alembic>=1.13.3           (Migrations)

Async/Messaging:
├── aiokafka>=0.11.0          (Kafka async client)

Validation:
├── pydantic[email]>=2.9.0    (Data validation)
├── pydantic-settings>=2.5.2  (Config management)

Real-time:
├── sse-starlette>=2.1.3      (SSE support)
├── greenlet>=3.1.0           (Context switching)
```

## 🚀 Recommended Fixes Priority

### Phase 1 (Critical - Make it runnable)
1. Create missing __init__.py files
2. Create app/main.py with proper lifespan
3. Create app/core/database.py
4. Rename kafka-producer.py → kafka.py
5. Create app/api/router.py
6. Create pyproject.toml with dependencies

### Phase 2 (High - Make it production-ready)
1. Add Dockerfile
2. Add alembic migrations
3. Add error handling in routes
4. Add input validation (event_id existence)
5. Add logging throughout
6. Add health check endpoint

### Phase 3 (Medium - Improve architecture)
1. Replace in-memory SSE with Redis
2. Add request authentication
3. Add database transaction handling
4. Move SSE broadcaster to background task
5. Add retry logic to Kafka operations

### Phase 4 (Polish)
1. Add comprehensive API documentation
2. Add request/response examples
3. Add integration tests
4. Add performance monitoring
5. Add graceful shutdown handling

## 🔐 Security Considerations

- [ ] Email validation (currently basic)
- [ ] Rate limiting on registration endpoint
- [ ] CORS configuration (currently open)
- [ ] Request timeout configuration
- [ ] SQL injection prevention (SQLAlchemy ORM handles)
- [ ] Input sanitization
- [ ] Audit logging for registrations
- [ ] PII handling and GDPR compliance

## 📈 Performance Metrics to Monitor

1. **Registration throughput**: registrations/second
2. **Kafka lag**: consumer group lag
3. **SSE connection count**: concurrent clients
4. **Database query time**: p50, p95, p99
5. **Event processing latency**: submission to delivery time
6. **Error rates**: failed registrations percentage

## 🔗 Integration Points

- **Upstream**: Registration clients (web/mobile)
- **Kafka**: Event stream platform
- **Database**: PostgreSQL for state
- **Downstream**: Registration processor, notification service

---
