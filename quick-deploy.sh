#!/bin/bash

# 🚀 QUICK DEPLOY - Fast deployment for existing setups
# Use this for quick updates and fixes

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

echo "=========================================="
echo "  🚀 QUICK DEPLOY - PIM System"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "Dockerfile" ] && [ ! -f "../../docker-compose.yml" ]; then
    print_error "Not in PIM-BE directory"
    exit 1
fi

print_info "Starting quick deployment..."

# Navigate to parent directory if multi-service
if [ -f "../../docker-compose.yml" ]; then
    print_info "Multi-service environment detected"
    cd ../..
fi

# Stop existing service
print_info "Stopping existing service..."
docker compose stop pim 2>/dev/null || true

# Start service
print_info "Starting PIM service..."
docker compose up -d pim

# Wait for service
print_info "Waiting for service to start..."
sleep 10

# Check status
if docker compose ps pim | grep -q "Up"; then
    print_success "Service started successfully!"
    
    # Test health
    if curl -s "http://localhost:8004/health" > /dev/null; then
        print_success "Health check passed!"
    else
        print_warning "Health check failed - service may still be starting"
    fi
else
    print_error "Service failed to start"
    docker compose logs pim --tail=10
    exit 1
fi

echo ""
print_success "🎉 Quick deployment completed!"
echo ""
echo "🌐 Access URLs:"
echo "  Application: http://localhost:8004"
echo "  Health: http://localhost:8004/health"
echo "  API Docs: http://localhost:8004/docs"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker compose logs pim -f"
echo "  Stop: docker compose stop pim"
echo "  Restart: docker compose restart pim"
