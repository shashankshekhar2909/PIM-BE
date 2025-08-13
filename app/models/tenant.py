from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships with cascade - when tenant is deleted, all related data is removed
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    progress = relationship("TenantProgress", back_populates="tenant", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="tenant", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="tenant", cascade="all, delete-orphan")
    field_mappings = relationship("FieldMapping", back_populates="tenant", cascade="all, delete-orphan")
    field_configurations = relationship("FieldConfiguration", back_populates="tenant", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="tenant", cascade="all, delete-orphan") 