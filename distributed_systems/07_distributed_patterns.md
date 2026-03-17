# Distributed Patterns

## Saga Pattern

Manages **distributed transactions** without 2PC. A sequence of local transactions, each publishing events or commands. If one step fails, **compensating transactions** undo previous steps.

```
Order Saga (Success):
  1. Order Service:    Create order (PENDING)        ──→
  2. Payment Service:  Charge payment                ──→
  3. Inventory Service: Reserve stock                ──→
  4. Shipping Service:  Create shipment              ──→
  5. Order Service:    Mark order (COMPLETED)         ✓

Order Saga (Failure at step 3):
  1. Order Service:    Create order (PENDING)        ──→
  2. Payment Service:  Charge payment                ──→
  3. Inventory Service: Reserve stock                ──→ FAIL! (out of stock)
  
  Compensations (reverse order):
  C2. Payment Service:  Refund payment               ←──
  C1. Order Service:    Cancel order                  ✓
```

### Choreography vs Orchestration

```
CHOREOGRAPHY (event-driven):
  Order ──"OrderCreated"──→ Payment ──"PaymentCharged"──→ Inventory ──"StockReserved"──→ Shipping
  Each service listens for events and reacts
  
  ✅ Loose coupling, no central coordinator
  ❌ Hard to understand flow, difficult to debug
  ❌ Risk of cyclic dependencies

ORCHESTRATION (central coordinator):
  ┌────────────────────┐
  │   Saga Orchestrator  │
  │                      │
  │ 1. Call Payment     │ ──→ Payment Service
  │ 2. Call Inventory   │ ──→ Inventory Service
  │ 3. Call Shipping    │ ──→ Shipping Service
  │                      │
  │ On failure: run     │
  │ compensations       │
  └────────────────────┘
  
  ✅ Clear flow, easy to debug
  ❌ Central point, tighter coupling
```

---

## CQRS (Command Query Responsibility Segregation)

Separate the **write model** (commands) from the **read model** (queries).

```
Traditional (single model):
  ┌──────────────┐
  │  Application  │ ── reads & writes ──→ ┌──────────┐
  └──────────────┘                        │ Database  │
                                          └──────────┘

CQRS (separate models):
  ┌──────────────┐                        ┌──────────────┐
  │   Command     │ ── writes ──────────→ │  Write DB     │
  │   Service     │                       │ (normalized)  │
  └──────────────┘                        └──────┬───────┘
                                                 │ events/CDC
                                                 ▼
  ┌──────────────┐                        ┌──────────────┐
  │   Query       │ ── reads ─────────→   │  Read DB      │
  │   Service     │                       │(denormalized) │
  └──────────────┘                        └──────────────┘
```

| Benefit | Description |
|---------|-------------|
| **Independent scaling** | Scale reads and writes separately |
| **Optimized models** | Write model normalized, read model denormalized for queries |
| **Different storage** | Write to SQL, read from Elasticsearch/Redis |
| **Performance** | Read-heavy systems benefit massively |

**Trade-off:** Eventual consistency between write and read sides. Added complexity.

---

## Event Sourcing

Store **events** (facts about what happened) instead of current state.

```
Traditional (state-based):
  Account: { id: 1, balance: 150 }    ← Only current state

Event Sourcing:
  Event Log:
    1. AccountCreated   { id: 1, balance: 0 }
    2. MoneyDeposited   { id: 1, amount: 200 }
    3. MoneyWithdrawn   { id: 1, amount: 50 }
    
  Current state = replay all events:
    0 + 200 - 50 = 150 ✓

  Every state change is an immutable event
  Can rebuild state at ANY point in time
  Natural audit trail
```

### Event Sourcing + CQRS

```
Commands ──→ Event Store (append-only) ──→ Projections ──→ Read Models
              │                                │
              │ Events: ordered, immutable      │ Materialized views
              │ "Source of truth"               │ optimized for queries
              └────────────────────────────────┘
```

**Benefits:** Complete audit log, temporal queries, debugging, replay
**Challenges:** Event schema evolution, storage growth, eventual consistency, complexity

---

## Outbox Pattern

Solve the **dual write problem**: atomically update database AND publish event.

```
❌ PROBLEM (dual write):
  1. Update database ✓
  2. Publish event to Kafka ✗ (crash between 1 and 2!)
  → Database updated but event never published → inconsistency

✅ SOLUTION (Outbox Pattern):
  1. In a SINGLE database transaction:
     a. Update business table
     b. Insert event into "outbox" table
  2. Separate process reads outbox → publishes to Kafka → marks as published

  ┌─────────────────────────────┐
  │        Database              │
  │  ┌─────────────┐            │
  │  │ orders table │ ← UPDATE  │    ┌───────────┐
  │  └─────────────┘            │    │           │
  │  ┌─────────────┐            │──→ │  Kafka    │
  │  │ outbox table │ ← INSERT  │    │           │
  │  └─────────────┘            │    └───────────┘
  │                              │
  │  Both in SAME transaction    │
  └─────────────────────────────┘
        ↑
    CDC (Debezium) or polling reads outbox
```

**Implementation options:**
- **Polling publisher:** Service polls outbox table periodically
- **CDC (Change Data Capture):** Use Debezium to capture outbox changes → publish to Kafka
- **Transaction log tailing:** Read database WAL/binlog directly

---

## Circuit Breaker Pattern

Prevent cascading failures by **stopping calls** to a failing downstream service.

```
States:
              ┌─────────────┐
    success   │             │   failure threshold
   ┌────────→ │   CLOSED    │ ────────────┐
   │          │ (normal)    │             │
   │          └─────────────┘             │
   │                                      ▼
   │                               ┌─────────────┐
   │         timeout expires       │    OPEN      │
   │         ┌────────────────────│ (rejecting)  │
   │         │                     └─────────────┘
   │         ▼                            │
   │   ┌─────────────┐                   │
   │   │  HALF-OPEN   │  failure         │
   └── │ (testing)    │ ─────────────────┘
       └─────────────┘

CLOSED:    All requests pass through normally
           Count failures → if threshold reached → OPEN

OPEN:      All requests immediately fail (no call to downstream)
           After timeout → HALF-OPEN

HALF-OPEN: Allow limited requests through
           If success → CLOSED
           If failure → back to OPEN
```

```python
# Pseudo-code
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=30):
        self.state = "CLOSED"
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
    
    def call(self, func):
        if self.state == "OPEN":
            if time_since(self.last_failure_time) > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Service unavailable")
        
        try:
            result = func()
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = now()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

---

## Bulkhead Pattern

**Isolate** components so that failure in one doesn't cascade to others.

```
WITHOUT BULKHEAD:
  ┌──────────────────────────────┐
  │     Shared Thread Pool (100) │
  │                              │
  │  Service A calls ═══════════╗│
  │  Service B calls ═══╗       ║│
  │  Service C calls ═╗ ║       ║│
  │                    ║ ║       ║│    If Service A hangs,
  │                    ║ ║       ║│    it consumes ALL 100 threads
  │                    ║ ║       ║│    → Services B and C also blocked!
  └──────────────────────────────┘

WITH BULKHEAD:
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │ Pool A (40)  │ │ Pool B (30)  │ │ Pool C (30)  │
  │              │ │              │ │              │
  │ Service A    │ │ Service B    │ │ Service C    │
  │ calls only   │ │ calls only   │ │ calls only   │
  │              │ │              │ │              │
  │ (if A hangs, │ │ B still has  │ │ C still has  │
  │  only A      │ │ its own 30   │ │ its own 30   │
  │  affected)   │ │ threads)     │ │ threads)     │
  └──────────────┘ └──────────────┘ └──────────────┘
```

---

## Sidecar Pattern

Deploy a helper process **alongside** your main application to handle cross-cutting concerns.

```
┌─────────────────────────────────────────┐
│                  Pod                     │
│                                         │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │  Application  │  │    Sidecar       │ │
│  │  (business    │──│  (logging,       │ │
│  │   logic)      │  │   monitoring,    │ │
│  │               │  │   mTLS, retries) │ │
│  └──────────────┘  └──────────────────┘ │
│                                         │
│  Share: network, storage, lifecycle     │
└─────────────────────────────────────────┘
```

**Use cases:**
- **Service mesh proxy** (Envoy sidecar in Istio)
- **Log collection** (Fluentd sidecar shipping logs)
- **mTLS termination** (encrypt/decrypt traffic)
- **Health checks** and metrics collection

---

## Service Mesh

Infrastructure layer for **managing service-to-service communication**.

```
┌─────────────────────────────────────────────────────────┐
│                     Service Mesh                         │
│                                                         │
│  ┌─────────┐         ┌─────────┐         ┌─────────┐  │
│  │Service A│←─proxy─→│Service B│←─proxy─→│Service C│  │
│  │ + Envoy │         │ + Envoy │         │ + Envoy │  │
│  └─────────┘         └─────────┘         └─────────┘  │
│       ▲                   ▲                   ▲        │
│       └───────────────────┴───────────────────┘        │
│                     Control Plane                       │
│                  (Istio / Linkerd)                      │
│         Config, certificates, routing rules             │
└─────────────────────────────────────────────────────────┘

Features:
  - mTLS (mutual TLS) between all services
  - Traffic management (canary, blue-green, A/B)
  - Observability (distributed tracing, metrics)
  - Retries, timeouts, circuit breaking
  - Rate limiting, access control
```

---

## Idempotency Pattern (Implementation)

```python
# Server-side idempotency with idempotency keys
import redis
import json

class IdempotentHandler:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 86400  # 24 hours
    
    def handle(self, idempotency_key, operation_fn):
        # Check if already processed
        cached = self.redis.get(f"idempotency:{idempotency_key}")
        if cached:
            return json.loads(cached)  # Return cached result
        
        # Process operation
        result = operation_fn()
        
        # Cache result with TTL
        self.redis.setex(
            f"idempotency:{idempotency_key}",
            self.ttl,
            json.dumps(result)
        )
        return result

# Client sends:
# POST /api/payments
# Idempotency-Key: "abc-123-unique"
# Body: { amount: 100, to: "bob" }
#
# Retry sends same Idempotency-Key → gets cached response
```

---

## Retry with Exponential Backoff

```python
import time
import random

def retry_with_backoff(func, max_retries=5, base_delay=1.0, max_delay=60.0):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise  # Final attempt failed
            
            # Exponential backoff with jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # 10% jitter
            time.sleep(delay + jitter)

# Attempt 0: wait ~1s
# Attempt 1: wait ~2s
# Attempt 2: wait ~4s
# Attempt 3: wait ~8s
# Attempt 4: wait ~16s (or max_delay)
```

**Why jitter?** Without jitter, if 100 clients fail simultaneously, they ALL retry at the same time → **thundering herd**. Random jitter spreads retries.

---

## Interview Questions — Distributed Patterns

### Q1: Saga vs 2PC — when to use each?

| Aspect | Saga | 2PC |
|--------|------|-----|
| Isolation | No (intermediate states visible) | Yes (all-or-nothing) |
| Availability | Higher (no coordinator blocking) | Lower (coordinator SPOF) |
| Complexity | Higher (compensating transactions) | Lower (protocol handles it) |
| Performance | Better (async, no locking) | Worse (blocking, locking) |
| Use case | Microservices, long-running processes | Homogeneous databases, short transactions |

### Q2: What is the dual write problem?

When a service needs to atomically update a database AND publish a message, but they're separate systems. A crash between the two operations causes inconsistency. **Solutions:** Outbox pattern, CDC (Debezium), transaction log tailing.

### Q3: When would you use CQRS?

- Read and write patterns are **very different** (different scales, different models)
- Read model needs to be **highly optimized** (denormalized, cached, different storage)
- System is **read-heavy** (90%+ reads)
- **Don't use** for simple CRUD with balanced reads/writes (overhead not justified)
