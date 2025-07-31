from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
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
    dynamic_fields = Column(JSON, nullable=False, default={})

    category = relationship("Category", back_populates="products") 