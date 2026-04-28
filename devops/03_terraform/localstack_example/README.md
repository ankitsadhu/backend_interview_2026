# LocalStack Production-Style Web App Example

This folder is a practical LocalStack learning project.

You will build a small production-style order processing backend locally using AWS-like services through LocalStack:

- FastAPI for the web API
- S3 for invoice/audit object storage
- SQS for async processing
- DynamoDB for order state
- Docker Compose for local orchestration
- bootstrap scripts for repeatable infrastructure setup

The goal is not to memorize commands. The goal is to learn how a real engineer thinks while building cloud-backed application behavior locally and safely.

## Architecture

```text
Client
  |
  v
FastAPI app
  |
  +-- DynamoDB: order records
  +-- S3: invoice and audit objects
  +-- SQS: order processing events
          |
          v
       Worker
          |
          +-- DynamoDB: status updates
          +-- S3: audit trail
```

## Folder Structure

```text
devops/06_localstack_example/
  app/
    aws_clients.py
    main.py
    settings.py
    worker.py
    requirements.txt
  docs/
    01_localstack_fundamentals.md
    02_project_walkthrough.md
    03_production_mapping.md
    04_interview_questions.md
  scripts/
    bootstrap_localstack.sh
    smoke_test.sh
    clean_localstack.sh
  docker-compose.yml
  Makefile
  .env.example
```

## Prerequisites

- Docker
- Docker Compose
- AWS CLI installed locally if you want to run scripts from your host
- Python knowledge helpful, but the app runs in containers

LocalStack exposes AWS-compatible APIs on port `4566`. This example uses the single endpoint URL:

```text
http://localhost:4566
```

Inside Docker Compose containers, the app uses:

```text
http://localstack:4566
```

## Quick Start

From this folder:

```bash
docker compose up -d localstack
make bootstrap
docker compose up --build app worker
```

In another terminal:

```bash
make smoke
```

Open API docs:

```text
http://localhost:8000/docs
```

## Useful Commands

```bash
# Start LocalStack only
docker compose up -d localstack

# Create S3 bucket, SQS queue, DynamoDB table
make bootstrap

# Start API and worker
docker compose up --build app worker

# Run an end-to-end smoke test
make smoke

# See LocalStack logs
docker compose logs -f localstack

# Clean local resources
make clean-local
```

## Study Order

1. Read [LocalStack Fundamentals](docs/01_localstack_fundamentals.md)
2. Read [Project Walkthrough](docs/02_project_walkthrough.md)
3. Run the app and smoke test
4. Read [Production Mapping](docs/03_production_mapping.md)
5. Practice [Interview Questions](docs/04_interview_questions.md)

## What This Teaches

- how local cloud emulation works
- how app code switches between local and real AWS using endpoints
- how to bootstrap cloud-like resources repeatably
- how API and worker services communicate asynchronously
- how to design local development workflows that resemble production
- how to discuss LocalStack in interviews without overselling it

