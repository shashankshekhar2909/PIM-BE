from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    schema_json = Column(JSON, nullable=False, default={})

    # Relationships with cascade
    tenant = relationship("Tenant", back_populates="categories")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan") 