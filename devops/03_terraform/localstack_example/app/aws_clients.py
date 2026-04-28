import boto3

from settings import settings


def boto3_client(service_name: str):
    return boto3.client(
        service_name,
        region_name=settings.aws_region,
        endpoint_url=settings.aws_endpoint_url,
    )


def boto3_resource(service_name: str):
    return boto3.resource(
        service_name,
        region_name=settings.aws_region,
        endpoint_url=settings.aws_endpoint_url,
    )


def get_queue_url() -> str:
    sqs = boto3_client("sqs")
    response = sqs.get_queue_url(QueueName=settings.orders_queue_name)
    return response["QueueUrl"]

