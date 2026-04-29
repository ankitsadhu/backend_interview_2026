# MANG-Level Interview Playbook (Kafka + Python)

This doc is written to help you answer confidently in interviews.

## Answer structure that works

For scenario questions, use a 4-part answer:

1. **Assumptions**: what consistency/latency you care about.
2. **Kafka model**: topics, partitions, keys, offsets, consumer groups.
3. **Guarantees**: exactly-once vs at-least-once vs at-most-once, and how you implement it.
4. **Operational plan**: monitoring, failure modes, rollout strategy, and how you verify correctness.

## High-frequency conceptual questions

### 1) What is Kafka and why would you use it?

Strong answer:

Kafka is a durable, partitioned log. It decouples producers/consumers, supports replay via offsets, and scales through partition parallelism. I’d use it when I need event history + multiple independent consumers or high throughput.

### 2) What ordering guarantees does Kafka provide?

Strong answer:

Ordering is guaranteed within a partition. If you need ordering per entity, you must route all events for that entity to the same partition via message keys.

### 3) Explain consumer groups and rebalancing.

Strong answer:

Consumer groups share partitions; each partition is processed by at most one consumer instance in a group. Membership changes trigger rebalances which move partitions between consumers. Correct commit timing and idempotent processing reduce correctness issues.

## Delivery semantics (the “must be crisp” section)

### 4) At-least-once vs at-most-once vs exactly-once

At-most-once:
- avoids duplicates,
- but can lose data if you commit/ack too early.

At-least-once:
- no data loss (usually),
- may duplicate, so processing must be idempotent.

Exactly-once:
- hardest end-to-end,
- requires Kafka transactional patterns and correct interaction with downstream sinks (or idempotent sinks).

### 5) How do you avoid duplicates in a consumer?

Strong answer:

Make processing idempotent using an event id/version (store last processed id per key, or use unique constraints). Then commit offsets only after successful processing. This yields practical “effectively once” behavior.

## Advanced/internal questions

### 6) What is ISR and how does it affect durability?

Strong answer:

ISR is the set of replicas caught up with the leader. With `acks=all` style durability, Kafka aims to ensure the leader acknowledges only after ISR replicas have replicated. If replicas fall behind, they leave ISR, impacting how strong the durability guarantee actually is.

### 7) What happens on broker failure?

Strong answer:

Controller elects a new leader based on partition state and ISR. Producers retry transient failures; consumers reconnect and resume based on committed offsets. Replication and leader changes impact availability and throughput but do not inherently corrupt the log.

## Python-focused implementation interview questions

### 8) How do you handle commits safely with processing?

Strong answer:

Typically disable auto-commit. Process the message first, then commit the offset after success. For failure, avoid committing so the message can be reprocessed. Combine with idempotent side effects to handle reprocessing duplicates.

### 9) How do you scale consumers without breaking correctness?

Strong answer:

Scaling consumers increases parallelism up to partition count. Rebalances will move partitions, so processing must handle partition movement (rebalance callbacks), and side effects must be idempotent. Monitor rebalance frequency and consumer lag.

## System design scenarios (practice prompts)

### Scenario A: “Payments system with Kafka”

Prompt: “How would you ensure correctness when producing and consuming payment events?”

What to say:

- Identify ordering key: `account_id` (or `payment_id` depending on requirements).
- Use producer acks/idempotence.
- Use at-least-once + idempotent database writes (most common in practice).
- If you truly need end-to-end exactly-once, discuss Kafka transactions and downstream transactional sink constraints.
- Monitor lag and duplicates prevention metrics.

### Scenario B: “Event replay and schema changes”

Prompt: “How do you support schema evolution while allowing replay?”

What to say:

- Use Schema Registry with compatibility rules.
- Backward compatible schema evolution for consumers during rollout.
- Include schema/version info in events (or rely on registry + readers).
- Test compatibility and maintain consumer decoders.

## Quick self-check: what interviewers probe

- Did you explain partitioning, ordering, and offsets clearly?
- Did you tie delivery guarantees to commit strategy?
- Did you mention idempotency and operational monitoring?
- Did you show you understand failure and replay behavior?

