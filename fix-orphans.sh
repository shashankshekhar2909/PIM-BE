#!/bin/bash

# Fix orphan containers script

echo "🧹 Fixing Orphan Containers"
echo "==========================="

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

# Stop all services and remove orphan containers
echo ""
echo "🛑 Stopping all services and removing orphan containers..."
cd ../.. && docker compose down --remove-orphans

if [ $? -eq 0 ]; then
    echo "✅ Successfully removed orphan containers"
else
    echo "❌ Failed to remove orphan containers"
    exit 1
fi

# Start PIM service
echo ""
echo "🚀 Starting PIM service..."
docker compose up -d pim

if [ $? -eq 0 ]; then
    echo "✅ PIM service started successfully"
else
    echo "❌ Failed to start PIM service"
    exit 1
fi

# Wait for service to start
echo ""
echo "⏳ Waiting for service to start..."
sleep 15

# Check health
echo ""
echo "🏥 Checking service health..."
if curl -f http://localhost:8004/health &> /dev/null; then
    echo "✅ PIM service is healthy"
    curl -s http://localhost:8004/health | jq . 2>/dev/null || curl -s http://localhost:8004/health
else
    echo "❌ PIM service health check failed"
    echo "Checking logs..."
    docker compose logs pim --tail=10
fi

echo ""
echo "🎉 Orphan containers fixed and PIM service restarted!"
echo "🌐 Service URL: http://localhost:8004"
echo "📊 Status: docker compose ps" 