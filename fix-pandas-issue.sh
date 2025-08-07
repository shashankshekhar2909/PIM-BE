#!/bin/bash

# Fix pandas issue by completely rebuilding PIM service

echo "🔧 Fixing Pandas Issue - Complete Rebuild"
echo "========================================="

# Check if docker-compose.yml exists in parent directory
if [[ -f "../../docker-compose.yml" ]]; then
    echo "✅ docker-compose.yml found in ../../"
else
    echo "❌ docker-compose.yml not found in ../../"
    echo "Please ensure docker-compose.yml is in the parent directory"
    exit 1
fi

echo ""
echo "🛑 Step 1: Stopping and removing PIM service..."
cd ../.. && docker compose down pim

echo ""
echo "🗑️  Step 2: Removing PIM container and image..."
docker compose rm -f pim
docker rmi apps-pim 2>/dev/null || echo "Image not found, continuing..."

echo ""
echo "🔨 Step 3: Building PIM service with updated requirements..."
docker compose build --no-cache pim

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    echo "Please check the build logs above"
    exit 1
fi

echo "✅ Build completed successfully"

echo ""
echo "🚀 Step 4: Starting PIM service..."
docker compose up -d pim

if [ $? -ne 0 ]; then
    echo "❌ Failed to start PIM service"
    exit 1
fi

echo "✅ PIM service started successfully"

echo ""
echo "⏳ Step 5: Waiting for service to start..."
sleep 20

echo ""
echo "📊 Step 6: Checking service status..."
docker compose ps pim

echo ""
echo "🏥 Step 7: Checking service health..."
max_attempts=12
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
        echo ""
        echo "🎉 Pandas issue fixed successfully!"
        exit 0
    else
        echo "⏳ Service not ready yet... (attempt $attempt/$max_attempts)"
        
        # Show recent logs every 3 attempts
        if [ $((attempt % 3)) -eq 0 ]; then
            echo "📋 Recent logs:"
            docker compose logs pim --tail=5
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    fi
done

echo "❌ Service did not become ready within 2 minutes"
echo ""
echo "🔍 Troubleshooting steps:"
echo "1. Check service logs: docker compose logs pim -f"
echo "2. Check if pandas is installed: docker compose exec pim pip list | grep pandas"
echo "3. Check if there are any other errors in the logs"
echo ""
echo "📋 Recent logs:"
docker compose logs pim --tail=20 