#!/bin/bash

# Health Check Script
set -e

echo "🏥 Checking service health..."

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
if docker-compose exec -T db pg_isready -U user > /dev/null 2>&1; then
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

echo "🎉 All services are healthy!"
