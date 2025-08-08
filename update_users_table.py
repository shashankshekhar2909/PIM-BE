#!/usr/bin/env python3
"""
Script to update the users table with new columns for superadmin functionality.
"""

import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.security import get_password_hash

def update_users_table():
    """Update the users table with new columns for superadmin functionality."""
    
    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    
    with engine.connect() as conn:
        try:
            # Check if new columns exist
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            print(f"Current columns: {columns}")
            
            # Add new columns to users table (without defaults first)
            new_columns = [
                ("first_name", "VARCHAR"),
                ("last_name", "VARCHAR"),
                ("is_active", "BOOLEAN"),
                ("is_blocked", "BOOLEAN"),
                ("last_login", "DATETIME"),
                ("created_at", "DATETIME"),
                ("updated_at", "DATETIME"),
                ("created_by", "INTEGER"),
                ("notes", "TEXT")
            ]
            
            for column_name, column_type in new_columns:
                if column_name not in columns:
                    print(f"Adding column {column_name}...")
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
                    print(f"✅ Added column {column_name} to users table")
                else:
                    print(f"ℹ️  Column {column_name} already exists")
            
            # Update existing users to have default values
            conn.execute(text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))
            conn.execute(text("UPDATE users SET is_blocked = 0 WHERE is_blocked IS NULL"))
            conn.execute(text("UPDATE users SET role = 'tenant_user' WHERE role IS NULL OR role = 'viewer'"))
            conn.execute(text("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
            conn.execute(text("UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))
            
            print("✅ Updated users table with default values")
            
            # Create default superadmin if none exists
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'superadmin'"))
            superadmin_count = result.fetchone()[0]
            
            if superadmin_count == 0:
                print("Creating default superadmin...")
                # Create default superadmin
                password_hash = get_password_hash("admin123")
                current_time = datetime.utcnow().isoformat()
                
                # Check if tenant_id is NOT NULL and handle accordingly
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns_info = result.fetchall()
                tenant_id_not_null = any(col[1] == 'tenant_id' and col[3] == 1 for col in columns_info)
                
                if tenant_id_not_null:
                    # Make tenant_id nullable for superadmins by creating a new table
                    print("Making tenant_id nullable for superadmins...")
                    conn.execute(text("""
                        CREATE TABLE users_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email VARCHAR UNIQUE NOT NULL,
                            password_hash VARCHAR,
                            tenant_id INTEGER,
                            role VARCHAR NOT NULL DEFAULT 'tenant_user',
                            supabase_user_id VARCHAR,
                            first_name VARCHAR,
                            last_name VARCHAR,
                            is_active BOOLEAN DEFAULT 1,
                            is_blocked BOOLEAN DEFAULT 0,
                            last_login DATETIME,
                            created_at DATETIME,
                            updated_at DATETIME,
                            created_by INTEGER,
                            notes TEXT,
                            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
                        )
                    """))
                    
                    # Copy data from old table to new table
                    conn.execute(text("""
                        INSERT INTO users_new (
                            id, email, password_hash, tenant_id, role, supabase_user_id,
                            first_name, last_name, is_active, is_blocked, last_login,
                            created_at, updated_at, created_by, notes
                        )
                        SELECT id, email, password_hash, tenant_id, role, supabase_user_id,
                               first_name, last_name, is_active, is_blocked, last_login,
                               created_at, updated_at, created_by, notes
                        FROM users
                    """))
                    
                    # Drop old table and rename new table
                    conn.execute(text("DROP TABLE users"))
                    conn.execute(text("ALTER TABLE users_new RENAME TO users"))
                    print("✅ Made tenant_id nullable")
                
                # Now create the superadmin
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
                
                print("✅ Created default superadmin user: admin@pim.com / admin123")
                print("⚠️  IMPORTANT: Please change the default password after first login!")
            else:
                print(f"ℹ️  Found {superadmin_count} existing superadmin user(s)")
            
            conn.commit()
            print("✅ Users table update completed successfully!")
            
        except Exception as e:
            print(f"❌ Error updating users table: {str(e)}")
            conn.rollback()
            raise

if __name__ == "__main__":
    try:
        update_users_table()
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        sys.exit(1) 