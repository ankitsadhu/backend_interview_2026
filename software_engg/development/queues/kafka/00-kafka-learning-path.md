# Kafka (Python) Learning Path: Basic → Advanced → MANG

This folder contains a curated set of Markdown notes designed for Kafka interviews and practical engineering.

## How to use these notes

1. Start with `01-kafka-overview.md` and `02-kafka-core-concepts.md` to build mental models.
2. Move to `03-kafka-python-producer-consumer.md` for Python-focused implementation details.
3. Then study delivery semantics: `04-delivery-semantics-and-exactly-once.md`.
4. Go deep on consumer groups: `05-consumer-groups-and-rebalancing.md`.
5. Learn how to design topics/partitions: `06-topic-and-partition-design.md`.
6. Understand replication and failure: `07-replication-fault-tolerance-and-internals.md`.
7. Finish with security, schema evolution, and troubleshooting: `08-schema-security-monitoring-troubleshooting.md`.
8. Use `09-mang-interview-playbook.md` to practice high-frequency interview questions and strong answer patterns.

## Practice checklist (recommended)

- Build a tiny pipeline: a producer publishes events, a consumer reads and processes.
- Add a consumer group and observe partition assignment.
- Introduce failures (kill consumers) and verify that rebalancing behaves as expected.
- Add retries and confirm you understand how you avoid duplicates (idempotency / transactional patterns).
- Measure and discuss “consumer lag” and “data loss vs duplication tradeoffs”.

## Topics covered (quick index)

- Kafka architecture & terminology
- Producers/consumers in Python
- At-most-once / at-least-once / exactly-once semantics
- Consumer groups & rebalancing
- Partition strategy & ordering guarantees
- Replication, ISR, leader election, and failure modes
- Security, schema compatibility, and operational troubleshooting
- MANG-level interview Q&A patterns

