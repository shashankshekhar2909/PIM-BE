#!/bin/bash

# 🚀 Development Database Setup Script
# Quick setup for local development

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

echo "=========================================="
echo "  🚀 Development Database Setup"
echo "=========================================="

print_info "Setting up development database..."

# Ensure data directory exists
mkdir -p data

# Create fresh development database
if python3 create_production_db.py; then
    print_success "Development database created successfully"
else
    print_error "Failed to create development database"
    exit 1
fi

print_success "🎉 Development database setup completed!"
echo ""
echo "📋 Database Details:"
echo "   Location: data/pim.db"
echo "   Admin User: admin@pim.com"
echo "   Password: admin123"
echo "   Role: superadmin"
echo ""
echo "🚀 You can now run your FastAPI application:"
echo "   source venv/bin/activate"
echo "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "⚠️  IMPORTANT: Change the default admin password after first login!"
