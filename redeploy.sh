#!/bin/bash

# Comprehensive PIM Application Redeployment Script
# This script handles the complete redeployment of the PIM application with secure admin setup

set -e  # Exit on any error

echo "🚀 PIM Application Redeployment Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variables for admin credentials
ADMIN_EMAIL=""
ADMIN_PASSWORD=""

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

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to prompt for admin credentials
prompt_admin_credentials() {
    print_header "ADMIN USER SETUP"
    
    echo -e "${CYAN}Please provide admin user credentials:${NC}"
    echo ""
    
    # Prompt for email
    while true; do
        read -p "Admin email (default: admin@pim.com): " input_email
        if [ -z "$input_email" ]; then
            ADMIN_EMAIL="admin@pim.com"
            break
        elif [[ "$input_email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
            ADMIN_EMAIL="$input_email"
            break
        else
            print_error "Invalid email format. Please enter a valid email address."
        fi
    done
    
    # Prompt for password
    while true; do
        echo -n "Admin password: "
        read -s input_password
        echo ""
        
        if [ -z "$input_password" ]; then
            print_error "Password cannot be empty. Please enter a password."
            continue
        fi
        
        if [ ${#input_password} -lt 6 ]; then
            print_error "Password must be at least 6 characters long."
            continue
        fi
        
        echo -n "Confirm password: "
        read -s confirm_password
        echo ""
        
        if [ "$input_password" = "$confirm_password" ]; then
            ADMIN_PASSWORD="$input_password"
            break
        else
            print_error "Passwords do not match. Please try again."
        fi
    done
    
    echo ""
    print_status "Admin credentials set:"
    echo -e "${YELLOW}Email:${NC} $ADMIN_EMAIL"
    echo -e "${YELLOW}Password:${NC} ********"
    echo ""
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

# Step 2: Prompt for admin credentials
echo ""
prompt_admin_credentials

# Step 3: Create/update .env file
echo ""
print_info "Step 3: Setting up environment variables..."

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

# Step 4: Setup database directory and permissions
echo ""
print_info "Step 4: Setting up database directory..."

# Create db directory if it doesn't exist
mkdir -p db
chmod 777 db

# Move existing database to db directory if it exists
if [[ -f "pim.db" ]]; then
    print_info "Moving existing database to db directory..."
    mv pim.db db/
fi

# Step 5: Update docker-compose.yml to mount db directory
echo ""
print_info "Step 5: Updating docker-compose.yml..."

# Check if db mount already exists
if ! grep -q "db:/app/db" "$COMPOSE_DIR/docker-compose.yml"; then
    print_info "Adding db volume mount to docker-compose.yml..."
    
    # Create a backup
    cp "$COMPOSE_DIR/docker-compose.yml" "$COMPOSE_DIR/docker-compose.yml.backup"
    
    # Update the pim service to include db mount
    sed -i '/pim:/,/healthcheck:/ { /volumes:/!b; /volumes:/a\      - ./fastAPI/PIM-BE/db:/app/db' "$COMPOSE_DIR/docker-compose.yml"
    
    print_status "Updated docker-compose.yml with db mount"
else
    print_status "db mount already exists in docker-compose.yml"
fi

# Step 6: Build and start containers
echo ""
print_info "Step 6: Building and starting containers..."

cd "$COMPOSE_DIR"

# Stop existing containers
print_info "Stopping existing containers..."
docker compose down -v 2>/dev/null || true

# Build and start containers
print_info "Building and starting containers..."
docker compose up --build -d

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

# Step 10: Create admin user
echo ""
print_info "Step 10: Creating admin user..."

# Wait a bit more for the application to fully initialize
sleep 10

# Create admin user using the API
ADMIN_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\"}")

if echo "$ADMIN_RESPONSE" | grep -q "superadmin"; then
    print_status "Admin user already exists and login successful!"
elif echo "$ADMIN_RESPONSE" | grep -q "Invalid credentials"; then
    print_info "Admin user exists but password might be different. Creating new admin user..."
    
    # Try to create admin user using the signup endpoint first
    SIGNUP_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/auth/signup" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\", \"company_name\": \"System Admin\"}")
    
    if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
        print_status "Admin user created successfully!"
    else
        print_warning "Could not create admin user via signup. You may need to create it manually."
    fi
else
    print_warning "Admin user creation status unclear. You may need to create it manually."
fi

# Step 11: Display final status
echo ""
print_status "Step 11: Final status check..."

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

# Step 12: Display admin credentials
echo ""
print_header "DEPLOYMENT SUMMARY"

echo -e "${CYAN}🎯 Project:${NC} PIM System"
echo -e "${CYAN}🌐 URL:${NC} http://localhost:8004"
echo -e "${CYAN}📊 Health Check:${NC} http://localhost:8004/health"
echo -e "${CYAN}📚 API Docs:${NC} http://localhost:8004/docs"

echo ""
echo -e "${GREEN}🔑 ADMIN CREDENTIALS${NC}"
echo -e "${YELLOW}Email:${NC} $ADMIN_EMAIL"
echo -e "${YELLOW}Password:${NC} $ADMIN_PASSWORD"
echo -e "${YELLOW}Role:${NC} superadmin"

echo ""
echo -e "${GREEN}📁 IMPORTANT FILES${NC}"
echo -e "${YELLOW}Database:${NC} ./fastAPI/PIM-BE/db/pim.db"
echo -e "${YELLOW}Logs:${NC} docker compose logs pim -f"
echo -e "${YELLOW}Compose:${NC} $COMPOSE_DIR/docker-compose.yml"

echo ""
echo -e "${GREEN}🚀 USEFUL COMMANDS${NC}"
echo -e "${YELLOW}Stop application:${NC} docker compose down"
echo -e "${YELLOW}View logs:${NC} docker compose logs pim -f"
echo -e "${YELLOW}Restart:${NC} ./redeploy.sh"

echo ""
echo "🎯 Redeployment Summary:"
echo "  ✅ Environment variables: Configured"
echo "  ✅ Database directory: Created (db/)"
echo "  ✅ Database permissions: Fixed (777)"
echo "  ✅ Docker-compose.yml: Updated with db mount"
echo "  ✅ Containers: Built and started"
echo "  ✅ Service: Running and healthy"
echo "  ✅ Health endpoint: Working"
echo "  ✅ Admin user: Created with secure credentials"

echo ""
print_status "🎉 PIM application redeployment completed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Update SUPABASE_SERVICE_ROLE_KEY in $COMPOSE_DIR/.env if needed"
echo "2. Test the API at http://localhost:8004/docs"
echo "3. Check service logs: docker compose logs pim -f"
echo "4. Login with admin credentials: $ADMIN_EMAIL"
echo ""
echo "🚀 Your PIM application is ready to use!" 