# Azure Messaging & Events

## Messaging Decision Tree

```
Need to communicate between services?
    │
    ├── Point-to-point message queue?
    │   ├── Simple, low cost → Storage Queues
    │   └── Enterprise (sessions, DLQ, transactions) → Service Bus Queues
    │
    ├── Pub/Sub (one-to-many)?
    │   ├── Enterprise messaging → Service Bus Topics
    │   └── Event-driven (react to Azure events) → Event Grid
    │
    └── High-throughput event streaming (logs, telemetry)?
        └── Event Hubs (Azure's Kafka)
```

---

## Service Comparison

| Feature | Storage Queues | Service Bus | Event Hubs | Event Grid |
|---------|---------------|-------------|------------|------------|
| **Pattern** | Queue | Queue + Pub/Sub | Event Streaming | Event Routing |
| **Throughput** | Low-Medium | Medium | **Millions/sec** | Medium |
| **Message Size** | 64 KB | 256 KB (Standard) / 100 MB (Premium) | 1 MB | 1 MB |
| **Ordering** | No guarantee | FIFO (sessions) | Per partition | No guarantee |
| **Dead-Letter Queue** | ❌ | ✅ | ❌ | ✅ |
| **Transactions** | ❌ | ✅ | ❌ | ❌ |
| **Consumer Groups** | ❌ | ❌ | ✅ (Kafka-like) | ❌ |
| **Max Retention** | 7 days | Unlimited | 7 days (Standard) / 90 days (Premium) | 24 hours |
| **Pricing** | Per operation | Per message | Per throughput unit | Per operation |
| **Best For** | Simple decoupling | Enterprise workflows | Big data streaming | React to Azure events |

---

## 1. Azure Service Bus

Enterprise-grade message broker with queues and topics.

### Queue (Point-to-Point)

```
Producer → [Queue] → Consumer
              │
         Features:
         ├── FIFO guarantee (with sessions)
         ├── Dead-letter queue (DLQ)
         ├── Duplicate detection
         ├── Scheduled delivery
         ├── Message deferral
         ├── Transactions (atomic send/complete)
         └── Auto-forwarding
```

```python
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Send messages
connection_str = "Endpoint=sb://mybus.servicebus.windows.net/;SharedAccessKey..."
client = ServiceBusClient.from_connection_string(connection_str)

with client:
    sender = client.get_queue_sender(queue_name="orders")
    with sender:
        message = ServiceBusMessage(
            body='{"order_id": 123, "amount": 99.99}',
            subject="new-order",
            content_type="application/json",
            session_id="customer-456"  # For FIFO ordering
        )
        sender.send_messages(message)

# Receive messages
with client:
    receiver = client.get_queue_receiver(queue_name="orders")
    with receiver:
        messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for msg in messages:
            print(f"Processing: {str(msg)}")
            receiver.complete_message(msg)  # Remove from queue
            # receiver.abandon_message(msg)   # Return to queue
            # receiver.dead_letter_message(msg, reason="Invalid format")
```

### Topic (Pub/Sub)

```
Publisher → [Topic] → Subscription 1 (filter: type='order') → Consumer A
                   → Subscription 2 (filter: type='payment') → Consumer B
                   → Subscription 3 (no filter, all messages) → Consumer C
```

```python
# Send to topic
sender = client.get_topic_sender(topic_name="events")
with sender:
    message = ServiceBusMessage(
        body='{"event": "order_placed"}',
        application_properties={"type": "order", "priority": "high"}
    )
    sender.send_messages(message)

# Receive from subscription
receiver = client.get_subscription_receiver(
    topic_name="events",
    subscription_name="order-processor"
)
```

### Sessions (FIFO Guarantee)

Sessions guarantee **ordered processing** for messages with the same `session_id`:

```python
# All messages with session_id="customer-123" processed in order by same consumer
message = ServiceBusMessage(
    body="order data",
    session_id="customer-123"
)

# Receive with session
session_receiver = client.get_queue_receiver(
    queue_name="orders",
    session_id="customer-123"  # or NEXT_AVAILABLE_SESSION
)
```

### Dead-Letter Queue (DLQ)

Messages that can't be processed end up in the DLQ:

```python
# Reasons for dead-lettering:
# 1. Max delivery count exceeded (default 10)
# 2. Message explicitly dead-lettered by consumer
# 3. TTL expired
# 4. Subscription filter doesn't match any subscription

# Read from DLQ
dlq_receiver = client.get_queue_receiver(
    queue_name="orders",
    sub_queue=ServiceBusSubQueue.DEAD_LETTER
)
```

---

## 2. Azure Event Hubs

Big data event streaming platform — **Azure's Kafka**.

```
Producers → [Event Hub] → Partition 0 → Consumer Group A → Consumer 1
                        → Partition 1                     → Consumer 2
                        → Partition 2 → Consumer Group B → Consumer 3
                        → Partition 3                     → Consumer 4
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Namespace** | Container for Event Hubs (like a Kafka cluster) |
| **Event Hub** | Equivalent to a Kafka topic |
| **Partition** | Ordered sequence within an Event Hub (2-32 default) |
| **Consumer Group** | Independent view of the event stream |
| **Throughput Unit (TU)** | 1 TU = 1 MB/s ingress, 2 MB/s egress |
| **Capture** | Auto-archive events to Blob Storage / Data Lake |

```python
from azure.eventhub import EventHubProducerClient, EventData

# Send events
producer = EventHubProducerClient.from_connection_string(
    conn_str="Endpoint=sb://myeventhub.servicebus.windows.net/;...",
    eventhub_name="telemetry"
)

with producer:
    batch = producer.create_batch()
    batch.add(EventData('{"sensor_id": "s1", "temp": 22.5}'))
    batch.add(EventData('{"sensor_id": "s2", "temp": 23.1}'))
    producer.send_batch(batch)

# Receive events (checkpoint-based)
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

checkpoint_store = BlobCheckpointStore.from_connection_string(
    blob_connection_str, "checkpoints"
)

consumer = EventHubConsumerClient.from_connection_string(
    conn_str, consumer_group="$Default", eventhub_name="telemetry",
    checkpoint_store=checkpoint_store
)

def on_event(partition_context, event):
    print(f"Partition: {partition_context.partition_id}, Data: {event.body_as_str()}")
    partition_context.update_checkpoint(event)

with consumer:
    consumer.receive(on_event=on_event, starting_position="-1")
```

### Event Hubs vs Kafka

| Feature | Event Hubs | Apache Kafka |
|---------|-----------|--------------|
| Managed? | Fully managed | Self-managed (or Confluent) |
| Protocol | AMQP, HTTPS, **Kafka protocol** | Kafka protocol |
| Partitions | Up to 32 (Standard), 2000 (Premium) | Unlimited |
| Retention | 7 days (Standard), 90 days (Premium) | Configurable |
| Consumer Groups | Up to 20 | Unlimited |
| Operations | Zero ops | High ops (ZooKeeper, brokers) |

> **Key:** Event Hubs supports the **Kafka protocol** — existing Kafka apps can connect with just an endpoint change.

---

## 3. Azure Event Grid

Reactive event routing — **respond to events from Azure resources or custom sources**.

```
Event Sources              Event Grid              Event Handlers
┌───────────────┐         ┌──────────┐           ┌───────────────┐
│ Blob Storage  │────────→│          │──────────→│ Azure Function │
│ Resource Group│────────→│  Event   │──────────→│ Logic App     │
│ IoT Hub       │────────→│  Grid    │──────────→│ Webhook       │
│ Custom Topic  │────────→│          │──────────→│ Service Bus   │
│ Azure AD      │────────→│          │──────────→│ Event Hub     │
└───────────────┘         └──────────┘           └───────────────┘
```

### Common Event Grid Scenarios

| Event Source | Event | Handler |
|-------------|-------|---------|
| Blob Storage | `BlobCreated` | Function processes uploaded file |
| Resource Group | `ResourceWriteSuccess` | Webhook logs resource changes |
| Container Registry | `ImagePushed` | Logic App triggers deployment |
| Azure AD | `UserCreated` | Function provisions user in app |
| Custom Topic | Any custom event | Multiple subscribers react |

```python
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential

client = EventGridPublisherClient(
    endpoint="https://mytopic.eastus-1.eventgrid.azure.net/api/events",
    credential=AzureKeyCredential("key...")
)

event = EventGridEvent(
    subject="/myapp/orders/123",
    event_type="Order.Placed",
    data={"order_id": 123, "amount": 99.99},
    data_version="1.0"
)

client.send([event])
```

---

## Event Grid vs Event Hubs vs Service Bus

| Dimension | Event Grid | Event Hubs | Service Bus |
|-----------|-----------|------------|-------------|
| **Purpose** | Event routing | Event streaming | Enterprise messaging |
| **Pattern** | Pub/Sub (push) | Stream (pull) | Queue + Pub/Sub |
| **When** | React to state changes | Process high-volume data | Reliable message delivery |
| **Analogy** | Webhook / notification | Kafka | RabbitMQ |
| **Ordering** | No | Per partition | FIFO (sessions) |
| **Retention** | 24 hours | 7-90 days | Unlimited |
| **Example** | Blob uploaded → resize | IoT sensor data → analytics | Order placed → payment |

---

## Common Interview Questions — Messaging

### Q1: When would you use Service Bus over Storage Queues?

**Service Bus** when you need: FIFO ordering (sessions), dead-letter queues, transactions, duplicate detection, topics (pub/sub), messages > 64 KB, at-most-once delivery. **Storage Queues** for: simple queue semantics, high volume (no frills), > 80 GB capacity, cost optimization, audit trail of all messages.

### Q2: How does Event Hubs compare to Kafka? Can you use Kafka clients?

Event Hubs is a fully managed event streaming service that supports the **Kafka producer/consumer protocol**. Existing Kafka apps can connect by changing the bootstrap server and auth config — no code changes. Event Hubs handles partition management, scaling, and retention. The main limitation is fewer consumer groups (20 vs unlimited) and shorter retention (7 days standard).

### Q3: Explain the Event Grid event delivery guarantee.

Event Grid guarantees **at-least-once delivery** with exponential backoff retry for up to 24 hours. If a handler fails, Event Grid retries with increasing delays. After max retries, events are either dead-lettered (if configured) or dropped. Handlers should be **idempotent** to handle duplicate deliveries.
