#!/bin/bash

# Comprehensive PIM Application Redeployment Script
# This script handles the complete redeployment of the PIM application

set -e  # Exit on any error

echo "🚀 PIM Application Redeployment Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Check if docker-compose.yml exists in parent directory
if [[ -f "../../docker-compose.yml" ]]; then
    print_status "docker-compose.yml found in ../../"
    COMPOSE_DIR="../../"
else
    print_error "docker-compose.yml not found in ../../"
    echo "Please ensure docker-compose.yml is in the parent directory"
    exit 1
fi

# Step 1: Check prerequisites
echo ""
print_info "Step 1: Checking prerequisites..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi
print_status "Docker is running"

# Check if docker compose is available
if ! docker compose version > /dev/null 2>&1; then
    print_error "docker compose command not found"
    echo "Please ensure Docker Compose is installed"
    exit 1
fi
print_status "Docker Compose is available"

# Step 2: Create/update .env file
echo ""
print_info "Step 2: Setting up environment variables..."

if [[ ! -f "$COMPOSE_DIR/.env" ]]; then
    print_warning ".env file not found, creating..."
    cat > "$COMPOSE_DIR/.env" << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://hhxuxthwvpeplhtprnhf.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhoeHV4dGh3dnBlcGxodHBybmhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NjE3MjQsImV4cCI6MjA3MDAzNzcyNH0.1f9e_bPsbLtV9BiSrSO2IvHEf0ePSC8j1Ki_S2I-j_Y
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Application Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./db/pim.db
EOF
    print_status "Created .env file"
    print_warning "Please update SUPABASE_SERVICE_ROLE_KEY and SECRET_KEY in $COMPOSE_DIR/.env"
else
    print_status ".env file exists"
fi

# Step 3: Setup database directory and permissions
echo ""
print_info "Step 3: Setting up database directory..."

# Create db directory if it doesn't exist
mkdir -p db
chmod 777 db

# Move existing database to db directory if it exists
if [[ -f "pim.db" ]]; then
    print_info "Moving existing database to db directory..."
    mv pim.db db/
fi

# Create database file in db directory if it doesn't exist
if [[ ! -f "db/pim.db" ]]; then
    print_info "Creating new database in db directory..."
    touch db/pim.db
fi

# Fix permissions on database file
chmod 777 db/pim.db
print_status "Database permissions set: $(ls -la db/pim.db | awk '{print $1}')"

# Step 4: Update docker-compose.yml with db mount
echo ""
print_info "Step 4: Updating docker-compose.yml..."

# Create backup of docker-compose.yml
cp "$COMPOSE_DIR/docker-compose.yml" "$COMPOSE_DIR/docker-compose.yml.backup"
print_status "Created backup: docker-compose.yml.backup"

# Update the PIM service configuration
cat > "$COMPOSE_DIR/docker-compose.yml" << 'EOF'
services:
  app1:
    build: ./fastAPI/app1
    container_name: app1
    volumes:
      - ./fastAPI/app1:/app  # Mount your code
    working_dir: /app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8001:8000"

  app2:
    build: ./fastAPI/app2
    container_name: app2
    volumes:
      - ./fastAPI/app2:/app
    working_dir: /app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8002:8000"

  giftg:
    build: ./fastAPI/giftg-BE
    container_name: giftg
    volumes:
      - ./fastAPI/giftg-BE:/app
    working_dir: /app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8003:8000"
    restart: unless-stopped

  pim:
    build: ./fastAPI/PIM-BE
    container_name: pim
    volumes:
      - ./fastAPI/PIM-BE:/app
      - ./fastAPI/PIM-BE/db:/app/db
    working_dir: /app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8004:8000"
    restart: unless-stopped
    environment:
      - PYTHONPATH=/app
      - SUPABASE_URL=${SUPABASE_URL:-}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY:-}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY:-}
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-here}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./db/pim.db}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOF

print_status "Updated docker-compose.yml with db mount"

# Step 5: Stop and remove existing containers
echo ""
print_info "Step 5: Stopping and removing existing containers..."

cd "$COMPOSE_DIR"
docker compose down -v
print_status "Stopped and removed all containers"

# Step 6: Build and start containers
echo ""
print_info "Step 6: Building and starting containers..."

docker compose up --build -d
if [ $? -ne 0 ]; then
    print_error "Failed to build and start containers"
    exit 1
fi
print_status "Containers built and started successfully"

# Step 7: Wait for service to be ready
echo ""
print_info "Step 7: Waiting for service to be ready..."
sleep 30

# Check service status
echo ""
print_info "Step 8: Checking service status..."
docker compose ps pim

# Wait for service to be ready
echo ""
print_info "Step 9: Checking service health..."
max_attempts=20
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt/$max_attempts: Checking service health..."
    
    if curl -f http://localhost:8004/health &> /dev/null; then
        print_status "PIM service is ready!"
        break
    else
        echo "⏳ Service not ready yet... (attempt $attempt/$max_attempts)"
        
        # Show recent logs every 5 attempts
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "📋 Recent logs:"
            docker compose logs pim --tail=5
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    print_error "Service did not become ready within 3.5 minutes"
    echo ""
    echo "📋 Recent logs:"
    docker compose logs pim --tail=20
    exit 1
fi

# Step 10: Display final status
echo ""
print_status "Step 10: Final status check..."

echo ""
echo "🏥 Health Check Response:"
curl -s http://localhost:8004/health | jq . 2>/dev/null || curl -s http://localhost:8004/health

echo ""
echo "🌐 Service URLs:"
echo "  PIM API:      http://localhost:8004"
echo "  API Docs:     http://localhost:8004/docs"
echo "  Health Check: http://localhost:8004/health"

echo ""
echo "📁 Database location: ./fastAPI/PIM-BE/db/pim.db"
echo "🔐 Database permissions: 777 (readable/writable by all)"

# Step 11: Test authentication (optional)
echo ""
print_info "Step 11: Testing authentication..."

SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:8004/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","company_name":"Test Company"}')

if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    print_status "Authentication test successful!"
elif echo "$SIGNUP_RESPONSE" | grep -q "readonly database"; then
    print_error "Database is still readonly - this should not happen with the new setup"
elif echo "$SIGNUP_RESPONSE" | grep -q "Email address.*invalid"; then
    print_warning "Email validation error - this is expected for some email formats"
    print_info "The database solution is working, but email validation is rejecting the test email"
else
    print_warning "Authentication test failed - this might be expected if email confirmation is required"
fi

echo ""
echo "🎯 Redeployment Summary:"
echo "  ✅ Environment variables: Configured"
echo "  ✅ Database directory: Created (db/)"
echo "  ✅ Database permissions: Fixed (777)"
echo "  ✅ Docker-compose.yml: Updated with db mount"
echo "  ✅ Containers: Built and started"
echo "  ✅ Service: Running and healthy"
echo "  ✅ Health endpoint: Working"

if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    echo "  ✅ Authentication: Working"
else
    echo "  ⚠️  Authentication: May need email confirmation"
fi

echo ""
print_status "🎉 PIM application redeployment completed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Update SUPABASE_SERVICE_ROLE_KEY in $COMPOSE_DIR/.env if needed"
echo "2. Test the API at http://localhost:8004/docs"
echo "3. Check service logs: docker compose logs pim -f"
echo ""
echo "🚀 Your PIM application is ready to use!" 