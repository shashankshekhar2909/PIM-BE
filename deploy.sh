#!/bin/bash

# 🚀 PIM System Deployment Script
# This is the ONLY deployment script you need to run

set -e  # Exit on any error

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
    print_success "Admin credentials set:"
    echo -e "${YELLOW}Email:${NC} $ADMIN_EMAIL"
    echo -e "${YELLOW}Password:${NC} ********"
    echo ""
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running"
        echo "Please start Docker and try again"
        exit 1
    fi
    print_success "Docker is running"
    
    # Check if docker compose is available
    if ! docker compose version > /dev/null 2>&1; then
        print_error "docker compose command not found"
        echo "Please ensure Docker Compose is installed"
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to setup environment
setup_environment() {
    print_info "Setting up environment..."
    
    # Create db directory if it doesn't exist
    mkdir -p db
    chmod 777 db
    
    # Move existing database to db directory if it exists
    if [[ -f "pim.db" ]]; then
        print_info "Moving existing database to db directory..."
        mv pim.db db/
    fi
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        print_info "Creating .env file..."
        cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://hhxuxthwvpeplhtprnhf.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhoeHV4dGh3dnBlcGxodHBybmhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NjE3MjQsImV4cCI6MjA3MDAzNzcyNH0.1f9e_bPsbLtV9BiSrSO2IvHEf0ePSC8j1Ki_S2I-j_Y
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Application Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./db/pim.db
EOF
        print_warning "Please update SUPABASE_SERVICE_ROLE_KEY and SECRET_KEY in .env"
    else
        print_success ".env file exists"
    fi
}

# Function to check if we're in a multi-service environment
check_multi_service() {
    if [[ -f "../../docker-compose.yml" ]]; then
        print_info "Multi-service environment detected"
        COMPOSE_DIR="../../"
        return 0
    elif [[ -f "docker-compose.yml" ]]; then
        print_info "Standalone environment detected"
        COMPOSE_DIR="."
        return 1
    else
        print_error "No docker-compose.yml found"
        exit 1
    fi
}

# Function to update docker-compose.yml for multi-service
update_multi_service_compose() {
    if [ "$COMPOSE_DIR" = "../../" ]; then
        print_info "Updating multi-service docker-compose.yml..."
        
        # Check if db mount already exists
        if ! grep -q "db:/app/db" "$COMPOSE_DIR/docker-compose.yml"; then
            # Create a backup
            cp "$COMPOSE_DIR/docker-compose.yml" "$COMPOSE_DIR/docker-compose.yml.backup"
            
            # Update the pim service to include db mount
            sed -i '/pim:/,/healthcheck:/ { /volumes:/!b; /volumes:/a\      - ./fastAPI/PIM-BE/db:/app/db' "$COMPOSE_DIR/docker-compose.yml"
            
            print_success "Updated docker-compose.yml with db mount"
        else
            print_success "db mount already exists in docker-compose.yml"
        fi
    fi
}

# Function to build and start containers
build_and_start() {
    print_info "Building and starting containers..."
    
    cd "$COMPOSE_DIR"
    
    # Stop existing containers
    docker compose down -v 2>/dev/null || true
    
    # Build and start containers
    docker compose up --build -d
    
    print_success "Containers built and started"
}

# Function to wait for service
wait_for_service() {
    print_info "Waiting for service to be ready..."
    
    max_attempts=20
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt/$max_attempts: Checking service health..."
        
        if curl -f http://localhost:8004/health &> /dev/null; then
            print_success "PIM service is ready!"
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
}

# Function to create admin user
create_admin_user() {
    print_info "Creating admin user..."
    
    # Wait a bit more for the application to fully initialize
    sleep 10
    
    # Try to login first to check if admin exists
    ADMIN_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\"}")
    
    if echo "$ADMIN_RESPONSE" | grep -q "superadmin"; then
        print_success "Admin user already exists and login successful!"
    elif echo "$ADMIN_RESPONSE" | grep -q "Invalid credentials"; then
        print_info "Admin user exists but password might be different. Creating new admin user..."
        
        # Try to create admin user using the signup endpoint
        SIGNUP_RESPONSE=$(curl -s -X POST "http://localhost:8004/api/v1/auth/signup" \
            -H "Content-Type: application/json" \
            -d "{\"email\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\", \"company_name\": \"System Admin\"}")
        
        if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
            print_success "Admin user created successfully!"
        else
            print_warning "Could not create admin user via signup. You may need to create it manually."
        fi
    else
        print_warning "Admin user creation status unclear. You may need to create it manually."
    fi
}

# Function to display summary
display_summary() {
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
    if [ "$COMPOSE_DIR" = "../../" ]; then
        echo -e "${YELLOW}Database:${NC} ./fastAPI/PIM-BE/db/pim.db"
        echo -e "${YELLOW}Compose:${NC} $COMPOSE_DIR/docker-compose.yml"
    else
        echo -e "${YELLOW}Database:${NC} ./db/pim.db"
        echo -e "${YELLOW}Compose:${NC} docker-compose.yml"
    fi
    echo -e "${YELLOW}Logs:${NC} docker compose logs pim -f"
    
    echo ""
    echo -e "${GREEN}🚀 USEFUL COMMANDS${NC}"
    echo -e "${YELLOW}Stop application:${NC} docker compose down"
    echo -e "${YELLOW}View logs:${NC} docker compose logs pim -f"
    echo -e "${YELLOW}Restart:${NC} ./deploy.sh"
    
    echo ""
    echo -e "${PURPLE}================================${NC}"
    echo -e "${GREEN}✅ PIM System deployed successfully!${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy with interactive admin setup"
    echo ""
    echo "Note: Admin credentials will be prompted during deployment for security."
    echo ""
    echo "This script automatically detects:"
    echo "  - Standalone Docker environment (docker-compose.yml in current dir)"
    echo "  - Multi-service Docker environment (docker-compose.yml in parent dir)"
}

# Main deployment function
main() {
    print_header "PIM SYSTEM DEPLOYMENT"
    
    # Check prerequisites
    check_prerequisites
    
    # Prompt for admin credentials
    prompt_admin_credentials
    
    # Setup environment
    setup_environment
    
    # Check environment type
    if check_multi_service; then
        # Multi-service environment
        update_multi_service_compose
    fi
    
    # Build and start containers
    build_and_start
    
    # Wait for service
    wait_for_service
    
    # Create admin user
    create_admin_user
    
    # Display summary
    display_summary
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run main deployment
main "$@" 