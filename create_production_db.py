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

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.dependencies import engine
from app.models import *
from app.models.base import Base
from app.core.migrations import run_migrations
from app.core.security import get_password_hash
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_production_database():
    """Create a fresh production database with admin user"""
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "pim.db"
    
    # Remove existing database if it exists
    if db_path.exists():
        logger.info(f"Removing existing database: {db_path}")
        db_path.unlink()
    
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
        
        # Set proper permissions
        os.chmod(db_path, 0o644)
        logger.info(f"✅ Database created successfully: {db_path}")
        logger.info(f"✅ Database size: {db_path.stat().st_size / 1024:.1f} KB")
        
        return True
        
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
        print(f"   Location: data/pim.db")
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
