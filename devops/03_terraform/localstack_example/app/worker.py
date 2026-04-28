import json
import logging
import time

from aws_clients import boto3_client, boto3_resource, get_queue_url
from settings import settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("order-worker")


def table():
    dynamodb = boto3_resource("dynamodb")
    return dynamodb.Table(settings.orders_table_name)


def process_message(message: dict):
    body = json.loads(message["Body"])
    order_id = body["order_id"]

    logger.info("processing order_id=%s", order_id)

    audit_key = f"audit/{order_id}/{int(time.time())}.json"
    audit_document = {
        "order_id": order_id,
        "event_type": body.get("event_type"),
        "processed_at": int(time.time()),
        "processor": "localstack-demo-worker",
    }

    s3 = boto3_client("s3")
    s3.put_object(
        Bucket=settings.invoice_bucket_name,
        Key=audit_key,
        Body=json.dumps(audit_document).encode("utf-8"),
        ContentType="application/json",
    )

    table().update_item(
        Key={"order_id": order_id},
        UpdateExpression="SET #status = :status, audit_object_key = :audit_key, updated_at = :updated_at",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":status": "PROCESSED",
            ":audit_key": audit_key,
            ":updated_at": int(time.time()),
        },
    )


def run_forever():
    sqs = boto3_client("sqs")
    queue_url = get_queue_url()

    logger.info("worker started queue_url=%s", queue_url)

    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=10,
            VisibilityTimeout=30,
        )

        for message in response.get("Messages", []):
            try:
                process_message(message)
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message["ReceiptHandle"],
                )
            except Exception:
                logger.exception("failed to process message")


if __name__ == "__main__":
    run_forever()

