import json
import time
import uuid
from decimal import Decimal
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel, Field

from aws_clients import boto3_client, boto3_resource, get_queue_url
from settings import settings


app = FastAPI(title="LocalStack Order Service", version="1.0.0")


class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(gt=0)
    price: Decimal = Field(gt=0)


class CreateOrderRequest(BaseModel):
    customer_email: str
    items: list[OrderItem]


def now_epoch() -> int:
    return int(time.time())


def decimal_to_json(value: Any):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [decimal_to_json(item) for item in value]
    if isinstance(value, dict):
        return {key: decimal_to_json(item) for key, item in value.items()}
    return value


def table():
    dynamodb = boto3_resource("dynamodb")
    return dynamodb.Table(settings.orders_table_name)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/orders", status_code=201)
def create_order(payload: CreateOrderRequest):
    order_id = str(uuid.uuid4())
    created_at = now_epoch()
    total = sum(item.quantity * item.price for item in payload.items)

    order = {
        "order_id": order_id,
        "customer_email": payload.customer_email,
        "items": [item.model_dump() for item in payload.items],
        "total": total,
        "status": "PENDING",
        "created_at": created_at,
        "updated_at": created_at,
    }

    table().put_item(Item=order)

    sqs = boto3_client("sqs")
    sqs.send_message(
        QueueUrl=get_queue_url(),
        MessageBody=json.dumps({
            "event_type": "ORDER_CREATED",
            "order_id": order_id,
            "created_at": created_at,
        }),
    )

    return decimal_to_json(order)


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    response = table().get_item(Key={"order_id": order_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="order not found")
    return decimal_to_json(item)


@app.get("/orders")
def list_orders():
    response = table().scan(Limit=50)
    return {"items": decimal_to_json(response.get("Items", []))}


@app.post("/orders/{order_id}/invoice")
async def upload_invoice(order_id: str, file: UploadFile):
    response = table().get_item(Key={"order_id": order_id})
    if "Item" not in response:
        raise HTTPException(status_code=404, detail="order not found")

    content = await file.read()
    object_key = f"invoices/{order_id}/{file.filename}"

    s3 = boto3_client("s3")
    s3.put_object(
        Bucket=settings.invoice_bucket_name,
        Key=object_key,
        Body=content,
        ContentType=file.content_type or "application/octet-stream",
    )

    table().update_item(
        Key={"order_id": order_id},
        UpdateExpression="SET invoice_object_key = :key, updated_at = :updated_at",
        ExpressionAttributeValues={
            ":key": object_key,
            ":updated_at": now_epoch(),
        },
    )

    return {
        "order_id": order_id,
        "bucket": settings.invoice_bucket_name,
        "object_key": object_key,
    }

