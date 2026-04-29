# Kafka with Python (Producer/Consumer Basics)

This page focuses on the “what you actually code” side of Kafka in Python.

## Two popular Python clients

1. `confluent-kafka` (librdkafka-backed, common for production)
2. `kafka-python` (pure Python-ish client, widely used for learning)

This notes both conceptually, but code examples use `confluent-kafka` because its configuration mirrors Kafka concepts cleanly.

## Producer: minimal example

```python
from confluent_kafka import Producer
import json

producer = Producer({
    "bootstrap.servers": "localhost:9092",
    # Use 'acks=all' in production when you care about durability.
    "acks": "all",
})

topic = "events"

event = {"type": "user.registered", "user_id": "u1"}
key = event["user_id"]  # ensures per-user ordering (if partitioning uses key)

def delivery_report(err, msg):
    if err is not None:
        # In production: log and potentially trigger retry / alerting.
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

producer.produce(
    topic=topic,
    key=key,
    value=json.dumps(event).encode("utf-8"),
    callback=delivery_report
)

producer.flush(10)  # ensure outstanding messages are sent
```

### Practical producer points (interview)

- You choose partitioning via `key`.
- Producer delivery report callback is where you observe success/failure.
- `flush()` (or background event handling) matters for graceful shutdown.

## Consumer: minimal example (manual loop)

```python
from confluent_kafka import Consumer, KafkaError
import json

consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "events-workers",
    "auto.offset.reset": "earliest",  # dev-friendly; consider 'latest' in prod
    "enable.auto.commit": False,       # prefer explicit commits when correctness matters
})

consumer.subscribe(["events"])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            raise RuntimeError(msg.error())

        event = json.loads(msg.value().decode("utf-8"))
        # Process event...

        # If processing succeeds:
        consumer.commit(message=msg)
finally:
    consumer.close()
```

### Consumer correctness idea

- If you commit before processing, failures can cause data loss (offset advanced but work not done).
- If you process and then commit, you reduce loss but may reprocess on crash (duplicate risk).

Delivery semantics doc explains how you manage this tradeoff.

## Rebalance-aware processing (important)

In production, consumers should be robust to rebalances:

- Use cooperative rebalancing if possible.
- Commit offsets only after successful processing.
- Keep processing idempotent.

See `05-consumer-groups-and-rebalancing.md` for deeper internals and strategies.

