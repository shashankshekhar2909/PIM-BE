#!/bin/bash

# Create .env file with existing Supabase configuration

echo "🔧 Creating .env file with existing configuration"
echo "================================================"

# Check if docker-compose.yml exists in parent directory
if [[ -f "../../docker-compose.yml" ]]; then
    echo "✅ docker-compose.yml found in ../../"
    COMPOSE_DIR="../../"
else
    echo "❌ docker-compose.yml not found in ../../"
    echo "Please ensure docker-compose.yml is in the parent directory"
    exit 1
fi

# Check if .env file already exists
if [[ -f "$COMPOSE_DIR/.env" ]]; then
    echo "⚠️  .env file already exists in $COMPOSE_DIR"
    echo "Current contents:"
    cat "$COMPOSE_DIR/.env"
    echo ""
    echo "Do you want to overwrite it? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted. Using existing .env file."
        exit 0
    fi
fi

echo "Creating .env file in $COMPOSE_DIR..."

# Create .env file with existing configuration
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
echo "📋 .env file contents:"
cat "$COMPOSE_DIR/.env"
echo ""
echo "⚠️  IMPORTANT: Please update the following values:"
echo "   1. SUPABASE_SERVICE_ROLE_KEY - Get from Supabase dashboard"
echo "   2. SECRET_KEY - Change to a secure random string"
echo ""
echo "🔍 To get your SUPABASE_SERVICE_ROLE_KEY:"
echo "   1. Go to https://app.supabase.com"
echo "   2. Select your project: https://hhxuxthwvpeplhtprnhf.supabase.co"
echo "   3. Navigate to Settings > API"
echo "   4. Copy the 'service_role' key (NOT the anon key)"
echo ""
echo "🎯 Next steps:"
echo "   1. Update the .env file with your actual values"
echo "   2. Run: ./fix-auth-issues.sh"
echo ""
echo "✅ .env file created successfully!" 