import logging
from sqlalchemy import text, create_engine
from app.core.config import settings

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
        
        # Add indexes for better performance
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_product_additional_data_product_id ON product_additional_data (product_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_mappings_tenant_id ON field_mappings (tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_mappings_original_name ON field_mappings (original_field_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_configurations_tenant_id ON field_configurations (tenant_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_configurations_field_name ON field_configurations (field_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_field_configurations_searchable ON field_configurations (is_searchable)"))
            logging.info("Created indexes")
        except Exception as e:
            logging.error(f"Error creating indexes: {e}")
        
        # Update products table to add new columns if they don't exist
        try:
            # Check if created_at column exists
            result = conn.execute(text("PRAGMA table_info(products)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'created_at' not in columns:
                conn.execute(text("ALTER TABLE products ADD COLUMN created_at DATETIME"))
                conn.execute(text("UPDATE products SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
                logging.info("Added created_at column to products table")
            
            if 'updated_at' not in columns:
                conn.execute(text("ALTER TABLE products ADD COLUMN updated_at DATETIME"))
                conn.execute(text("UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))
                logging.info("Added updated_at column to products table")
            
            # Remove dynamic_fields column if it exists (replaced by additional_data table)
            if 'dynamic_fields' in columns:
                logging.info("Removing dynamic_fields column (replaced by additional_data table)...")
                # Create new table without dynamic_fields
                conn.execute(text("""
                    CREATE TABLE products_new (
                        id INTEGER NOT NULL, 
                        tenant_id INTEGER NOT NULL, 
                        category_id INTEGER, 
                        sku_id VARCHAR NOT NULL, 
                        price FLOAT, 
                        manufacturer VARCHAR, 
                        supplier VARCHAR, 
                        image_url VARCHAR, 
                        created_at DATETIME,
                        updated_at DATETIME,
                        PRIMARY KEY (id), 
                        FOREIGN KEY(tenant_id) REFERENCES tenants (id), 
                        FOREIGN KEY(category_id) REFERENCES categories (id)
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
                
                # Recreate indexes
                conn.execute(text("CREATE INDEX ix_products_id ON products (id)"))
                conn.execute(text("CREATE INDEX ix_products_sku_id ON products (sku_id)"))
                
                logging.info("Recreated products table without dynamic_fields column")
                
        except Exception as e:
            logging.error(f"Error updating products table: {e}")
        
        conn.commit()
        logging.info("Migrations completed successfully") 