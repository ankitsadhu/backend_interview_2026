# Consumer Groups & Rebalancing (How Kafka Distributes Work)

## Consumer groups: the core rule

For a topic partitioned into `P` partitions and a consumer group:

- Kafka assigns partitions to consumer instances in the group.
- A single partition is processed by **only one** consumer in a group at a time.

If you scale out consumers, you only increase throughput up to `P` active workers.

## What triggers a rebalance?

Rebalances happen when the group membership or subscription changes, for example:

- consumer joins or leaves,
- consumer group coordinator changes,
- topic/partition count changes (new partitions added),
- configuration differences between consumers (misconfiguration can cause repeated rebalances).

## Rebalancing strategies

Historically, Kafka used “eager” rebalancing.
Modern clients can use “cooperative” rebalancing (less disruptive).

The interview-worthy idea:

- Rebalance causes partitions to move.
- During movement, consumers stop/rewind processing based on committed offsets and state.

## Commit timing and correctness

Common strategy:

- Disable auto-commit.
- Process record(s).
- Commit only after success.

But you must handle what happens during rebalances:

- callbacks/hooks may be called on revoke/assign events.
- you should ensure you don’t “ack” offsets for messages you haven’t finished.

## Poison pill / retry loops

If a message always fails:

- you need a dead-letter queue (DLQ) pattern,
- otherwise the consumer may repeatedly retry the same partition offsets and stall progress.

## Key interview scenarios

1. “We see duplicates after scaling consumers.”
   - likely commit-after-processing mismatch or non-idempotent processing.
2. “Lag increases after deploy.”
   - maybe consumer group stuck in repeated rebalances or processing throughput < produce rate.
3. “Ordering is broken.”
   - ordering is only guaranteed within partition; your key/partitioning must match ordering needs.

