# Redis High Availability & Scaling

## Replication (Master-Replica)

### How Replication Works

```
                    Writes
                      │
                      ▼
               ┌──────────────┐
               │   MASTER     │
               │ (read/write) │
               └──────┬───────┘
                      │  Replication Stream
           ┌──────────┼──────────┐
           │          │          │
    ┌──────▼─────┐ ┌──▼────────┐ ┌──▼────────┐
    │ REPLICA-1  │ │ REPLICA-2 │ │ REPLICA-3 │
    │ (read-only)│ │(read-only)│ │(read-only)│
    └────────────┘ └───────────┘ └───────────┘
          ↑              ↑             ↑
       Reads          Reads         Reads
```

### Configuration

```redis
-- On the replica:
REPLICAOF 192.168.1.100 6379       -- Connect to master
REPLICAOF NO ONE                   -- Promote to master

-- redis.conf
replicaof 192.168.1.100 6379
masterauth "password"               -- If master requires auth

-- Read-only replica (default)
replica-read-only yes
```

### Replication Process

```
1. REPLICA sends PSYNC to MASTER
2. MASTER starts BGSAVE (creates RDB snapshot)
3. MASTER sends RDB file to REPLICA
4. REPLICA loads RDB into memory
5. MASTER sends backlog of writes that happened during BGSAVE
6. Now in sync: MASTER streams every write command to REPLICA

Full Sync vs Partial Sync:
- Full Sync: Initial connection or replication buffer overflow
- Partial Sync: After brief disconnection (uses replication backlog buffer)
```

### Replication Characteristics

| Feature | Behavior |
|---------|----------|
| **Consistency** | Asynchronous (eventual consistency) |
| **Write Availability** | Only master accepts writes |
| **Read Scaling** | Distribute reads across replicas |
| **Data Safety** | Replicas provide redundancy |
| **Chain Replication** | Replica can be master to another replica |

### `WAIT` Command (Semi-Synchronous)

```redis
SET important-data "value"
WAIT 2 5000    -- Wait for 2 replicas to ACK within 5000ms
-- Returns number of replicas that acknowledged
```

---

## Redis Sentinel (Automatic Failover)

Sentinel monitors master/replica instances and performs **automatic failover**.

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Sentinel 1  │  │  Sentinel 2  │  │  Sentinel 3  │
│  (monitor)   │  │  (monitor)   │  │  (monitor)   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │     Monitoring all instances      │
       │                 │                 │
┌──────▼─────┐    ┌──────▼─────┐    ┌──────▼─────┐
│   MASTER   │    │  REPLICA-1 │    │  REPLICA-2 │
│ 6379       │    │  6380      │    │  6381      │
└────────────┘    └────────────┘    └────────────┘
```

### Sentinel Configuration

```ini
# sentinel.conf
sentinel monitor mymaster 192.168.1.100 6379 2
# "2" = quorum — minimum sentinels that must agree master is down

sentinel down-after-milliseconds mymaster 5000
# Mark as subjectively down after 5s of no response

sentinel failover-timeout mymaster 60000
# Abort failover if takes longer than 60s

sentinel parallel-syncs mymaster 1
# How many replicas sync from new master simultaneously
```

### Failover Process

```
1. Sentinel detects master is unreachable (SDOWN — Subjective Down)
2. Sentinel asks other Sentinels to confirm (ODOWN — Objective Down)
3. If quorum agrees → Leader election among Sentinels
4. Leader Sentinel picks best replica:
   - Highest priority (lower `replica-priority` value)
   - Most replication offset (most up-to-date)
   - Lexicographically smallest runid (tiebreaker)
5. Promoted replica executes REPLICAOF NO ONE
6. Other replicas reconfigured to replicate from new master
7. Clients notified of new master address
```

### Connecting Through Sentinel (Python)

```python
from redis.sentinel import Sentinel

sentinel = Sentinel(
    [('sentinel1', 26379), ('sentinel2', 26379), ('sentinel3', 26379)],
    socket_timeout=0.5
)

# Get master connection (auto-failover)
master = sentinel.master_for('mymaster', socket_timeout=0.5)
master.set('key', 'value')

# Get replica for reads
replica = sentinel.slave_for('mymaster', socket_timeout=0.5)
value = replica.get('key')
```

---

## Redis Cluster (Horizontal Scaling)

Redis Cluster provides **automatic sharding** across multiple nodes with built-in failover.

### Hash Slots

```
Total: 16,384 hash slots distributed across nodes

Node A: Slots 0-5460
Node B: Slots 5461-10922
Node C: Slots 10923-16383

Key → Slot mapping:
  slot = CRC16(key) % 16384

Example:
  CRC16("user:1001") % 16384 = 12539 → Node C
  CRC16("user:1002") % 16384 = 3210  → Node A
```

### Cluster Architecture

```
┌──────────────────Cluster──────────────────────────┐
│                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │  Master A   │  │  Master B   │  │  Master C   ││
│  │ Slots 0-5460│  │Slots 5461-  │  │Slots 10923- ││
│  │             │  │    10922    │  │    16383    ││
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘│
│         │                │                │        │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐│
│  │ Replica A1  │  │ Replica B1  │  │ Replica C1  ││
│  └─────────────┘  └─────────────┘  └─────────────┘│
│                                                    │
└────────────────────────────────────────────────────┘
```

### Setup

```bash
# Create a 6-node cluster (3 masters + 3 replicas)
redis-cli --cluster create \
  127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 \
  127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 \
  --cluster-replicas 1

# Check cluster status
redis-cli -c -p 7000 CLUSTER INFO
redis-cli -c -p 7000 CLUSTER NODES
```

### Hash Tags (Force Keys to Same Slot)

```redis
-- Keys with same hash tag go to same slot
SET {user:1001}.profile "data"
SET {user:1001}.settings "data"
SET {user:1001}.session "data"
-- All three → CRC16("user:1001") % 16384 → same slot!

-- This enables multi-key operations across these keys
MGET {user:1001}.profile {user:1001}.settings
```

### MOVED and ASK Redirections

```
Client sends: GET user:1001 to Node A
If key is on Node C:
  Node A responds: -MOVED 12539 192.168.1.3:7002
  Client retries: GET user:1001 to Node C

During resharding (slot migration):
  Node responds: -ASK 12539 192.168.1.3:7002
  Client sends: ASKING + GET user:1001 to Node C
```

### Cluster Limitations

- **No multi-key operations** across different slots (unless using hash tags)
- **No multi-database** (`SELECT` not supported, only db 0)
- **Pub/Sub** messages broadcast to ALL nodes (not slot-specific)
- **Lua scripts** must use keys in same slot
- **Larger cluster → more gossip overhead**

---

## Comparison

| Feature | Standalone | Sentinel | Cluster |
|---------|-----------|----------|---------|
| **Sharding** | ❌ | ❌ | ✅ Auto (16,384 slots) |
| **Failover** | ❌ | ✅ Automatic | ✅ Automatic |
| **Max Data** | Single node RAM | Single master RAM | Sum of all masters' RAM |
| **Write Scaling** | Single node | Single master | Multiple masters |
| **Read Scaling** | ❌ | ✅ Replicas | ✅ Replicas |
| **Complexity** | Low | Medium | High |
| **Min Nodes** | 1 | 3 Sentinels + 1 Master + 1 Replica | 6 (3 masters + 3 replicas) |

---

## Interview Questions — High Availability

### Q1: You have a Redis Cluster with 3 masters. Master B goes down. What happens?

**Answer:**
1. Other masters detect B is unreachable (via gossip protocol / heartbeats)
2. After `cluster-node-timeout` (default 15 seconds), B is marked as `PFAIL` (probably fail)
3. When majority of masters agree → B is marked as `FAIL`
4. **Replica B1** is promoted to master and takes over slots 5461-10922
5. If Replica B1 also fails → cluster goes into `FAIL` state for those slots
6. `cluster-require-full-coverage yes` (default): entire cluster stops accepting writes
7. `cluster-require-full-coverage no`: only queries for affected slots fail

---

### Q2: How do you handle "split-brain" in Redis?

**Answer:**
Split-brain occurs when network partition causes **two masters** to accept writes.

**Prevention:**
1. **`min-replicas-to-write`**: Master refuses writes if fewer than N replicas connected
   ```redis
   min-replicas-to-write 1
   min-replicas-max-lag 10
   ```
   If master can't reach any replica for 10 seconds, it stops accepting writes.

2. **Sentinel quorum**: Requires majority of sentinels to agree before failover

3. **WAIT command**: For critical writes, wait for replica acknowledgment

4. **Network design**: Keep Sentinels on separate network segments

**On resolution:** The old master (now isolated) becomes replica of new master, losing any writes that occurred during partition.

---

### Q3: Your Redis Cluster needs to add a 4th master. Walk through the process.

**Answer:**

```bash
# 1. Add new empty node to cluster
redis-cli --cluster add-node 127.0.0.1:7006 127.0.0.1:7000

# 2. Reshard: Move slots from existing masters to new master
redis-cli --cluster reshard 127.0.0.1:7000
# Specify: move ~4096 slots (16384/4) to the new node
# Source: existing 3 masters

# 3. Add a replica for the new master
redis-cli --cluster add-node 127.0.0.1:7007 127.0.0.1:7000 \
  --cluster-slave --cluster-master-id <new-master-id>

# 4. Verify
redis-cli --cluster check 127.0.0.1:7000
```

Resharding is **online** — keys are migrated one by one. During migration:
- Reads for migrating keys: `ASK` redirect to target
- Writes still work (may redirect)
- No downtime!

---

### Q4: Explain the difference between Sentinel and Cluster. When would you use each?

**Answer:**

**Use Sentinel when:**
- Single dataset fits in one server's RAM
- Need automatic failover + monitoring
- Read scaling via replicas is sufficient
- Simpler operational overhead

**Use Cluster when:**
- Dataset exceeds single server's RAM
- Need to scale writes (multi-master)
- Need both sharding + failover
- Accept the complexity and limitations (no multi-key across slots)

**Common pattern:** Start with Sentinel, migrate to Cluster when outgrowing single-node capacity.
