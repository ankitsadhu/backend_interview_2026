# Designing Topics & Partitions (Interview + Real Engineering)

## Partitioning strategy: your biggest lever

Partition count and partitioning key shape:

- throughput,
- ordering behavior,
- scalability,
- hot-spot risk,
- operational complexity (rebalances, replication cost).

### Ordering

If you require ordering for a business key (example: `user_id`):

- Use that business key as the Kafka message key.
- Ensure you always use the same key for related events.

### Parallelism

More partitions generally means more parallelism (within a topic).

But “more partitions” has tradeoffs:

- more metadata and replication overhead,
- more consumer work units,
- harder operations if partitions are too small or too hot.

## Partition count sizing (practical heuristic)

There is no universal formula, but a common approach:

1. Estimate peak events/sec.
2. Estimate payload size and target throughput per partition.
3. Add headroom for spikes and replication overhead.
4. Ensure consumer group can process partitions in parallel.

In interviews, it’s fine to say:

> “We size partitions based on throughput per partition, expected consumer concurrency, and leave room for growth, then monitor lag and adjust when necessary.”

## Key design: avoiding hot partitions

If your key distribution is skewed:

- one partition becomes a hot spot,
- consumer throughput becomes bottlenecked,
- ordering for that hot key is preserved, but overall throughput collapses.

Mitigation patterns:

- change key granularity (if acceptable),
- introduce salting (careful: affects ordering),
- split topics by access pattern when needed.

## Multi-topic vs single-topic (tradeoff)

Consider:

- schema evolution and compatibility,
- consumer isolation (independent scaling),
- operational complexity (more topics to manage),
- ability to replay specific event types.

Many systems use:

- “one topic per event type” for clarity,
- keys for ordering,
- schema registry for evolution.

