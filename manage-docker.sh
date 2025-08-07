#!/bin/bash

# PIM Docker Management Script
# This script helps manage docker-compose from the PIM-BE directory
# when docker-compose.yml is in a parent directory

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we're in the PIM-BE directory
if [[ ! -f "Dockerfile" ]] || [[ ! -d "app" ]]; then
    print_error "This script must be run from the PIM-BE directory"
    print_error "Current directory: $(pwd)"
    print_error "Expected to find: Dockerfile and app/ directory"
    exit 1
fi

# Find the docker-compose.yml file (should be in parent directory)
COMPOSE_DIR=""
if [[ -f "../docker-compose.yml" ]]; then
    COMPOSE_DIR=".."
elif [[ -f "../../docker-compose.yml" ]]; then
    COMPOSE_DIR="../.."
elif [[ -f "../../../docker-compose.yml" ]]; then
    COMPOSE_DIR="../../.."
else
    print_error "docker-compose.yml not found in parent directories"
    print_error "Please ensure docker-compose.yml exists in a parent directory"
    exit 1
fi

print_status "Found docker-compose.yml in: $COMPOSE_DIR"

# Function to run docker-compose commands
run_compose() {
    local cmd="$1"
    print_status "Running: docker-compose $cmd (from $COMPOSE_DIR)"
    cd "$COMPOSE_DIR" && docker-compose $cmd
    local exit_code=$?
    cd "$SCRIPT_DIR"
    return $exit_code
}

# Function to check if .env file exists in compose directory
check_env() {
    if [[ ! -f "$COMPOSE_DIR/.env" ]]; then
        print_warning ".env file not found in $COMPOSE_DIR"
        print_status "Creating .env template..."
        cat > "$COMPOSE_DIR/.env" << EOF
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Application Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./pim.db
EOF
        print_status "Created .env template in $COMPOSE_DIR/.env"
        print_warning "Please update the .env file with your actual values"
        return 1
    fi
    return 0
}

# Function to show help
show_help() {
    print_header "PIM Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build          Build all services"
    echo "  build-pim      Build only PIM service"
    echo "  up             Start all services"
    echo "  up-pim         Start only PIM service"
    echo "  down           Stop all services"
    echo "  restart        Restart all services"
    echo "  restart-pim    Restart only PIM service"
    echo "  logs           Show all logs"
    echo "  logs-pim       Show PIM service logs"
    echo "  status         Show service status"
    echo "  health         Check PIM service health"
    echo "  shell          Enter PIM container shell"
    echo "  clean          Remove orphan containers"
    echo "  help           Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 up-pim      # Start only PIM service"
    echo "  $0 logs-pim    # View PIM logs"
    echo "  $0 health      # Check PIM health"
    echo ""
}

# Function to check PIM service health
check_health() {
    print_status "Checking PIM service health..."
    if curl -f http://localhost:8004/health > /dev/null 2>&1; then
        print_status "✅ PIM service is healthy"
        curl -s http://localhost:8004/health | jq . 2>/dev/null || curl -s http://localhost:8004/health
    else
        print_error "❌ PIM service health check failed"
        print_status "Checking if service is running..."
        run_compose "ps pim"
    fi
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    run_compose "ps"
    
    echo ""
    print_status "Service URLs:"
    echo "App1:     http://localhost:8001"
    echo "App2:     http://localhost:8002"
    echo "GiftG:    http://localhost:8003"
    echo "PIM:      http://localhost:8004"
    echo "PIM Docs: http://localhost:8004/docs"
    echo "PIM Health: http://localhost:8004/health"
}

# Function to clean orphan containers
clean_orphans() {
    print_status "Removing orphan containers..."
    run_compose "down --remove-orphans"
    print_status "Orphan containers removed"
}

# Main script logic
case "${1:-help}" in
    "build")
        print_header "Building All Services"
        check_env
        run_compose "build"
        ;;
    "build-pim")
        print_header "Building PIM Service"
        check_env
        run_compose "build pim"
        ;;
    "up")
        print_header "Starting All Services"
        check_env
        run_compose "up -d"
        show_status
        ;;
    "up-pim")
        print_header "Starting PIM Service"
        check_env
        run_compose "up -d pim"
        check_health
        ;;
    "down")
        print_header "Stopping All Services"
        run_compose "down"
        ;;
    "restart")
        print_header "Restarting All Services"
        run_compose "restart"
        ;;
    "restart-pim")
        print_header "Restarting PIM Service"
        run_compose "restart pim"
        check_health
        ;;
    "logs")
        print_header "Showing All Logs"
        run_compose "logs"
        ;;
    "logs-pim")
        print_header "Showing PIM Service Logs"
        run_compose "logs pim"
        ;;
    "status")
        print_header "Service Status"
        show_status
        ;;
    "health")
        print_header "Health Check"
        check_health
        ;;
    "shell")
        print_header "Entering PIM Container Shell"
        run_compose "exec pim bash"
        ;;
    "clean")
        print_header "Cleaning Orphan Containers"
        clean_orphans
        ;;
    "help"|*)
        show_help
        ;;
esac 