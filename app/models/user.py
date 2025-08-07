from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    supabase_user_id = Column(String, index=True, nullable=True)  # Supabase user ID
    password_hash = Column(String, nullable=True, default="")  # Made optional for Supabase auth
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    role = Column(String, nullable=False, default="viewer")

    tenant = relationship("Tenant", back_populates="users") 