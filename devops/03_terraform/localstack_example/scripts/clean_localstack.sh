#!/usr/bin/env bash
set -euo pipefail

ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"
TABLE_NAME="${ORDERS_TABLE_NAME:-orders}"
QUEUE_NAME="${ORDERS_QUEUE_NAME:-orders-events}"
BUCKET_NAME="${INVOICE_BUCKET_NAME:-order-invoices-local}"

export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
export AWS_DEFAULT_REGION="${AWS_REGION:-us-east-1}"

aws_local() {
  aws --endpoint-url "$ENDPOINT_URL" "$@"
}

echo "Deleting SQS queue if it exists"
QUEUE_URL="$(aws_local sqs get-queue-url --queue-name "$QUEUE_NAME" --query QueueUrl --output text 2>/dev/null || true)"
if [ -n "$QUEUE_URL" ]; then
  aws_local sqs delete-queue --queue-url "$QUEUE_URL" || true
fi

echo "Deleting S3 bucket contents and bucket if it exists"
if aws_local s3api head-bucket --bucket "$BUCKET_NAME" >/dev/null 2>&1; then
  aws_local s3 rm "s3://$BUCKET_NAME" --recursive || true
  aws_local s3api delete-bucket --bucket "$BUCKET_NAME" || true
fi

echo "Deleting DynamoDB table if it exists"
if aws_local dynamodb describe-table --table-name "$TABLE_NAME" >/dev/null 2>&1; then
  aws_local dynamodb delete-table --table-name "$TABLE_NAME" >/dev/null
fi

echo "Clean complete"

