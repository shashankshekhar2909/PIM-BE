#!/bin/bash

# 🚀 PIM System Deployment Script
# This script deploys the complete PIM system and creates a default admin user

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="PIM System"
DEFAULT_ADMIN_EMAIL="admin@pim.com"
DEFAULT_ADMIN_NAME="System Administrator"
PORT="8004"
DOCKER_IMAGE_NAME="pim-system"
CONTAINER_NAME="pim-container"

# Variables for admin credentials
ADMIN_EMAIL=""
ADMIN_PASSWORD=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        print_warning "Port $PORT is already in use. Stopping existing process..."
        sudo lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to prompt for admin credentials
prompt_admin_credentials() {
    print_header "ADMIN USER SETUP"
    
    echo -e "${CYAN}Please provide admin user credentials:${NC}"
    echo ""
    
    # Prompt for email
    while true; do
        read -p "Admin email (default: $DEFAULT_ADMIN_EMAIL): " input_email
        if [ -z "$input_email" ]; then
            ADMIN_EMAIL="$DEFAULT_ADMIN_EMAIL"
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

# Function to create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    source venv/bin/activate
    
    # Run migrations
    python3 -c "
import sys
sys.path.append('.')
from app.core.migrations import run_migrations
run_migrations()
"
    print_success "Database setup completed"
}

# Function to create admin user
create_admin_user() {
    print_status "Creating admin user..."
    source venv/bin/activate
    
    # Check if admin user already exists
    python3 -c "
import sys
sys.path.append('.')
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={'check_same_thread': False})
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM users WHERE email = \"$ADMIN_EMAIL\"'))
    count = result.scalar()
    if count > 0:
        print('Admin user already exists')
        exit(0)
    else:
        print('Admin user does not exist')
        exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_status "Admin user already exists"
    else
        # Create admin user
        python3 -c "
import sys
sys.path.append('.')
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.security import get_password_hash
from datetime import datetime

engine = create_engine(settings.DATABASE_URL, connect_args={'check_same_thread': False})
with engine.connect() as conn:
    password_hash = get_password_hash('$ADMIN_PASSWORD')
    current_time = datetime.utcnow().isoformat()
    
    conn.execute(text('''
        INSERT INTO users (
            email, password_hash, role, first_name, last_name, 
            is_active, is_blocked, created_at, updated_at, notes
        ) VALUES (
            '$ADMIN_EMAIL', :password_hash, 'superadmin', 'System', 'Administrator',
            1, 0, :created_at, :updated_at, 'Default superadmin user created by deployment script'
        )
    '''), {
        'password_hash': password_hash,
        'created_at': current_time,
        'updated_at': current_time
    })
    conn.commit()
    print('Admin user created successfully')
"
        print_success "Admin user created"
    fi
}

# Function to start the application
start_application() {
    print_status "Starting PIM application..."
    source venv/bin/activate
    
    # Start the application in background
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload > pim.log 2>&1 &
    APP_PID=$!
    echo $APP_PID > pim.pid
    
    # Wait for application to start
    sleep 5
    
    # Check if application is running
    if curl -s http://localhost:$PORT/health > /dev/null; then
        print_success "Application started successfully on port $PORT"
    else
        print_error "Failed to start application"
        exit 1
    fi
}

# Function to test the application
test_application() {
    print_status "Testing application..."
    
    # Test health endpoint
    if curl -s http://localhost:$PORT/health | grep -q "OK"; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        exit 1
    fi
    
    # Test admin login
    LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:$PORT/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$ADMIN_EMAIL\", \"password\": \"$ADMIN_PASSWORD\"}")
    
    if echo "$LOGIN_RESPONSE" | grep -q "superadmin"; then
        print_success "Admin login test passed"
    else
        print_error "Admin login test failed"
        echo "Response: $LOGIN_RESPONSE"
        exit 1
    fi
}

# Function to display deployment summary
display_summary() {
    print_header "DEPLOYMENT SUMMARY"
    
    echo -e "${CYAN}🎯 Project:${NC} $PROJECT_NAME"
    echo -e "${CYAN}🌐 URL:${NC} http://localhost:$PORT"
    echo -e "${CYAN}📊 Health Check:${NC} http://localhost:$PORT/health"
    echo -e "${CYAN}📚 API Docs:${NC} http://localhost:$PORT/docs"
    
    echo ""
    echo -e "${GREEN}🔑 ADMIN CREDENTIALS${NC}"
    echo -e "${YELLOW}Email:${NC} $ADMIN_EMAIL"
    echo -e "${YELLOW}Password:${NC} $ADMIN_PASSWORD"
    echo -e "${YELLOW}Role:${NC} superadmin"
    
    echo ""
    echo -e "${GREEN}📁 IMPORTANT FILES${NC}"
    echo -e "${YELLOW}Logs:${NC} pim.log"
    echo -e "${YELLOW}PID:${NC} pim.pid"
    echo -e "${YELLOW}Database:${NC} pim.db"
    
    echo ""
    echo -e "${GREEN}🚀 USEFUL COMMANDS${NC}"
    echo -e "${YELLOW}Stop application:${NC} ./stop_pim.sh"
    echo -e "${YELLOW}View logs:${NC} tail -f pim.log"
    echo -e "${YELLOW}Restart:${NC} ./deploy_pim.sh"
    
    echo ""
    echo -e "${PURPLE}================================${NC}"
    echo -e "${GREEN}✅ PIM System deployed successfully!${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to cleanup on exit
cleanup() {
    if [ -f "pim.pid" ]; then
        PID=$(cat pim.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_status "Stopping application (PID: $PID)..."
            kill $PID 2>/dev/null || true
        fi
        rm -f pim.pid
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main deployment function
main() {
    print_header "PIM SYSTEM DEPLOYMENT"
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command_exists python3; then
        print_error "Python3 is not installed"
        exit 1
    fi
    
    if ! command_exists pip; then
        print_error "pip is not installed"
        exit 1
    fi
    
    if ! command_exists curl; then
        print_error "curl is not installed"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
    
    # Prompt for admin credentials
    prompt_admin_credentials
    
    # Check port availability
    check_port
    
    # Create virtual environment
    create_venv
    
    # Install dependencies
    install_dependencies
    
    # Setup database
    setup_database
    
    # Create admin user
    create_admin_user
    
    # Start application
    start_application
    
    # Test application
    test_application
    
    # Display summary
    display_summary
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -p, --port     Specify port (default: 8004)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy with interactive admin setup"
    echo "  $0 -p 8080           # Deploy on port 8080"
    echo ""
    echo "Note: Admin credentials will be prompted during deployment for security."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -p|--port)
            PORT="$2"
            shift 2
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