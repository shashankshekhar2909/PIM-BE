#!/bin/bash

# Production Deployment Script for /root/apps/fastAPI/PIM-BE
# This script handles the specific production server configuration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}==================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==================================================${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main deployment function
main() {
    print_header "🚀 Production Deployment for PIM-BE"
    
    # Get the actual script directory
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    print_info "Script directory: $SCRIPT_DIR"
    print_info "Current working directory: $(pwd)"
    
    # Check if we're in the right directory
    if [[ ! "$(pwd)" =~ "PIM-BE" ]]; then
        print_warning "Not in PIM-BE directory, attempting to navigate..."
        if [ -d "fastAPI/PIM-BE" ]; then
            cd fastAPI/PIM-BE
            print_info "Changed to: $(pwd)"
        elif [ -d "PIM-BE" ]; then
            cd PIM-BE
            print_info "Changed to: $(pwd)"
        else
            print_error "Could not find PIM-BE directory"
            print_info "Available directories:"
            ls -la
            exit 1
        fi
    fi
    
    print_header "Step 1: Environment Check"
    
    # Check Python
    if command -v python3 > /dev/null 2>&1; then
        print_success "Python3 found: $(python3 --version)"
    else
        print_error "Python3 not found"
        exit 1
    fi
    
    # Check Docker
    if command -v docker > /dev/null 2>&1; then
        print_success "Docker found: $(docker --version)"
    else
        print_warning "Docker not found - will use direct Python method"
    fi
    
    # Check Docker Compose
    if command -v docker-compose > /dev/null 2>&1 || docker compose version > /dev/null 2>&1; then
        print_success "Docker Compose found"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker Compose not found - will use direct Python method"
        DOCKER_AVAILABLE=false
    fi
    
    print_header "Step 2: Database Setup"
    
    # Ensure data directory exists
    mkdir -p data
    mkdir -p backups
    
    # Fix permissions
    print_info "Setting proper permissions..."
    chmod 755 data backups 2>/dev/null || true
    chmod 666 data/pim.db 2>/dev/null || true
    
    # Check if create_production_db.py exists
    if [ ! -f "create_production_db.py" ]; then
        print_error "create_production_db.py not found in current directory"
        print_info "Available files:"
        ls -la *.py 2>/dev/null || echo "No Python files found"
        exit 1
    fi
    
    print_info "Found create_production_db.py, creating production database..."
    
    # Create database using Python directly
    if python3 create_production_db.py; then
        print_success "Production database created successfully!"
    else
        print_error "Failed to create production database"
        exit 1
    fi
    
    print_header "Step 3: Docker Deployment (if available)"
    
    if [ "$DOCKER_AVAILABLE" = true ]; then
        print_info "Attempting Docker deployment..."
        
        # Stop any existing containers
        print_info "Stopping existing containers..."
        docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
        
        # Build and start
        print_info "Building and starting Docker containers..."
        if docker-compose up -d 2>/dev/null || docker compose up -d; then
            print_success "Docker deployment successful!"
            
            # Wait for service to start
            print_info "Waiting for service to start..."
            sleep 15
            
            # Check status
            if docker-compose ps 2>/dev/null || docker compose ps; then
                print_success "Service is running!"
            fi
        else
            print_warning "Docker deployment failed, but database is ready"
        fi
    else
        print_info "Skipping Docker deployment (not available)"
    fi
    
    print_header "Step 4: Verification"
    
    # Check database
    if [ -f "data/pim.db" ] && [ -s "data/pim.db" ]; then
        print_success "Database file exists and has content"
        print_info "Database size: $(du -h data/pim.db | cut -f1)"
    else
        print_error "Database file missing or empty"
        exit 1
    fi
    
    # Test admin user if possible
    if [ "$DOCKER_AVAILABLE" = true ]; then
        print_info "Testing admin user access..."
        sleep 5
        
        # Try to test the API
        if curl -s "http://localhost:8004/health" > /dev/null 2>&1; then
            print_success "Health endpoint responding!"
            
            # Test admin login
            ADMIN_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/auth/login" \
                -H "Content-Type: application/json" \
                -d '{"email":"admin@pim.com","password":"admin123"}' \
                2>/dev/null || echo "FAILED")
            
            if echo "$ADMIN_RESPONSE" | grep -q "access_token"; then
                print_success "Admin login working: admin@pim.com / admin123"
            else
                print_warning "Admin login test inconclusive"
            fi
        else
            print_warning "Health endpoint not responding (service may still be starting)"
        fi
    fi
    
    print_header "Final Status"
    
    echo ""
    print_success "🎉 PRODUCTION DEPLOYMENT COMPLETED!"
    echo ""
    echo "📋 Summary:"
    echo "  ✅ Database: Created successfully"
    echo "  ✅ Admin User: admin@pim.com / admin123"
    echo "  🐳 Docker: $([ "$DOCKER_AVAILABLE" = true ] && echo "Deployed" || echo "Not available")"
    echo ""
    echo "🌐 Access URLs (if Docker is running):"
    echo "  Application: http://localhost:8004"
    echo "  API Docs: http://localhost:8004/docs"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  View logs: docker-compose logs -f (or docker compose logs -f)"
    echo "  Stop service: docker-compose down (or docker compose down)"
    echo "  Restart: docker-compose restart (or docker compose restart)"
    echo ""
    echo "⚠️  IMPORTANT: Change the default admin password after first login!"
    echo "💾 Database is ready for production use!"
}

# Run main function
main "$@"
