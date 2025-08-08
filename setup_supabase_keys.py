#!/usr/bin/env python3
"""
Script to help set up Supabase keys for the PIM system.
"""

import os
import sys

def check_supabase_config():
    """Check current Supabase configuration."""
    print("🔍 Checking current Supabase configuration...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return False
    
    # Read current .env file
    with open('.env', 'r') as f:
        env_content = f.read()
    
    # Check for Supabase keys
    lines = env_content.split('\n')
    supabase_url = None
    supabase_anon_key = None
    supabase_service_key = None
    
    for line in lines:
        if line.startswith('SUPABASE_URL='):
            supabase_url = line.split('=', 1)[1].strip()
        elif line.startswith('SUPABASE_ANON_KEY='):
            supabase_anon_key = line.split('=', 1)[1].strip()
        elif line.startswith('SUPABASE_SERVICE_ROLE_KEY='):
            supabase_service_key = line.split('=', 1)[1].strip()
    
    print(f"📋 Current configuration:")
    print(f"   SUPABASE_URL: {'✅ Set' if supabase_url and supabase_url != 'your-url-here' else '❌ Not set'}")
    print(f"   SUPABASE_ANON_KEY: {'✅ Set' if supabase_anon_key and supabase_anon_key != 'your-anon-key-here' else '❌ Not set'}")
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if supabase_service_key and supabase_service_key != 'your-service-role-key-here' else '❌ Not set'}")
    
    if not supabase_service_key or supabase_service_key == 'your-service-role-key-here':
        print("\n⚠️  SUPABASE_SERVICE_ROLE_KEY is not set!")
        print("\n📝 To get your service role key:")
        print("1. Go to your Supabase dashboard: https://app.supabase.com")
        print("2. Select your project")
        print("3. Go to Settings > API")
        print("4. Copy the 'service_role' key (not the anon key)")
        print("5. Update your .env file with the service role key")
        return False
    
    return True

def update_service_role_key():
    """Update the service role key in .env file."""
    print("\n🔧 Updating service role key...")
    
    # Get the new service role key from user
    new_service_key = input("Enter your Supabase service role key: ").strip()
    
    if not new_service_key:
        print("❌ Service role key cannot be empty!")
        return False
    
    # Read current .env file
    with open('.env', 'r') as f:
        env_content = f.read()
    
    # Update the service role key
    lines = env_content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('SUPABASE_SERVICE_ROLE_KEY='):
            updated_lines.append(f'SUPABASE_SERVICE_ROLE_KEY={new_service_key}')
        else:
            updated_lines.append(line)
    
    # Write back to .env file
    with open('.env', 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ Service role key updated successfully!")
    return True

def test_supabase_connection():
    """Test Supabase connection with current configuration."""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        # Import after potential config update
        from app.core.supabase import get_supabase_admin_client
        
        supabase_admin = get_supabase_admin_client()
        if not supabase_admin:
            print("❌ Failed to get Supabase admin client")
            return False
        
        # Try to list users to test connection
        users = supabase_admin.auth.admin.list_users()
        print(f"✅ Supabase connection successful! Found {len(users.users)} users.")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Supabase Configuration Setup")
    print("=" * 40)
    
    if not check_supabase_config():
        print("\n❌ Supabase configuration is incomplete!")
        
        response = input("\nWould you like to update the service role key now? (y/n): ").strip().lower()
        if response == 'y':
            if update_service_role_key():
                if test_supabase_connection():
                    print("\n🎉 Supabase configuration is now complete!")
                else:
                    print("\n❌ Connection test failed. Please check your keys.")
            else:
                print("\n❌ Failed to update service role key.")
        else:
            print("\n⚠️  Please update your .env file manually and run this script again.")
    else:
        print("\n✅ Supabase configuration looks good!")
        if test_supabase_connection():
            print("\n🎉 Everything is set up correctly!")
        else:
            print("\n❌ Connection test failed. Please check your configuration.") 