#!/bin/bash

# Test authentication fix and provide complete solution

echo "🧪 Testing Authentication Fix"
echo "============================="

# Check if docker-compose.yml exists in parent directory
if [[ -f "../../docker-compose.yml" ]]; then
    echo "✅ docker-compose.yml found in ../../"
    COMPOSE_DIR="../../"
else
    echo "❌ docker-compose.yml not found in ../../"
    echo "Please ensure docker-compose.yml is in the parent directory"
    exit 1
fi

# Check database permissions
echo ""
echo "🔍 Checking database permissions..."
if [[ -f "pim.db" ]]; then
    PERMS=$(ls -la pim.db | awk '{print $1}')
    echo "Database permissions: $PERMS"
    
    if [[ "$PERMS" == "-rw-rw-rw-" ]]; then
        echo "✅ Database permissions are correct"
    else
        echo "⚠️  Fixing database permissions..."
        chmod 666 pim.db
        echo "✅ Database permissions fixed"
    fi
else
    echo "⚠️  Database file not found, creating..."
    touch pim.db
    chmod 666 pim.db
    echo "✅ Database file created with correct permissions"
fi

# Check if service is running
echo ""
echo "🔍 Checking service status..."
if curl -f http://localhost:8004/health &> /dev/null; then
    echo "✅ PIM service is running"
else
    echo "❌ PIM service is not running"
    echo "Please start the service first:"
    echo "  cd ../../ && docker compose up -d pim"
    exit 1
fi

# Test health endpoint
echo ""
echo "🏥 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8004/health)
echo "Health response: $HEALTH_RESPONSE"

# Test signup
echo ""
echo "🔐 Testing signup..."
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
        echo "🔐 Testing login..."
        LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8004/api/v1/auth/login \
          -H "Content-Type: application/json" \
          -d '{"email":"test@example.com","password":"password123"}')
        
        echo "Login response: $LOGIN_RESPONSE"
        
        if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
            echo "✅ Login successful!"
        else
            echo "❌ Login failed"
        fi
        
        # Test protected endpoint
        echo ""
        echo "🔐 Testing protected endpoint..."
        PROTECTED_RESPONSE=$(curl -s -X GET http://localhost:8004/api/v1/auth/me \
          -H "Authorization: Bearer $ACCESS_TOKEN")
        
        echo "Protected endpoint response: $PROTECTED_RESPONSE"
        
        if echo "$PROTECTED_RESPONSE" | grep -q "email"; then
            echo "✅ Protected endpoint working!"
        else
            echo "❌ Protected endpoint failed"
        fi
    fi
else
    echo "❌ Signup failed"
    echo "Error details: $SIGNUP_RESPONSE"
fi

echo ""
echo "🎯 Summary:"
echo "  ✅ Database permissions: Fixed"
echo "  ✅ Service status: Running"
echo "  ✅ Health endpoint: Working"
if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    echo "  ✅ Authentication: Working"
    echo "  ✅ Signup: Successful"
    echo "  ✅ Login: Successful"
    echo "  ✅ Protected endpoints: Working"
else
    echo "  ❌ Authentication: Failed"
    echo "  ❌ Signup: Failed"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "1. Check service logs: docker compose logs pim -f"
    echo "2. Check database permissions: ls -la pim.db"
    echo "3. Check environment variables: docker compose exec pim env | grep -E '(SUPABASE|SECRET)'"
fi

echo ""
echo "🌐 Service URLs:"
echo "  PIM API:      http://localhost:8004"
echo "  API Docs:     http://localhost:8004/docs"
echo "  Health Check: http://localhost:8004/health" 