# Redis Pub/Sub & Messaging

## Pub/Sub (Publish/Subscribe)

Redis Pub/Sub allows **fire-and-forget** messaging between publishers and subscribers.

```
Publisher                              Subscribers
┌────────┐    PUBLISH "news"    ┌────────────────┐
│ App A  │ ──────────────────→  │ Subscriber 1   │
└────────┘         │            │ Subscriber 2   │
                   │            │ Subscriber 3   │
             ┌─────┴─────┐     └────────────────┘
             │   Redis    │
             │  Channel   │
             │  "news"    │
             └───────────┘
```

### Basic Usage

```redis
-- Subscriber (Terminal 1)
SUBSCRIBE news                    -- Listen to "news" channel
SUBSCRIBE news sports tech        -- Listen to multiple channels

-- Publisher (Terminal 2)
PUBLISH news "Breaking news!"     -- Returns number of subscribers who received it
PUBLISH sports "Goal scored!"

-- Pattern-based subscription
PSUBSCRIBE news.*                 -- Subscribe to news.tech, news.sports, etc.
PSUBSCRIBE user:*:events          -- Wildcard patterns
```

### Python Example

```python
import redis
import threading

r = redis.Redis()

# Publisher
def publish_events():
    r.publish("notifications", "New order received!")
    r.publish("notifications", "Payment confirmed!")
    r.publish("alerts", "Server CPU high!")

# Subscriber
def listen_notifications():
    pubsub = r.pubsub()
    pubsub.subscribe("notifications", "alerts")
    
    for message in pubsub.listen():
        if message["type"] == "message":
            channel = message["channel"].decode()
            data = message["data"].decode()
            print(f"[{channel}] {data}")

# Start listener in background thread
thread = threading.Thread(target=listen_notifications, daemon=True)
thread.start()

# Publish
publish_events()
```

### Pub/Sub Characteristics

| Feature | Behavior |
|---------|----------|
| **Delivery** | At-most-once (fire and forget) |
| **Persistence** | None — if no subscriber, message is lost |
| **Buffering** | None — subscriber must be connected to receive |
| **History** | No message history or replay |
| **Acknowledgment** | No ACKs — publisher doesn't know if received |
| **Multi-channel** | One subscriber can listen to many channels |

### When to Use Pub/Sub

✅ Real-time notifications, chat messages, live updates
✅ Cache invalidation across multiple app instances
✅ Event broadcasting where message loss is acceptable

❌ Need guaranteed delivery → Use Streams or a proper message queue
❌ Need message history/replay → Use Streams
❌ Need consumer groups → Use Streams

---

## Redis Streams (Reliable Messaging)

Streams are Redis's answer to Apache Kafka — an **append-only log** with consumer groups.

### Why Streams over Pub/Sub?

| Feature | Pub/Sub | Streams |
|---------|---------|---------|
| Message persistence | ❌ No | ✅ Yes |
| Message replay | ❌ No | ✅ Yes |
| Consumer groups | ❌ No | ✅ Yes |
| Acknowledgment | ❌ No | ✅ Yes |
| Backpressure | ❌ No | ✅ Yes (BLOCK) |
| At-least-once delivery | ❌ No | ✅ Yes |

### Stream Operations

```redis
-- Add entries (producer)
XADD orders * user_id 1001 product "laptop" total 999.99
XADD orders * user_id 1002 product "phone" total 599.99
-- * = auto-generated ID (timestamp-sequence)

-- Read all entries
XRANGE orders - +                  -- oldest to newest
XREVRANGE orders + -               -- newest to oldest
XRANGE orders - + COUNT 5          -- first 5 entries

-- Read new entries (blocking)
XREAD COUNT 10 BLOCK 5000 STREAMS orders $
-- $ = only new messages from now, BLOCK 5000 = wait up to 5s

-- Stream info
XLEN orders                        -- Number of entries
XINFO STREAM orders                -- Detailed stream info
```

### Consumer Groups

```redis
-- Create a consumer group
XGROUP CREATE orders order-processors 0
-- 0 = start reading from the beginning
-- $ = start from new messages only

-- Consumer reads from group
XREADGROUP GROUP order-processors worker-1 COUNT 1 BLOCK 5000 STREAMS orders >
-- > = only undelivered messages

XREADGROUP GROUP order-processors worker-2 COUNT 1 BLOCK 5000 STREAMS orders >
-- Each message goes to ONLY ONE consumer in the group

-- Acknowledge processing
XACK orders order-processors 1526569495631-0

-- Check pending (unacknowledged) messages
XPENDING orders order-processors
XPENDING orders order-processors - + 10    -- Details of pending

-- Claim messages from failed consumer (after timeout)
XCLAIM orders order-processors worker-2 60000 1526569495631-0
-- Claim message stuck with another consumer for >60s
```

### Stream Architecture Example

```
Producers                    Redis Stream             Consumer Groups
┌──────────┐                ┌──────────────┐
│ Web App  │ ─── XADD ───→ │              │     ┌─────────────────┐
└──────────┘                │   orders     │ ──→ │ Group: payments  │
┌──────────┐                │              │     │  ├─ worker-1     │
│ API      │ ─── XADD ───→ │   [entry-1]  │     │  ├─ worker-2     │
└──────────┘                │   [entry-2]  │     │  └─ worker-3     │
┌──────────┐                │   [entry-3]  │     └─────────────────┘
│ Webhook  │ ─── XADD ───→ │   [entry-4]  │     ┌─────────────────┐
└──────────┘                │   [entry-5]  │ ──→ │ Group: analytics │
                            └──────────────┘     │  └─ worker-1     │
                                                 └─────────────────┘

Each group independently reads ALL messages.
Within a group, each message goes to ONE consumer.
```

---

## Message Queue with Lists (Simple)

The simplest queue pattern using `LPUSH` / `BRPOP`.

```python
# Producer
def enqueue_task(task_data):
    r.lpush("task_queue", json.dumps(task_data))

# Consumer (blocking pop)
def worker():
    while True:
        _, task = r.brpop("task_queue", timeout=30)
        if task:
            process_task(json.loads(task))

# Reliable queue with BRPOPLPUSH
def reliable_worker():
    while True:
        task = r.brpoplpush("task_queue", "processing_queue", timeout=30)
        if task:
            try:
                process_task(json.loads(task))
                r.lrem("processing_queue", 1, task)  # Remove from processing
            except Exception:
                # Will be retried — task stays in processing_queue
                pass
```

---

## Keyspace Notifications

Redis can publish events when keys are modified.

```redis
-- Enable keyspace notifications (in redis.conf or at runtime)
CONFIG SET notify-keyspace-events KEA
-- K = Keyspace events
-- E = Keyevent events
-- A = All events (g$lszt for specific types)

-- Subscribe to all SET events
SUBSCRIBE __keyevent@0__:set

-- Subscribe to events on a specific key
SUBSCRIBE __keyspace@0__:user:1001

-- Subscribe to all expired key events
SUBSCRIBE __keyevent@0__:expired
```

**Use Cases:**
- Trigger actions when a session key expires
- Monitor cache invalidation
- Audit log of key modifications

---

## Interview Questions — Messaging

### Q1: Design a real-time chat system using Redis. Which features would you use?

**Answer:**

```
Architecture:
┌──────────┐       ┌─────────────┐       ┌──────────┐
│ Client A │ ←───→ │  WebSocket  │ ←───→ │  Redis   │
│ Client B │ ←───→ │   Server    │       └──────────┘
│ Client C │       └─────────────┘
└──────────┘

Redis features used:
 1. Pub/Sub          → Real-time message broadcast within a chat room
 2. Streams          → Persistent message history + guaranteed delivery
 3. Sorted Sets      → Online user list with last-seen timestamps
 4. Hashes           → User profiles, room metadata
 5. Lists            → Unread message queue per user
```

- **Pub/Sub** for real-time delivery to connected users
- **Streams** for persistent message storage (user can fetch history)
- **Sorted Sets** (`ZADD online:{room} {timestamp} {user}`) for presence tracking
- For unread messages: `LPUSH unread:{user_id} {message_id}`

---

### Q2: When would you choose Redis Streams over Apache Kafka?

| Criteria | Redis Streams | Apache Kafka |
|----------|--------------|--------------|
| Throughput | ~100K msg/sec | Millions msg/sec |
| Persistence | In-memory (with AOF) | Disk-based (durable) |
| Complexity | Simple, part of Redis | Requires ZooKeeper/KRaft, brokers |
| Message Size | Keep small (<1MB) | Can handle large payloads |
| Consumer Groups | ✅ Built-in | ✅ Built-in |
| Replay | ✅ XRANGE/XREAD with ID | ✅ Offset-based replay |
| Ordering | Per-stream guaranteed | Per-partition guaranteed |
| Best For | Small-medium workloads, existing Redis | High-throughput event streaming |

**Choose Streams when:** Already using Redis, moderate throughput, want simplicity
**Choose Kafka when:** Very high throughput, complex event processing, long-term retention

---

### Q3: How do you handle a consumer that crashes in a Redis Stream consumer group?

**Answer:**

1. The message stays in the **Pending Entries List (PEL)**
2. Use `XPENDING` to detect messages stuck with a dead consumer
3. Use `XCLAIM` or `XAUTOCLAIM` to reassign to another consumer

```redis
-- Check what's pending
XPENDING orders mygroup - + 10

-- Auto-claim messages idle for >60 seconds
XAUTOCLAIM orders mygroup alive-worker 60000 0
-- Returns messages that were idle and assigns them to alive-worker

-- Or manually claim specific messages
XCLAIM orders mygroup alive-worker 60000 1526569495631-0
```

4. Implement a **dead-letter pattern** — after N claim attempts, move to a separate stream:

```python
def process_with_retry(stream, group, consumer, max_retries=3):
    pending = r.xpending_range(stream, group, "-", "+", 10)
    for entry in pending:
        if entry["times_delivered"] >= max_retries:
            # Move to dead-letter stream
            msg = r.xrange(stream, entry["message_id"], entry["message_id"])
            r.xadd(f"{stream}:dead_letter", msg[0][1])
            r.xack(stream, group, entry["message_id"])
```
