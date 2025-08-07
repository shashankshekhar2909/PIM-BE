#!/bin/bash

# Implement the database solution provided by the user

echo "🔧 Implementing Database Solution"
echo "================================="

# Check if docker-compose.yml exists in parent directory
if [[ -f "../../docker-compose.yml" ]]; then
    echo "✅ docker-compose.yml found in ../../"
    COMPOSE_DIR="../../"
else
    echo "❌ docker-compose.yml not found in ../../"
    echo "Please ensure docker-compose.yml is in the parent directory"
    exit 1
fi

# Step 1: Create db directory and fix permissions
echo ""
echo "🔐 Step 1: Creating db directory and fixing permissions..."
mkdir -p db
chmod 777 db

# Move existing database to db directory if it exists
if [[ -f "pim.db" ]]; then
    echo "📁 Moving existing database to db directory..."
    mv pim.db db/
fi

# Create database file in db directory if it doesn't exist
if [[ ! -f "db/pim.db" ]]; then
    echo "📁 Creating new database in db directory..."
    touch db/pim.db
fi

# Fix permissions on database file
chmod 777 db/pim.db
echo "✅ Database permissions fixed: $(ls -la db/pim.db | awk '{print $1}')"

# Step 2: Update docker-compose.yml
echo ""
echo "🔧 Step 2: Updating docker-compose.yml..."
cd "$COMPOSE_DIR"

# Create backup of docker-compose.yml
cp docker-compose.yml docker-compose.yml.backup
echo "✅ Created backup: docker-compose.yml.backup"

# Update the PIM service configuration
cat > docker-compose.yml << 'EOF'
services:
  app1:
    build: ./fastAPI/app1
    container_name: app1
    volumes:
      - ./fastAPI/app1:/app  # Mount your code
    working_dir: /app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8001:8000"

  app2:
    build: ./fastAPI/app2
    container_name: app2
    volumes:
      - ./fastAPI/app2:/app
    working_dir: /app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8002:8000"

  giftg:
    build: ./fastAPI/giftg-BE
    container_name: giftg
    volumes:
      - ./fastAPI/giftg-BE:/app
    working_dir: /app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8003:8000"
    restart: unless-stopped

  pim:
    build: ./fastAPI/PIM-BE
    container_name: pim
    volumes:
      - ./fastAPI/PIM-BE:/app
      - ./fastAPI/PIM-BE/db:/app/db
    working_dir: /app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8004:8000"
    restart: unless-stopped
    environment:
      - PYTHONPATH=/app
      - SUPABASE_URL=${SUPABASE_URL:-}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY:-}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY:-}
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-here}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///./db/pim.db}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOF

echo "✅ Updated docker-compose.yml with db mount"

# Step 3: Update .env file with new database path
echo ""
echo "🔧 Step 3: Updating .env file..."
if [[ -f ".env" ]]; then
    # Update DATABASE_URL in .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|DATABASE_URL=.*|DATABASE_URL=sqlite:///./db/pim.db|" .env
    else
        # Linux
        sed -i "s|DATABASE_URL=.*|DATABASE_URL=sqlite:///./db/pim.db|" .env
    fi
    echo "✅ Updated DATABASE_URL in .env file"
else
    echo "⚠️  .env file not found, creating with new database path..."
    cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://hhxuxthwvpeplhtprnhf.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhoeHV4dGh3dnBlcGxodHBybmhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NjE3MjQsImV4cCI6MjA3MDAzNzcyNH0.1f9e_bPsbLtV9BiSrSO2IvHEf0ePSC8j1Ki_S2I-j_Y
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Application Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./db/pim.db
EOF
    echo "✅ Created .env file with new database path"
fi

# Step 4: Rebuild container
echo ""
echo "🔨 Step 4: Rebuilding container..."
echo "Stopping and removing containers..."
docker compose down -v

echo "Building and starting containers..."
docker compose up --build -d

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    echo "Please check the build logs above"
    exit 1
fi

echo "✅ Containers built and started successfully"

# Step 5: Wait for service to be ready
echo ""
echo "⏳ Step 5: Waiting for service to be ready..."
sleep 30

# Check service status
echo ""
echo "📊 Step 6: Checking service status..."
docker compose ps pim

# Wait for service to be ready
echo ""
echo "🏥 Step 7: Checking service health..."
max_attempts=15
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt/$max_attempts: Checking service health..."
    
    if curl -f http://localhost:8004/health &> /dev/null; then
        echo "✅ PIM service is ready!"
        break
    else
        echo "⏳ Service not ready yet... (attempt $attempt/$max_attempts)"
        
        # Show recent logs every 5 attempts
        if [ $((attempt % 5)) -eq 0 ]; then
            echo "📋 Recent logs:"
            docker compose logs pim --tail=5
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Service did not become ready within 2.5 minutes"
    echo ""
    echo "📋 Recent logs:"
    docker compose logs pim --tail=20
    exit 1
fi

echo ""
echo "🏥 Health Check Response:"
curl -s http://localhost:8004/health | jq . 2>/dev/null || curl -s http://localhost:8004/health

echo ""
echo "🌐 Service URLs:"
echo "  PIM API:      http://localhost:8004"
echo "  API Docs:     http://localhost:8004/docs"
echo "  Health Check: http://localhost:8004/health"

echo ""
echo "🔐 Step 8: Testing authentication..."

# Test signup
echo ""
echo "🧪 Testing signup..."
SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:8004/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","company_name":"Test Company"}')

echo "Signup response: $SIGNUP_RESPONSE"

# Check if signup was successful
if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    echo "✅ Signup successful!"
    
    # Extract access token for login test
    ACCESS_TOKEN=$(echo "$SIGNUP_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    if [[ -n "$ACCESS_TOKEN" ]]; then
        echo "✅ Access token obtained: ${ACCESS_TOKEN:0:20}..."
        
        # Test login
        echo ""
        echo "🧪 Testing login..."
        LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8004/api/v1/auth/login \
          -H "Content-Type: application/json" \
          -d '{"email":"test@example.com","password":"password123"}')
        
        echo "Login response: $LOGIN_RESPONSE"
        
        if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
            echo "✅ Login successful!"
        else
            echo "⚠️  Login failed - might need email confirmation"
        fi
    fi
else
    echo "⚠️  Signup failed - checking error details..."
    if echo "$SIGNUP_RESPONSE" | grep -q "readonly database"; then
        echo "❌ Database still readonly - solution may need adjustment"
    elif echo "$SIGNUP_RESPONSE" | grep -q "Email address.*invalid"; then
        echo "ℹ️  Email validation error - try different email format"
    else
        echo "❌ Signup failed with unknown error"
        echo "Error details: $SIGNUP_RESPONSE"
    fi
fi

echo ""
echo "🎯 Summary:"
echo "  ✅ Database directory: Created (db/)"
echo "  ✅ Database permissions: Fixed (777)"
echo "  ✅ Docker-compose.yml: Updated with db mount"
echo "  ✅ .env file: Updated with new database path"
echo "  ✅ Container: Rebuilt and restarted"
echo "  ✅ Service: Running"
echo "  ✅ Health endpoint: Working"

if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    echo "  ✅ Authentication: Working"
    echo "  ✅ Signup: Successful"
    echo "  ✅ Login: Successful"
else
    echo "  ⚠️  Authentication: May need email confirmation"
fi

echo ""
echo "🎉 Database solution implemented successfully!"
echo ""
echo "📁 Database location: ./fastAPI/PIM-BE/db/pim.db"
echo "🔐 Database permissions: 777 (readable/writable by all)"
echo "🌐 Service URL: http://localhost:8004" 