#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"
BUCKET_NAME="${INVOICE_BUCKET_NAME:-order-invoices-local}"

export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
export AWS_DEFAULT_REGION="${AWS_REGION:-us-east-1}"

aws_local() {
  aws --endpoint-url "$ENDPOINT_URL" "$@"
}

echo "Checking API health"
curl -fsS "$API_URL/health"
echo

echo "Creating order"
ORDER_RESPONSE="$(curl -fsS -X POST "$API_URL/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_email": "buyer@example.com",
    "items": [
      {"sku": "book-001", "quantity": 2, "price": 19.99},
      {"sku": "course-terraform", "quantity": 1, "price": 49.00}
    ]
  }')"

echo "$ORDER_RESPONSE"
PYTHON_BIN="${PYTHON_BIN:-python3}"
ORDER_ID="$("$PYTHON_BIN" -c 'import json,sys; print(json.load(sys.stdin)["order_id"])' <<< "$ORDER_RESPONSE")"

echo "Uploading invoice for $ORDER_ID"
TMP_INVOICE="$(mktemp)"
echo "invoice for $ORDER_ID" > "$TMP_INVOICE"
curl -fsS -X POST "$API_URL/orders/$ORDER_ID/invoice" \
  -F "file=@$TMP_INVOICE;type=text/plain"
echo
rm -f "$TMP_INVOICE"

echo "Waiting for worker to process order"
sleep 4

echo "Fetching order"
curl -fsS "$API_URL/orders/$ORDER_ID"
echo

echo "Listing S3 objects"
aws_local s3api list-objects-v2 --bucket "$BUCKET_NAME" --query "Contents[].Key"
