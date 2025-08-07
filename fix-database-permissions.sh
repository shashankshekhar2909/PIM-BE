#!/bin/bash

# Fix database permissions issue

echo "🔧 Fixing Database Permissions"
echo "=============================="

# Check if docker-compose.yml exists in parent directory
if [[ -f "../../docker-compose.yml" ]]; then
    echo "✅ docker-compose.yml found in ../../"
    COMPOSE_DIR="../../"
else
    echo "❌ docker-compose.yml not found in ../../"
    echo "Please ensure docker-compose.yml is in the parent directory"
    exit 1
fi

# Check if database file exists
if [[ -f "pim.db" ]]; then
    echo "✅ Database file found: pim.db"
else
    echo "⚠️  Database file not found: pim.db"
    echo "Creating empty database file..."
    touch pim.db
fi

# Fix permissions for the database file
echo ""
echo "🔐 Fixing database file permissions..."

# Make sure the database file is writable
chmod 666 pim.db

# Also fix permissions for the entire PIM-BE directory
echo "🔐 Fixing directory permissions..."
chmod -R 755 .

echo "✅ Permissions fixed"

# Stop PIM service
echo ""
echo "🛑 Step 1: Stopping PIM service..."
cd "$COMPOSE_DIR" && docker compose stop pim

# Remove PIM container to force rebuild
echo ""
echo "🗑️  Step 2: Removing PIM container..."
docker compose rm -f pim

# Build PIM service
echo ""
echo "🔨 Step 3: Building PIM service..."
docker compose build --no-cache pim

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    echo "Please check the build logs above"
    exit 1
fi

echo "✅ Build completed successfully"

# Start PIM service
echo ""
echo "🚀 Step 4: Starting PIM service..."
docker compose up -d pim

if [ $? -ne 0 ]; then
    echo "❌ Failed to start PIM service"
    exit 1
fi

echo "✅ PIM service started successfully"

# Wait for service to start
echo ""
echo "⏳ Step 5: Waiting for service to start..."
sleep 20

# Check service status
echo ""
echo "📊 Step 6: Checking service status..."
docker compose ps pim

# Wait for service to be ready
echo ""
echo "🏥 Step 7: Checking service health..."
max_attempts=12
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt/$max_attempts: Checking service health..."
    
    if curl -f http://localhost:8004/health &> /dev/null; then
        echo "✅ PIM service is ready!"
        echo ""
        echo "🏥 Health Check Response:"
        curl -s http://localhost:8004/health | jq . 2>/dev/null || curl -s http://localhost:8004/health
        echo ""
        echo "🌐 Service URLs:"
        echo "  PIM API:      http://localhost:8004"
        echo "  API Docs:     http://localhost:8004/docs"
        echo "  Health Check: http://localhost:8004/health"
        echo ""
        echo "🔐 Database Status:"
        echo "  ✅ Database file permissions fixed"
        echo "  ✅ Database should be writable now"
        echo ""
        echo "🧪 Test authentication:"
        echo "  # Test signup (should work now)"
        echo "  curl -X POST http://localhost:8004/api/v1/auth/signup \\"
        echo "    -H \"Content-Type: application/json\" \\"
        echo "    -d '{\"email\":\"test@example.com\",\"password\":\"password123\",\"company_name\":\"Test Company\"}'"
        echo ""
        echo "  # Test login (should work now)"
        echo "  curl -X POST http://localhost:8004/api/v1/auth/login \\"
        echo "    -H \"Content-Type: application/json\" \\"
        echo "    -d '{\"email\":\"test@example.com\",\"password\":\"password123\"}'"
        echo ""
        echo "🎉 Database permissions fixed successfully!"
        exit 0
    else
        echo "⏳ Service not ready yet... (attempt $attempt/$max_attempts)"
        
        # Show recent logs every 3 attempts
        if [ $((attempt % 3)) -eq 0 ]; then
            echo "📋 Recent logs:"
            docker compose logs pim --tail=5
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    fi
done

echo "❌ Service did not become ready within 2 minutes"
echo ""
echo "🔍 Troubleshooting steps:"
echo "1. Check service logs: docker compose logs pim -f"
echo "2. Check database permissions: ls -la pim.db"
echo "3. Check if there are any other errors in the logs"
echo ""
echo "📋 Recent logs:"
docker compose logs pim --tail=20 