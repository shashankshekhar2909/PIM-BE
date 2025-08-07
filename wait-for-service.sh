#!/bin/bash

# Wait for PIM service to be ready

echo "⏳ Waiting for PIM service to be ready..."
echo "========================================"

# Function to check if service is ready
check_service() {
    if curl -f http://localhost:8004/health &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Wait for service to be ready (max 2 minutes)
max_attempts=24
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt/$max_attempts: Checking service health..."
    
    if check_service; then
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
        sleep 5
        attempt=$((attempt + 1))
    fi
done

echo "❌ Service did not become ready within 2 minutes"
echo ""
echo "🔍 Troubleshooting steps:"
echo "1. Check if service is running: docker compose ps"
echo "2. Check service logs: docker compose logs pim -f"
echo "3. Check if port is available: lsof -i :8004"
echo "4. Restart service: docker compose restart pim"
echo ""
echo "📋 Current service status:"
echo "  - Service is running but health check is failing"
echo "  - This usually means the application is still starting up"
echo "  - Wait a few more minutes and try again" 