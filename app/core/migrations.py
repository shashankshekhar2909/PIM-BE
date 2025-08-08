import logging
from sqlalchemy import text, create_engine
from app.core.config import settings
from app.core.security import get_password_hash
from datetime import datetime

def run_migrations():
    """Run database migrations."""
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    
    with engine.connect() as conn:
        # Check if migrations have been run
        try:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='field_mappings'"))
            if result.fetchone():
                logging.info("Migrations already applied")
                return
        except Exception:
            pass
        
        logging.info("Running migrations...")
        
        # Create product_additional_data table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS product_additional_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    field_name VARCHAR NOT NULL,
                    field_label VARCHAR NOT NULL,
                    field_value TEXT,
                    field_type VARCHAR NOT NULL DEFAULT 'string',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
                )
            """))
            logging.info("Created product_additional_data table")
        except Exception as e:
            logging.error(f"Error creating product_additional_data table: {e}")
        
        # Create field_mappings table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS field_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    original_field_name VARCHAR NOT NULL,
                    normalized_field_name VARCHAR NOT NULL,
                    field_label VARCHAR NOT NULL,
                    field_type VARCHAR NOT NULL DEFAULT 'string',
                    is_standard_field INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
                )
            """))
            logging.info("Created field_mappings table")
        except Exception as e:
            logging.error(f"Error creating field_mappings table: {e}")
        
        # Create field_configurations table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS field_configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id INTEGER NOT NULL,
                    field_name VARCHAR NOT NULL,
                    field_label VARCHAR NOT NULL,
                    field_type VARCHAR NOT NULL DEFAULT 'string',
                    is_searchable BOOLEAN DEFAULT 0,
                    is_editable BOOLEAN DEFAULT 1,
                    is_primary BOOLEAN DEFAULT 0,
                    is_secondary BOOLEAN DEFAULT 0,
                    display_order INTEGER DEFAULT 0,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
                )
            """))
            logging.info("Created field_configurations table")
        except Exception as e:
            logging.error(f"Error creating field_configurations table: {e}")
        
        # Create audit_logs table
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action VARCHAR NOT NULL,
                    resource_type VARCHAR NOT NULL,
                    resource_id INTEGER,
                    resource_name VARCHAR,
                    details TEXT,
                    ip_address VARCHAR,
                    user_agent VARCHAR,
                    audit_metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            logging.info("Created audit_logs table")
        except Exception as e:
            logging.error(f"Error creating audit_logs table: {e}")
        
        # Create indexes
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_mappings_tenant_id ON field_mappings (tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_mappings_original_name ON field_mappings (original_field_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_configurations_tenant_id ON field_configurations (tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_configurations_field_name ON field_configurations (field_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_configurations_searchable ON field_configurations (is_searchable)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs (action)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs (resource_type)"))
            logging.info("Created indexes")
        except Exception as e:
            logging.error(f"Error creating indexes: {e}")
        
        # Update users table to add new columns if they don't exist
        try:
            # Check if new columns exist
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            # Add new columns to users table
            new_columns = [
                ("first_name", "VARCHAR"),
                ("last_name", "VARCHAR"),
                ("is_active", "BOOLEAN DEFAULT 1"),
                ("is_blocked", "BOOLEAN DEFAULT 0"),
                ("last_login", "DATETIME"),
                ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
                ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
                ("created_by", "INTEGER"),
                ("notes", "TEXT")
            ]
            
            for column_name, column_type in new_columns:
                if column_name not in columns:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
                    logging.info(f"Added column {column_name} to users table")
            
            # Update existing users to have default values
            conn.execute(text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))
            conn.execute(text("UPDATE users SET is_blocked = 0 WHERE is_blocked IS NULL"))
            conn.execute(text("UPDATE users SET role = 'tenant_user' WHERE role IS NULL OR role = 'viewer'"))
            
            logging.info("Updated users table")
        except Exception as e:
            logging.error(f"Error updating users table: {e}")
        
        # Update products table to add new columns if they don't exist
        try:
            # Check if created_at column exists
            result = conn.execute(text("PRAGMA table_info(products)"))
            columns = [row[1] for row in result.fetchall()]
            
            if "created_at" not in columns:
                conn.execute(text("ALTER TABLE products ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                logging.info("Added created_at column to products table")
            
            if "updated_at" not in columns:
                conn.execute(text("ALTER TABLE products ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                logging.info("Added updated_at column to products table")
            
            # Remove dynamic_fields column if it exists (legacy)
            if "dynamic_fields" in columns:
                # Create new table without dynamic_fields
                conn.execute(text("""
                    CREATE TABLE products_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tenant_id INTEGER NOT NULL,
                        category_id INTEGER,
                        sku_id VARCHAR NOT NULL,
                        price FLOAT,
                        manufacturer VARCHAR,
                        supplier VARCHAR,
                        image_url VARCHAR,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tenant_id) REFERENCES tenants (id),
                        FOREIGN KEY (category_id) REFERENCES categories (id)
                    )
                """))
                
                # Copy data from old table to new table
                conn.execute(text("""
                    INSERT INTO products_new (id, tenant_id, category_id, sku_id, price, manufacturer, supplier, image_url, created_at, updated_at)
                    SELECT id, tenant_id, category_id, sku_id, price, manufacturer, supplier, image_url, created_at, updated_at
                    FROM products
                """))
                
                # Drop old table and rename new table
                conn.execute(text("DROP TABLE products"))
                conn.execute(text("ALTER TABLE products_new RENAME TO products"))
                
                logging.info("Removed dynamic_fields column from products table")
            
        except Exception as e:
            logging.error(f"Error updating products table: {e}")
        
        # Create default superadmin if none exists
        try:
            # Check if superadmin exists
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'superadmin'"))
            superadmin_count = result.fetchone()[0]
            
            if superadmin_count == 0:
                # Create default superadmin
                password_hash = get_password_hash("admin123")
                current_time = datetime.utcnow().isoformat()
                
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
                
                logging.info("✅ Created default superadmin user: admin@pim.com / admin123")
                logging.info("⚠️  IMPORTANT: Please change the default password after first login!")
            else:
                logging.info("ℹ️  Superadmin user already exists, skipping default creation")
                
        except Exception as e:
            logging.error(f"Error creating default superadmin: {e}")
        
        conn.commit()
        logging.info("Migrations completed successfully")

if __name__ == "__main__":
    run_migrations() 