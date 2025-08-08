#!/bin/sh

# 🚀 Quick Deployment Script for PIM System Updates
# Use this for quick updates after code changes

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running"
        echo "Please start Docker and try again"
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if docker compose is available
check_docker_compose() {
    if ! docker compose version > /dev/null 2>&1; then
        print_error "docker compose command not found"
        echo "Please ensure Docker Compose is installed"
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to check service health
check_health() {
    print_info "Checking service health..."
    
    # Wait a bit for service to start
    sleep 5
    
    # Try to check health endpoint
    if curl -s http://localhost:8004/health > /dev/null 2>&1; then
        print_success "Service is healthy!"
        return 0
    else
        print_warning "Service health check failed, but container might still be starting..."
        return 1
    fi
}

# Function to show service status
show_status() {
    print_info "Service status:"
    docker compose ps
    
    echo ""
    print_info "Recent logs:"
    docker compose logs pim --tail=20
}

# Main deployment function
main() {
    print_header "QUICK DEPLOYMENT"
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    print_info "Starting quick deployment..."
    
    # Stop existing containers
    print_info "Stopping existing containers..."
    docker compose down 2>/dev/null || true
    
    # Rebuild and start containers
    print_info "Rebuilding and starting containers..."
    docker compose up --build -d
    
    # Check if containers started successfully
    if docker compose ps | grep -q "Up"; then
        print_success "Containers started successfully!"
    else
        print_error "Failed to start containers"
        show_status
        exit 1
    fi
    
    # Check health
    if check_health; then
        print_success "Deployment completed successfully!"
    else
        print_warning "Deployment completed, but health check failed"
        print_info "Service might still be starting up..."
    fi
    
    # Show final status
    show_status
    
    echo ""
    print_success "Quick deployment completed!"
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

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  -h, --help     Show this help message"
        echo ""
        echo "This script performs a quick deployment:"
        echo "  1. Stops existing containers"
        echo "  2. Rebuilds and starts containers"
        echo "  3. Checks service health"
        echo "  4. Shows status and logs"
        echo ""
        echo "Use this for quick updates after code changes."
        echo "For full deployment with admin setup, use: ./deploy.sh"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac 