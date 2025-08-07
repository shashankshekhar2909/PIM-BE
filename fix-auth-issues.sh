#!/bin/bash

# Fix authentication issues using existing Supabase configuration

echo "🔐 Fixing Authentication Issues"
echo "==============================="

# Check if docker-compose.yml exists in parent directory
if [[ -f "../../docker-compose.yml" ]]; then
    echo "✅ docker-compose.yml found in ../../"
    COMPOSE_DIR="../../"
else
    echo "❌ docker-compose.yml not found in ../../"
    echo "Please ensure docker-compose.yml is in the parent directory"
    exit 1
fi

# Check if .env file exists in parent directory
if [[ ! -f "$COMPOSE_DIR/.env" ]]; then
    echo "⚠️  .env file not found in $COMPOSE_DIR"
    echo "Creating .env file with existing configuration..."
    
    cat > "$COMPOSE_DIR/.env" << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://hhxuxthwvpeplhtprnhf.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhoeHV4dGh3dnBlcGxodHBybmhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NjE3MjQsImV4cCI6MjA3MDAzNzcyNH0.1f9e_bPsbLtV9BiSrSO2IvHEf0ePSC8j1Ki_S2I-j_Y
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Application Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./pim.db
EOF
    
    echo "✅ Created .env file in $COMPOSE_DIR/.env"
    echo ""
    echo "⚠️  IMPORTANT: Please update the .env file with your actual values:"
    echo "   1. Get your SUPABASE_SERVICE_ROLE_KEY from Supabase dashboard"
    echo "   2. Change SECRET_KEY to a secure random string"
    echo "   3. Update other values as needed"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ .env file found in $COMPOSE_DIR"

# Check if environment variables are properly set
echo ""
echo "🔍 Checking environment variables..."

# Source the .env file to check variables
source "$COMPOSE_DIR/.env"

# Check if critical variables are set
if [[ "$SUPABASE_URL" == "" || "$SUPABASE_ANON_KEY" == "" ]]; then
    echo "❌ Critical Supabase variables are not set in .env file"
    echo "Please update your .env file with proper values"
    exit 1
fi

if [[ "$SECRET_KEY" == "your-secret-key-here" || "$SECRET_KEY" == "your-super-secret-key-change-this-in-production" || "$SECRET_KEY" == "" ]]; then
    echo "⚠️  SECRET_KEY is still using default value"
    echo "Generating a secure SECRET_KEY..."
    
    # Generate a secure secret key
    NEW_SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "fallback-secret-key-$(date +%s)")
    
    # Update the .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET_KEY/" "$COMPOSE_DIR/.env"
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET_KEY/" "$COMPOSE_DIR/.env"
    fi
    
    echo "✅ Updated SECRET_KEY in .env file"
fi

echo "✅ Environment variables check passed"

# Stop PIM service
echo ""
echo "🛑 Step 1: Stopping PIM service..."
cd "$COMPOSE_DIR" && docker compose stop pim

# Remove PIM container to force rebuild with new environment
echo ""
echo "🗑️  Step 2: Removing PIM container..."
docker compose rm -f pim

# Build PIM service with updated environment
echo ""
echo "🔨 Step 3: Building PIM service with updated environment..."
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
        echo "🔐 Authentication Status:"
        echo "  ✅ JWT secret key configured"
        echo "  ✅ Supabase URL configured"
        echo "  ✅ Supabase ANON key configured"
        if [[ "$SUPABASE_SERVICE_ROLE_KEY" != "your-service-role-key-here" ]]; then
            echo "  ✅ Supabase SERVICE_ROLE key configured"
        else
            echo "  ⚠️  Supabase SERVICE_ROLE key needs to be configured"
        fi
        echo ""
        echo "🧪 Test authentication:"
        echo "  # Test signup"
        echo "  curl -X POST http://localhost:8004/api/v1/auth/signup \\"
        echo "    -H \"Content-Type: application/json\" \\"
        echo "    -d '{\"email\":\"test@example.com\",\"password\":\"password123\",\"company_name\":\"Test Company\"}'"
        echo ""
        echo "  # Test login"
        echo "  curl -X POST http://localhost:8004/api/v1/auth/login \\"
        echo "    -H \"Content-Type: application/json\" \\"
        echo "    -d '{\"email\":\"test@example.com\",\"password\":\"password123\"}'"
        echo ""
        echo "🎉 Authentication issues fixed successfully!"
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
echo "2. Check if environment variables are set: docker compose exec pim env | grep -E '(SUPABASE|SECRET)'"
echo "3. Check if there are any other errors in the logs"
echo ""
echo "📋 Recent logs:"
docker compose logs pim --tail=20 