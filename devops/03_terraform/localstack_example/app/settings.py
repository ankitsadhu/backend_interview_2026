from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_endpoint_url: str = Field(default="http://localhost:4566", alias="AWS_ENDPOINT_URL")
    orders_table_name: str = Field(default="orders", alias="ORDERS_TABLE_NAME")
    orders_queue_name: str = Field(default="orders-events", alias="ORDERS_QUEUE_NAME")
    invoice_bucket_name: str = Field(default="order-invoices-local", alias="INVOICE_BUCKET_NAME")


settings = Settings()

