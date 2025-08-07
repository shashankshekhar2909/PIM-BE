#!/bin/bash

# PIM System Deployment Script
# This script helps deploy the PIM system in the existing multi-service environment

echo "🚀 PIM System Deployment Script"
echo "================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found in current directory"
    echo "Please run this script from the root directory where docker-compose.yml is located"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating .env template..."
    cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Application Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./pim.db
EOF
    echo "✅ Created .env template. Please update it with your actual values."
    echo "Then run this script again."
    exit 1
fi

# Check if PIM-BE directory exists
if [ ! -d "fastAPI/PIM-BE" ]; then
    echo "❌ Error: fastAPI/PIM-BE directory not found"
    echo "Please ensure the PIM-BE directory exists in the fastAPI folder"
    exit 1
fi

echo "✅ Environment check passed"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Error: Docker is not running"
        echo "Please start Docker and try again"
        exit 1
    fi
}

# Function to build and start services
deploy_services() {
    echo "🔨 Building and starting services..."
    
    # Build all services
    docker-compose build
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to build services"
        exit 1
    fi
    
    # Start services
    docker-compose up -d
    
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to start services"
        exit 1
    fi
    
    echo "✅ Services started successfully"
}

# Function to check service health
check_health() {
    echo "🏥 Checking service health..."
    
    # Wait a bit for services to start
    sleep 10
    
    # Check PIM service health
    if curl -f http://localhost:8004/health > /dev/null 2>&1; then
        echo "✅ PIM service is healthy"
    else
        echo "⚠️  PIM service health check failed"
        echo "Checking logs..."
        docker-compose logs pim
    fi
    
    # Check other services
    for service in app1 app2 giftg; do
        if docker-compose ps $service | grep -q "Up"; then
            echo "✅ $service is running"
        else
            echo "⚠️  $service is not running"
        fi
    done
}

# Function to show service status
show_status() {
    echo ""
    echo "📊 Service Status:"
    echo "=================="
    docker-compose ps
    
    echo ""
    echo "🌐 Service URLs:"
    echo "================"
    echo "App1:     http://localhost:8001"
    echo "App2:     http://localhost:8002"
    echo "GiftG:    http://localhost:8003"
    echo "PIM:      http://localhost:8004"
    echo "PIM Docs: http://localhost:8004/docs"
    echo "PIM Health: http://localhost:8004/health"
}

# Function to show logs
show_logs() {
    echo ""
    echo "📋 Recent logs for PIM service:"
    echo "================================"
    docker-compose logs --tail=20 pim
}

# Main execution
main() {
    check_docker
    deploy_services
    check_health
    show_status
    show_logs
    
    echo ""
    echo "🎉 Deployment completed!"
    echo "========================"
    echo "PIM System is now running at: http://localhost:8004"
    echo "API Documentation: http://localhost:8004/docs"
    echo "Health Check: http://localhost:8004/health"
    echo ""
    echo "To view logs: docker-compose logs -f pim"
    echo "To stop services: docker-compose down"
    echo "To restart: docker-compose restart pim"
}

# Run main function
main 