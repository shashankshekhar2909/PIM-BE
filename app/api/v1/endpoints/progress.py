from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.models.progress import OnboardingStep, TenantProgress
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

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

def validate_logo_url(logo_url: str) -> bool:
    """Validate if the logo URL is valid and points to an image"""
    if not logo_url:
        return True  # Empty URL is allowed
    
    # Check if it's a valid URL
    try:
        result = urlparse(logo_url)
        if not all([result.scheme, result.netloc]):
            return False
    except:
        return False
    
    # Check if it's likely an image URL (common image extensions)
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.tiff']
    parsed_url = urlparse(logo_url)
    path = parsed_url.path.lower()
    
    # Check if URL ends with image extension
    if any(path.endswith(ext) for ext in image_extensions):
        return True
    
    # Check if URL contains image-related keywords
    image_keywords = ['image', 'img', 'logo', 'icon', 'photo', 'picture']
    if any(keyword in path for keyword in image_keywords):
        return True
    
    # If no clear image indicators, still allow it (user might know what they're doing)
    return True

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
    for step in steps:
        progress = progress_map.get(step.step_key)
        steps_data.append({
            "step_key": step.step_key,
            "title": step.title,
            "description": step.description,
            "order": step.order,
            "is_required": step.is_required,
            "category": step.category,
            "icon": step.icon,
            "estimated_time": step.estimated_time,
            "is_completed": progress.is_completed if progress else False,
            "completed_at": progress.completed_at if progress else None,
            "data": progress.data if progress else {}
        })
    
    return {
        "tenant_id": tenant_id,
        "steps": steps_data,
        "total_steps": len(steps),
        "completed_steps": len([s for s in steps_data if s["is_completed"]]),
        "progress_percentage": round((len([s for s in steps_data if s["is_completed"]]) / len(steps)) * 100, 1)
    }

@router.get("/overview")
def get_progress_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress overview for the current tenant"""
    return get_tenant_progress(db, current_user.tenant_id)

@router.get("/steps")
def get_progress_steps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all onboarding steps with progress"""
    progress = get_tenant_progress(db, current_user.tenant_id)
    
    # Get tenant details for company setup step
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if tenant:
        # Update company setup step with current tenant data
        for step in progress["steps"]:
            if step["step_key"] == "company_setup":
                step["data"] = {
                    "company_name": tenant.company_name,
                    "logo_url": tenant.logo_url
                }
                step["is_completed"] = bool(tenant.company_name and tenant.logo_url)
                break
    
    return progress

@router.post("/steps/{step_key}/complete")
def complete_step(
    step_key: str,
    data: Dict[str, Any] = Body({}),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a step as completed.
    
    For company_setup step, supports direct URL pasting for logo:
    - Accepts any valid URL pointing to an image
    - Common formats: .jpg, .jpeg, .png, .gif, .svg, .webp, .bmp, .tiff
    - Also accepts URLs with image-related keywords in the path
    """
    # Verify step exists
    step = db.query(OnboardingStep).filter(OnboardingStep.step_key == step_key).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    
    # Handle company setup step specifically
    if step_key == "company_setup":
        tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Validate company name
        company_name = data.get("company_name")
        if not company_name or not company_name.strip():
            raise HTTPException(status_code=400, detail="Company name is required")
        
        # Validate logo URL if provided
        logo_url = data.get("logo_url")
        if logo_url is not None and logo_url.strip():
            if not validate_logo_url(logo_url.strip()):
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid logo URL. Please provide a valid URL pointing to an image file."
                )
            logo_url = logo_url.strip()
        
        # Update tenant with company setup data
        tenant.company_name = company_name.strip()
        tenant.logo_url = logo_url
        db.commit()
    
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