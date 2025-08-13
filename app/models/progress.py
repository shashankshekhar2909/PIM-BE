from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class OnboardingStep(Base):
    """Model for defining onboarding steps"""
    __tablename__ = "onboarding_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    step_key = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True)
    category = Column(String, nullable=False)  # e.g., "setup", "configuration", "data"
    icon = Column(String, nullable=True)
    estimated_time = Column(Integer, nullable=True)  # in minutes

class TenantProgress(Base):
    """Model for tracking tenant onboarding progress"""
    __tablename__ = "tenant_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    step_key = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    data = Column(JSON, nullable=True)  # Store any additional data for the step
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with cascade
    tenant = relationship("Tenant", back_populates="progress") 