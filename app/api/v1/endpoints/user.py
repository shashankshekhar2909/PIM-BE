from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import get_password_hash, verify_password
from typing import List
from pydantic import BaseModel

# Pydantic models for request validation
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class AdminPasswordChangeRequest(BaseModel):
    new_password: str

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

@router.post("/change-password")
def change_own_password(
    password_data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change current user's own password."""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")
    
    # Hash new password
    new_password_hash = get_password_hash(password_data.new_password)
    
    # Update password
    current_user.password_hash = new_password_hash
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Password changed successfully",
        "user_id": current_user.id,
        "email": current_user.email
    }

@router.post("/{id}/change-password")
def change_user_password(
    id: int,
    password_data: AdminPasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change any user's password. Only superadmin users can change other users' passwords."""
    
    # Check if current user is superadmin
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmin users can change other users' passwords")
    
    # Find the user to update
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters long")
    
    # Hash new password
    new_password_hash = get_password_hash(password_data.new_password)
    
    # Update password
    user.password_hash = new_password_hash
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"Password changed successfully for user {user.email}",
        "user_id": user.id,
        "email": user.email,
        "changed_by": current_user.email
    }

@router.delete("/{id}")
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user and all associated data.
    Only superadmin users can delete users.
    
    ⚠️  WARNING: This will permanently delete:
    - User account
    - All audit logs created by the user
    - All chat sessions by the user
    """
    # Only superadmin can delete users
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmin users can delete users")
    
    # Prevent superadmin from deleting themselves
    if current_user.id == id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Find the user to delete
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user info for response
    user_info = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id
    }
    
    # Delete the user (cascade will handle related data)
    db.delete(user)
    db.commit()
    
    return {
        "message": f"User '{user_info['email']}' and all associated data deleted successfully",
        "deleted_user": user_info,
        "deleted_by": current_user.email
    } 