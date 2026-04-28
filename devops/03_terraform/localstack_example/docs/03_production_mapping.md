# Production Mapping

LocalStack helps you develop the integration shape locally. Production still needs cloud-grade security, reliability, observability, and deployment discipline.

## Local vs Production

| Concern | LocalStack Example | Production Version |
|---------|--------------------|--------------------|
| API | FastAPI container | ECS, EKS, App Runner, Lambda, or EC2 |
| Queue | LocalStack SQS | Real SQS with DLQ and alarms |
| Object storage | LocalStack S3 | S3 with encryption, lifecycle, IAM, block public access |
| Database | LocalStack DynamoDB | DynamoDB with PITR, capacity planning, alarms |
| Credentials | dummy `test/test` | IAM roles, OIDC, short-lived credentials |
| Network | Docker Compose network | VPC, private subnets, endpoints, security groups |
| Logs | container logs | CloudWatch/OpenTelemetry/SIEM |
| Deployment | local Docker Compose | CI/CD with approvals and IaC |

## Reliability Gaps to Add in Production

### SQS Dead-Letter Queue

If a message fails repeatedly, it should move to a DLQ.

Why:

```text
Without a DLQ, one poison message can be retried forever and hide real failures.
```

### Idempotency

SQS can deliver messages more than once.

Worker logic should tolerate duplicates.

Example strategy:

```text
If order is already PROCESSED, skip processing.
```

### Visibility Timeout

Visibility timeout should be longer than expected processing time.

If it is too short:

```text
two workers may process the same message concurrently.
```

### Transaction Boundaries

This app writes to S3 and DynamoDB separately.

Production question:

```text
What if S3 succeeds but DynamoDB update fails?
```

Possible answers:

- retry with idempotent keys
- reconciliation job
- outbox pattern
- compensating cleanup
- event-driven state repair

## Security Controls

Production S3:

- block public access
- bucket encryption
- least-privilege IAM
- access logs if required
- lifecycle rules

Production DynamoDB:

- IAM scoped to table
- PITR enabled
- encryption
- backup strategy
- no broad wildcard permissions

Production SQS:

- least-privilege send/receive/delete permissions
- DLQ
- encryption
- alarms on queue depth and oldest message age

## Observability

Track:

- API latency and error rate
- created orders count
- SQS queue depth
- SQS oldest message age
- worker success/failure count
- DynamoDB throttles/errors
- S3 put failures
- trace ID across API and worker

Interview answer:

```text
For async systems, I always monitor queue depth and oldest message age. They reveal worker lag before users report stale state.
```

## LocalStack in CI

Use LocalStack in CI for integration tests:

```text
start LocalStack
bootstrap resources
run app integration tests
tear down
```

Benefits:

- fast feedback
- no cloud cost
- repeatable test environment

Limits:

- not a substitute for staging in real AWS
- may not perfectly emulate IAM, networking, or service-specific behavior

## How This Maps to IaC

This local project uses shell scripts for clarity.

A production version should use:

- Terraform
- CloudFormation
- CDK
- Pulumi

Local shell bootstrap teaches the service model. IaC teaches controlled production lifecycle.

## Production Upgrade Path

1. Replace shell bootstrap with Terraform.
2. Add DLQ for SQS.
3. Add idempotency to worker.
4. Add structured logs with correlation IDs.
5. Add OpenTelemetry traces.
6. Add IAM policies per component.
7. Add CI integration tests using LocalStack.
8. Deploy to a real AWS dev environment.
9. Run load and failure tests.

