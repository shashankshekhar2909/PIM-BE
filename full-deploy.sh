#!/bin/bash

# Full Deployment Script for PIM-BE
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
    print_header "🚀 Full Deployment for PIM-BE"
    
    print_header "Step 1: Environment Check"
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker not found - required for deployment"
        print_info "Install Docker first:"
        print_info "  Ubuntu/Debian: curl -fsSL https://get.docker.com | sh"
        print_info "  CentOS/RHEL: yum install -y docker"
        exit 1
    fi
    print_success "Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! (command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1); then
        print_error "Docker Compose not found - required for deployment"
        print_info "Install Docker Compose first:"
        print_info "  curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose"
        print_info "  chmod +x /usr/local/bin/docker-compose"
        exit 1
    fi
    print_success "Docker Compose found"
    
    print_header "Step 2: Directory Setup"
    
    # Create required directories
    print_info "Setting up directories..."
    mkdir -p data backups
    
    # Fix permissions - try with sudo if regular chmod fails
    print_info "Setting directory permissions..."
    if ! chmod 777 data backups 2>/dev/null; then
        print_info "Trying with sudo..."
        sudo chmod 777 data backups
    fi
    
    # Try to set file permissions if file exists
    if [ -f "data/pim.db" ]; then
        if ! chmod 666 data/pim.db 2>/dev/null; then
            print_info "Trying with sudo..."
            sudo chmod 666 data/pim.db
        fi
    fi
    print_success "Directory setup complete"
    
    print_header "Step 3: Docker Cleanup"
    
    # Stop and remove existing containers
    print_info "Cleaning up existing containers..."
    docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
    print_success "Cleanup complete"
    
    print_header "Step 4: Docker Build"
    
    # Build fresh Docker image
    print_info "Building Docker image..."
    if ! (docker-compose build --no-cache 2>/dev/null || docker compose build --no-cache); then
        print_error "Docker build failed"
        exit 1
    fi
    print_success "Docker image built successfully"
    
    print_header "Step 5: Database Setup"
    
    # Create database using Docker
    print_info "Creating database using Docker..."
    if ! (docker-compose run --rm pim python3 /app/create_production_db.py 2>/dev/null || \
          docker compose run --rm pim python3 /app/create_production_db.py); then
        print_error "Database creation failed"
        print_info "Checking container logs..."
        docker-compose logs 2>/dev/null || docker compose logs
        exit 1
    fi
    print_success "Database created successfully"
    
    # Fix permissions again after database creation
    if [ -f "data/pim.db" ]; then
        print_info "Setting database file permissions..."
        if ! chmod 666 data/pim.db 2>/dev/null; then
            print_info "Trying with sudo..."
            sudo chmod 666 data/pim.db
        fi
    fi
    
    print_header "Step 6: Start Services"
    
    # Start services
    print_info "Starting services..."
    if ! (docker-compose up -d 2>/dev/null || docker compose up -d); then
        print_error "Failed to start services"
        print_info "Checking logs..."
        docker-compose logs 2>/dev/null || docker compose logs
        exit 1
    fi
    print_success "Services started successfully"
    
    # Wait for service to be ready
    print_info "Waiting for service to start..."
    sleep 15
    
    # Health check
    print_info "Running health check..."
    RETRIES=0
    MAX_RETRIES=5
    while [ $RETRIES -lt $MAX_RETRIES ]; do
        if curl -s "http://localhost:8004/health" >/dev/null 2>&1; then
            print_success "Health check passed!"
            break
        fi
        RETRIES=$((RETRIES + 1))
        if [ $RETRIES -eq $MAX_RETRIES ]; then
            print_error "Health check failed after $MAX_RETRIES attempts"
            print_info "Container logs:"
            docker-compose logs --tail=50 2>/dev/null || docker compose logs --tail=50
            exit 1
        fi
        print_info "Retrying health check in 5 seconds... (Attempt $RETRIES/$MAX_RETRIES)"
        sleep 5
    done
    
    print_header "Step 7: Verify Admin Access"
    
    # Test admin login
    print_info "Testing admin user access..."
    ADMIN_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@pim.com","password":"admin123"}' \
        2>/dev/null || echo "FAILED")
    
    if echo "$ADMIN_RESPONSE" | grep -q "access_token"; then
        print_success "Admin login working: admin@pim.com / admin123"
    else
        print_warning "Admin login not working yet - this may be normal on first deploy"
        print_info "Try manual login after a few minutes"
    fi
    
    print_header "✨ Deployment Complete!"
    echo ""
    echo "🔧 Service Information:"
    echo "  - API URL: http://localhost:8004"
    echo "  - Admin Login: admin@pim.com / admin123"
    echo ""
    echo "📝 Useful Commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Restart service: docker-compose restart"
    echo "  - Stop service: docker-compose down"
    echo ""
    echo "⚠️  IMPORTANT: Change the default admin password after first login!"
}

# Run main function
main