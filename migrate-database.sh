#!/bin/bash

# 🗄️ Database Migration Script for PIM System
# This script migrates the existing database to the new data directory structure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Main migration function
main() {
    print_header "DATABASE MIGRATION"
    
    print_info "Current directory: $(pwd)"
    
    # Check if we're in the right directory
    if [ ! -f "Dockerfile" ]; then
        print_error "Not in the correct directory"
        echo "Please run this script from the PIM-BE directory"
        exit 1
    fi
    
    # Create data directory if it doesn't exist
    if [ ! -d "data" ]; then
        print_info "Creating data directory..."
        mkdir -p data
        print_success "Data directory created"
    fi
    
    # Check if database exists in current location
    if [ -f "pim.db" ]; then
        print_info "Found existing database: pim.db"
        
        # Check if database exists in data directory
        if [ -f "data/pim.db" ]; then
            print_warning "Database already exists in data directory"
            read -p "Do you want to overwrite it? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_info "Overwriting existing database in data directory..."
                cp pim.db data/pim.db
                print_success "Database copied to data directory"
            else
                print_info "Keeping existing database in data directory"
            fi
        else
            print_info "Copying database to data directory..."
            cp pim.db data/pim.db
            print_success "Database copied to data directory"
        fi
        
        # Set proper permissions
        print_info "Setting database permissions..."
        chmod 644 data/pim.db
        print_success "Database permissions set"
        
        # Create backup of original
        print_info "Creating backup of original database..."
        cp pim.db pim.db.backup.$(date +%Y%m%d_%H%M%S)
        print_success "Backup created"
        
    else
        print_warning "No existing database found in current directory"
        print_info "A new database will be created when the service starts"
    fi
    
    # Set directory permissions
    print_info "Setting directory permissions..."
    chmod 755 data
    print_success "Directory permissions set"
    
    print_success "Database migration completed!"
    echo ""
    echo -e "${BLUE}📁 Database location:${NC}"
    echo -e "  ${GREEN}data/pim.db${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo -e "  1. Run: ${YELLOW}./simple-deploy.sh${NC}"
    echo -e "  2. The service will use the new database location"
    echo -e "  3. Check logs: ${YELLOW}docker compose logs pim -f${NC}"
}

# Run main function
main "$@"
