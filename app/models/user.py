from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    supabase_user_id = Column(String, index=True, nullable=True)  # Supabase user ID
    password_hash = Column(String, nullable=True, default="")  # Made optional for Supabase auth
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)  # Nullable for superadmin/analyst
    role = Column(String, nullable=False, default="tenant_user")  # superadmin, analyst, tenant_admin, tenant_user
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # Who created this user
    notes = Column(Text, nullable=True)  # Admin notes about the user

    # Relationships with cascade
    tenant = relationship("Tenant", back_populates="users")
    created_users = relationship("User", backref="creator", remote_side=[id])
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email
    
    @property
    def is_superadmin(self):
        """Check if user is superadmin"""
        return self.role == "superadmin"
    
    @property
    def is_analyst(self):
        """Check if user is analyst"""
        return self.role == "analyst"
    
    @property
    def is_tenant_admin(self):
        """Check if user is tenant admin"""
        return self.role == "tenant_admin"
    
    @property
    def is_tenant_user(self):
        """Check if user is tenant user"""
        return self.role == "tenant_user"
    
    @property
    def can_view_all_tenants(self):
        """Check if user can view all tenants"""
        return self.is_superadmin or self.is_analyst
    
    @property
    def can_edit_all_tenants(self):
        """Check if user can edit all tenants"""
        return self.is_superadmin
    
    @property
    def can_manage_users(self):
        """Check if user can manage users"""
        return self.is_superadmin or self.is_tenant_admin 