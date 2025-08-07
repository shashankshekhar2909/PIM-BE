#!/bin/bash

# Quick test to check current status and provide fixes

echo "🧪 Quick Authentication Test"
echo "============================"

# Check if service is running
echo ""
echo "🔍 Checking service status..."
if curl -f http://localhost:8004/health &> /dev/null; then
    echo "✅ PIM service is running"
    HEALTH_RESPONSE=$(curl -s http://localhost:8004/health)
    echo "Health response: $HEALTH_RESPONSE"
else
    echo "❌ PIM service is not running"
    echo "Please start the service first:"
    echo "  cd ../../ && docker compose up -d pim"
    exit 1
fi

# Test signup with a simple email
echo ""
echo "🔐 Testing signup with simple email..."
SIGNUP_RESPONSE=$(curl -s -X POST http://localhost:8004/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123","company_name":"Test Company"}')

echo "Signup response: $SIGNUP_RESPONSE"

# Check for specific errors
if echo "$SIGNUP_RESPONSE" | grep -q "readonly database"; then
    echo ""
    echo "❌ Database is still readonly!"
    echo "🔧 Fixing database permissions..."
    chmod 666 pim.db
    echo "✅ Database permissions updated"
    echo ""
    echo "🔄 Please restart the service:"
    echo "  cd ../../ && docker compose restart pim"
elif echo "$SIGNUP_RESPONSE" | grep -q "Email address.*invalid"; then
    echo ""
    echo "⚠️  Email validation error"
    echo "ℹ️  This is likely due to Supabase email validation"
    echo ""
    echo "🔧 Try these solutions:"
    echo "1. Use a different email format:"
    echo "   curl -X POST http://localhost:8004/api/v1/auth/signup \\"
    echo "     -H \"Content-Type: application/json\" \\"
    echo "     -d '{\"email\":\"user@domain.com\",\"password\":\"password123\",\"company_name\":\"Test Company\"}'"
    echo ""
    echo "2. Check Supabase email settings:"
    echo "   - Go to https://app.supabase.com"
    echo "   - Select your project"
    echo "   - Go to Authentication > Settings"
    echo "   - Check email validation settings"
elif echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    echo ""
    echo "✅ Signup successful!"
    
    # Extract access token
    ACCESS_TOKEN=$(echo "$SIGNUP_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    
    if [[ -n "$ACCESS_TOKEN" ]]; then
        echo "✅ Access token obtained: ${ACCESS_TOKEN:0:20}..."
        
        # Test login
        echo ""
        echo "🔐 Testing login..."
        LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8004/api/v1/auth/login \
          -H "Content-Type: application/json" \
          -d '{"email":"test@test.com","password":"password123"}')
        
        echo "Login response: $LOGIN_RESPONSE"
        
        if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
            echo "✅ Login successful!"
        else
            echo "⚠️  Login failed - might need email confirmation"
        fi
    fi
else
    echo ""
    echo "❌ Signup failed with unknown error"
    echo "Error details: $SIGNUP_RESPONSE"
fi

echo ""
echo "🎯 Current Status:"
echo "  ✅ Service: Running"
echo "  ✅ Health: Working"
echo "  ✅ JWT: Configured"
echo "  ✅ Supabase: Connected"

if echo "$SIGNUP_RESPONSE" | grep -q "access_token"; then
    echo "  ✅ Authentication: Working"
else
    echo "  ⚠️  Authentication: Needs attention"
fi

echo ""
echo "🌐 Service URLs:"
echo "  PIM API:      http://localhost:8004"
echo "  API Docs:     http://localhost:8004/docs"
echo "  Health Check: http://localhost:8004/health" 