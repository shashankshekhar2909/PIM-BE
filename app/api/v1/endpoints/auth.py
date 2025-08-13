from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import verify_password, create_access_token, get_password_hash
from sqlalchemy.exc import IntegrityError
import logging
from typing import Optional
from datetime import timedelta, datetime
from app.core.config import settings

router = APIRouter()

@router.post("/signup")
def signup(
    email: str = Body(...),
    password: str = Body(...),
    company_name: str = Body(...),
    db: Session = Depends(get_db)
):
    """Sign up a new user with email and password."""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create tenant first
        tenant = Tenant(
            company_name=company_name,
            logo_url=None,
            created_at=datetime.now(datetime.timezone.utc)
        )
        db.add(tenant)
        db.flush()  # Get the tenant ID
        
        # Create user
        user = User(
            email=email,
            password_hash=get_password_hash(password),
            role="tenant_admin",
            first_name="",
            last_name="",
            is_active=True,
            is_blocked=False,
            tenant_id=tenant.id
        )
        db.add(user)
        db.commit()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": f"{user.first_name} {user.last_name}".strip() or "User",
                "role": user.role,
                "isSetupComplete": True,
                "companyId": str(tenant.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_blocked": user.is_blocked,
                "tenant_id": user.tenant_id,
                "tenant": {
                    "id": str(tenant.id),
                    "name": tenant.company_name,
                    "is_active": True
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Signup error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.post("/login")
def login(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Login user with email and password."""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid login credentials")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid login credentials")
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is deactivated")
        
        # Check if user is blocked
        if user.is_blocked:
            raise HTTPException(status_code=403, detail="User account is blocked")
        
        # Get tenant information
        tenant = None
        if user.tenant_id:
            tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": f"{user.first_name} {user.last_name}".strip() or "User",
                "role": user.role,
                "isSetupComplete": True,
                "companyId": str(tenant.id) if tenant else "",
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_blocked": user.is_blocked,
                "tenant_id": user.tenant_id,
                "tenant": {
                    "id": str(tenant.id),
                    "name": tenant.company_name,
                    "is_active": tenant.is_active
                } if tenant else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user details with company information."""
    # Handle superadmin and analyst users who don't have a tenant
    if current_user.is_superadmin or current_user.is_analyst:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "name": f"{current_user.first_name} {current_user.last_name}".strip() or "User",
            "role": current_user.role,
            "isSetupComplete": True,
            "companyId": "",
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "is_active": current_user.is_active,
            "is_blocked": current_user.is_blocked,
            "tenant_id": current_user.tenant_id,
            "tenant": None
        }
    
    # Get tenant information for regular users
    tenant = None
    if current_user.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": f"{current_user.first_name} {current_user.last_name}".strip() or "User",
        "role": current_user.role,
        "isSetupComplete": True,
        "companyId": str(tenant.id) if tenant else "",
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_active": current_user.is_active,
        "is_blocked": current_user.is_blocked,
        "tenant_id": current_user.tenant_id,
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.company_name,
            "is_active": tenant.is_active
        } if tenant else None
    }

@router.post("/logout")
def logout():
    """Logout user (client-side token removal)."""
    return {"message": "Successfully logged out"}

@router.post("/refresh")
def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Refresh access token."""
    # Create new access token
    access_token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    } 