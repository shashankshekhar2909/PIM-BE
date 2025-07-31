from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.models.progress import OnboardingStep, TenantProgress
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

# Default onboarding steps configuration
DEFAULT_ONBOARDING_STEPS = [
    {
        "step_key": "company_setup",
        "title": "Company Setup",
        "description": "Basic company information and branding",
        "order": 1,
        "is_required": True,
        "category": "setup",
        "icon": "🏢",
        "estimated_time": 5
    },
    {
        "step_key": "user_invitation",
        "title": "Invite Team Members",
        "description": "Add team members to your organization",
        "order": 2,
        "is_required": False,
        "category": "setup",
        "icon": "👥",
        "estimated_time": 3
    },
    {
        "step_key": "category_setup",
        "title": "Product Categories",
        "description": "Set up your product categories and schemas",
        "order": 3,
        "is_required": True,
        "category": "configuration",
        "icon": "📂",
        "estimated_time": 10
    },
    {
        "step_key": "product_import",
        "title": "Import Products",
        "description": "Import your product catalog",
        "order": 4,
        "is_required": True,
        "category": "data",
        "icon": "📦",
        "estimated_time": 15
    },
    {
        "step_key": "ai_configuration",
        "title": "AI Configuration",
        "description": "Configure AI features for your catalog",
        "order": 5,
        "is_required": False,
        "category": "configuration",
        "icon": "🤖",
        "estimated_time": 8
    },
    {
        "step_key": "integration_setup",
        "title": "Integrations",
        "description": "Connect with external systems",
        "order": 6,
        "is_required": False,
        "category": "configuration",
        "icon": "🔗",
        "estimated_time": 12
    }
]

def initialize_onboarding_steps(db: Session):
    """Initialize default onboarding steps if they don't exist"""
    existing_steps = db.query(OnboardingStep).count()
    if existing_steps == 0:
        for step_data in DEFAULT_ONBOARDING_STEPS:
            step = OnboardingStep(**step_data)
            db.add(step)
        db.commit()

def get_tenant_progress(db: Session, tenant_id: int) -> Dict[str, Any]:
    """Get progress for a specific tenant"""
    # Initialize steps if needed
    initialize_onboarding_steps(db)
    
    # Get all steps
    steps = db.query(OnboardingStep).order_by(OnboardingStep.order).all()
    
    # Get tenant progress
    tenant_progress = db.query(TenantProgress).filter(
        TenantProgress.tenant_id == tenant_id
    ).all()
    
    # Create progress map
    progress_map = {tp.step_key: tp for tp in tenant_progress}
    
    # Build response
    steps_data = []
    total_steps = len(steps)
    completed_steps = 0
    required_steps = 0
    completed_required_steps = 0
    
    for step in steps:
        progress = progress_map.get(step.step_key)
        is_completed = progress.is_completed if progress else False
        
        if is_completed:
            completed_steps += 1
        if step.is_required:
            required_steps += 1
            if is_completed:
                completed_required_steps += 1
        
        step_data = {
            "step_key": step.step_key,
            "title": step.title,
            "description": step.description,
            "order": step.order,
            "is_required": step.is_required,
            "category": step.category,
            "icon": step.icon,
            "estimated_time": step.estimated_time,
            "is_completed": is_completed,
            "completed_at": progress.completed_at if progress else None,
            "data": progress.data if progress else None
        }
        steps_data.append(step_data)
    
    # Calculate percentages
    overall_progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
    required_progress = (completed_required_steps / required_steps * 100) if required_steps > 0 else 0
    
    return {
        "overall_progress": round(overall_progress, 1),
        "required_progress": round(required_progress, 1),
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "required_steps": required_steps,
        "completed_required_steps": completed_required_steps,
        "steps": steps_data
    }

@router.get("/overview")
def get_progress_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall progress overview for the current user's tenant"""
    return get_tenant_progress(db, current_user.tenant_id)

@router.get("/steps")
def get_progress_steps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed progress for all steps"""
    progress = get_tenant_progress(db, current_user.tenant_id)
    
    # Group steps by category
    categories = {}
    for step in progress["steps"]:
        category = step["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(step)
    
    return {
        "overview": {
            "overall_progress": progress["overall_progress"],
            "required_progress": progress["required_progress"],
            "total_steps": progress["total_steps"],
            "completed_steps": progress["completed_steps"],
            "required_steps": progress["required_steps"],
            "completed_required_steps": progress["completed_required_steps"]
        },
        "categories": categories
    }

@router.post("/steps/{step_key}/complete")
def complete_step(
    step_key: str,
    data: Dict[str, Any] = Body({}),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a step as completed"""
    # Verify step exists
    step = db.query(OnboardingStep).filter(OnboardingStep.step_key == step_key).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    # Check if already completed
    existing_progress = db.query(TenantProgress).filter(
        TenantProgress.tenant_id == current_user.tenant_id,
        TenantProgress.step_key == step_key
    ).first()
    
    if existing_progress:
        # Update existing progress
        existing_progress.is_completed = True
        existing_progress.completed_at = datetime.utcnow()
        existing_progress.data = data
        existing_progress.updated_at = datetime.utcnow()
    else:
        # Create new progress
        progress = TenantProgress(
            tenant_id=current_user.tenant_id,
            step_key=step_key,
            is_completed=True,
            completed_at=datetime.utcnow(),
            data=data
        )
        db.add(progress)
    
    db.commit()
    
    return {
        "step_key": step_key,
        "is_completed": True,
        "completed_at": datetime.utcnow(),
        "data": data
    }

@router.post("/steps/{step_key}/reset")
def reset_step(
    step_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset a step (mark as incomplete)"""
    # Verify step exists
    step = db.query(OnboardingStep).filter(OnboardingStep.step_key == step_key).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    # Find and update progress
    progress = db.query(TenantProgress).filter(
        TenantProgress.tenant_id == current_user.tenant_id,
        TenantProgress.step_key == step_key
    ).first()
    
    if progress:
        progress.is_completed = False
        progress.completed_at = None
        progress.updated_at = datetime.utcnow()
        db.commit()
    
    return {
        "step_key": step_key,
        "is_completed": False,
        "completed_at": None
    }

@router.get("/next-steps")
def get_next_steps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the next pending steps for the tenant"""
    progress = get_tenant_progress(db, current_user.tenant_id)
    
    # Filter for incomplete steps
    pending_steps = [
        step for step in progress["steps"] 
        if not step["is_completed"]
    ]
    
    # Sort by order
    pending_steps.sort(key=lambda x: x["order"])
    
    return {
        "pending_steps": pending_steps,
        "next_step": pending_steps[0] if pending_steps else None,
        "total_pending": len(pending_steps)
    } 