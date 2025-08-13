from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from typing import List

router = APIRouter()

@router.get("")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users in the current user's tenant."""
    # Handle superadmin and analyst users who can see all users
    if current_user.is_superadmin or current_user.is_analyst:
        users = db.query(User).all()
    else:
        # Regular users can only see users in their own tenant
        if not current_user.tenant_id:
            raise HTTPException(status_code=404, detail="Tenant not found")
        users = db.query(User).filter(User.tenant_id == current_user.tenant_id).all()
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "tenant_id": user.tenant_id
        }
        for user in users
    ]

@router.get("/{id}")
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user details by ID. Users can only access users in their own tenant."""
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Handle superadmin and analyst users who can see all users
    if not (current_user.is_superadmin or current_user.is_analyst):
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get tenant details
    tenant = None
    if user.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "tenant": {
            "id": tenant.id,
            "company_name": tenant.company_name,
            "logo_url": tenant.logo_url,
            "created_at": tenant.created_at
        } if tenant else None
    }

@router.patch("/{id}/role")
def update_user_role(
    id: int,
    role: str = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user role. Only superadmin users can update roles."""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmin users can update user roles")
    
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Superadmin can update any user's role
    # Regular admin users can only update users in their own tenant
    if not current_user.is_superadmin and user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate role
    valid_roles = ["superadmin", "analyst", "tenant_admin", "tenant_user"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
    
    # Prevent superadmin from changing their own role
    if current_user.id == id and role != "superadmin":
        raise HTTPException(status_code=400, detail="Cannot change your own superadmin role")
    
    user.role = role
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id
    } 