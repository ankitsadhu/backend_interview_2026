# Scalability & Load Balancing

## Scaling Strategies

### Vertical Scaling (Scale Up)

```
Before:                    After:
┌──────────────┐          ┌──────────────────┐
│  4 CPU cores │          │  32 CPU cores    │
│  16 GB RAM   │   ──→    │  256 GB RAM      │
│  500 GB SSD  │          │  4 TB NVMe       │
└──────────────┘          └──────────────────┘
   Small server              Bigger server
```

**Pros:** Simple (no code changes), no distributed complexity
**Cons:** Hardware limits, expensive at scale, single point of failure

### Horizontal Scaling (Scale Out)

```
Before:                    After:
┌──────────────┐          ┌──────────┐ ┌──────────┐ ┌──────────┐
│  1 server    │   ──→    │ Server A │ │ Server B │ │ Server C │
│              │          └──────────┘ └──────────┘ └──────────┘
└──────────────┘                 ↑           ↑           ↑
                                 └───────────┼───────────┘
                                       Load Balancer
```

**Pros:** Theoretically unlimited scale, fault tolerance
**Cons:** Distributed systems complexity, data consistency challenges

### Comparison

| Aspect | Vertical | Horizontal |
|--------|----------|-----------|
| Cost curve | Exponential (bigger machines cost more per unit) | Linear (add commodity hardware) |
| Complexity | Low | High (distributed state, networking) |
| Limits | Hardware ceiling | Virtually unlimited |
| Downtime | Often requires restart | Zero-downtime (add/remove nodes) |
| Data | Single machine, simple | Must partition or replicate |

---

## Load Balancing

### Algorithms

| Algorithm | How It Works | Best For |
|-----------|-------------|----------|
| **Round Robin** | Cycle through servers in order | Equal-capacity servers, stateless |
| **Weighted Round Robin** | Round robin with weights (powerful server = more requests) | Heterogeneous servers |
| **Least Connections** | Send to server with fewest active connections | Varying request durations |
| **Weighted Least Connections** | Least connections adjusted by server weight | Mixed capacity + variable load |
| **IP Hash** | Hash client IP → consistent server | Session affinity without cookies |
| **Least Response Time** | Send to fastest-responding server | Latency-sensitive applications |
| **Random** | Pick a random server | Good baseline, simple |
| **Consistent Hashing** | Hash-ring based | Cache layers (Memcached, Redis) |

### Layer 4 vs Layer 7 Load Balancing

```
Layer 4 (Transport):                Layer 7 (Application):
  ┌──────────────┐                    ┌──────────────┐
  │  TCP/UDP LB   │                    │   HTTP LB     │
  │               │                    │               │
  │ Routes based  │                    │ Routes based  │
  │ on IP + port  │                    │ on URL, headers│
  │               │                    │ cookies, body │
  │ Fast, no      │                    │               │
  │ inspection    │                    │ Can do SSL    │
  └──────────────┘                    │ termination,  │
                                      │ content-based │
                                      │ routing       │
                                      └──────────────┘

Layer 4: AWS NLB, HAProxy (TCP mode)
Layer 7: AWS ALB, nginx, HAProxy (HTTP mode), Envoy
```

### Load Balancer Patterns

```
DNS-Based:
  client → DNS → returns different IPs (round robin)
  ✅ Simple, no extra infrastructure
  ❌ DNS caching = slow failover, no health checks

Hardware LB:
  F5 BIG-IP, Citrix ADC
  ✅ High performance, SSL offloading
  ❌ Expensive, vendor lock-in

Software LB:
  nginx, HAProxy, Envoy, Traefik
  ✅ Flexible, programmable, free/cheap
  ❌ Needs server to run on

Cloud-Managed:
  AWS ALB/NLB, GCP LB, Azure LB
  ✅ Auto-scaling, managed, integrated
  ❌ Cloud lock-in, cost at scale
```

---

## CDN (Content Delivery Network)

Cache content at **edge locations** near users for lower latency.

```
Without CDN:
  User (Tokyo) ──────── 200ms ──────── Origin (US-East)

With CDN:
  User (Tokyo) ── 5ms ── CDN Edge (Tokyo) ── cache miss ── Origin (US-East)
                                             (only first request)

  ┌────────────────────────────────────────────────────────┐
  │                                                        │
  │     CDN Edge         CDN Edge         CDN Edge         │
  │     (Tokyo)          (London)         (São Paulo)      │
  │        │                │                │             │
  │        └────────────────┼────────────────┘             │
  │                         │                              │
  │                    Origin Server                       │
  │                    (US-East)                            │
  └────────────────────────────────────────────────────────┘
```

### CDN Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Pull CDN** | CDN fetches from origin on cache miss | General websites |
| **Push CDN** | You upload content to CDN proactively | Large files, videos |
| **Cache invalidation** | Purge stale content from CDN | Content updates |
| **TTL-based** | Content expires after configured time | Balance freshness vs cache hit ratio |

**Cache Headers:**
```http
Cache-Control: public, max-age=86400    # Cache for 24 hours
Cache-Control: private, no-cache        # Don't cache
ETag: "abc123"                          # Conditional revalidation
Vary: Accept-Encoding                   # Separate cache per encoding
```

---

## Caching Strategies

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client   │ ──→ │  Cache   │ ──→ │ Database │
│           │ ←── │ (Redis)  │ ←── │          │
└──────────┘     └──────────┘     └──────────┘
```

### Cache-Aside (Lazy Loading)

```
Read:
  1. Check cache → hit? return cached
  2. Cache miss → read from DB
  3. Write to cache → return

Write:
  1. Write to DB
  2. Invalidate cache (delete key)

✅ Only caches what's requested (memory efficient)
❌ Cache miss penalty (extra round trip)
❌ Stale data possible between DB write and cache invalidation
```

### Write-Through

```
Write:
  1. Write to cache
  2. Cache writes to DB (synchronously)

Read:
  1. Always read from cache (always up-to-date)

✅ Cache always consistent with DB
❌ Write latency (cache + DB on every write)
❌ Caches data that may never be read
```

### Write-Behind (Write-Back)

```
Write:
  1. Write to cache (immediately acknowledged)
  2. Cache asynchronously writes to DB (batched)

✅ Very fast writes (only cache latency)
❌ Risk of data loss if cache crashes before flushing
❌ Complex consistency guarantees
```

### Cache Invalidation Problems

```
1. Thundering Herd (Cache Stampede):
   Cache key expires → 1000 concurrent requests → ALL hit DB
   Solution: Mutex/lock on cache miss (only one fetches, others wait)
            Or probabilistic early expiration

2. Cache Penetration:
   Queries for non-existent data → always miss → always hit DB
   Solution: Cache null results, Bloom filter

3. Cache Avalanche:
   Many keys expire simultaneously → massive DB load
   Solution: Random TTL jitter, warm cache before expiration
```

---

## Auto-Scaling

```
           Scaling Policy
        (CPU > 70% for 5 min)
                │
                ▼
         ┌──────────┐
         │ Scaler    │ ── monitors ── metrics (CPU, memory, latency, queue depth)
         │           │
         │ Scale up  │ ── add instances when load increases
         │ Scale down│ ── remove instances when load decreases
         └──────────┘
```

### Scaling Metrics

| Metric | Scale Up When | Scale Down When |
|--------|-------------|----------------|
| **CPU** | > 70% sustained | < 30% sustained |
| **Memory** | > 80% | < 40% |
| **Request latency** | P99 > threshold | P50 well below threshold |
| **Queue depth** | Messages growing | Queue nearly empty |
| **Custom** | Business-specific (active users, requests/sec) | |

### Scaling Strategies

```
REACTIVE (Auto-scaling):
  Monitor metrics → threshold breached → scale
  ✅ Responds to actual demand
  ❌ Lag time (scale-up delay: 2-5 min for VMs, 30s for containers)

PREDICTIVE:
  Analyze historical patterns → scale BEFORE demand spike
  ✅ No lag time
  ❌ Needs accurate prediction models

SCHEDULED:
  Scale up at 8 AM, scale down at 8 PM (known traffic patterns)
  ✅ Simple, predictable
  ❌ Only works for predictable traffic
```

---

## Back-Pressure

When a system is overwhelmed, push back on the input instead of crashing.

```
WITHOUT BACK-PRESSURE:
  Producer (1000 msg/s) ──→ Consumer (100 msg/s)
  → Consumer overwhelmed → OOM → crash → data loss!

WITH BACK-PRESSURE:
  Producer (1000 msg/s) ──→ [Buffer: FULL] ──→ Consumer (100 msg/s)
                             │
                             └── Signal: "Slow down!"
                             Producer reduces to 100 msg/s
```

### Back-Pressure Strategies

| Strategy | How | Example |
|----------|-----|---------|
| **Block** | Producer blocks until consumer catches up | TCP flow control |
| **Buffer + drop** | Fixed buffer → drop oldest/newest when full | Video streaming |
| **Rate limit** | Limit producer's send rate | API rate limiting |
| **Resize** | Dynamically adjust batch sizes | Kafka consumers |
| **Load shed** | Reject low-priority requests | HTTP 503 |

---

## Rate Limiting

Control the rate of requests to protect services.

### Algorithms

```
TOKEN BUCKET:
  Bucket holds N tokens, refilled at rate R
  Each request consumes 1 token
  If bucket empty → reject (429 Too Many Requests)
  ✅ Allows bursts (up to bucket size)

SLIDING WINDOW:
  Count requests in past W seconds
  If count >= limit → reject
  ✅ Smooth rate limiting, no burst issues

FIXED WINDOW:
  Count requests in current time window (e.g., per minute)
  Reset counter at window boundary
  ❌ Burst at window edges (double rate across boundary)

LEAKY BUCKET:
  Queue requests, process at fixed rate
  If queue full → reject
  ✅ Smooth output rate
```

---

## Interview Questions — Scalability

### Q1: How would you scale a service from 100 to 10M users?

```
100 users:        Single server (monolith)
1K users:         Separate DB, add caching (Redis)
10K users:        Load balancer + multiple app servers
100K users:       Read replicas, CDN, connection pooling
1M users:         Microservices, message queues, sharding DB
10M users:        Multi-region, global LB, database partitioning,
                  eventual consistency where acceptable
```

### Q2: What's the difference between a reverse proxy and a load balancer?

| Aspect | Reverse Proxy | Load Balancer |
|--------|--------------|---------------|
| **Primary purpose** | Gateway (SSL, compression, caching) | Distribute traffic across servers |
| **Backends** | Can be one server | Multiple servers (required) |
| **Health checks** | Optional | Essential |
| **Examples** | nginx (reverse proxy mode) | nginx (upstream), HAProxy, ALB |

In practice, most tools do both (nginx is both a reverse proxy and load balancer).

### Q3: How do you handle cache invalidation in a distributed system?

1. **TTL-based:** Set expiration time (simple but stale window)
2. **Event-driven:** Publish invalidation events on data change
3. **Write-through:** Update cache on every write (always consistent)
4. **Versioned keys:** Include version in cache key (`user:123:v5`)
5. **Pub/Sub invalidation:** Redis Pub/Sub to notify all instances

**Best practice:** TTL as safety net + event-driven invalidation for freshness.
