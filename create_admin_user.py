#!/usr/bin/env python3
"""
Quick Admin User Creation Script
Creates an admin user for troubleshooting login issues
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.dependencies import engine
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

def create_admin_user():
    """Create admin user manually"""
    print("🔧 Creating admin user manually...")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@pim.com").first()
        
        if existing_admin:
            print(f"✅ Admin user already exists: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            print(f"   Active: {existing_admin.is_active}")
            print(f"   Blocked: {existing_admin.is_blocked}")
            
            # Update password to ensure it's correct
            existing_admin.password_hash = get_password_hash("admin123")
            existing_admin.is_active = True
            existing_admin.is_blocked = False
            db.commit()
            print("✅ Admin user password updated to: admin123")
            
        else:
            # Create new admin user
            admin_user = User(
                email="admin@pim.com",
                password_hash=get_password_hash("admin123"),
                role="superadmin",
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_blocked=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print("✅ Created new admin user:")
            print(f"   Email: {admin_user.email}")
            print(f"   Password: admin123")
            print(f"   Role: {admin_user.role}")
            print(f"   ID: {admin_user.id}")
        
        # Verify user can be found
        admin = db.query(User).filter(User.email == "admin@pim.com").first()
        if admin:
            print(f"✅ Verification: Admin user found in database")
            print(f"   Password hash length: {len(admin.password_hash)}")
        else:
            print("❌ Verification failed: Admin user not found")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    if create_admin_user():
        print("\n🎉 Admin user creation completed successfully!")
        print("   Login with: admin@pim.com / admin123")
    else:
        print("\n❌ Admin user creation failed!")
        sys.exit(1)
