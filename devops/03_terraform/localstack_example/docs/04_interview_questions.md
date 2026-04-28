# LocalStack Interview Questions

## Fundamentals

### 1. What is LocalStack?

LocalStack is a local AWS-compatible emulator used for local development and integration testing against AWS-like APIs.

### 2. Why use LocalStack?

To develop and test cloud integrations locally without creating real cloud resources or paying for every test cycle.

### 3. Is LocalStack a replacement for AWS staging?

No. It improves local feedback, but staging tests in real AWS are still needed for IAM, networking, service limits, latency, and managed service behavior.

### 4. How does application code switch between LocalStack and real AWS?

By configuring endpoint URLs and credentials through environment variables. Local uses `http://localhost:4566`; production omits the custom endpoint and uses real AWS endpoints.

## Practical Design

### 5. Why use SQS between API and worker?

SQS decouples synchronous API handling from slower background work, improves resilience, and lets workers scale independently.

### 6. Why store invoices in S3 instead of DynamoDB?

S3 is better for object/blob storage. DynamoDB is better for structured queryable metadata and state.

### 7. Why use DynamoDB for orders?

It provides simple key-value/document access with predictable performance for order lookup by `order_id`.

### 8. What can go wrong when using SQS?

Duplicate delivery, poison messages, visibility timeout issues, worker crashes, queue backlog, and missing DLQ.

### 9. How do you make the worker production-ready?

Add idempotency, DLQ, retries with backoff, structured logs, metrics, tracing, graceful shutdown, and alarms on queue depth and oldest message age.

### 10. What is visibility timeout?

It is the period during which a received SQS message is hidden from other consumers. If not deleted before timeout, it can be delivered again.

## LocalStack Cross Questions

### 11. If code works in LocalStack, can it still fail in AWS?

Yes. IAM, networking, quotas, service-specific behavior, latency, eventual consistency, and security policies may differ.

### 12. What should you avoid hardcoding?

Endpoint URLs, credentials, regions, resource names, and environment-specific settings.

### 13. Why use dummy credentials locally?

LocalStack accepts them for local API compatibility. Real credentials should not be needed for local emulation.

### 14. How would you run this in CI?

Start LocalStack as a service, bootstrap resources, run integration tests, collect logs, and tear down the environment.

### 15. How do you prevent tests from depending on old local state?

Use unique resource names per test run or clean resources before/after tests.

## Production Cross Questions

### 16. What if the API writes to DynamoDB but fails to send SQS message?

The order stays `PENDING`. Fix options include transactional outbox, reconciliation job, retry policy, or DynamoDB streams.

### 17. What if worker writes S3 audit but fails updating DynamoDB?

Use idempotent object keys, retry update, and reconciliation logic that can compare audit objects with order state.

### 18. Why is idempotency critical?

Distributed systems retry. SQS can deliver duplicates. Idempotency prevents duplicate side effects.

### 19. What metrics matter most?

API errors/latency, SQS queue depth, oldest message age, worker failures, DynamoDB throttles, S3 failures, and end-to-end processing time.

### 20. How would you secure the production version?

Use IAM roles, least-privilege policies, encrypted S3/DynamoDB/SQS, private networking where needed, secret management, audit logs, and no public buckets.

## MANG-Style Scenario

### 21. Orders are created, but status remains `PENDING`. Debug it.

Check:

1. API successfully sends SQS message.
2. SQS queue depth and oldest message age.
3. Worker is running and polling correct queue URL.
4. Worker logs for processing errors.
5. DynamoDB update permissions/errors.
6. Visibility timeout and retries.
7. DLQ for poison messages.

Strong answer:

```text
I would follow the event path: API write, queue enqueue, worker receive, side effects, message delete, and final state update.
```

### 22. In production, users report invoices uploaded but missing later. Debug it.

Check S3 put success, bucket/key naming, DynamoDB object key update, IAM permissions, lifecycle rules, accidental deletes, region mismatch, and app logs with correlation ID.

### 23. How would you evolve this architecture for high scale?

Scale API and workers independently, tune SQS batching/visibility timeout, add DLQ, use DynamoDB partition-key design carefully, add autoscaling based on queue age, and add end-to-end tracing.

