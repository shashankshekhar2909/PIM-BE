#!/bin/bash

# Quick Deploy Script - After Pull
# This script deploys the PIM system after pulling latest changes

echo "🚀 PIM System Deployment - After Pull"
echo "====================================="

# Check if we're in the PIM-BE directory
if [[ ! -f "Dockerfile" ]] || [[ ! -d "app" ]]; then
    echo "❌ Error: This script must be run from the PIM-BE directory"
    echo "Current directory: $(pwd)"
    echo "Please run: cd fastAPI/PIM-BE && ./deploy-after-pull.sh"
    exit 1
fi

echo "✅ Current directory: $(pwd)"

# Step 1: Build the updated service
echo ""
echo "🔨 Step 1: Building PIM service..."
./manage-docker.sh build-pim

if [ $? -ne 0 ]; then
    echo "❌ Error: Build failed"
    exit 1
fi

echo "✅ Build completed successfully"

# Step 2: Restart the service
echo ""
echo "🔄 Step 2: Restarting PIM service..."
./manage-docker.sh restart-pim

if [ $? -ne 0 ]; then
    echo "❌ Error: Restart failed"
    exit 1
fi

echo "✅ Service restarted successfully"

# Step 3: Wait a bit for service to start
echo ""
echo "⏳ Step 3: Waiting for service to start..."
sleep 10

# Step 4: Verify deployment
echo ""
echo "🏥 Step 4: Verifying deployment..."
./manage-docker.sh health

if [ $? -ne 0 ]; then
    echo "❌ Error: Health check failed"
    echo "Checking logs..."
    ./manage-docker.sh logs-pim
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo "====================================="
echo "PIM System is now running with latest changes"
echo ""
echo "🌐 Service URLs:"
echo "  PIM API:      http://localhost:8004"
echo "  API Docs:     http://localhost:8004/docs"
echo "  Health Check: http://localhost:8004/health"
echo ""
echo "🧪 Test the new multi-value search:"
echo "  curl \"http://localhost:8004/api/v1/products?manufacturer=Adidas,Apple,Bosch,Hasbro,Home Depot\""
echo ""
echo "📊 Service Status:"
./manage-docker.sh status 