# LocalStack Fundamentals

## What Is LocalStack?

LocalStack is a local AWS-compatible cloud emulator.

Instead of creating real AWS resources, your app calls a local endpoint that behaves like AWS for many development and testing workflows.

In this project:

```text
real AWS endpoint:      https://sqs.us-east-1.amazonaws.com
LocalStack endpoint:    http://localhost:4566
container endpoint:     http://localstack:4566
```

## Why Use LocalStack?

Use LocalStack to:

- develop cloud-backed services locally
- test AWS integrations without real cloud cost
- run repeatable integration tests in CI
- practice AWS workflows safely
- debug app logic before deploying to real AWS

## What LocalStack Is Not

LocalStack is not a perfect replacement for AWS.

Differences may exist in:

- IAM enforcement
- service limits
- latency
- edge networking
- eventual consistency
- advanced managed service behavior
- production security controls

Interview answer:

```text
LocalStack is excellent for local integration feedback, but final confidence still needs tests against real cloud environments.
```

## Services Used in This Project

### S3

Stores invoice files and worker audit records.

Production equivalent:

```text
Amazon S3 bucket with encryption, lifecycle policies, public access blocked, IAM controls, and event logging.
```

### SQS

Decouples API request handling from background order processing.

Production equivalent:

```text
SQS queue with dead-letter queue, visibility timeout tuning, alarms, and idempotent consumers.
```

### DynamoDB

Stores order state.

Production equivalent:

```text
DynamoDB table with partition key design, on-demand or provisioned capacity, PITR, alarms, and access policies.
```

## Endpoint Configuration

The key difference between local and real AWS is endpoint configuration.

Local:

```python
boto3.client(
    "sqs",
    endpoint_url="http://localhost:4566",
    region_name="us-east-1",
)
```

Real AWS:

```python
boto3.client(
    "sqs",
    region_name="us-east-1",
)
```

Production-friendly lesson:

```text
Do not hardcode local endpoints in business logic. Put endpoint configuration behind environment variables.
```

## Dummy Credentials

LocalStack accepts dummy AWS credentials for local use.

This project uses:

```text
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

Real AWS should use:

- IAM roles
- managed identity equivalent
- OIDC federation
- short-lived credentials

Never commit real cloud credentials.

## Human Workflow

A human building this locally would usually:

1. Start LocalStack.
2. Bootstrap required resources.
3. Start app services.
4. Create test data through API.
5. Verify resource state in S3, SQS, and DynamoDB.
6. Add production controls once behavior works.

That is exactly how this folder is structured.

