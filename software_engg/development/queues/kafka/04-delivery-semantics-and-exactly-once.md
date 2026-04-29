# Delivery Semantics (At-most-once, At-least-once, Exactly-once)

Kafka itself gives you durability and ordered logs, but **end-to-end processing semantics** depend on how you:

- configure producer delivery (`acks`, retries, idempotence),
- handle consumer commits relative to processing,
- optionally use Kafka transactions.

## At-most-once

Goal: “Never process the same record twice.”

How it usually happens:

- commit offsets early, or
- “fire-and-forget” production without safe retry semantics.

Failure behavior:

- If the consumer crashes after committing but before processing, you can lose events.

Interview line:

> “At-most-once favors avoiding duplicates at the cost of possible data loss.”

## At-least-once

Goal: “Never lose records; duplicates are allowed.”

Common approach:

- process first,
- then commit offsets.

Failure behavior:

- If the consumer crashes after processing but before committing, it may reprocess the record.

How you handle duplicates:

- make processing idempotent (deduplicate by event id / version),
- or store processed offsets / keys.

Interview line:

> “At-least-once gives durability to processing via reprocessing, and idempotency handles duplicates.”

## Exactly-once (practical nuance)

End-to-end exactly-once is the hardest promise.

In Kafka, the “exactly-once” story is typically implemented via **transactions**:

- enable **idempotent producer**,
- enable producer transactions,
- consume, process, and produce within a transaction boundary.

Why it’s complex:

- you need correct transaction IDs,
- consumer must commit offsets as part of the transaction,
- downstream systems (databases) must also support idempotency/transactions (or you must build it).

Interview line:

> “Kafka exactly-once is ‘end-to-end exactly-once’ when both Kafka and your sinks participate correctly.”

## Key producer configurations (conceptual)

- `acks`: how many replicas must acknowledge before success.
- retries: retry on transient failures.
- idempotence (idempotent producer): prevents duplicates due to retries.
- transactions: enable Kafka transactional writes.

## Key consumer rule of thumb

If you want fewer surprises:

- do not commit offsets before successful processing,
- keep processing idempotent (even with exactly-once patterns, real systems can still need guardrails).

