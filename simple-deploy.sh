#!/bin/sh

# 🚀 Simple Deployment Script for PIM System Updates
# This is a simpler version that should work in multi-service environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Main deployment function
main() {
    print_header "SIMPLE DEPLOYMENT"
    
    print_info "Current directory: $(pwd)"
    
    # Check if we're in the right directory
    if [ ! -f "Dockerfile" ] && [ ! -f "../../docker-compose.yml" ]; then
        print_error "Not in the correct directory"
        echo "Please run this script from the PIM-BE directory"
        exit 1
    fi
    
    # Navigate to the correct directory for docker-compose
    if [ -f "../../docker-compose.yml" ]; then
        print_info "Multi-service environment detected"
        cd ../..
        print_info "Changed to directory: $(pwd)"
    fi
    
    # Stop existing containers
    print_info "Stopping existing containers..."
    docker compose down 2>/dev/null || true
    
    # Rebuild and start only the pim service
    print_info "Rebuilding and starting PIM service..."
    docker compose up --build -d pim
    
    # Wait a moment for the service to start
    sleep 3
    
    # Check if the service is running
    if docker compose ps pim | grep -q "Up"; then
        print_success "PIM service started successfully!"
    else
        print_error "Failed to start PIM service"
        print_info "Checking logs..."
        docker compose logs pim --tail=20
        exit 1
    fi
    
    # Check health
    print_info "Checking service health..."
    sleep 5
    
    if curl -s http://localhost:8004/health > /dev/null 2>&1; then
        print_success "Service is healthy!"
    else
        print_warning "Health check failed, but service might still be starting..."
    fi
    
    # Show final status
    print_info "Service status:"
    docker compose ps pim
    
    echo ""
    print_success "Simple deployment completed!"
    echo -e "${BLUE}🌐 Access URLs:${NC}"
    echo -e "  Application: ${GREEN}http://localhost:8004${NC}"
    echo -e "  Health Check: ${GREEN}http://localhost:8004/health${NC}"
    echo -e "  API Docs: ${GREEN}http://localhost:8004/docs${NC}"
    echo ""
    echo -e "${BLUE}📋 Useful Commands:${NC}"
    echo -e "  View logs: ${YELLOW}docker compose logs pim -f${NC}"
    echo -e "  Stop service: ${YELLOW}docker compose down${NC}"
    echo -e "  Full deploy: ${YELLOW}./deploy.sh${NC}"
}

# Run main function
main "$@" 