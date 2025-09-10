#!/bin/bash

# KF Project Setup Script
set -e

echo "🚀 Setting up KF Angular-Python-AWS project..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p frontend/src/app/{features,shared,core}
mkdir -p frontend/cypress/{e2e,fixtures,support}
mkdir -p backend/{app,core,api,models,schemas,services}
mkdir -p scripts

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# Install backend dependencies
echo "🐍 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run health checks
echo "🏥 Running health checks..."
./scripts/health-check.sh

echo "✅ Setup complete!"
echo ""
echo "🌐 Services available at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  LocalStack: http://localhost:4566"
echo ""
echo "📚 Documentation available in .docs/"
echo "🎯 Context engineering rules in .cursor/"
