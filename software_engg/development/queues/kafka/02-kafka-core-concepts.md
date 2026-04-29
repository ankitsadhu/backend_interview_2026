# Kafka Core Concepts (Topics, Partitions, Offsets)

## Topics and partitions

- A **topic** is a logical stream name.
- A topic is split into **partitions**.
- Each partition is:
  - An ordered sequence of records.
  - Stored durably as an append-only log.

### Ordering guarantee

Kafka guarantees ordering **within a partition**.

If you need ordering for a key (example: all events for a user), you must:

1. Use a **partition key** (commonly the same as the ordering key).
2. Ensure all related events map to the same partition.

## Offsets (the “cursor”)

Offsets are monotonically increasing sequence numbers per partition.

- Consumers read records and advance offsets.
- The “committed offset” is how Kafka remembers progress for a consumer group.
- If a consumer restarts, it typically resumes from the last committed offset (depending on config and commit strategy).

Interview phrasing to remember:

> “Offsets live per partition, but consumer progress is tracked by consumer groups.”

## Producers and partitioning

When producing to a topic:

- The producer chooses the target partition using the **message key** (if provided) or a default strategy (e.g. round-robin).
- If you always provide the same key, Kafka routes records with that key consistently to the same partition (ordering + scaling).

## Consumer groups: how work is split

For a given topic:

- A consumer group gets partitions assigned.
- In the group, each partition is processed by at most one active consumer instance at a time.
- If the number of consumers exceeds partitions, some consumers will be idle.

## Retention (what happens to old data?)

Kafka brokers keep records according to retention policies:

- `retention.ms` / `retention.bytes` for time/size-based retention.
- **Log compaction** for key-based compaction (latest value per key, subject to configuration).

Retention is key for replay and for understanding “how far back can I read?”

## Durability vs replication vs commit

This is a classic interview confusion point:

- “Delivered to broker” does not necessarily mean “replicated to all replicas”.
- “Acknowledged by producer” can mean different durability levels depending on `acks`.
- “Offset committed” is about consumer progress tracking, not broker persistence.

Study the delivery semantics doc next for exact details.

