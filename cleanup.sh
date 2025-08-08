#!/bin/bash

# 🧹 PIM System Cleanup Script
# This script removes all confusing deployment files and keeps only the essential ones

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

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

print_header "PIM SYSTEM CLEANUP"

echo "This script will remove all confusing deployment files and keep only the essential ones."
echo ""
echo "Files to be REMOVED:"
echo "  - Multiple deployment scripts (deploy_pim.sh, deploy_docker.sh, redeploy.sh)"
echo "  - Multiple documentation files (DEPLOYMENT_README.md, SECURE_DEPLOYMENT_SUMMARY.md, etc.)"
echo "  - Test scripts (test-*.sh)"
echo "  - Old setup scripts (add_superadmin.sh, setup_*.py)"
echo "  - Redundant documentation files"
echo ""
echo "Files to be KEPT:"
echo "  - deploy.sh (main deployment script)"
echo "  - README.md (main documentation)"
echo "  - docker-compose.yml"
echo "  - Dockerfile"
echo "  - requirements.txt"
echo "  - app/ directory"
echo "  - sample_data/ directory"
echo ""

read -p "Do you want to continue with the cleanup? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Cleanup cancelled"
    exit 0
fi

print_info "Starting cleanup..."

# Remove multiple deployment scripts
print_info "Removing multiple deployment scripts..."
rm -f deploy_pim.sh
rm -f deploy_docker.sh
rm -f redeploy.sh
rm -f stop_pim.sh
rm -f add_superadmin.sh
print_status "Removed multiple deployment scripts"

# Remove test scripts
print_info "Removing test scripts..."
rm -f test-*.sh
rm -f test-*.py
print_status "Removed test scripts"

# Remove old setup scripts
print_info "Removing old setup scripts..."
rm -f add_default_superadmin.py
rm -f setup_supabase_keys.py
rm -f setup_supabase_superadmin.py
rm -f create_default_superadmin.py
rm -f update_users_table.py
print_status "Removed old setup scripts"

# Remove redundant documentation files
print_info "Removing redundant documentation files..."
rm -f DEPLOYMENT_README.md
rm -f SECURE_DEPLOYMENT_SUMMARY.md
rm -f DEPLOYMENT_SUMMARY.md
rm -f DOCKER_DEPLOYMENT_SECURE.md
rm -f DOCKER_DEPLOYMENT.md
rm -f EXISTING_DEPLOYMENT.md
rm -f PRODUCTION_DEPLOYMENT.md
rm -f REDEPLOYMENT_README.md
rm -f DEPLOYMENT_GUIDE.md
rm -f MULTI_SERVICE_MANAGEMENT.md
rm -f MULTI_VALUE_SEARCH.md
rm -f SUPERADMIN_CREDENTIALS.md
rm -f AUTHENTICATION_SETUP.md
rm -f SUPERADMIN_SUMMARY.md
rm -f SUPERADMIN_SETUP.md
rm -f COMPLETE_USER_MANAGEMENT_IMPLEMENTATION.md
rm -f AUDIT_FIX_SUMMARY.md
rm -f SUPERADMIN_README.md
rm -f FINAL_INTEGRATION_SUMMARY.md
print_status "Removed redundant documentation files"

# Remove UI documentation (keep only essential)
print_info "Removing UI documentation..."
rm -f UI_INTEGRATION_GUIDE.md
rm -f UI_QUICK_REFERENCE.md
print_status "Removed UI documentation"

print_header "CLEANUP COMPLETED"

echo "✅ Cleanup completed successfully!"
echo ""
echo "📁 Remaining essential files:"
echo "  - deploy.sh (main deployment script)"
echo "  - README.md (main documentation)"
echo "  - docker-compose.yml"
echo "  - Dockerfile"
echo "  - requirements.txt"
echo "  - app/ (application code)"
echo "  - sample_data/ (sample data)"
echo ""
echo "🚀 To deploy the system:"
echo "  ./deploy.sh"
echo ""
echo "📚 For documentation:"
echo "  cat README.md" 