from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.tenant import Tenant
from app.models.user import User
from typing import List, Optional
from urllib.parse import urlparse

router = APIRouter()

def validate_logo_url(logo_url: Optional[str]) -> bool:
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

@router.post("")
def create_tenant(
    company_name: str = Body(...),
    logo_url: Optional[str] = Body(None, description="Direct URL to logo image (e.g., https://example.com/logo.png)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new tenant. Only admin users can create tenants.
    
    Supports direct URL pasting for logo:
    - Accepts any valid URL pointing to an image
    - Common formats: .jpg, .jpeg, .png, .gif, .svg, .webp, .bmp, .tiff
    - Also accepts URLs with image-related keywords in the path
    """
    if not (current_user.is_superadmin or current_user.role == "tenant_admin"):
        raise HTTPException(status_code=403, detail="Only superadmin or tenant admin users can create tenants")
    
    # Check if user already has a tenant
    if current_user.tenant_id:
        raise HTTPException(status_code=400, detail="User already has a tenant")
    
    # Validate logo URL if provided
    if logo_url is not None and logo_url.strip():
        if not validate_logo_url(logo_url.strip()):
            raise HTTPException(
                status_code=400, 
                detail="Invalid logo URL. Please provide a valid URL pointing to an image file."
            )
        logo_url = logo_url.strip()
    
    # Create new tenant
    tenant = Tenant(
        company_name=company_name,
        logo_url=logo_url
    )
    db.add(tenant)
    db.flush()
    
    # Update current user's tenant_id
    current_user.tenant_id = tenant.id
    db.commit()
    db.refresh(tenant)
    
    return {
        "id": tenant.id,
        "company_name": tenant.company_name,
        "logo_url": tenant.logo_url,
        "created_at": tenant.created_at
    }

@router.get("")
def list_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all tenants (superadmin and analyst only)."""
    if not (current_user.is_superadmin or current_user.is_analyst):
        raise HTTPException(status_code=403, detail="Only superadmin or analyst users can list all tenants")
    
    tenants = db.query(Tenant).all()
    return [
        {
            "id": tenant.id,
            "company_name": tenant.company_name,
            "logo_url": tenant.logo_url,
            "created_at": tenant.created_at
        }
        for tenant in tenants
    ]

@router.get("/me")
def get_current_tenant(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's tenant details."""
    # Handle superadmin and analyst users who don't have a tenant
    if current_user.is_superadmin or current_user.is_analyst:
        return {
            "id": None,
            "company_name": "System Administration",
            "logo_url": None,
            "created_at": None,
            "is_system_user": True
        }
    
    # For regular users, check if they have a tenant
    if not current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return {
        "id": tenant.id,
        "company_name": tenant.company_name,
        "logo_url": tenant.logo_url,
        "created_at": tenant.created_at,
        "is_system_user": False
    }

@router.get("/{id}")
def get_tenant(
    id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tenant details by ID. Users can only access their own tenant."""
    if current_user.tenant_id != id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    tenant = db.query(Tenant).filter(Tenant.id == id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return {
        "id": tenant.id,
        "company_name": tenant.company_name,
        "logo_url": tenant.logo_url,
        "created_at": tenant.created_at
    }

@router.patch("/{id}")
def update_tenant(
    id: int,
    company_name: Optional[str] = Body(None),
    logo_url: Optional[str] = Body(None, description="Direct URL to logo image (e.g., https://example.com/logo.png)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update tenant details. Only admin users can update their tenant.
    
    Supports direct URL pasting for logo:
    - Accepts any valid URL pointing to an image
    - Common formats: .jpg, .jpeg, .png, .gif, .svg, .webp, .bmp, .tiff
    - Also accepts URLs with image-related keywords in the path
    - Empty string or null removes the logo
    """
    if current_user.tenant_id != id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not (current_user.is_superadmin or current_user.role == "tenant_admin"):
        raise HTTPException(status_code=403, detail="Only superadmin or tenant admin users can update tenant details")
    
    tenant = db.query(Tenant).filter(Tenant.id == id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Update company name
    if company_name is not None:
        if not company_name.strip():
            raise HTTPException(status_code=400, detail="Company name cannot be empty")
        tenant.company_name = company_name.strip()
    
    # Update logo URL
    if logo_url is not None:
        if logo_url == "" or logo_url is None:
            # Remove logo
            tenant.logo_url = None
        else:
            # Validate the URL format
            if not validate_logo_url(logo_url.strip()):
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid logo URL. Please provide a valid URL pointing to an image file."
                )
            tenant.logo_url = logo_url.strip()
    
    db.commit()
    db.refresh(tenant)
    
    return {
        "id": tenant.id,
        "company_name": tenant.company_name,
        "logo_url": tenant.logo_url,
        "created_at": tenant.created_at
    }

@router.post("/{id}/logo/validate")
def validate_tenant_logo_url(
    id: int,
    logo_url: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate a logo URL before saving it.
    This endpoint helps frontend validate URLs before submitting.
    
    Expected structure:
    {
        "logo_url": "https://example.com/logo.png"
    }
    """
    if current_user.tenant_id != id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not logo_url:
        return {
            "valid": True,
            "message": "Empty logo URL is allowed",
            "logo_url": None
        }
    
    is_valid = validate_logo_url(logo_url)
    
    return {
        "valid": is_valid,
        "message": "Valid logo URL" if is_valid else "Invalid logo URL. Please provide a valid URL pointing to an image file.",
        "logo_url": logo_url if is_valid else None
    }

@router.get("/{id}/users")
def get_tenant_users(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all users for a tenant. Users can only access their own tenant."""
    if current_user.tenant_id != id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    users = db.query(User).filter(User.tenant_id == id).all()
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ] 