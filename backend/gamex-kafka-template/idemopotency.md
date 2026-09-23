Here is how producer idempotency is handled using **`confluent-kafka` (v2.15)**, the official **Apache Kafka image (broker properties)**, and the async alternative **`aiokafka`** inside a FastAPI application.

---

### 1. `confluent-kafka` (v2.15) with FastAPI

`confluent-kafka-python` is a wrapper around the C library `librdkafka`.

> **Important Default:** Unlike Java (where idempotence is enabled by default since Kafka 3.0), `librdkafka` and `confluent-kafka` in Python default to `enable.idempotence = False`. You **must enable it explicitly**.

When `enable.idempotence = True` is set:

* It forces `acks = all` under the hood.
* It restricts `max.in.flight.requests.per.connection` to $\le 5$ to guarantee in-order delivery upon retries.
* The client tracks sequence numbers per partition and retries transient errors automatically without creating duplicate messages on the broker.

#### Implementation in FastAPI

In FastAPI, create a single shared producer during application startup using the `lifespan` handler, and call `producer.flush()` on shutdown to ensure pending buffers are committed:

* **Component:** **`confluent-kafka` (v2.15) / Python & FastAPI**
* **Option / Configuration:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from confluent_kafka import Producer
import json

# 1. Configure the idempotent producer
producer_conf = {
    "bootstrap.servers": "localhost:9092",
    "enable.idempotence": True,           # <-- Required: enables PID & sequence tracking
    "acks": "all",                        # Automatically set by idempotence
    "retries": 1000000,                   # Automatic retry for transient errors
    "max.in.flight.requests.per.connection": 5
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize single producer instance
    app.state.producer = Producer(producer_conf)
    yield
    # Shutdown: Flush uncommitted messages
    app.state.producer.flush(timeout=10)

app = FastAPI(lifespan=lifespan)

def delivery_callback(err, msg):
    if err:
        print(f"Message delivery failed: {err}")

@app.post("/invoices")
async def create_invoice(invoice: dict):
    producer: Producer = app.state.producer
    try:
        producer.produce(
            topic="raw_invoices",
            key=invoice["invoice_id"],
            value=json.dumps(invoice).encode("utf-8"),
            on_delivery=delivery_callback
        )
        # Serve delivery callbacks from previous requests without blocking
        producer.poll(0)
        return {"status": "accepted", "invoice_id": invoice["invoice_id"]}
    except BufferError:
        raise HTTPException(status_code=503, detail="Producer queue full")

```



---

### 2. Can This Be Handled on the Apache Kafka Broker / Docker Image?

**No, broker properties alone cannot compensate for a non-idempotent client.**

* **Why?** Idempotence requires a two-way handshake: the **client library** must allocate a Producer ID (PID), attach a monotonically increasing sequence number ($0, 1, 2 \dots$) to every message batch, and manage retries. If the client does not send sequence numbers, the broker has no way to detect whether an incoming message is a duplicate retry.
* **What the Broker Image DOES Enforce:**
In the official Apache Kafka Docker image (`apache/kafka:latest` or `confluentinc/cp-kafka`):
* Broker idempotence is enabled by default (`enable.idempotence` capability supported since Kafka 0.11 / default standard in Kafka 3.x+).
* You can enforce broker-side durability properties in `server.properties` or Docker environment variables:
```properties
# Minimum in-sync replicas that must acknowledge
min.insync.replicas=2
# Ensure transaction logs and metadata replicas are durable
offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2

```


* If cluster ACLs are active, the broker requires the producer to have the `IdempotentWrite` ACL permission (`cluster:IdempotentWrite`).



---

### 3. Can `aiokafka` Handle This?

**Yes.** `aiokafka` is an asyncio-native pure Python Kafka library that explicitly supports idempotent producing.

* **Key Difference vs `confluent-kafka`:**
* `confluent-kafka` runs in C (`librdkafka`) with synchronous callbacks and requires calling `.poll(0)` to trigger events.
* `aiokafka` is natively integrated with Python's `asyncio` event loop. You use standard `await producer.send_and_wait()`.



#### Implementation with `aiokafka` in FastAPI

* **Component:** **`aiokafka` & FastAPI**
* **Option / Configuration:**
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from aiokafka import AIOKafkaProducer
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize async producer with idempotence enabled
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
        enable_idempotence=True,  # <-- Automatically forces acks="all"
        max_batch_size=16384,
        linger_ms=10
    )
    await producer.start()
    app.state.producer = producer
    yield
    await producer.stop()

app = FastAPI(lifespan=lifespan)

@app.post("/invoices")
async def create_invoice(invoice: dict):
    producer: AIOKafkaProducer = app.state.producer
    payload = json.dumps(invoice).encode("utf-8")

    # Await delivery confirmation (guaranteed idempotent by broker & client)
    record_metadata = await producer.send_and_wait(
        topic="raw_invoices",
        key=invoice["invoice_id"].encode("utf-8"),
        value=payload
    )
    return {
        "status": "delivered",
        "partition": record_metadata.partition,
        "offset": record_metadata.offset
    }

```



---

### Summary Comparison

| Requirement | `confluent-kafka` (v2.15) | `aiokafka` | Apache Kafka Image / Broker |
| --- | --- | --- | --- |
| **Idempotence Option** | `conf = {"enable.idempotence": True}` | `AIOKafkaProducer(enable_idempotence=True)` | Supported natively (Kafka 3.0+ defaults). |
| **Default Setting** | `False` (must explicitly set `True`) | `False` (must explicitly set `True`) | Broker-side support is enabled. |
| **FastAPI Integration** | Uses event callbacks (`on_delivery`) and `producer.poll(0)` | Native `async` / `await producer.send_and_wait()` | N/A (runs on Docker / VM / Kubernetes). |
| **Performance** | Highest throughput (C-based engine). | Lower raw throughput than C, but simpler async Python code. | Handles sequence number deduplication per PID. |