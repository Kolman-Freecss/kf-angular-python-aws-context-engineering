# AWS LocalStack Setup Pattern

## LocalStack Configuration

```yaml
# docker-compose.localstack.yml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,dynamodb,lambda,apigateway,iam,sts
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "localstack_data:/tmp/localstack"
    networks:
      - localstack-network

  # Your application services
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - API_URL=http://backend:8000
      - AWS_ENDPOINT=http://localstack:4566
    depends_on:
      - localstack
    networks:
      - localstack-network

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AWS_ENDPOINT=http://localstack:4566
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_DEFAULT_REGION=us-east-1
    depends_on:
      - localstack
    networks:
      - localstack-network

volumes:
  localstack_data:

networks:
  localstack-network:
    driver: bridge
```

## AWS SDK Configuration

```python
# backend/core/aws_config.py
import boto3
from botocore.config import Config
import os

def get_aws_client(service_name: str):
    """Get AWS client configured for LocalStack"""
    endpoint_url = os.getenv('AWS_ENDPOINT', 'http://localhost:4566')
    
    config = Config(
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        retries={'max_attempts': 3}
    )
    
    return boto3.client(
        service_name,
        endpoint_url=endpoint_url,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test'),
        config=config
    )

# Usage examples
s3_client = get_aws_client('s3')
dynamodb_client = get_aws_client('dynamodb')
```

## LocalStack Initialization Script

```python
# scripts/init_localstack.py
import boto3
from botocore.exceptions import ClientError
import time

def wait_for_localstack():
    """Wait for LocalStack to be ready"""
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            s3.list_buckets()
            print("LocalStack is ready!")
            return True
        except ClientError:
            print(f"Waiting for LocalStack... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(2)
    
    raise Exception("LocalStack failed to start")

def create_s3_bucket(bucket_name: str):
    """Create S3 bucket in LocalStack"""
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Created bucket: {bucket_name}")
    except ClientError as e:
        if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
            raise

def create_dynamodb_table(table_name: str):
    """Create DynamoDB table in LocalStack"""
    dynamodb = boto3.client(
        'dynamodb',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"Created table: {table_name}")
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            raise

if __name__ == "__main__":
    wait_for_localstack()
    create_s3_bucket('my-app-bucket')
    create_dynamodb_table('my-app-table')
```

## Testing with LocalStack

```python
# tests/test_aws_integration.py
import pytest
import boto3
from moto import mock_s3, mock_dynamodb

@pytest.fixture
def s3_client():
    with mock_s3():
        s3 = boto3.client(
            's3',
            endpoint_url='http://localhost:4566',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
        s3.create_bucket(Bucket='test-bucket')
        yield s3

def test_s3_upload(s3_client):
    """Test S3 upload functionality"""
    s3_client.put_object(
        Bucket='test-bucket',
        Key='test-file.txt',
        Body='test content'
    )
    
    response = s3_client.get_object(
        Bucket='test-bucket',
        Key='test-file.txt'
    )
    
    assert response['Body'].read().decode() == 'test content'
```
