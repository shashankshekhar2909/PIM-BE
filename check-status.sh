#!/bin/bash

# Simple status check script for PIM service

echo "🔍 PIM Service Status Check"
echo "=========================="

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

# Check if docker compose command is available
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose command available"
else
    echo "❌ Docker Compose command not found"
    exit 1
fi

# Check service status
echo ""
echo "📊 Service Status:"
cd ../.. && docker compose ps

# Check PIM service logs
echo ""
echo "📋 PIM Service Logs (last 20 lines):"
docker compose logs pim --tail=20

# Check if service is responding
echo ""
echo "🏥 Health Check:"
if curl -f http://localhost:8004/health &> /dev/null; then
    echo "✅ PIM service is healthy"
    curl -s http://localhost:8004/health | jq . 2>/dev/null || curl -s http://localhost:8004/health
else
    echo "❌ PIM service health check failed"
    echo "Service might still be starting up..."
fi

# Check for orphan containers
echo ""
echo "🧹 Orphan Containers Check:"
if docker ps -a --filter "label=com.docker.compose.project" | grep -q "nginx"; then
    echo "⚠️  Found orphan containers (nginx)"
    echo "To clean up, run: docker compose down --remove-orphans"
else
    echo "✅ No orphan containers found"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. If service is not running: docker compose up -d pim"
echo "2. If orphan containers: docker compose down --remove-orphans"
echo "3. If health check fails: wait a few minutes and try again"
echo "4. Check logs: docker compose logs pim -f" 