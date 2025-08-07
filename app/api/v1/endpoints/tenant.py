from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.tenant import Tenant
from app.models.user import User
from typing import List

router = APIRouter()

@router.post("")
def create_tenant(
    company_name: str = Body(...),
    logo_url: str = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tenant. Only admin users can create tenants."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create tenants")
    
    # Check if user already has a tenant
    if current_user.tenant_id:
        raise HTTPException(status_code=400, detail="User already has a tenant")
    
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
    """List all tenants (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can list all tenants")
    
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
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return {
        "id": tenant.id,
        "company_name": tenant.company_name,
        "logo_url": tenant.logo_url,
        "created_at": tenant.created_at
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
    company_name: str = Body(None),
    logo_url: str = Body(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update tenant details. Only admin users can update their tenant."""
    if current_user.tenant_id != id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update tenant details")
    
    tenant = db.query(Tenant).filter(Tenant.id == id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if company_name is not None:
        tenant.company_name = company_name
    if logo_url is not None:
        tenant.logo_url = logo_url
    
    db.commit()
    db.refresh(tenant)
    
    return {
        "id": tenant.id,
        "company_name": tenant.company_name,
        "logo_url": tenant.logo_url,
        "created_at": tenant.created_at
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