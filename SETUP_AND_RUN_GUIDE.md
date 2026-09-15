# Registration Service - Setup and Run Guide

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

#### Prerequisites
- Docker
- Docker Compose

#### Steps

```bash
# Navigate to registration service directory
cd apps/registration-service

# Copy environment template
cp .env.example .env

# Start all services (PostgreSQL, Kafka, Registration Service)
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f registration-service

# Stop services
docker-compose down
```

**Service Endpoints:**
- Registration Service: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Kafka UI: http://localhost:8080

---

### Option 2: Local Development Setup

#### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Kafka 7.0+
- pip/uv

#### Installation Steps

1. **Clone and navigate to the service**
```bash
cd apps/registration-service
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
# Using pip
pip install -e .

# OR using uv (faster)
uv pip install -e .
```

4. **Setup environment**
```bash
# Copy and configure environment
cp .env.example .env

# Edit .env with your local settings
# Make sure these match your local setup:
# - DATABASE_URL (PostgreSQL connection)
# - KAFKA_BOOTSTRAP_SERVERS (Kafka broker)
```

5. **Ensure services are running**
```bash
# PostgreSQL should be running (default: localhost:5432)
psql -U postgres -c "CREATE DATABASE app;" 2>/dev/null || true

# Kafka should be running (default: localhost:9092)
# Test connection: python -c "from aiokafka import AIOKafkaProducer"
```

6. **Initialize database**
```bash
# Create tables (auto-created on first run)
python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"
```

7. **Run the service**
```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# OR production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

8. **(Optional) Run SSE Broadcaster in separate terminal**
```bash
python app/consumers/sse_broadcaster.py
```

#### Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","service":"registration-service","version":"0.1.0"}

# Access API documentation
open http://localhost:8000/docs
```

---

## 📋 API Endpoints

### 1. Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "ok",
  "service": "registration-service",
  "version": "0.1.0"
}
```

### 2. Create Registration
```
POST /api/v1/registrations
Content-Type: application/json

{
  "event_id": 1,
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

**Response (HTTP 202):**
```json
{
  "message": "Registration submitted successfully",
  "registration_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

### 3. Real-time Status Updates (SSE)
```
GET /api/v1/sse/registrations/{registration_id}

Accept: text/event-stream
```

**Response Stream:**
```
event: registration_update
data: {"registration_id":"550e8400-e29b-41d4-a716-446655440000","status":"confirmed","timestamp":"2024-01-15T10:30:00Z"}

event: ping
data: keepalive
```

---

## 🧪 Testing the Service

### Using curl

```bash
# 1. Create a registration
REGISTRATION_ID=$(curl -X POST http://localhost:8000/api/v1/registrations \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "full_name": "Test User",
    "email": "test@example.com",
    "phone": "+1234567890"
  }' | jq -r '.registration_id')

echo "Registration ID: $REGISTRATION_ID"

# 2. Subscribe to SSE updates (in another terminal)
curl -N http://localhost:8000/api/v1/sse/registrations/$REGISTRATION_ID \
  -H "Accept: text/event-stream"
```

### Using Python

```python
import asyncio
import httpx
import json

async def test_registration():
    async with httpx.AsyncClient() as client:
        # Create registration
        response = await client.post(
            "http://localhost:8000/api/v1/registrations",
            json={
                "event_id": 1,
                "full_name": "Test User",
                "email": "test@example.com",
                "phone": "+1234567890"
            }
        )
        
        registration = response.json()
        registration_id = registration["registration_id"]
        
        print(f"Registration created: {registration_id}")
        print(f"Status: {registration['status']}")
        
        # Subscribe to updates
        async with client.stream(
            "GET",
            f"http://localhost:8000/api/v1/sse/registrations/{registration_id}"
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    print(f"Update: {line[6:]}")

asyncio.run(test_registration())
```

### Using JavaScript/Node.js

```javascript
// Test with EventSource
const registrationId = "550e8400-e29b-41d4-a716-446655440000";
const eventSource = new EventSource(
  `/api/v1/sse/registrations/${registrationId}`
);

eventSource.addEventListener("registration_update", (event) => {
  console.log("Status update:", JSON.parse(event.data));
});

eventSource.addEventListener("ping", (event) => {
  console.log("Keep-alive received");
});

eventSource.addEventListener("error", (event) => {
  console.error("Connection error:", event);
  eventSource.close();
});
```

---

## 📊 Monitoring

### Using Docker

```bash
# View service logs
docker-compose logs registration-service -f

# View all logs
docker-compose logs -f

# Check service status
docker-compose ps

# Access container shell
docker-compose exec registration-service /bin/bash
```

### Check Kafka Topics

```bash
# List topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# View messages in registrations topic
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic event.registrations \
  --from-beginning

# View messages in results topic
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic event.registration.results \
  --from-beginning
```

### Check Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d app

# List tables
\dt

# Query registrations
SELECT * FROM registrations;

# Check connection stats
SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
```

### Kafka UI

Access the Kafka UI at http://localhost:8080 to:
- View topics and partitions
- Monitor consumer groups
- Inspect messages
- Check broker metrics

---

## 🐛 Troubleshooting

### Service won't start

```bash
# Check if ports are in use
lsof -i :8000   # Registration Service
lsof -i :5432   # PostgreSQL
lsof -i :9092   # Kafka

# Kill process on port
lsof -ti:8000 | xargs kill -9
```

### Database connection errors

```bash
# Verify PostgreSQL is running
docker-compose logs postgres

# Check connection string
psql postgresql://postgres:postgres@localhost:5432/app

# Reset database
docker-compose down -v  # Remove volumes
docker-compose up postgres -d
```

### Kafka connection errors

```bash
# Verify Kafka is running
docker-compose logs kafka

# Test broker connection
docker-compose exec kafka kafka-broker-api-versions \
  --bootstrap-server localhost:9092

# Check Zookeeper
docker-compose logs zookeeper
```

### SSE not updating

```bash
# Verify broadcaster is running
docker-compose logs registration-service | grep "broadcast"

# Check Kafka consumer group
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --list

# Inspect consumer group
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group sse-broadcaster \
  --describe
```

---

## 📦 Production Deployment

### Before Deploying

1. **Update environment variables** (use secrets management)
   ```bash
   cp .env.example .env.production
   # Use environment-specific values
   ```

2. **Enable database migrations**
   - Set up Alembic for schema management
   - Run migrations on deployment

3. **Configure Kafka** for production
   - Use multiple brokers
   - Configure replication factor
   - Set up monitoring

4. **Update CORS settings**
   - Restrict `allow_origins` to specific domains
   - Remove `*` wildcard

5. **Enable authentication**
   - Add API key validation
   - Implement JWT tokens if needed

6. **Set up monitoring**
   - Application metrics (Prometheus)
   - Log aggregation (ELK stack)
   - Health checks
   - Alerting

7. **Scale considerations**
   - Replace in-memory SSE with Redis
   - Use Kubernetes for orchestration
   - Configure load balancing
   - Set up auto-scaling

### Docker Compose Production Deployment

```bash
# Build with production settings
docker-compose -f docker-compose.yml build

# Start with replicas
docker-compose -f docker-compose.yml up -d --scale registration-service=3

# Monitor
docker-compose logs -f registration-service
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests:
- `deployment.yaml` - Service deployment
- `service.yaml` - Service exposure
- `configmap.yaml` - Configuration
- `secret.yaml` - Sensitive data
- `ingress.yaml` - External access

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [aiokafka Documentation](https://aiokafka.readthedocs.io/)
- [Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html)

---

## 🔄 Development Workflow

### Making Changes

```bash
# 1. Make code changes
# 2. Run tests
pytest tests/ -v

# 3. Check code style
black app/
flake8 app/

# 4. Type checking
mypy app/

# 5. Restart service
docker-compose restart registration-service
```

### Adding Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head

# Downgrade if needed
alembic downgrade -1
```

---

## ✅ Checklist

- [ ] Prerequisites installed (Docker, Python 3.12+)
- [ ] Repository cloned
- [ ] Environment variables configured
- [ ] Services started successfully
- [ ] Health check endpoint responding
- [ ] API documentation accessible
- [ ] Test registration created
- [ ] SSE updates working
- [ ] Logs checked for errors
- [ ] Database tables created

---
