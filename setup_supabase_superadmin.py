#!/usr/bin/env python3
"""
Script to set up superadmin user in Supabase and local database.
This script will:
1. Create the superadmin user in Supabase
2. Create the superadmin user in our local database
3. Link them together
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.supabase import get_supabase_admin_client
from app.models.user import User
from app.models.tenant import Tenant

def setup_supabase_superadmin():
    """Set up superadmin user in Supabase and local database."""
    
    print("🚀 Setting up superadmin user in Supabase and local database...")
    
    # Get Supabase admin client
    supabase_admin = get_supabase_admin_client()
    if not supabase_admin:
        print("❌ Failed to get Supabase admin client. Please check your Supabase configuration.")
        return False
    
    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Step 1: Create superadmin user in Supabase
        print("📝 Creating superadmin user in Supabase...")
        
        supabase_user_data = {
            "email": "admin@pim.com",
            "password": "admin123",
            "email_confirm": True,
            "user_metadata": {
                "first_name": "System",
                "last_name": "Administrator",
                "role": "superadmin"
            }
        }
        
        try:
            # Create user in Supabase
            supabase_response = supabase_admin.auth.admin.create_user(supabase_user_data)
            
            if not supabase_response.user:
                print("❌ Failed to create user in Supabase")
                return False
            
            supabase_user_id = supabase_response.user.id
            print(f"✅ Created user in Supabase with ID: {supabase_user_id}")
            
        except Exception as e:
            print(f"❌ Error creating user in Supabase: {str(e)}")
            # Check if user already exists
            try:
                # Try to get existing user
                existing_users = supabase_admin.auth.admin.list_users()
                for user in existing_users.users:
                    if user.email == "admin@pim.com":
                        supabase_user_id = user.id
                        print(f"✅ Found existing user in Supabase with ID: {supabase_user_id}")
                        break
                else:
                    print("❌ User not found in Supabase and creation failed")
                    return False
            except Exception as e2:
                print(f"❌ Error checking existing users: {str(e2)}")
                return False
        
        # Step 2: Create superadmin user in local database
        print("📝 Creating superadmin user in local database...")
        
        # Check if user already exists in local database
        existing_user = db.query(User).filter(User.email == "admin@pim.com").first()
        
        if existing_user:
            print("ℹ️  User already exists in local database, updating...")
            existing_user.supabase_user_id = supabase_user_id
            existing_user.role = "superadmin"
            existing_user.first_name = "System"
            existing_user.last_name = "Administrator"
            existing_user.is_active = True
            existing_user.is_blocked = False
            existing_user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_user)
            print("✅ Updated existing user in local database")
            user = existing_user
        else:
            # Create new user in local database
            user = User(
                email="admin@pim.com",
                supabase_user_id=supabase_user_id,
                role="superadmin",
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_blocked=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                notes="Superadmin user created via Supabase setup"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("✅ Created new user in local database")
        
        # Step 3: Verify the setup
        print("🔍 Verifying setup...")
        
        # Check Supabase
        try:
            supabase_user = supabase_admin.auth.admin.get_user_by_id(supabase_user_id)
            if supabase_user.user:
                print(f"✅ Supabase user verified: {supabase_user.user.email}")
            else:
                print("❌ Failed to verify Supabase user")
        except Exception as e:
            print(f"⚠️  Warning: Could not verify Supabase user: {str(e)}")
        
        # Check local database
        local_user = db.query(User).filter(User.email == "admin@pim.com").first()
        if local_user:
            print(f"✅ Local user verified: {local_user.email} (ID: {local_user.id})")
            print(f"   Role: {local_user.role}")
            print(f"   Supabase ID: {local_user.supabase_user_id}")
            print(f"   Active: {local_user.is_active}")
            print(f"   Blocked: {local_user.is_blocked}")
        else:
            print("❌ Failed to verify local user")
            return False
        
        print("\n🎉 Superadmin setup completed successfully!")
        print("\n🔑 Login Credentials:")
        print("   Email: admin@pim.com")
        print("   Password: admin123")
        print("   Role: superadmin")
        print("\n⚠️  IMPORTANT: Please change the default password after first login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up superadmin: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def test_supabase_connection():
    """Test Supabase connection and configuration."""
    print("🔍 Testing Supabase connection...")
    
    try:
        supabase_admin = get_supabase_admin_client()
        if not supabase_admin:
            print("❌ Failed to get Supabase admin client")
            return False
        
        # Try to list users to test connection
        users = supabase_admin.auth.admin.list_users()
        print(f"✅ Supabase connection successful. Found {len(users.users)} users.")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up superadmin user in Supabase and local database")
    parser.add_argument("--test-connection", action="store_true", help="Test Supabase connection only")
    
    args = parser.parse_args()
    
    if args.test_connection:
        test_supabase_connection()
    else:
        if not test_supabase_connection():
            print("❌ Supabase connection failed. Please check your configuration.")
            sys.exit(1)
        
        if setup_supabase_superadmin():
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed!")
            sys.exit(1) 