from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sku_id = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=True)
    manufacturer = Column(String, nullable=True)
    supplier = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    additional_data = relationship("ProductAdditionalData", back_populates="product", cascade="all, delete-orphan")

class ProductAdditionalData(Base):
    __tablename__ = "product_additional_data"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    field_name = Column(String, nullable=False)  # Normalized field name (e.g., "brand", "warranty")
    field_label = Column(String, nullable=False)  # Human-readable label (e.g., "Brand Name", "Warranty Period")
    field_value = Column(String, nullable=True)   # The actual value
    field_type = Column(String, nullable=False, default="string")  # string, number, boolean, date
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="additional_data")

class FieldMapping(Base):
    __tablename__ = "field_mappings"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    original_field_name = Column(String, nullable=False)  # Original field name from CSV
    normalized_field_name = Column(String, nullable=False)  # AI-normalized field name
    field_label = Column(String, nullable=False)  # Human-readable label
    field_type = Column(String, nullable=False, default="string")  # string, number, boolean, date
    is_standard_field = Column(Integer, default=0)  # 1 if it's a standard field (sku_id, price, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FieldConfiguration(Base):
    __tablename__ = "field_configurations"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    field_name = Column(String, nullable=False)  # Normalized field name (e.g., "brand", "warranty")
    field_label = Column(String, nullable=False)  # Human-readable label (e.g., "Brand Name", "Warranty Period")
    field_type = Column(String, nullable=False, default="string")  # string, number, boolean, date
    
    # Configuration options
    is_searchable = Column(Boolean, default=False)  # Can be searched (implies search index)
    is_editable = Column(Boolean, default=True)     # Can be edited
    is_primary = Column(Boolean, default=False)     # Primary field (e.g., sku_id)
    is_secondary = Column(Boolean, default=False)   # Secondary field (e.g., price, manufacturer)
    
    # Additional metadata
    display_order = Column(Integer, default=0)  # Order for display
    description = Column(String, nullable=True)  # Field description
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 