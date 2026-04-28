#!/usr/bin/env bash
set -euo pipefail

ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"
AWS_REGION="${AWS_REGION:-us-east-1}"
TABLE_NAME="${ORDERS_TABLE_NAME:-orders}"
QUEUE_NAME="${ORDERS_QUEUE_NAME:-orders-events}"
BUCKET_NAME="${INVOICE_BUCKET_NAME:-order-invoices-local}"

export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
export AWS_DEFAULT_REGION="$AWS_REGION"

aws_local() {
  aws --endpoint-url "$ENDPOINT_URL" "$@"
}

echo "Waiting for LocalStack at $ENDPOINT_URL"
until aws_local sts get-caller-identity >/dev/null 2>&1; do
  sleep 2
done

echo "Creating SQS queue: $QUEUE_NAME"
aws_local sqs create-queue \
  --queue-name "$QUEUE_NAME" \
  --attributes VisibilityTimeout=30,ReceiveMessageWaitTimeSeconds=10 >/dev/null

echo "Creating S3 bucket: $BUCKET_NAME"
if [ "$AWS_REGION" = "us-east-1" ]; then
  aws_local s3api create-bucket --bucket "$BUCKET_NAME" >/dev/null 2>&1 || true
else
  aws_local s3api create-bucket \
    --bucket "$BUCKET_NAME" \
    --create-bucket-configuration LocationConstraint="$AWS_REGION" >/dev/null 2>&1 || true
fi

echo "Creating DynamoDB table: $TABLE_NAME"
if ! aws_local dynamodb describe-table --table-name "$TABLE_NAME" >/dev/null 2>&1; then
  aws_local dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName=order_id,AttributeType=S \
    --key-schema AttributeName=order_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST >/dev/null

  aws_local dynamodb wait table-exists --table-name "$TABLE_NAME"
fi

echo "Bootstrap complete"
aws_local sqs get-queue-url --queue-name "$QUEUE_NAME"
aws_local s3api list-buckets --query "Buckets[].Name"
aws_local dynamodb describe-table --table-name "$TABLE_NAME" --query "Table.TableStatus"

