# Replication, Fault Tolerance & Internals (Leader, ISR, Failures)

This doc focuses on the internals that show up in advanced interviews.

## Leaders and followers

For each partition:

- One broker is the **leader** (handles reads/writes).
- Other brokers are **followers/replicas** (replicate from leader).

## Replication factor and durability

The **replication factor** determines:

- how many replicas exist,
- how many failures the partition can tolerate while still having available replicas.

## ISR (In-Sync Replicas)

Kafka tracks replicas that are “caught up enough” with the leader in the **ISR set**.

When acknowledgements are configured with `acks=all` (conceptually), Kafka will wait for replicas in ISR.

Interview-worthy phrase:

> “If a replica is out of sync, it may be removed from ISR, affecting what `acks=all` actually means.”

## Under-replicated partitions

If enough replicas are down/out of ISR:

- producers may fail (depending on configuration),
- consumers might experience unavailability until reassignment completes.

## Leader election / failover

On broker failure:

- controller triggers partition leader election,
- ISR influences who becomes new leader,
- consumers reconnect and continue from committed offsets.

## Log retention and compaction (internals tie-in)

Two major retention styles:

1. Time/size retention (records removed after retention window)
2. Log compaction (keep latest record per key, subject to settings)

Why it matters:

- compaction is useful for “current state” topics (careful with tombstones),
- time-based retention is useful for event history replay.

