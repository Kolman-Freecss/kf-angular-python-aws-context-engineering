# Docker & AWS Setup Guide

## Docker Configuration

### Multi-stage Dockerfile for Frontend
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
USER nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Multi-stage Dockerfile for Backend
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS production
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose for Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
    volumes:
      - frontend_static:/usr/share/nginx/html

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - AWS_ENDPOINT=http://localstack:4566
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_DEFAULT_REGION=us-east-1
    depends_on:
      - db
      - localstack
    volumes:
      - backend_logs:/app/logs

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,dynamodb,lambda,apigateway,iam,sts
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "localstack_data:/tmp/localstack"

volumes:
  frontend_static:
  backend_logs:
  postgres_data:
  localstack_data:
```

## AWS LocalStack Setup

### LocalStack Configuration
```yaml
# docker-compose.localstack.yml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,dynamodb,lambda,apigateway,iam,sts,ses,sns,sqs
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
      - DOCKER_HOST=unix:///var/run/docker.sock
      - LAMBDA_EXECUTOR=docker
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "localstack_data:/tmp/localstack"
    networks:
      - localstack-network

volumes:
  localstack_data:

networks:
  localstack-network:
    driver: bridge
```

### AWS SDK Configuration
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
lambda_client = get_aws_client('lambda')
```

### LocalStack Initialization
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

## Environment Configuration

### Environment Variables
```bash
# .env.development
NODE_ENV=development
API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
AWS_ENDPOINT=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1
```

```bash
# .env.production
NODE_ENV=production
API_URL=https://api.myapp.com
DATABASE_URL=postgresql://user:pass@prod-db:5432/mydb
AWS_ENDPOINT=https://s3.amazonaws.com
AWS_ACCESS_KEY_ID=your-real-access-key
AWS_SECRET_ACCESS_KEY=your-real-secret-key
AWS_DEFAULT_REGION=us-east-1
```

## Deployment Scripts

### Build and Deploy Script
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "Building and deploying application..."

# Build frontend
echo "Building frontend..."
cd frontend
npm ci
npm run build
cd ..

# Build backend
echo "Building backend..."
cd backend
pip install -r requirements.txt
cd ..

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Initialize LocalStack resources
echo "Initializing LocalStack resources..."
python scripts/init_localstack.py

echo "Deployment complete!"
```

### Health Check Script
```bash
#!/bin/bash
# scripts/health-check.sh

echo "Checking service health..."

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
    exit 1
fi

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
    exit 1
fi

# Check database
if docker-compose exec db pg_isready -U user > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "❌ Database is not responding"
    exit 1
fi

# Check LocalStack
if curl -f http://localhost:4566/_localstack/health > /dev/null 2>&1; then
    echo "✅ LocalStack is healthy"
else
    echo "❌ LocalStack is not responding"
    exit 1
fi

echo "All services are healthy!"
```

## Best Practices

1. **Use multi-stage builds** to optimize image size
2. **Run services as non-root users** for security
3. **Use environment variables** for configuration
4. **Implement health checks** for all services
5. **Use named volumes** for persistent data
6. **Separate development and production** configurations
7. **Implement proper logging** and monitoring
8. **Use LocalStack** for local AWS service testing
9. **Automate deployment** with scripts
10. **Test in production-like environment** before deployment
