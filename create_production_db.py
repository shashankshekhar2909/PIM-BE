#!/usr/bin/env python3
"""
Production Database Initialization Script
Creates a fresh SQLite database with admin user for production deployment
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'app'))

from app.core.dependencies import engine
from app.models import *
from app.models.base import Base
from app.core.migrations import run_migrations
from app.core.security import get_password_hash
from sqlalchemy import text

def ensure_directory_exists(path):
    """Ensure directory exists and is writable"""
    try:
        os.makedirs(path, exist_ok=True)
        os.chmod(path, 0o777)  # Make directory writable by all
        return True
    except Exception as e:
        logger.error(f"Failed to create/chmod directory {path}: {e}")
        return False

def create_production_database():
    """Create a fresh production database with admin user"""
    
    # Ensure data directory exists with absolute path
    data_dir = os.path.join(PROJECT_ROOT, "data")
    if not ensure_directory_exists(data_dir):
        logger.error("Failed to create/setup data directory")
        return False
    
    db_path = os.path.join(data_dir, "pim.db")
    logger.info(f"Using database path: {db_path}")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        logger.info(f"Removing existing database: {db_path}")
        try:
            os.remove(db_path)
            logger.info("✅ Existing database removed successfully")
        except PermissionError:
            logger.warning("⚠️  Cannot remove existing database due to permissions - will overwrite")
            try:
                os.chmod(db_path, 0o666)
                logger.info("✅ Made existing database writable")
            except Exception as e:
                logger.warning(f"⚠️  Could not change permissions: {e}")
        except Exception as e:
            logger.warning(f"⚠️  Could not remove existing database: {e}")
            logger.info("ℹ️  Will attempt to overwrite existing database")
    
    logger.info("Creating fresh production database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Enable foreign key support for SQLite
        if "sqlite" in str(engine.url):
            with engine.connect() as conn:
                conn.execute(text("PRAGMA foreign_keys=ON"))
                logger.info("✅ Foreign key support enabled")
        
        # Run migrations
        run_migrations()
        logger.info("✅ Migrations completed successfully")
        
        # Verify admin user was created
        with engine.connect() as conn:
            result = conn.execute(text("SELECT email, role FROM users WHERE role = 'superadmin'"))
            admin_users = result.fetchall()
            
            if admin_users:
                logger.info("✅ Admin users found:")
                for user in admin_users:
                    logger.info(f"   - {user[0]} (Role: {user[1]})")
            else:
                logger.warning("⚠️  No admin users found - creating default admin...")
                create_default_admin(conn)
        
        # Ensure the database file exists and set permissions
        if os.path.exists(db_path):
            try:
                os.chmod(db_path, 0o666)  # Make readable/writable by all
                logger.info(f"✅ Database permissions set: {db_path}")
                logger.info(f"✅ Database size: {os.path.getsize(db_path) / 1024:.1f} KB")
                
                # Double-check the file is actually there and readable
                with open(db_path, 'rb') as f:
                    f.seek(0, 2)  # Seek to end
                    size = f.tell()
                    logger.info(f"✅ Verified database is readable, size: {size / 1024:.1f} KB")
                
                return True
            except Exception as e:
                logger.error(f"❌ Error verifying database: {e}")
                return False
        else:
            logger.error(f"❌ Database file not found at: {db_path}")
            # List directory contents for debugging
            try:
                logger.info("Directory contents:")
                for item in os.listdir(data_dir):
                    logger.info(f"  - {item}")
            except Exception as e:
                logger.error(f"Could not list directory contents: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error creating production database: {e}")
        return False

def create_default_admin(conn):
    """Create default admin user if none exists"""
    try:
        password_hash = get_password_hash("admin123")
        current_time = datetime.now(timezone.utc).isoformat()
        
        conn.execute(text("""
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
        
        logger.info("✅ Created default superadmin user: admin@pim.com / admin123")
        logger.info("⚠️  IMPORTANT: Please change the default password after first login!")
        
        conn.commit()
        
    except Exception as e:
        logger.error(f"❌ Error creating default admin user: {e}")

def main():
    """Main function"""
    print("🚀 Production Database Initialization")
    print("=" * 50)
    
    if create_production_database():
        print("\n🎉 SUCCESS: Production database created!")
        print("\n📋 Database Details:")
        db_path = os.path.join(PROJECT_ROOT, "data", "pim.db")
        print(f"   Location: {db_path}")
        print(f"   Admin User: admin@pim.com")
        print(f"   Password: admin123")
        print(f"   Role: superadmin")
        print("\n⚠️  IMPORTANT: Change the default admin password after first login!")
        print("\n🚀 Ready for production deployment!")
    else:
        print("\n❌ FAILED: Could not create production database")
        sys.exit(1)

if __name__ == "__main__":
    main()