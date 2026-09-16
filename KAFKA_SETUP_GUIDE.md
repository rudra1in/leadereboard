# Kafka Topic Setup - Complete Guide

## 🎯 Why Kafka Topics Matter

The registration flow depends on Kafka:

```
User Registration
       ↓
POST /registrations → Registration Service
       ↓
Save to Database
       ↓
Publish to Kafka Topic: event.registrations
       ↓
Kafka Consumer (SSE Broadcaster)
       ↓
Send SSE Event to Browser
       ↓
Show Confirmation Modal
```

**Without Kafka topics created**, the SSE stream won't work and users won't see confirmations!

---

## 📋 Topics Required

You need to create **2 Kafka topics**:

### Topic 1: `event.registrations`
```
Purpose: Registration events from the API
Partitions: 3
Replication Factor: 1
Retention: 7 days
```

### Topic 2: `event.registration.results`
```
Purpose: Confirmation results back to clients
Partitions: 3
Replication Factor: 1
Retention: 7 days
```

---

## 🚀 Setup Methods

### Method 1: Using Docker Compose (RECOMMENDED)

If using Docker Compose, Kafka topics are created automatically via initialization script.

**File:** `docker-compose.yml`

Add this to your Kafka service configuration:

```yaml
version: '3.8'

services:
  # ... other services ...

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: registration_kafka
    depends_on:
      zookeeper:
        condition: service_started
    ports:
      - "9092:9092"
      - "9101:9101"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions.sh", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - registration-network

  # Service to create topics automatically
  kafka-init:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      kafka:
        condition: service_healthy
    entrypoint: ['/bin/sh', '-c']
    command: |
      kafka-topics --bootstrap-server kafka:29092 --list &&
      kafka-topics --bootstrap-server kafka:29092 --create --if-not-exists --topic event.registrations --partitions 3 --replication-factor 1 &&
      kafka-topics --bootstrap-server kafka:29092 --create --if-not-exists --topic event.registration.results --partitions 3 --replication-factor 1 &&
      echo "Topics created successfully!"
    networks:
      - registration-network
    restart: on-failure

networks:
  registration-network:
    driver: bridge
```

### Method 2: Manual Topic Creation (If Already Running Kafka)

```bash
# Check Kafka container is running
docker ps | grep kafka

# Enter Kafka container
docker exec -it registration_kafka bash

# Create event.registrations topic
kafka-topics --bootstrap-server localhost:9092 \
  --create \
  --if-not-exists \
  --topic event.registrations \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=604800000 \
  --config compression.type=snappy

# Create event.registration.results topic
kafka-topics --bootstrap-server localhost:9092 \
  --create \
  --if-not-exists \
  --topic event.registration.results \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms=604800000 \
  --config compression.type=snappy

# Verify topics created
kafka-topics --bootstrap-server localhost:9092 --list
```

### Method 3: Using Kafka UI (Visual Method)

If you have Kafka UI running (port 8080):

1. **Open browser:** `http://localhost:8080`
2. **Click:** "Clusters" → Select your cluster
3. **Click:** "Topics" → "+ Create Topic"
4. **Create first topic:**
   - Name: `event.registrations`
   - Partitions: 3
   - Replication Factor: 1
   - Click "Create"
5. **Repeat for second topic:**
   - Name: `event.registration.results`
   - Partitions: 3
   - Replication Factor: 1
   - Click "Create"

---

## ✅ Verification

### Check If Topics Exist

**Method 1: Using Docker**
```bash
docker exec registration_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list
```

**Expected output:**
```
__consumer_offsets
event.registrations
event.registration.results
```

### Method 2: Using Kafka UI
```
http://localhost:8080/ui/clusters/local/topics
```

Should see both topics listed with:
- ✅ `event.registrations`
- ✅ `event.registration.results`

### Method 3: Describe Topic Details
```bash
docker exec registration_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic event.registrations
```

Expected output:
```
Topic: event.registrations
PartitionCount: 3
ReplicationFactor: 1
Configs: compression.type=snappy
Partition: 0  Leader: 1  Replicas: 1  Isr: 1
Partition: 1  Leader: 1  Replicas: 1  Isr: 1
Partition: 2  Leader: 1  Replicas: 1  Isr: 1
```

---

## 🔧 Configuration Details

### Topic: `event.registrations`

**What it's for:** Registration events coming from users

**Configuration:**
```
Name:                  event.registrations
Partitions:            3
Replication Factor:    1
Retention Time:        7 days (604800000 ms)
Compression:           snappy
Cleanup Policy:        delete (default)
Min In-Sync Replicas:  1
```

**Message Format:**
```json
{
  "registration_id": "uuid-1234-5678",
  "event_id": 1,
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "timestamp": "2026-09-15T10:30:00Z"
}
```

### Topic: `event.registration.results`

**What it's for:** Confirmation results sent back to browsers via SSE

**Configuration:**
```
Name:                  event.registration.results
Partitions:            3
Replication Factor:    1
Retention Time:        7 days (604800000 ms)
Compression:           snappy
Cleanup Policy:        delete (default)
Min In-Sync Replicas:  1
```

**Message Format:**
```json
{
  "registration_id": "uuid-1234-5678",
  "status": "confirmed",
  "message": "Registration confirmed!",
  "timestamp": "2026-09-15T10:30:05Z"
}
```

---

## 🔄 Data Flow Through Kafka

```
1. USER SUBMITS REGISTRATION
   └─ Full Name, Email, Phone
   └─ Event ID

2. REGISTRATION SERVICE
   ├─ Validates input
   ├─ Saves to PostgreSQL
   ├─ Generates registration_id
   └─ Publishes to Kafka topic: event.registrations
      {
        "registration_id": "uuid-123",
        "event_id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
      }

3. KAFKA STORES MESSAGE
   └─ Topic: event.registrations
   └─ Partition: 0, 1, or 2 (based on registration_id)
   └─ Retained for 7 days

4. KAFKA CONSUMERS LISTEN
   ├─ registration_processor.py (stores additional processing)
   └─ sse_broadcaster.py (sends to SSE clients)

5. SSE BROADCASTER
   ├─ Reads from Kafka
   ├─ Formats confirmation message
   ├─ Publishes to event.registration.results
   └─ Sends SSE event to connected browsers

6. BROWSER RECEIVES SSE EVENT
   ├─ Parses confirmation data
   ├─ Updates UI state
   ├─ Shows confirmation modal
   └─ Displays all registration details

7. MESSAGE RETENTION
   └─ After 7 days, messages auto-deleted
      (can be configured)
```

---

## 📊 Topic Partitioning Strategy

### Why 3 Partitions?

```
Partitions: 3
└─ Allows parallel processing
└─ Better throughput
└─ Fault tolerance
└─ Scaling capability

Distribution:
Partition 0: registration_id hash % 3 = 0
Partition 1: registration_id hash % 3 = 1
Partition 2: registration_id hash % 3 = 2

Consumer Group Can Have:
Up to 3 consumers (one per partition)
Or 1 consumer consuming all
Or 2 consumers (load balanced)
```

### Replication Factor: 1

```
Why 1 (Not 3)?
└─ Development/Testing environment
└─ Single broker setup
└─ Speed over availability
└─ Lower resource usage

For Production: Use 3
└─ Better fault tolerance
└─ Data redundancy
└─ High availability
```

---

## 🐛 Troubleshooting Kafka Topics

### Issue 1: Topics Don't Exist After Starting

**Problem:**
```bash
kafka-topics --list
# Shows: Only __consumer_offsets
# Missing: event.registrations, event.registration.results
```

**Solution:**
```bash
# Create topics manually
docker exec registration_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic event.registrations \
  --partitions 3 \
  --replication-factor 1

docker exec registration_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic event.registration.results \
  --partitions 3 \
  --replication-factor 1
```

### Issue 2: Kafka Container Not Running

**Problem:**
```
Error: Cannot connect to Kafka
```

**Solution:**
```bash
# Check if running
docker ps | grep kafka

# If not running, start it
docker-compose up -d kafka zookeeper

# Wait for health check (30 seconds)
docker-compose logs -f kafka | grep "started"
```

### Issue 3: SSE Not Sending Confirmations

**Problem:**
- User submits registration
- No confirmation appears
- Form stuck on "Processing..."

**Cause:** Topics might not exist or Kafka consumers not running

**Solution:**
```bash
# 1. Verify topics exist
docker exec registration_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list | grep event.registration

# 2. Check for messages in topic
docker exec registration_kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic event.registrations \
  --from-beginning \
  --timeout-ms 5000

# 3. Verify consumers are running
docker-compose logs -f sse_broadcaster
docker-compose logs -f registration_processor

# 4. Check registration service logs
docker-compose logs -f registration-service
```

### Issue 4: Message Not Being Processed

**Problem:**
```
Messages appear in Kafka but SSE doesn't send confirmation
```

**Solution:**
```bash
# Check SSE broadcaster logs
docker-compose logs sse_broadcaster

# Expected:
# "Listening to event.registrations topic"
# "Processing registration: uuid-123"
# "Publishing to event.registration.results"

# Check registration processor logs
docker-compose logs registration_processor

# Expected:
# "Consumer started"
# "Processing registration: uuid-123"
```

---

## 📝 Complete Setup Checklist

- [ ] **Zookeeper running**
  ```bash
  docker-compose logs zookeeper | grep "started"
  ```

- [ ] **Kafka broker running**
  ```bash
  docker-compose logs kafka | grep "started"
  ```

- [ ] **Topics created**
  ```bash
  docker exec registration_kafka kafka-topics \
    --bootstrap-server localhost:9092 --list | grep event.registration
  ```

- [ ] **Registration service running**
  ```bash
  curl http://localhost:8000/health
  # {"status":"ok"}
  ```

- [ ] **SSE broadcaster running** (in background)
  ```bash
  docker-compose logs sse_broadcaster | grep "Listening"
  ```

- [ ] **Kafka UI accessible** (optional)
  ```
  http://localhost:8080
  ```

- [ ] **Test registration flow**
  - Go to http://localhost:4321/events/event-register
  - Fill form and submit
  - Wait for confirmation modal
  - Check Kafka UI for messages

---

## 🔍 Monitoring Kafka

### Using Kafka UI (Recommended)

**Access:** `http://localhost:8080`

**Check:**
1. Clusters → Your Cluster
2. Topics → event.registrations
   - See partition count
   - View messages in real-time
   - Check consumer lag

### Using Command Line

**List all topics:**
```bash
docker exec registration_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list
```

**Describe a topic:**
```bash
docker exec registration_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic event.registrations
```

**Monitor messages in real-time:**
```bash
docker exec registration_kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic event.registrations \
  --from-beginning \
  --property print.timestamp=true \
  --property print.key=true
```

**Count messages:**
```bash
docker exec registration_kafka kafka-run-class \
  kafka.tools.JmxTool \
  --object-name kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec \
  --attributes Count
```

---

## 🧹 Cleanup (If Needed)

**Delete a topic:**
```bash
docker exec registration_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic event.registrations
```

**Reset consumer group:**
```bash
docker exec registration_kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group registration-processor \
  --reset-offsets \
  --to-earliest \
  --execute \
  --all-topics
```

**Purge all messages from topic:**
```bash
# Set retention to 1 minute, wait, then reset
docker exec registration_kafka kafka-configs \
  --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name event.registrations \
  --alter \
  --add-config retention.ms=60000
```

---

## 📚 Full Integration Example

### Complete Docker Setup with Kafka Topics

```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"
    networks:
      - registration-network

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      zookeeper:
        condition: service_started
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    healthcheck:
      test: ["CMD", "kafka-broker-api-versions.sh", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - registration-network

  # Auto-create topics on startup
  kafka-init:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      kafka:
        condition: service_healthy
    entrypoint: ['/bin/sh', '-c']
    command: |
      echo "Waiting for Kafka to be ready..."
      sleep 10
      echo "Creating topics..."
      kafka-topics --bootstrap-server kafka:29092 --create --if-not-exists \
        --topic event.registrations \
        --partitions 3 \
        --replication-factor 1 \
        --config retention.ms=604800000 \
        --config compression.type=snappy
      kafka-topics --bootstrap-server kafka:29092 --create --if-not-exists \
        --topic event.registration.results \
        --partitions 3 \
        --replication-factor 1 \
        --config retention.ms=604800000 \
        --config compression.type=snappy
      echo "Topics created successfully!"
      kafka-topics --bootstrap-server kafka:29092 --list
    networks:
      - registration-network
    restart: on-failure

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    depends_on:
      - kafka
    networks:
      - registration-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppassword
      POSTGRES_DB: appdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - registration-network

  registration-service:
    build:
      context: ./apps/registration-service
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://appuser:apppassword@postgres:5432/appdb
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      DEBUG: "false"
    depends_on:
      postgres:
        condition: service_started
      kafka-init:
        condition: service_completed_successfully
    networks:
      - registration-network

networks:
  registration-network:
    driver: bridge

volumes:
  postgres_data:
```

---

## ✅ Final Verification

After complete setup, verify everything works:

```bash
# 1. Check all services running
docker-compose ps
# All should show: Up

# 2. Verify topics exist
docker exec registration_kafka kafka-topics \
  --bootstrap-server localhost:9092 --list
# Should show: event.registrations, event.registration.results

# 3. Test registration flow
# Go to: http://localhost:4321/events/event-register
# Fill form and submit
# Should see confirmation modal in 5-10 seconds

# 4. Monitor Kafka messages
docker exec registration_kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic event.registrations \
  --from-beginning
# Should show your registration message in JSON format
```

---

## 📌 Summary

**Kafka topics are CRITICAL for:**
- ✅ Real-time registration confirmations
- ✅ SSE streaming to browsers
- ✅ Asynchronous message processing
- ✅ Decoupling services
- ✅ Event sourcing

**Without topics setup:**
- ❌ Registration service can't publish events
- ❌ SSE broadcaster won't work
- ❌ Users won't see confirmations
- ❌ Application appears broken

**Always create Kafka topics BEFORE running registration service!**

---

