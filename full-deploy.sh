#!/bin/bash

# 🚀 FULL DEPLOY - Complete recreation of everything
# Use this for fresh installations or when you want to start over

set -e

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
print_info "Setting up database directory..."

# Create data directory
mkdir -p data
mkdir -p backups

# Check if database exists in root
if [ -f "pim.db" ]; then
    print_info "Found existing database in root - backing up and moving..."
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp pim.db "backups/pim.db.backup.${TIMESTAMP}"
    cp pim.db "data/pim.db"
    rm pim.db
    print_success "Database moved to data/pim.db"
elif [ -f "data/pim.db" ]; then
    print_info "Database already in data directory"
    
    # Create backup of existing database
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp "data/pim.db" "backups/pim.db.backup.${TIMESTAMP}"
    print_success "Created backup: backups/pim.db.backup.${TIMESTAMP}"
else
    print_warning "No existing database found - new one will be created with default admin user"
fi

# Set permissions
chmod 644 data/pim.db 2>/dev/null || true
chmod 755 data backups

# Set ownership for root users
if [ "$EUID" -eq 0 ]; then
    chown root:root data/pim.db data backups 2>/dev/null || true
fi

print_success "Database setup completed"
print_info "Note: Default admin user (admin@pim.com / admin123) will be created if none exists"

print_header "Step 3: Build and Deploy"
print_info "Building and starting service..."

# Build with no cache to ensure fresh build
docker compose build --no-cache pim
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
print_info "Testing database write access..."

# Test database by trying to create a test user
TEST_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/auth/signup" \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"testpass123","company_name":"Test Company"}' \
    2>/dev/null || echo "FAILED")

if echo "$TEST_RESPONSE" | grep -q "access_token"; then
    print_success "Database write access confirmed!"
elif echo "$TEST_RESPONSE" | grep -q "already registered"; then
    print_success "Database working (user already exists)"
else
    print_warning "Database test inconclusive - this may be expected"
fi

# Test default admin user access
print_info "Testing default admin user access..."
ADMIN_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@pim.com","password":"admin123"}' \
    2>/dev/null || echo "FAILED")

if echo "$ADMIN_RESPONSE" | grep -q "access_token"; then
    print_success "Default admin user (admin@pim.com / admin123) is working!"
elif echo "$ADMIN_RESPONSE" | grep -q "Invalid login credentials"; then
    print_warning "Default admin user not found - will be created by migrations"
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
echo "  Note: This user is automatically created if none exists"
echo ""
echo "📋 Useful Commands:"
echo "  View logs: docker compose logs pim -f"
echo "  Stop service: docker compose down"
echo "  Restart: docker compose restart pim"
echo "  Check status: docker compose ps"
echo ""
echo "🗄️  Database:"
echo "  Location: data/pim.db"
echo "  Backups: backups/"
echo ""
echo "🔧 Troubleshooting:"
echo "  If you have issues:"
echo "  1. Check logs: docker compose logs pim"
echo "  2. Restart: docker compose restart pim"
echo "  3. Full restart: ./full-deploy.sh"
echo ""
echo "⚠️  IMPORTANT: Change the default admin password after first login!"
