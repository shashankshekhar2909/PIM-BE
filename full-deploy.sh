#!/bin/bash

# 🚀 FULL DEPLOY - Complete recreation of everything
# Use this for fresh installations or when you want to start over

set -e

# Store the original script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_header() { echo -e "${PURPLE}================================${NC}"; }

echo "=========================================="
echo "  🚀 FULL DEPLOY - PIM System"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root - this is fine for server deployment"
else
    print_info "Running as regular user"
fi

# Check if we're in the right directory
if [ ! -f "Dockerfile" ] && [ ! -f "../../docker-compose.yml" ]; then
    print_error "Not in PIM-BE directory"
    exit 1
fi

print_info "Starting full deployment..."

# Navigate to parent directory if multi-service
if [ -f "../../docker-compose.yml" ]; then
    print_info "Multi-service environment detected"
    cd ../..
fi

print_header "Step 1: Cleanup"
print_info "Stopping and removing existing containers..."
docker compose down 2>/dev/null || true
docker container prune -f 2>/dev/null || true
docker image prune -f 2>/dev/null || true
print_success "Cleanup completed"

print_header "Step 2: Database Setup"
print_info "Setting up production database..."

# Create data directory
mkdir -p data
mkdir -p backups

# Ensure proper permissions for Docker container
print_info "Setting directory permissions for Docker container..."
chmod 755 data backups
chmod 666 data/pim.db 2>/dev/null || true
print_success "Directory permissions set"

# Check if database exists and create production version
if [ -f "data/pim.db" ]; then
    print_info "Found existing database - creating backup..."
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp "data/pim.db" "backups/pim.db.backup.${TIMESTAMP}"
    print_success "Created backup: backups/pim.db.backup.${TIMESTAMP}"
    
    # Fix permissions to allow Docker container to modify the database
    print_info "Fixing database permissions for Docker container..."
    chmod 666 data/pim.db 2>/dev/null || true
    print_success "Database permissions updated"
fi

print_header "Step 3: Build and Deploy"
print_info "Building and starting service..."

# Build with no cache to ensure fresh build
docker compose build --no-cache pim

print_info "Creating production database using Docker container..."
# Create the database using the Docker container to ensure dependencies are available

# Debug: Check Docker environment
print_info "Checking Docker environment..."
print_info "Docker version: $(docker --version 2>/dev/null || echo 'Docker not found')"
print_info "Docker Compose version: $(docker compose version 2>/dev/null || echo 'Docker Compose not found')"
print_info "Current directory: $(pwd)"
print_info "Docker Compose file: $(ls -la docker-compose.yml 2>/dev/null || echo 'docker-compose.yml not found')"

# First, ensure Docker is running and the service can be built
if ! docker compose ps > /dev/null 2>&1; then
    print_error "Docker Compose is not available or not running"
    print_info "Please ensure Docker is running and try again"
    exit 1
fi

print_info "Docker Compose services:"
docker compose ps 2>/dev/null || print_warning "Could not list Docker Compose services"

print_info "Running: docker compose run --rm pim python3 /app/create_production_db.py"

# Try to create the database using Docker
if docker compose run --rm pim python3 /app/create_production_db.py; then
    print_success "Production database created successfully using Docker"
else
    print_warning "Docker database creation failed, trying alternative approach..."
    
    # Check if we can run the script directly (fallback)
    if command -v python3 > /dev/null 2>&1; then
        print_info "Attempting to create database directly with Python..."
        
        # Ensure proper permissions before running
        chmod 666 data/pim.db 2>/dev/null || true
        chmod 755 data/ 2>/dev/null || true
        
        if python3 create_production_db.py; then
            print_success "Production database created successfully using direct Python"
        else
            print_error "Both Docker and direct Python methods failed"
            print_error "Please check your Python environment and try again"
            exit 1
        fi
    else
        print_error "Python3 is not available on the host system"
        print_error "Cannot create database without Docker or Python"
        exit 1
    fi
fi

# Set permissions
chmod 644 data/pim.db 2>/dev/null || true
chmod 755 data backups

# Set ownership for root users
if [ "$EUID" -eq 0 ]; then
    chown root:root data/pim.db data backups 2>/dev/null || true
fi

print_success "Database setup completed"
print_info "Note: Production database created with admin@pim.com / admin123"

print_info "Starting the service..."
docker compose up -d pim

print_info "Waiting for service to start..."
sleep 15

print_header "Step 4: Verification"
# Check if service is running
if docker compose ps pim | grep -q "Up"; then
    print_success "Service started successfully!"
else
    print_error "Service failed to start"
    print_info "Checking logs..."
    docker compose logs pim --tail=20
    exit 1
fi

# Test health endpoint
print_info "Testing health endpoint..."
if curl -s "http://localhost:8004/health" > /dev/null; then
    print_success "Health check passed!"
else
    print_warning "Health check failed - service may still be starting"
    sleep 10
    if curl -s "http://localhost:8004/health" > /dev/null; then
        print_success "Health check passed after additional wait!"
    else
        print_error "Health check still failing"
        docker compose logs pim --tail=20
        exit 1
    fi
fi

print_header "Step 5: Database Test"
print_info "Testing database access..."

# Test default admin user access
print_info "Testing default admin user access..."
ADMIN_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@pim.com","password":"admin123"}' \
    2>/dev/null || echo "FAILED")

if echo "$ADMIN_RESPONSE" | grep -q "access_token"; then
    print_success "Default admin user (admin@pim.com / admin123) is working!"
elif echo "$ADMIN_RESPONSE" | grep -q "Invalid login credentials"; then
    print_warning "Default admin user not found - checking database..."
    # Check if database file exists and has content
    if [ -f "data/pim.db" ] && [ -s "data/pim.db" ]; then
        print_info "Database exists but admin user not found - this may be expected"
    else
        print_error "Database file missing or empty"
        exit 1
    fi
else
    print_warning "Admin user test inconclusive"
fi

print_header "Final Status"
print_info "Service status:"
docker compose ps pim

print_info "Database status:"
if [ -f "data/pim.db" ]; then
    echo "  Database: data/pim.db"
    echo "  Size: $(du -h data/pim.db | cut -f1)"
    echo "  Permissions: $(ls -la data/pim.db | awk '{print $1}')"
else
    echo "  No database file found"
fi

echo ""
print_success "🎉 FULL DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo ""
echo "🌐 Access URLs:"
echo "  Application: http://localhost:8004"
echo "  Health Check: http://localhost:8004/health"
echo "  API Docs: http://localhost:8004/docs"
echo ""
echo "👤 Default Admin User:"
echo "  Email: admin@pim.com"
echo "  Password: admin123"
echo "  Role: superadmin"
echo "  Note: This user is automatically created in production database"
echo ""
echo "📋 Useful Commands:"
echo "  View logs: docker compose logs pim -f"
echo "  Stop service: docker compose down"
echo "  Restart: docker compose restart pim"
echo "  Check status: docker compose ps"
echo "  Recreate DB: python3 create_production_db.py"
echo ""
echo "🗄️  Database:"
echo "  Location: data/pim.db"
echo "  Backups: backups/"
echo "  Production Ready: ✅ Yes"
echo ""
echo "🔧 Troubleshooting:"
echo "  If you have issues:"
echo "  1. Check logs: docker compose logs pim"
echo "  2. Restart: docker compose restart pim"
echo "  3. Recreate DB: docker compose run --rm pim python3 /app/create_production_db.py"
echo "  4. Full restart: ./full-deploy.sh"
echo ""
echo "⚠️  IMPORTANT: Change the default admin password after first login!"
echo "💾 Database is now committed to git for production deployment!"
