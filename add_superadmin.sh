#!/bin/bash

# Script to add a default superadmin user to the PIM system

echo "🚀 Adding default superadmin to PIM system..."
echo ""

# Check if Python script exists
if [ ! -f "create_default_superadmin.py" ]; then
    echo "❌ Error: create_default_superadmin.py not found!"
    exit 1
fi

# Run the superadmin creation script
echo "📝 Creating default superadmin..."
python3 create_default_superadmin.py --action create

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Superadmin creation completed!"
    echo ""
    echo "🔑 Default credentials:"
    echo "   Email: admin@pim.com"
    echo "   Password: admin123"
    echo ""
    echo "⚠️  IMPORTANT: Please change the default password after first login!"
    echo ""
    echo "🌐 You can now login to the system with these credentials."
else
    echo ""
    echo "❌ Failed to create superadmin!"
    exit 1
fi 