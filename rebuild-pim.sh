#!/bin/bash

# Rebuild PIM service with updated requirements

echo "🔨 Rebuilding PIM Service with Updated Requirements"
echo "=================================================="

# Check if docker-compose.yml exists in parent directory
if [[ -f "../../docker-compose.yml" ]]; then
    echo "✅ docker-compose.yml found in ../../"
else
    echo "❌ docker-compose.yml not found in ../../"
    echo "Please ensure docker-compose.yml is in the parent directory"
    exit 1
fi

# Check if docker command is available
if command -v docker &> /dev/null; then
    echo "✅ Docker command available"
else
    echo "❌ Docker command not found"
    echo "Please ensure Docker is installed and in your PATH"
    exit 1
fi

# Stop PIM service
echo ""
echo "🛑 Stopping PIM service..."
cd ../.. && docker compose stop pim

# Remove PIM container to force rebuild
echo ""
echo "🗑️  Removing PIM container..."
docker compose rm -f pim

# Build PIM service with updated requirements
echo ""
echo "🔨 Building PIM service with updated requirements..."
docker compose build --no-cache pim

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Build completed successfully"

# Start PIM service
echo ""
echo "🚀 Starting PIM service..."
docker compose up -d pim

if [ $? -ne 0 ]; then
    echo "❌ Failed to start PIM service"
    exit 1
fi

echo "✅ PIM service started successfully"

# Wait for service to start
echo ""
echo "⏳ Waiting for service to start..."
sleep 15

# Check service status
echo ""
echo "📊 Service Status:"
docker compose ps pim

# Wait for service to be ready
echo ""
echo "⏳ Waiting for service to be ready (max 3 minutes)..."
max_attempts=36
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt/$max_attempts: Checking service health..."
    
    if curl -f http://localhost:8004/health &> /dev/null; then
        echo "✅ PIM service is ready!"
        echo ""
        echo "🏥 Health Check Response:"
        curl -s http://localhost:8004/health | jq . 2>/dev/null || curl -s http://localhost:8004/health
        echo ""
        echo "🌐 Service URLs:"
        echo "  PIM API:      http://localhost:8004"
        echo "  API Docs:     http://localhost:8004/docs"
        echo "  Health Check: http://localhost:8004/health"
        echo ""
        echo "🧪 Test the new multi-value search:"
        echo "  curl \"http://localhost:8004/api/v1/products?manufacturer=Adidas,Apple,Bosch,Hasbro,Home Depot\""
        exit 0
    else
        echo "⏳ Service not ready yet... (attempt $attempt/$max_attempts)"
        
        # Show recent logs every 5 attempts
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "📋 Recent logs:"
            docker compose logs pim --tail=5
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    fi
done

echo "❌ Service did not become ready within 3 minutes"
echo ""
echo "🔍 Troubleshooting steps:"
echo "1. Check service logs: docker compose logs pim -f"
echo "2. Check if all dependencies are installed"
echo "3. Check if there are any other errors in the logs"
echo ""
echo "📋 Recent logs:"
docker compose logs pim --tail=20 