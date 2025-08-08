from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # create, read, update, delete, login, logout, block, unblock
    resource_type = Column(String, nullable=False)  # user, tenant, product, category, etc.
    resource_id = Column(Integer, nullable=True)  # ID of the affected resource
    resource_name = Column(String, nullable=True)  # Name/identifier of the resource
    details = Column(Text, nullable=True)  # Additional details about the action
    ip_address = Column(String, nullable=True)  # IP address of the user
    user_agent = Column(String, nullable=True)  # User agent string
    audit_metadata = Column(JSON, nullable=True)  # Additional metadata as JSON (renamed from metadata)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action}, resource_type={self.resource_type})>" 