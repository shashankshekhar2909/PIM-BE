#!/bin/bash

# Comprehensive troubleshooting script for PIM service

echo "🔍 PIM Service Troubleshooting"
echo "=============================="

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

# Check service status
echo ""
echo "📊 Current Service Status:"
cd ../.. && docker compose ps

# Check if PIM service is running
if docker compose ps | grep -q "pim.*Up"; then
    echo "✅ PIM service is running"
else
    echo "❌ PIM service is not running"
    echo "Starting PIM service..."
    docker compose up -d pim
    sleep 10
fi

# Check service logs
echo ""
echo "📋 PIM Service Logs (last 30 lines):"
docker compose logs pim --tail=30

# Check if there are any errors in the logs
if docker compose logs pim --tail=30 | grep -i "error\|exception\|traceback"; then
    echo ""
    echo "⚠️  Found errors in logs. Common issues:"
    echo "1. Database initialization issues"
    echo "2. Missing environment variables"
    echo "3. Port conflicts"
    echo "4. File permission issues"
fi

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
echo ""
echo "1. Check if port 8004 is available:"
echo "   lsof -i :8004"
echo ""
echo "2. Check service logs in real-time:"
echo "   docker compose logs pim -f"
echo ""
echo "3. Restart the service:"
echo "   docker compose restart pim"
echo ""
echo "4. Check environment variables:"
echo "   docker compose exec pim env | grep SUPABASE"
echo ""
echo "5. Check if database file exists:"
echo "   docker compose exec pim ls -la pim.db"
echo ""
echo "6. Check file permissions:"
echo "   docker compose exec pim ls -la /app"
echo ""
echo "📋 Common Issues and Solutions:"
echo "  - Database initialization taking time: Wait a few more minutes"
echo "  - Missing environment variables: Check .env file in ../../"
echo "  - Port conflicts: Check if port 8004 is in use"
echo "  - File permissions: Ensure mounted volumes have correct permissions"
echo "  - Memory issues: Check if container has enough resources" 