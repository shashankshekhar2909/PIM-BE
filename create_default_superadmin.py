#!/usr/bin/env python3
"""
Script to create a default superadmin user for the PIM system.
This script will create a superadmin user if one doesn't already exist.
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

def create_default_superadmin():
    """Create a default superadmin user if one doesn't exist."""
    
    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if a superadmin already exists using raw SQL
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE role = 'superadmin'"))
        superadmin_count = result.scalar()
        
        if superadmin_count > 0:
            # Get existing superadmin details
            result = db.execute(text("SELECT id, email, first_name, last_name, role, is_active, is_blocked FROM users WHERE role = 'superadmin' LIMIT 1"))
            existing_superadmin = result.fetchone()
            
            print(f"✅ Superadmin already exists: {existing_superadmin[1]}")
            print(f"   Name: {existing_superadmin[2]} {existing_superadmin[3]}")
            print(f"   Role: {existing_superadmin[4]}")
            print(f"   Active: {existing_superadmin[5]}")
            print(f"   Blocked: {existing_superadmin[6]}")
            return existing_superadmin
        
        # Create default superadmin
        password_hash = get_password_hash("admin123")
        current_time = datetime.utcnow().isoformat()
        
        result = db.execute(text("""
            INSERT INTO users (
                email, password_hash, role, first_name, last_name, 
                is_active, is_blocked, created_at, updated_at, notes
            ) VALUES (
                'admin@pim.com', :password_hash, 'superadmin', 'System', 'Administrator',
                1, 0, :created_at, :updated_at, 'Default superadmin user created by system'
            )
        """), {
            "password_hash": password_hash,
            "created_at": current_time,
            "updated_at": current_time
        })
        
        db.commit()
        
        # Get the created superadmin
        result = db.execute(text("SELECT id, email, first_name, last_name, role FROM users WHERE email = 'admin@pim.com'"))
        new_superadmin = result.fetchone()
        
        print("✅ Default superadmin created successfully!")
        print(f"   Email: {new_superadmin[1]}")
        print(f"   Password: admin123")
        print(f"   Name: {new_superadmin[2]} {new_superadmin[3]}")
        print(f"   Role: {new_superadmin[4]}")
        print(f"   ID: {new_superadmin[0]}")
        print("\n⚠️  IMPORTANT: Please change the default password after first login!")
        
        return new_superadmin
        
    except Exception as e:
        print(f"❌ Error creating superadmin: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def create_custom_superadmin(email, password, first_name="System", last_name="Administrator"):
    """Create a custom superadmin user with specified credentials."""
    
    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user already exists
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE email = :email"), {"email": email})
        user_exists = result.scalar() > 0
        
        if user_exists:
            print(f"❌ User with email {email} already exists!")
            return None
        
        # Create custom superadmin
        password_hash = get_password_hash(password)
        current_time = datetime.utcnow().isoformat()
        
        result = db.execute(text("""
            INSERT INTO users (
                email, password_hash, role, first_name, last_name, 
                is_active, is_blocked, created_at, updated_at, notes
            ) VALUES (
                :email, :password_hash, 'superadmin', :first_name, :last_name,
                1, 0, :created_at, :updated_at, 'Custom superadmin user created by script'
            )
        """), {
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "created_at": current_time,
            "updated_at": current_time
        })
        
        db.commit()
        
        # Get the created superadmin
        result = db.execute(text("SELECT id, email, first_name, last_name, role FROM users WHERE email = :email"), {"email": email})
        new_superadmin = result.fetchone()
        
        print("✅ Custom superadmin created successfully!")
        print(f"   Email: {new_superadmin[1]}")
        print(f"   Name: {new_superadmin[2]} {new_superadmin[3]}")
        print(f"   Role: {new_superadmin[4]}")
        print(f"   ID: {new_superadmin[0]}")
        
        return new_superadmin
        
    except Exception as e:
        print(f"❌ Error creating custom superadmin: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def list_superadmins():
    """List all superadmin users in the system."""
    
    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        result = db.execute(text("""
            SELECT id, email, first_name, last_name, role, is_active, is_blocked, 
                   created_at, last_login, notes
            FROM users 
            WHERE role = 'superadmin'
            ORDER BY created_at DESC
        """))
        
        superadmins = result.fetchall()
        
        if not superadmins:
            print("ℹ️  No superadmin users found in the system.")
            return []
        
        print(f"📋 Found {len(superadmins)} superadmin user(s):")
        print("-" * 80)
        
        for admin in superadmins:
            print(f"ID: {admin[0]}")
            print(f"Email: {admin[1]}")
            print(f"Name: {admin[2]} {admin[3]}")
            print(f"Role: {admin[4]}")
            print(f"Active: {admin[5]}")
            print(f"Blocked: {admin[6]}")
            print(f"Created: {admin[7]}")
            print(f"Last Login: {admin[8] or 'Never'}")
            if admin[9]:
                print(f"Notes: {admin[9]}")
            print("-" * 80)
        
        return superadmins
        
    except Exception as e:
        print(f"❌ Error listing superadmins: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create or manage superadmin users")
    parser.add_argument("--action", choices=["create", "create-custom", "list"], 
                       default="create", help="Action to perform")
    parser.add_argument("--email", help="Email for custom superadmin")
    parser.add_argument("--password", help="Password for custom superadmin")
    parser.add_argument("--first-name", default="System", help="First name for custom superadmin")
    parser.add_argument("--last-name", default="Administrator", help="Last name for custom superadmin")
    
    args = parser.parse_args()
    
    try:
        if args.action == "create":
            create_default_superadmin()
        elif args.action == "create-custom":
            if not args.email or not args.password:
                print("❌ Email and password are required for custom superadmin creation!")
                sys.exit(1)
            create_custom_superadmin(args.email, args.password, args.first_name, args.last_name)
        elif args.action == "list":
            list_superadmins()
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        sys.exit(1) 