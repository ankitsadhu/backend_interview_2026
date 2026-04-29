# Schema, Security, Monitoring & Troubleshooting

## Schema management (evolution)

Kafka itself moves bytes/records; your **schemas** define meaning.

Common approach: use a **Schema Registry** with:

- Avro
- Protobuf
- JSON Schema (less common in strict environments)

### Compatibility (must-know interview topic)

Schema evolution must be backward/forward compatible so old producers/consumers can coexist during deployments.

Compatibility modes you’ll hear:

- Backward: new schema can read old data.
- Forward: old schema can read new data.
- Full: both directions.

Key principle:

> “Design schemas so additions/removals follow compatibility rules; avoid breaking changes without coordinated rollout.”

## Security: authentication, encryption, authorization

### Encryption in transit

- TLS between clients and brokers.

### Authentication

Common mechanisms:

- SASL (mechanisms like SCRAM, OAuth-based variants, or Kerberos depending on setup)

### Authorization

Kafka ACLs can restrict:

- who can produce to a topic,
- who can consume,
- who can describe topics, etc.

Interview advice:

> “Assume least privilege: producers and consumers should only have permissions for the topics they need.”

## Monitoring: what to watch

You should monitor (at minimum):

- Consumer lag (per group / partition)
- Request errors / latency (produce/fetch)
- Under-replicated partitions
- Rebalance frequency (symptom of issues)
- Disk usage / segment sizes / retention behavior

## Troubleshooting: common problems and what to check

### Symptom: consumer lag grows

Likely causes:

- consumers slower than producers,
- stuck consumer (poison message, blocking dependency),
- repeated rebalances,
- partition skew (hot partitions).

Actions:

- inspect consumer group state,
- check processing times,
- validate partitioning key distribution,
- ensure DLQ/retry strategy.

### Symptom: duplicates after failure

Likely causes:

- commit strategy before successful processing,
- non-idempotent side effects,
- retry behavior without deduplication.

Actions:

- make processing idempotent,
- commit after success,
- consider transactional/idempotent patterns.

