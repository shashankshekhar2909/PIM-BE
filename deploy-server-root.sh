#!/bin/bash

# 🚀 SERVER DEPLOYMENT SCRIPT FOR ROOT EXECUTION
# This script is designed for server deployment where root execution is necessary

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
PROJECT_NAME="PIM-BE"
SERVICE_NAME="pim"
CONTAINER_NAME="pim"
PORT="8004"
HEALTH_ENDPOINT="http://localhost:${PORT}/health"
BACKUP_DIR="backups"
DATA_DIR="data"

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

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root for server deployment"
        print_info "Please run: sudo ./deploy-server-root.sh"
        exit 1
    fi
    print_warning "Running as root for server deployment"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Installing Docker..."
        install_docker
    fi
    
    # Check if Docker Compose is available
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Installing Docker Compose..."
        install_docker_compose
    fi
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed. Installing curl..."
        apt-get update && apt-get install -y curl
    fi
    
    # Ensure Docker daemon is running
    print_info "Ensuring Docker daemon is running..."
    systemctl start docker
    systemctl enable docker
    
    print_success "All prerequisites are satisfied"
}

# Install Docker if not present
install_docker() {
    print_info "Installing Docker..."
    
    # Update package index
    apt-get update
    
    # Install prerequisites
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    print_success "Docker installed successfully"
}

# Install Docker Compose if not present
install_docker_compose() {
    print_info "Installing Docker Compose..."
    
    # Install Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose installed successfully"
}

# Create necessary directories
setup_directories() {
    print_step "Setting up directories..."
    
    # Create data directory
    if [ ! -d "$DATA_DIR" ]; then
        mkdir -p "$DATA_DIR"
        print_info "Created data directory: $DATA_DIR"
    fi
    
    # Create backup directory
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        print_info "Created backup directory: $BACKUP_DIR"
    fi
    
    # Set proper ownership and permissions
    chown -R root:root "$DATA_DIR" "$BACKUP_DIR"
    chmod 755 "$DATA_DIR" "$BACKUP_DIR"
    
    print_success "Directories setup completed"
}

# Database management
manage_database() {
    print_step "Managing database..."
    
    # Check if database exists in current location
    if [ -f "pim.db" ]; then
        print_info "Found existing database: pim.db"
        
        # Create timestamped backup
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="${BACKUP_DIR}/pim.db.backup.${TIMESTAMP}"
        
        print_info "Creating backup: $BACKUP_FILE"
        cp pim.db "$BACKUP_FILE"
        print_success "Backup created: $BACKUP_FILE"
        
        # Copy to data directory if not exists
        if [ ! -f "${DATA_DIR}/pim.db" ]; then
            print_info "Copying database to data directory..."
            cp pim.db "${DATA_DIR}/pim.db"
            print_success "Database copied to data directory"
        else
            print_warning "Database already exists in data directory"
            read -p "Do you want to overwrite it? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_info "Overwriting existing database in data directory..."
                cp pim.db "${DATA_DIR}/pim.db"
                print_success "Database overwritten"
            fi
        fi
        
        # Set proper permissions
        chown root:root "${DATA_DIR}/pim.db"
        chmod 644 "${DATA_DIR}/pim.db"
        print_success "Database permissions set"
        
    else
        print_warning "No existing database found"
        print_info "A new database will be created when the service starts"
    fi
    
    # Set directory permissions
    chown root:root "$DATA_DIR" "$BACKUP_DIR"
    chmod 755 "$DATA_DIR" "$BACKUP_DIR"
    print_success "Directory permissions set"
}

# Clean up old containers and images
cleanup_docker() {
    print_step "Cleaning up Docker resources..."
    
    # Stop and remove existing containers
    if docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        print_info "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
        print_success "Existing container removed"
    fi
    
    # Remove old images (keep only the latest)
    print_info "Cleaning up old images..."
    docker image prune -f
    print_success "Docker cleanup completed"
}

# Build and deploy
deploy_service() {
    print_step "Building and deploying service..."
    
    # Navigate to parent directory if docker-compose.yml exists there
    if [ -f "../../docker-compose.yml" ]; then
        print_info "Multi-service environment detected"
        cd ../..
        print_info "Changed to directory: $(pwd)"
    fi
    
    # Stop existing services
    print_info "Stopping existing services..."
    docker compose down 2>/dev/null || true
    
    # Build and start the service
    print_info "Building and starting $SERVICE_NAME service..."
    docker compose up --build -d "$SERVICE_NAME"
    
    # Wait for service to start
    print_info "Waiting for service to start..."
    sleep 5
    
    # Check if service is running
    if docker compose ps "$SERVICE_NAME" | grep -q "Up"; then
        print_success "Service started successfully!"
    else
        print_error "Failed to start service"
        print_info "Checking logs..."
        docker compose logs "$SERVICE_NAME" --tail=20
        exit 1
    fi
}

# Health check
check_health() {
    print_step "Checking service health..."
    
    # Wait a bit more for the service to fully initialize
    sleep 10
    
    # Check health endpoint
    if curl -s "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
        print_success "Service is healthy!"
        print_info "Health check response:"
        curl -s "$HEALTH_ENDPOINT" | jq . 2>/dev/null || curl -s "$HEALTH_ENDPOINT"
    else
        print_warning "Health check failed, but service might still be starting..."
        print_info "Checking service status..."
        docker compose ps "$SERVICE_NAME"
    fi
}

# Show final status
show_status() {
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
}

# Main deployment function
main() {
    print_header "SERVER DEPLOYMENT (ROOT)"
    
    print_info "Project: $PROJECT_NAME"
    print_info "Service: $SERVICE_NAME"
    print_info "Port: $PORT"
    print_info "Current directory: $(pwd)"
    print_warning "Running as root for server deployment"
    
    # Check if we're in the right directory
    if [ ! -f "Dockerfile" ] && [ ! -f "../../docker-compose.yml" ]; then
        print_error "Not in the correct directory"
        echo "Please run this script from the PIM-BE directory"
        exit 1
    fi
    
    # Run deployment steps
    check_root
    check_prerequisites
    setup_directories
    manage_database
    cleanup_docker
    deploy_service
    check_health
    show_status
    
    # Success message
    echo ""
    print_success "🎉 SERVER DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo ""
    echo -e "${BLUE}🌐 Access URLs:${NC}"
    echo -e "  Application: ${GREEN}http://localhost:${PORT}${NC}"
    echo -e "  Health Check: ${GREEN}${HEALTH_ENDPOINT}${NC}"
    echo -e "  API Docs: ${GREEN}http://localhost:${PORT}/docs${NC}"
    echo ""
    echo -e "${BLUE}📋 Useful Commands:${NC}"
    echo -e "  View logs: ${YELLOW}docker compose logs $SERVICE_NAME -f${NC}"
    echo -e "  Stop service: ${YELLOW}docker compose down${NC}"
    echo -e "  Restart service: ${YELLOW}docker compose restart $SERVICE_NAME${NC}"
    echo -e "  Check status: ${YELLOW}docker compose ps${NC}"
    echo ""
    echo -e "${BLUE}🗄️  Database:${NC}"
    echo -e "  Location: ${GREEN}${DATA_DIR}/pim.db${NC}"
    echo -e "  Backups: ${GREEN}${BACKUP_DIR}/${NC}"
    echo ""
    echo -e "${BLUE}🔧 Troubleshooting:${NC}"
    echo -e "  If you encounter issues:"
    echo -e "  1. Check logs: ${YELLOW}docker compose logs $SERVICE_NAME${NC}"
    echo -e "  2. Check container status: ${YELLOW}docker compose ps${NC}"
    echo -e "  3. Restart service: ${YELLOW}docker compose restart $SERVICE_NAME${NC}"
    echo -e "  4. Full restart: ${YELLOW}./deploy-server-root.sh${NC}"
}

# Run main function
main "$@"
