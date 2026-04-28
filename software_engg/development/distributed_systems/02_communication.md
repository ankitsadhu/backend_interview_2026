# Communication in Distributed Systems

## Synchronous vs Asynchronous Communication

```
SYNCHRONOUS (Request-Response):
  Client ──request──→ Server
  Client ←─response── Server
  (Client blocks/waits)

ASYNCHRONOUS (Message-Based):
  Producer ──message──→ [  Queue  ] ──message──→ Consumer
  (Producer continues immediately)
```

| Aspect | Synchronous | Asynchronous |
|--------|------------|--------------|
| **Coupling** | Tight (both must be running) | Loose (producer doesn't know consumer) |
| **Latency** | Caller waits for response | Fire-and-forget (or poll later) |
| **Error handling** | Immediate error response | Dead letter queues, retry policies |
| **Throughput** | Limited by slowest service | Buffered by queue |
| **Use case** | Real-time queries, user-facing APIs | Event processing, background jobs |

---

## RPC (Remote Procedure Call)

Makes a **remote service call look like a local function call**. Abstracts the network.

```
┌──────────────┐          ┌──────────────┐
│   Client      │          │   Server      │
│  ┌─────────┐  │  network │  ┌─────────┐  │
│  │  Client  │──┼──────────┼─▶│  Server  │  │
│  │  Stub    │  │          │  │  Stub    │  │
│  └─────────┘  │          │  └─────────┘  │
│               │          │               │
│ user.getById  │          │ def getById() │
│   (123)       │          │   → query DB  │
└──────────────┘          └──────────────┘

Steps:
1. Client calls stub (looks like local function)
2. Stub serializes arguments → sends over network
3. Server stub deserializes → calls actual function
4. Result serialized → sent back to client stub
5. Client stub deserializes → returns to caller
```

### Leaky Abstractions of RPC

| Local Function Call | RPC |
|--------------------|-----|
| Always reaches the function | Network may fail |
| Returns or throws | May timeout (no response at all) |
| Deterministic latency (~ns) | Variable latency (~ms to seconds) |
| Single machine failure | Partial failure (client up, server down) |
| Pass by reference possible | Must serialize everything |

---

## REST vs gRPC vs GraphQL

### REST (Representational State Transfer)

```http
GET    /api/users/123        → Read user
POST   /api/users            → Create user
PUT    /api/users/123        → Full update
PATCH  /api/users/123        → Partial update
DELETE /api/users/123        → Delete user

Response: JSON
Content-Type: application/json

{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com"
}
```

### gRPC (Google Remote Procedure Call)

```protobuf
// user.proto — Protocol Buffers definition
syntax = "proto3";

service UserService {
  rpc GetUser (GetUserRequest) returns (User);
  rpc ListUsers (ListUsersRequest) returns (stream User);  // Server streaming
  rpc CreateUsers (stream User) returns (CreateResponse);   // Client streaming
  rpc Chat (stream Message) returns (stream Message);       // Bidirectional
}

message GetUserRequest {
  int32 id = 1;
}

message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
```

### Comparison

| Feature | REST | gRPC | GraphQL |
|---------|------|------|---------|
| **Protocol** | HTTP/1.1 or HTTP/2 | HTTP/2 (always) | HTTP/1.1 or HTTP/2 |
| **Payload** | JSON (text) | Protobuf (binary) | JSON |
| **Contract** | OpenAPI/Swagger (optional) | `.proto` file (required) | Schema (required) |
| **Streaming** | Limited (SSE, WebSocket) | Built-in (4 types) | Subscriptions |
| **Browser support** | Native | Needs grpc-web proxy | Native |
| **Performance** | Good | Excellent (2-10x faster) | Good |
| **Code generation** | Optional | Built-in (multi-language) | Optional |
| **Best for** | External/public APIs | Internal microservices | Flexible client queries |

---

## Serialization Formats

How data is encoded for transmission.

| Format | Type | Speed | Size | Schema | Use Case |
|--------|------|-------|------|--------|----------|
| **JSON** | Text | Slow | Large | None | REST APIs, config |
| **Protocol Buffers** | Binary | Fast | Small | `.proto` | gRPC, internal services |
| **Avro** | Binary | Fast | Small | JSON schema | Kafka, data pipelines |
| **MessagePack** | Binary | Fast | Small | None | Redis, general IPC |
| **Thrift** | Binary | Fast | Small | `.thrift` | Facebook services |
| **BSON** | Binary | Medium | Medium | None | MongoDB |

### Schema Evolution

How do you change the schema without breaking existing consumers?

```
Protocol Buffers — Forward & Backward Compatible:

Version 1:                    Version 2:
message User {                message User {
  int32 id = 1;                int32 id = 1;
  string name = 2;             string name = 2;
}                               string email = 3;  ← New field (optional)
                              }

Old reader + new data → ignores unknown field 3 (forward compatible)
New reader + old data → email is empty/default (backward compatible)

Rules:
  ✅ Add optional fields with new field numbers
  ✅ Remove optional fields (old number never reused)
  ❌ Never change field numbers
  ❌ Never change field types (int → string)
  ❌ Never remove required fields
```

---

## Message Queues

Decouple producers from consumers. Messages are **buffered** in the queue.

```
                    ┌──────────────────┐
Producer A ──msg──▶ │                  │ ──msg──▶ Consumer 1
Producer B ──msg──▶ │   Message Queue  │ ──msg──▶ Consumer 2
                    │  (RabbitMQ, SQS) │
                    └──────────────────┘

Key properties:
  - Messages delivered to ONE consumer (competing consumers)
  - Messages persist until acknowledged
  - FIFO ordering (usually per-partition/queue)
  - Dead letter queue for failed messages
```

### Queue vs Topic (Pub/Sub)

```
QUEUE (Point-to-Point):           TOPIC (Publish-Subscribe):
  Producer → [Queue] → Consumer     Publisher → [Topic] → Subscriber A
  Each message to ONE consumer                          → Subscriber B
  (load balancing)                                      → Subscriber C
                                    Each message to ALL subscribers
                                    (fan-out / broadcast)
```

### Popular Message Brokers

| Broker | Model | Ordering | Persistence | Use Case |
|--------|-------|----------|-------------|----------|
| **RabbitMQ** | Queue + Exchange routing | Per-queue FIFO | Disk + memory | Task queues, RPC |
| **Apache Kafka** | Distributed log (topics + partitions) | Per-partition | Disk (append-only) | Event streaming, data pipelines |
| **Amazon SQS** | Managed queue | Best-effort (FIFO available) | Managed | Serverless, AWS-native |
| **Amazon SNS** | Managed pub/sub | No ordering guarantee | Managed | Fan-out notifications |
| **Redis Streams** | In-memory log | Per-stream | Optional | Real-time, low-latency |
| **NATS** | Lightweight pub/sub | Per-subject | Optional (JetStream) | Cloud-native, IoT |

---

## Apache Kafka Deep Dive

```
┌────────────────────────────────────────────────────────┐
│                    Kafka Cluster                        │
│                                                        │
│  Topic: "orders"                                       │
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │  Partition 0     │  │  Partition 1     │             │
│  │  [msg0][msg1]... │  │  [msg0][msg1]... │             │
│  │  Leader: Broker1 │  │  Leader: Broker2 │             │
│  │  Replica: Broker2│  │  Replica: Broker3│             │
│  └─────────────────┘  └─────────────────┘             │
│                                                        │
│  Consumer Group: "order-service"                       │
│   Consumer A reads Partition 0                         │
│   Consumer B reads Partition 1                         │
│   (parallelism = number of partitions)                 │
└────────────────────────────────────────────────────────┘
```

### Kafka Key Concepts

| Concept | Description |
|---------|-------------|
| **Topic** | Named log/stream of records (like a table) |
| **Partition** | Ordered, immutable sequence within a topic |
| **Offset** | Sequential ID of message within a partition |
| **Producer** | Publishes messages to a topic |
| **Consumer** | Reads messages from a topic |
| **Consumer Group** | Set of consumers sharing the work (each partition → one consumer) |
| **Broker** | Kafka server that stores data |
| **Replication** | Each partition replicated across brokers for fault tolerance |

### Kafka Guarantees

```
Producer:
  acks=0  → Fire and forget (fastest, may lose data)
  acks=1  → Leader acknowledges (fast, may lose if leader crashes)
  acks=all → All in-sync replicas acknowledge (safest, slowest)

Consumer:
  At-most-once:  Commit offset BEFORE processing
  At-least-once: Commit offset AFTER processing (may reprocess on crash)
  Exactly-once:  Kafka Transactions (idempotent producer + transactional consumer)
```

---

## Communication Patterns

### Request-Response

```
Client ──GET /users/123──→ Server
Client ←── {id: 123, ...} ── Server
```

Standard synchronous pattern. Simple but creates coupling.

### Event-Driven

```
Order Service ──"OrderCreated"──→ [Event Bus] ──→ Payment Service
                                              ──→ Inventory Service
                                              ──→ Notification Service

Each service reacts independently to events.
Services don't know about each other (decoupled).
```

### Request-Reply via Message Queue

```
Client ──request──→ [Request Queue] ──→ Service
Client ←──reply──── [Reply Queue]   ←── Service
(Correlation ID links request to response)
```

### Choreography vs Orchestration

```
CHOREOGRAPHY (Event-Driven, Decentralized):
  Order → "OrderCreated" → Payment → "PaymentCompleted" → Shipping → "ShipmentCreated"
  Each service knows what to do when it sees an event
  ✅ Loosely coupled, ❌ Hard to track overall flow

ORCHESTRATION (Central Coordinator):
  Saga Orchestrator:
    1. Call Payment Service → wait for result
    2. Call Inventory Service → wait for result
    3. Call Shipping Service → wait for result
  ✅ Clear flow, ❌ Single point of failure, tighter coupling
```

---

## Service Discovery

How do services find each other in a dynamic environment?

```
CLIENT-SIDE DISCOVERY:                SERVER-SIDE DISCOVERY:
  ┌──────┐  query  ┌──────────┐        ┌──────┐  request  ┌──────────┐
  │Client│ ──────→ │ Registry │        │Client│ ────────→ │   Load    │
  │      │ ←────── │(Consul,  │        │      │          │ Balancer  │
  │      │ IP list │ etcd,    │        └──────┘          │  (nginx)  │
  │      │         │ ZooKeeper│                          │     │     │
  │      │ ──req──→│)         │                          │  ┌──┴──┐  │
  └──────┘ direct  └──────────┘                          │  │query│  │
                                                         │  ▼     ▼  │
                                                    ┌──────────┐
                                                    │ Registry │
                                                    └──────────┘
```

| Method | Examples | Pros | Cons |
|--------|----------|------|------|
| **DNS-based** | Route53, CoreDNS | Simple, universal | DNS cache = stale entries |
| **Service registry** | Consul, etcd, ZooKeeper | Real-time, health checks | Extra infrastructure |
| **Platform-native** | Kubernetes Services, AWS ECS | Built-in, no extra setup | Platform lock-in |

---

## Interview Questions — Communication

### Q1: When would you use gRPC over REST?

- **Internal microservice communication** (faster, smaller payloads)
- **Streaming needs** (bidirectional streaming built-in)
- **Strong contract enforcement** (Protobuf schema = code gen)
- **Multi-language** systems (auto-generated clients in any language)
- **High-performance** requirements (binary serialization, HTTP/2 multiplexing)

### Q2: What is back-pressure and how do you handle it?

**Back-pressure** = when a downstream service can't keep up with incoming requests.

**Handling strategies:**
1. **Buffering** — queue messages until consumer catches up (limited by queue size)
2. **Dropping** — discard messages intentionally (load shedding)
3. **Rate limiting** — limit producer's send rate
4. **Scaling** — add more consumer instances
5. **Circuit breaking** — stop sending to overwhelmed service temporarily

### Q3: Kafka vs RabbitMQ — when to use each?

| Aspect | Kafka | RabbitMQ |
|--------|-------|----------|
| Model | Distributed log | Message broker with exchanges |
| Retention | Keeps messages (configurable retention) | Deletes after consumption |
| Ordering | Per-partition guaranteed | Per-queue FIFO |
| Throughput | Very high (100K+ msg/s) | High (50K+ msg/s) |
| Replayability | ✅ Re-read from any offset | ❌ Once consumed, gone |
| Best for | Event streaming, data pipelines, audit logs | Task queues, RPC, routing patterns |
