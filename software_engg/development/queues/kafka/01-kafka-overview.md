# Kafka Overview (What, Why, When)

## What is Kafka?

Apache Kafka is a distributed event streaming platform that:

- Stores events durably in an append-only log.
- Scales by splitting logs into **partitions**.
- Lets multiple independent applications **consume** from the same topic at their own pace.

Kafka is often used as the “system nerve” between services: producers publish events; consumers process asynchronously.

## Why Kafka (tradeoffs)?

Kafka is a good fit when you need:

- **Decoupling**: producer and consumer evolve independently.
- **Durability**: events persist in the cluster (not just in memory).
- **Replay**: consumers can re-process historical events using offsets.
- **Throughput & parallelism**: partitions enable horizontal scaling.

Kafka is less ideal when you only need simple request/response messaging with tight coupling (sometimes a queue/RPC is simpler).

## Common use cases

- Event-driven microservices (order lifecycle, billing events, analytics events)
- Streaming analytics / ETL pipelines
- Log aggregation (especially when coupled with schema)
- Change Data Capture (CDC) patterns

## Key Kafka terms (interview-ready definitions)

- **Topic**: a named stream of records.
- **Partition**: an ordered log inside a topic.
- **Offset**: position of a record within a partition.
- **Consumer group**: a set of consumers that share work for a topic (each partition is processed by one consumer in the group at a time).
- **Broker**: a Kafka server node that hosts partitions.
- **Replication factor**: number of replicas per partition for fault tolerance.
- **Leader**: the broker responsible for reads/writes for a partition.
- **Follower replicas**: replicate from the leader.

## Kafka vs other systems (high-level)

- Kafka vs traditional queues:
  - Queues usually have a single delivery stream; Kafka supports multiple independent consumers via offsets.
  - Kafka emphasizes durable log + replay.
- Kafka vs pub/sub:
  - Kafka supports replay (by offsets), not just transient delivery.

## A simple mental model

Think: “Kafka = durable, partitioned commit log + consumer offsets + consumer groups.”

