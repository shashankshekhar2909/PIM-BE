#!/usr/bin/env python3
"""
Script to sync users from Supabase to local database
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.models.tenant import Tenant
from app.core.supabase import get_supabase_client

def get_supabase_users():
    """Get all users from Supabase"""
    try:
        supabase = get_supabase_client()
        if not supabase:
            print("❌ Supabase client not configured")
            return []
        
        # Get users from Supabase
        response = supabase.auth.admin.list_users()
        if hasattr(response, 'users'):
            return response.users
        else:
            print("❌ Failed to get users from Supabase")
            return []
    except Exception as e:
        print(f"❌ Error getting Supabase users: {str(e)}")
        return []

def sync_user_to_local_db(supabase_user, db):
    """Sync a single user from Supabase to local database"""
    try:
        email = supabase_user.email
        supabase_user_id = supabase_user.id
        
        # Check if user already exists in local database
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            # Update supabase_user_id if not set
            if not existing_user.supabase_user_id:
                existing_user.supabase_user_id = supabase_user_id
                existing_user.updated_at = datetime.utcnow()
                db.commit()
                print(f"✅ Updated existing user: {email}")
            else:
                print(f"⏭️  User already exists: {email}")
            return existing_user
        else:
            # Create new user in local database
            # First, create a default tenant if needed
            default_tenant = db.query(Tenant).filter(Tenant.company_name == "Default Company").first()
            if not default_tenant:
                default_tenant = Tenant(company_name="Default Company")
                db.add(default_tenant)
                db.flush()
            
            # Create user
            new_user = User(
                email=email,
                supabase_user_id=supabase_user_id,
                tenant_id=default_tenant.id,
                role="tenant_user",  # Default role
                is_active=True,
                is_blocked=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"✅ Created new user: {email}")
            return new_user
            
    except Exception as e:
        print(f"❌ Error syncing user {email}: {str(e)}")
        db.rollback()
        return None

def main():
    """Main sync function"""
    print("🔄 Starting Supabase user sync...")
    
    # Initialize database connection
    try:
        engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return
    
    try:
        # Get users from Supabase
        print("🔍 Fetching users from Supabase...")
        supabase_users = get_supabase_users()
        
        if not supabase_users:
            print("❌ No users found in Supabase or failed to fetch")
            return
        
        print(f"📊 Found {len(supabase_users)} users in Supabase")
        
        # Sync each user
        synced_count = 0
        updated_count = 0
        error_count = 0
        
        for supabase_user in supabase_users:
            if supabase_user.email:
                result = sync_user_to_local_db(supabase_user, db)
                if result:
                    if result.created_at == result.updated_at:
                        synced_count += 1
                    else:
                        updated_count += 1
                else:
                    error_count += 1
        
        print(f"\n📈 Sync Summary:")
        print(f"✅ New users created: {synced_count}")
        print(f"🔄 Existing users updated: {updated_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📊 Total processed: {len(supabase_users)}")
        
    except Exception as e:
        print(f"❌ Sync failed: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 