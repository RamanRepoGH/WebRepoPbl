"""
Wrapper around AWS Firehose. Please note that in production, we should be using
put_record_batch to implement batching/chunking to cater to millions of customers
along with retries etc.
"""
import json
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError

class FirehoseClient:
    def __init__(self, stream_name: str):
        if os.getenv("MOCK_AWS", "true").lower() == "true":
            self.client = None
            self.stream_name = 'Mock Stream'
        else:
            self.client = boto3.client("firehose", region_name=os.environ.get('AWS_REGION', 'us-east-1'))
            self.stream_name = stream_name

    def send(self, event: dict):
        payload = (json.dumps(event) + "\n").encode("utf-8")
        try:
            if self.client is None:
                print(f"[MOCK] Sending to Firehose {self.stream_name}: {payload}")
                return {"RecordId": "mock-id-123"}
            return self.client.put_record(
                DeliveryStreamName=self.stream_name,
                Record={"Data": payload}
            )
        except (BotoCoreError, ClientError) as e:
            # Log error internally
            print(f"Error sending to Firehose: {e}")
            raise e
