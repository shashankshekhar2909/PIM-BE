#!/bin/bash

# 🛑 PIM System Stop Script
# This script stops the PIM application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  PIM SYSTEM STOP${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to stop application
stop_application() {
    print_status "Stopping PIM application..."
    
    if [ -f "pim.pid" ]; then
        PID=$(cat pim.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_status "Stopping process (PID: $PID)..."
            kill $PID 2>/dev/null || true
            
            # Wait for process to stop
            sleep 2
            
            if ! ps -p $PID > /dev/null 2>&1; then
                print_success "Application stopped successfully"
            else
                print_warning "Process still running, force killing..."
                kill -9 $PID 2>/dev/null || true
                sleep 1
                if ! ps -p $PID > /dev/null 2>&1; then
                    print_success "Application force stopped"
                else
                    print_error "Failed to stop application"
                    exit 1
                fi
            fi
        else
            print_warning "Process not running (PID: $PID)"
        fi
        
        # Remove PID file
        rm -f pim.pid
    else
        print_warning "PID file not found, checking for running processes..."
        
        # Check for running uvicorn processes
        PIDS=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || true)
        if [ -n "$PIDS" ]; then
            print_status "Found running processes: $PIDS"
            echo $PIDS | xargs kill 2>/dev/null || true
            sleep 2
            echo $PIDS | xargs kill -9 2>/dev/null || true
            print_success "All PIM processes stopped"
        else
            print_status "No running PIM processes found"
        fi
    fi
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    # Remove PID file if it exists
    if [ -f "pim.pid" ]; then
        rm -f pim.pid
    fi
    
    # Check if any PIM processes are still running
    PIDS=$(pgrep -f "uvicorn.*app.main:app" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        print_warning "Some processes may still be running: $PIDS"
    else
        print_success "All PIM processes stopped and cleaned up"
    fi
}

# Main function
main() {
    print_header
    
    stop_application
    cleanup
    
    echo ""
    echo -e "${GREEN}✅ PIM System stopped successfully!${NC}"
    echo ""
    echo -e "${YELLOW}To restart:${NC} ./deploy_pim.sh"
    echo -e "${YELLOW}To view logs:${NC} tail -f pim.log"
}

# Run main function
main "$@" 