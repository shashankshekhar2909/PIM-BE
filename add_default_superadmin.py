#!/usr/bin/env python3
"""
Script to add a default superadmin user with local authentication.
This superadmin will use local password authentication while regular users use Supabase.
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash

def add_default_superadmin():
    """Add default superadmin user with local authentication."""
    
    print("🚀 Adding default superadmin user with local authentication...")
    
    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if superadmin already exists
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE email = 'admin@pim.com'"))
        existing_count = result.scalar()
        
        if existing_count > 0:
            print("ℹ️  Superadmin already exists. Updating...")
            
            # Update existing superadmin
            password_hash = get_password_hash("admin123")
            current_time = datetime.utcnow().isoformat()
            
            db.execute(text("""
                UPDATE users SET 
                    password_hash = :password_hash,
                    role = 'superadmin',
                    first_name = 'System',
                    last_name = 'Administrator',
                    is_active = 1,
                    is_blocked = 0,
                    updated_at = :updated_at,
                    notes = 'Default superadmin user with local authentication'
                WHERE email = 'admin@pim.com'
            """), {
                "password_hash": password_hash,
                "updated_at": current_time
            })
            
            print("✅ Updated existing superadmin user")
        else:
            print("📝 Creating new superadmin user...")
            
            # Create new superadmin
            password_hash = get_password_hash("admin123")
            current_time = datetime.utcnow().isoformat()
            
            db.execute(text("""
                INSERT INTO users (
                    email, password_hash, role, first_name, last_name, 
                    is_active, is_blocked, created_at, updated_at, notes
                ) VALUES (
                    'admin@pim.com', :password_hash, 'superadmin', 'System', 'Administrator',
                    1, 0, :created_at, :updated_at, 'Default superadmin user with local authentication'
                )
            """), {
                "password_hash": password_hash,
                "created_at": current_time,
                "updated_at": current_time
            })
            
            print("✅ Created new superadmin user")
        
        db.commit()
        
        # Verify the superadmin
        result = db.execute(text("""
            SELECT id, email, role, first_name, last_name, is_active, is_blocked, created_at
            FROM users WHERE email = 'admin@pim.com'
        """))
        
        superadmin = result.fetchone()
        
        if superadmin:
            print("\n🎉 Superadmin setup completed successfully!")
            print(f"\n📋 User Details:")
            print(f"   ID: {superadmin[0]}")
            print(f"   Email: {superadmin[1]}")
            print(f"   Role: {superadmin[2]}")
            print(f"   Name: {superadmin[3]} {superadmin[4]}")
            print(f"   Active: {superadmin[5]}")
            print(f"   Blocked: {superadmin[6]}")
            print(f"   Created: {superadmin[7]}")
            
            print(f"\n🔑 Login Credentials:")
            print(f"   Email: admin@pim.com")
            print(f"   Password: admin123")
            print(f"   Authentication: Local (bcrypt)")
            
            print(f"\n⚠️  IMPORTANT:")
            print(f"   - This superadmin uses LOCAL authentication (not Supabase)")
            print(f"   - Regular users will still use Supabase authentication")
            print(f"   - Please change the default password after first login!")
            
            return True
        else:
            print("❌ Failed to verify superadmin creation")
            return False
        
    except Exception as e:
        print(f"❌ Error creating superadmin: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    try:
        if add_default_superadmin():
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        sys.exit(1) 