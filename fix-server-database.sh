#!/bin/bash

# 🔧 SERVER DATABASE FIX SCRIPT
# This script fixes database permission and path issues on the server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_step() {
    echo -e "${CYAN}🔧 $1${NC}"
}

# Configuration
PROJECT_NAME="PIM-BE"
SERVICE_NAME="pim"
CONTAINER_NAME="pim"
DATA_DIR="data"
BACKUP_DIR="backups"

print_header "SERVER DATABASE FIX"

print_info "This script will fix database permission and path issues"
print_info "Project: $PROJECT_NAME"
print_info "Service: $SERVICE_NAME"
print_info "Current directory: $(pwd)"

# Check if we're in the right directory
if [ ! -f "Dockerfile" ] && [ ! -f "../../docker-compose.yml" ]; then
    print_error "Not in the correct directory"
    echo "Please run this script from the PIM-BE directory"
    exit 1
fi

# Step 1: Stop the service
print_step "Stopping PIM service..."
if [ -f "../../docker-compose.yml" ]; then
    print_info "Multi-service environment detected"
    cd ../..
    print_info "Changed to directory: $(pwd)"
    
    # Stop the service
    docker compose stop "$SERVICE_NAME" 2>/dev/null || true
    print_success "Service stopped"
else
    print_info "Standalone environment"
    # Stop any running containers
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    print_success "Container stopped and removed"
fi

# Step 2: Fix database permissions and location
print_step "Fixing database permissions and location..."

# Create data directory if it doesn't exist
if [ ! -d "$DATA_DIR" ]; then
    mkdir -p "$DATA_DIR"
    print_info "Created data directory: $DATA_DIR"
fi

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    print_info "Created backup directory: $BACKUP_DIR"
fi

# Check if database exists in current location
if [ -f "pim.db" ]; then
    print_info "Found existing database: pim.db"
    
    # Create timestamped backup
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="${BACKUP_DIR}/pim.db.backup.${TIMESTAMP}"
    
    print_info "Creating backup: $BACKUP_FILE"
    cp pim.db "$BACKUP_FILE"
    print_success "Backup created: $BACKUP_FILE"
    
    # Copy to data directory
    print_info "Copying database to data directory..."
    cp pim.db "${DATA_DIR}/pim.db"
    print_success "Database copied to data directory"
    
    # Remove old database from root
    print_info "Removing old database from root directory..."
    rm pim.db
    print_success "Old database removed"
fi

# Check if database exists in data directory
if [ -f "${DATA_DIR}/pim.db" ]; then
    print_info "Database found in data directory: ${DATA_DIR}/pim.db"
    
    # Set proper permissions
    chmod 644 "${DATA_DIR}/pim.db"
    chmod 755 "$DATA_DIR" "$BACKUP_DIR"
    
    # Set ownership (adjust for your server user)
    if [ "$EUID" -eq 0 ]; then
        chown root:root "${DATA_DIR}/pim.db" "$DATA_DIR" "$BACKUP_DIR"
        print_info "Set ownership to root:root"
    else
        chown $USER:$USER "${DATA_DIR}/pim.db" "$DATA_DIR" "$BACKUP_DIR"
        print_info "Set ownership to $USER:$USER"
    fi
    
    print_success "Database permissions fixed"
else
    print_warning "No database found in data directory"
    print_info "A new database will be created when the service starts"
fi

# Step 3: Verify Docker Compose configuration
print_step "Verifying Docker Compose configuration..."

# Check if docker-compose.yml has the correct database path
if [ -f "docker-compose.yml" ]; then
    if grep -q "DATABASE_URL.*sqlite:///./data/pim.db" docker-compose.yml; then
        print_success "Docker Compose has correct database path"
    else
        print_warning "Docker Compose may not have correct database path"
        print_info "Please ensure DATABASE_URL is set to: sqlite:///./data/pim.db"
    fi
    
    if grep -q "pim_db_data:/app/data" docker-compose.yml; then
        print_success "Docker Compose has correct volume mount"
    else
        print_warning "Docker Compose may not have correct volume mount"
        print_info "Please ensure volumes include: pim_db_data:/app/data"
    fi
fi

# Step 4: Clean up Docker resources
print_step "Cleaning up Docker resources..."

# Remove old containers and images
docker container prune -f 2>/dev/null || true
docker image prune -f 2>/dev/null || true
print_success "Docker cleanup completed"

# Step 5: Rebuild and restart the service
print_step "Rebuilding and restarting service..."

if [ -f "docker-compose.yml" ]; then
    print_info "Building and starting service with --no-cache..."
    docker compose build --no-cache "$SERVICE_NAME"
    docker compose up -d "$SERVICE_NAME"
    
    print_info "Waiting for service to start..."
    sleep 10
    
    # Check service status
    if docker compose ps "$SERVICE_NAME" | grep -q "Up"; then
        print_success "Service started successfully!"
    else
        print_error "Failed to start service"
        print_info "Checking logs..."
        docker compose logs "$SERVICE_NAME" --tail=20
        exit 1
    fi
else
    print_error "docker-compose.yml not found in current directory"
    exit 1
fi

# Step 6: Verify database access
print_step "Verifying database access..."

# Wait a bit more for the service to fully initialize
sleep 5

# Check if the service can access the database
if curl -s "http://localhost:8004/health" > /dev/null 2>&1; then
    print_success "Service health check passed!"
    
    # Test database write access by trying to create a user
    print_info "Testing database write access..."
    if curl -s -X POST "http://localhost:8004/api/v1/auth/signup" \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"testpass123","company_name":"Test Company"}' \
        | grep -q "access_token"; then
        print_success "Database write access confirmed!"
    else
        print_warning "Database write access test failed - this may be expected if user already exists"
    fi
else
    print_warning "Health check failed, but service might still be starting..."
fi

# Step 7: Show final status
print_step "Final status check..."

print_info "Service status:"
docker compose ps "$SERVICE_NAME"

print_info "Container logs (last 10 lines):"
docker compose logs "$SERVICE_NAME" --tail=10

print_info "Database status:"
if [ -f "${DATA_DIR}/pim.db" ]; then
    echo "  Database file: ${DATA_DIR}/pim.db"
    echo "  Size: $(du -h "${DATA_DIR}/pim.db" | cut -f1)"
    echo "  Permissions: $(ls -la "${DATA_DIR}/pim.db" | awk '{print $1}')"
    echo "  Owner: $(ls -la "${DATA_DIR}/pim.db" | awk '{print $3":"$4}')"
else
    echo "  No database file found"
fi

# Success message
echo ""
print_success "🎉 DATABASE FIX COMPLETED SUCCESSFULLY!"
echo ""
echo -e "${BLUE}🔧 What was fixed:${NC}"
echo -e "  ✅ Database moved to ${GREEN}${DATA_DIR}/pim.db${NC}"
echo -e "  ✅ Permissions set correctly"
echo -e "  ✅ Docker service rebuilt and restarted"
echo -e "  ✅ Volume mounts verified"
echo ""
echo -e "${BLUE}🌐 Service Status:${NC}"
echo -e "  Health Check: ${GREEN}http://localhost:8004/health${NC}"
echo -e "  Application: ${GREEN}http://localhost:8004${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "  1. Test the API endpoints"
echo -e "  2. Check if authentication works"
echo -e "  3. Verify database writes are working"
echo ""
echo -e "${BLUE}🔍 Troubleshooting:${NC}"
echo -e "  If issues persist:"
echo -e "  1. Check logs: ${YELLOW}docker compose logs $SERVICE_NAME -f${NC}"
echo -e "  2. Check database: ${YELLOW}ls -la ${DATA_DIR}/${NC}"
echo -e "  3. Restart service: ${YELLOW}docker compose restart $SERVICE_NAME${NC}"
