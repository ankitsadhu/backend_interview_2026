# Observability & Reliability

## The Three Pillars of Observability

```
                    Observability
                    /     |     \
                   /      |      \
              Logs     Metrics    Traces
           (events)  (aggregates) (requests)
```

| Pillar | What | Example | Tool |
|--------|------|---------|------|
| **Logs** | Discrete events with context | `ERROR: payment failed for user_123` | ELK, Loki, CloudWatch |
| **Metrics** | Numeric values over time | `http_request_duration_seconds: 0.25` | Prometheus, Datadog, CloudWatch |
| **Traces** | End-to-end request journey | Request A → Service B → DB → Cache | Jaeger, Zipkin, OpenTelemetry |

---

## Distributed Tracing

Track a request as it flows through multiple services.

```
User Request (Trace ID: abc-123)
  │
  ├─ Span 1: API Gateway (5ms)
  │   │
  │   ├─ Span 2: Auth Service (3ms)
  │   │
  │   ├─ Span 3: Order Service (50ms)
  │   │   │
  │   │   ├─ Span 4: Database Query (15ms)
  │   │   │
  │   │   └─ Span 5: Payment Service (30ms)
  │   │       │
  │   │       └─ Span 6: Stripe API (25ms)  ← bottleneck!
  │   │
  │   └─ Span 7: Notification Service (2ms)
  │
  └─ Total: 55ms

Each span contains:
  - Trace ID (same across all spans in one request)
  - Span ID (unique per span)
  - Parent Span ID (who called this)
  - Service name, operation, duration
  - Tags (http.status_code, error, etc.)
```

### Context Propagation

```
Service A ──HTTP──→ Service B ──gRPC──→ Service C

Headers carry trace context:
  traceparent: 00-abc123-span456-01
  
  version-traceid-parentspanid-flags

OpenTelemetry standard (W3C Trace Context):
  traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
```

---

## Metrics

### Types of Metrics

| Type | Description | Example |
|------|-------------|---------|
| **Counter** | Monotonically increasing value | `http_requests_total` |
| **Gauge** | Value that goes up and down | `active_connections`, `cpu_usage` |
| **Histogram** | Distribution of values in buckets | `request_duration_seconds` |
| **Summary** | Pre-calculated quantiles | `request_duration_p99` |

### RED Method (Request-Oriented)

For **request-driven services** (APIs, web services):

| Metric | What to Monitor |
|--------|----------------|
| **R**ate | Requests per second |
| **E**rrors | Failed requests per second (or error rate %) |
| **D**uration | Response time (p50, p95, p99) |

### USE Method (Resource-Oriented)

For **infrastructure resources** (CPU, memory, disk, network):

| Metric | What to Monitor |
|--------|----------------|
| **U**tilization | How busy is the resource (%) |
| **S**aturation | Amount of work queued (waiting) |
| **E**rrors | Error events (disk errors, network drops) |

### The Four Golden Signals (Google SRE)

| Signal | Description |
|--------|-------------|
| **Latency** | Time to handle a request (separate success from error latency) |
| **Traffic** | Demand on the system (requests/sec, sessions) |
| **Errors** | Rate of failed requests (explicit 500s, implicit timeouts) |
| **Saturation** | How "full" the system is (CPU, memory, I/O, queue depth) |

---

## Logging Best Practices

### Structured Logging

```json
// ❌ BAD — unstructured log
"2026-03-17 10:30:00 ERROR Payment failed for user 123 amount 99.99"

// ✅ GOOD — structured log (JSON)
{
  "timestamp": "2026-03-17T10:30:00.000Z",
  "level": "ERROR",
  "service": "payment-service",
  "trace_id": "abc-123",
  "user_id": "123",
  "message": "Payment failed",
  "error": "insufficient_funds",
  "amount": 99.99,
  "currency": "USD",
  "payment_method": "credit_card",
  "duration_ms": 250
}
```

### Log Levels

| Level | When to Use |
|-------|------------|
| **DEBUG** | Detailed diagnostics (disabled in production) |
| **INFO** | Normal operations (request processed, service started) |
| **WARN** | Unexpected but handled (retry succeeded, degraded mode) |
| **ERROR** | Failed operation, needs attention (payment failed, DB timeout) |
| **FATAL** | System cannot continue (cannot bind port, DB connection lost) |

### Centralized Logging Stack

```
Services ──→ Log Collector ──→ Log Aggregator ──→ Dashboard
              (Fluentd,         (Elasticsearch,    (Kibana,
               Filebeat,         Loki,              Grafana)
               Vector)           CloudWatch)
```

---

## SLIs, SLOs, and SLAs

```
SLI (Service Level Indicator):
  A measurable metric that reflects service quality
  Example: "99.2% of requests complete within 200ms"

SLO (Service Level Objective):
  A target for an SLI
  Example: "P99 latency should be < 200ms"
  Example: "Availability should be >= 99.9%"

SLA (Service Level Agreement):
  A contract with consequences for missing SLOs
  Example: "If availability drops below 99.9%, customer gets 10% credit"
```

### Error Budget

```
SLO: 99.9% availability = 0.1% allowed downtime

Per month (30 days):
  0.1% × 30 × 24 × 60 = 43.2 minutes of allowed downtime

Error Budget = 43.2 minutes

If you've used 40 minutes → 3.2 minutes remaining → freeze deployments!
If you've used 10 minutes → 33 minutes remaining → push features!
```

| Availability | Downtime/Year | Downtime/Month |
|-------------|---------------|----------------|
| 99% (two 9s) | 3.65 days | 7.3 hours |
| 99.9% (three 9s) | 8.76 hours | 43.2 minutes |
| 99.95% | 4.38 hours | 21.6 minutes |
| 99.99% (four 9s) | 52.6 minutes | 4.32 minutes |
| 99.999% (five 9s) | 5.26 minutes | 25.9 seconds |

---

## Chaos Engineering

Deliberately inject failures to **find weaknesses before they find you**.

```
Principles of Chaos Engineering:
  1. Define "steady state" (normal behavior metrics)
  2. Hypothesize that steady state will hold during failure
  3. Introduce real-world failures (kill nodes, inject latency)
  4. Observe the difference → disprove hypothesis or gain confidence
  5. Automate and run continuously
```

### Types of Failure Injection

| Type | What | Tools |
|------|------|-------|
| **Instance failure** | Kill random servers/containers | Chaos Monkey, LitmusChaos |
| **Network failure** | Partition, latency, packet loss | tc (Linux), Toxiproxy |
| **Dependency failure** | Kill database, cache, queue | Manual, Chaos Toolkit |
| **Resource exhaustion** | CPU stress, memory leak, disk fill | stress-ng, Chaos Mesh |
| **Clock skew** | Offset system clock | chrony manipulation |

### Blast Radius

```
Start small, increase gradually:

Level 1: Single instance (one pod)
  → "Does auto-scaling replace the instance?"

Level 2: Availability zone (one rack/DC zone)
  → "Does failover work across zones?"

Level 3: Full region
  → "Does multi-region disaster recovery work?"

Level 4: Cascading (dependency chain)
  → "If DB slows, does circuit breaker protect upstream?"

ALWAYS have a kill switch to stop the experiment!
```

---

## Failure Handling Patterns

### Timeout + Retry + Circuit Breaker

```
Request Flow:
  1. Set TIMEOUT (e.g., 3 seconds)
     → If no response in 3s → fail

  2. RETRY with exponential backoff
     → Attempt 1: wait 1s
     → Attempt 2: wait 2s  
     → Attempt 3: wait 4s (give up after 3 retries)

  3. CIRCUIT BREAKER
     → If 5 failures in 10 seconds → OPEN circuit
     → Stop calling for 30 seconds
     → Try again (HALF-OPEN) → if success, CLOSE circuit

  Combined:
    Timeout → Retry (with backoff) → Circuit Breaker → Fallback
```

### Fallback Strategies

| Strategy | Description | Example |
|----------|-------------|---------|
| **Cached response** | Return stale cached data | Product catalog from cache |
| **Default value** | Return a safe default | Default recommendations |
| **Degraded mode** | Reduced functionality | Show text instead of images |
| **Queue for later** | Accept and process later | Submit order to queue |
| **Fail fast** | Return error immediately | "Service unavailable, try later" |

### Health Checks

```
Liveness Check: "Is the process alive?"
  → Returns 200 if process is running
  → If fails → restart the container

Readiness Check: "Can the service handle requests?"
  → Returns 200 if dependencies are connected
  → If fails → remove from load balancer (don't restart)

Startup Check: "Has the service finished initializing?"
  → Returns 200 once initialization is complete
  → Prevents liveness/readiness checks during slow startup
```

---

## Disaster Recovery

### RPO and RTO

```
                  Disaster
                     │
  ◄──── RPO ────►    │    ◄──── RTO ────►
                     │
  Last backup ──────│──────── Recovery complete
                     │

RPO (Recovery Point Objective):
  How much data loss is acceptable?
  RPO = 1 hour → backups every hour
  RPO = 0 → synchronous replication (no data loss)

RTO (Recovery Time Objective):
  How quickly must service be restored?
  RTO = 4 hours → can tolerate 4 hours of downtime
  RTO = 0 → hot standby with auto-failover
```

### Disaster Recovery Strategies

| Strategy | RPO | RTO | Cost |
|----------|-----|-----|------|
| **Backup & Restore** | Hours | Hours | $ |
| **Pilot Light** | Minutes | 10-30 min | $$ |
| **Warm Standby** | Seconds | Minutes | $$$ |
| **Multi-Site Active-Active** | ~0 | ~0 | $$$$ |

---

## Interview Questions — Observability & Reliability

### Q1: What are the differences between logs, metrics, and traces?

| Aspect | Logs | Metrics | Traces |
|--------|------|---------|--------|
| Data type | Text events | Numeric time series | Request flow graph |
| Cardinality | High (every event) | Low (aggregated) | Medium (per request) |
| Storage cost | High | Low | Medium |
| Query speed | Slower (text search) | Fast (numeric) | Medium |
| Best for | Debugging specific events | Alerting, dashboards | Finding bottlenecks |

### Q2: How do you set SLOs for a new service?

1. **Identify SLIs:** What matters? (latency, availability, error rate)
2. **Measure baseline:** Deploy and collect data for 1-2 weeks
3. **Set realistic SLOs:** Based on measurements (not aspirational)
4. **Calculate error budget:** SLO → allowed failures per period
5. **Alert on burn rate:** Alert when error budget is consumed faster than expected
6. **Review and adjust:** Tighten SLOs as system matures

### Q3: What is the difference between RPO and RTO?

- **RPO (Recovery Point Objective):** Maximum acceptable data loss (measured in time). "How old can the backup be?"
- **RTO (Recovery Time Objective):** Maximum acceptable downtime. "How quickly must we recover?"

Lower RPO → more frequent backups (or synchronous replication)
Lower RTO → hotter standby infrastructure (more expensive)
