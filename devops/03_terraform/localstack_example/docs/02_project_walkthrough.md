# Project Walkthrough

This walkthrough treats the project like a real engineering task.

Goal:

```text
Build an order API where order creation is fast, processing is async, invoices are stored as objects, and order state is queryable.
```

## Step 1: Define the System Boundary

We need:

- API for users or frontend
- database for order state
- object storage for invoice files
- queue for background processing
- worker for async tasks

Local services:

```text
FastAPI + LocalStack S3 + LocalStack SQS + LocalStack DynamoDB
```

Production mapping:

```text
ECS/EKS/App Runner/Lambda + S3 + SQS + DynamoDB
```

## Step 2: Start LocalStack

```bash
docker compose up -d localstack
```

Check health:

```bash
curl http://localhost:4566/_localstack/health
```

## Step 3: Bootstrap Infrastructure

```bash
make bootstrap
```

This creates:

- SQS queue: `orders-events`
- S3 bucket: `order-invoices-local`
- DynamoDB table: `orders`

Why a script?

```text
Because local environments should be reproducible. Manual clicking does not scale to teams.
```

## Step 4: Start API and Worker

```bash
docker compose up --build app worker
```

API:

```text
http://localhost:8000
```

Swagger docs:

```text
http://localhost:8000/docs
```

## Step 5: Create an Order

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "buyer@example.com",
    "items": [
      {"sku": "book-001", "quantity": 2, "price": 19.99}
    ]
  }'
```

What happens:

1. API validates request.
2. API writes order to DynamoDB with `PENDING` status.
3. API sends `ORDER_CREATED` message to SQS.
4. API returns immediately.

## Step 6: Worker Processes the Event

The worker long-polls SQS.

When it receives the message:

1. Reads `order_id`.
2. Writes audit document to S3.
3. Updates DynamoDB status to `PROCESSED`.
4. Deletes SQS message.

This is a classic async backend pattern.

## Step 7: Upload an Invoice

```bash
echo "invoice body" > /tmp/invoice.txt

curl -X POST http://localhost:8000/orders/<order_id>/invoice \
  -F "file=@/tmp/invoice.txt;type=text/plain"
```

What happens:

1. API checks that the order exists.
2. API uploads file to S3.
3. API stores object key on order record.

## Step 8: Inspect Local AWS Resources

```bash
aws --endpoint-url http://localhost:4566 dynamodb scan \
  --table-name orders

aws --endpoint-url http://localhost:4566 sqs list-queues

aws --endpoint-url http://localhost:4566 s3api list-objects-v2 \
  --bucket order-invoices-local
```

## Step 9: Run Smoke Test

```bash
make smoke
```

The smoke test:

- checks API health
- creates order
- uploads invoice
- waits for worker
- fetches final order
- lists S3 objects

## Step 10: Think Like Production

Before real deployment, ask:

- What happens if the worker crashes?
- What happens if S3 upload succeeds but DynamoDB update fails?
- What happens if the same SQS message is delivered twice?
- What is the retry and dead-letter strategy?
- How do we trace one order across API, SQS, worker, and storage?
- What alarms would catch failures?

This is where LocalStack practice turns into interview-ready engineering.

