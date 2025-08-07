from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, get_auth_service
from app.models.user import User
from app.models.tenant import Tenant
from app.core.auth_service import SupabaseAuthService
from sqlalchemy.exc import IntegrityError
import logging
from typing import Optional

router = APIRouter()

@router.post("/signup")
def signup(
    email: str = Body(...),
    password: str = Body(...),
    company_name: str = Body(...),
    db: Session = Depends(get_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Sign up a new user with email and password using Supabase."""
    try:
        result = auth_service.signup_with_email(email, password, company_name, db)
        return {
            "msg": "Signup successful",
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.post("/login")
def login(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Login user with email and password using Supabase."""
    try:
        result = auth_service.login_with_email(email, password, db)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/signup/social")
def signup_social(
    provider: str = Body(...),  # e.g., "google", "github", "facebook"
    access_token: str = Body(...),
    company_name: str = Body(...),
    db: Session = Depends(get_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Sign up a new user with social login using Supabase."""
    try:
        result = auth_service.signup_with_social(provider, access_token, company_name, db)
        return {
            "msg": "Social signup successful",
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Social signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user with social login")

@router.post("/login/social")
def login_social(
    provider: str = Body(...),
    access_token: str = Body(...),
    db: Session = Depends(get_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    """Login user with social login using Supabase."""
    try:
        # For social login, we'll use the same flow as signup but check if user exists
        result = auth_service.signup_with_social(provider, access_token, "Temporary Company", db)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Social login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Social login failed")

@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user details with company information."""
    # Get tenant details
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "tenant": {
            "id": tenant.id,
            "company_name": tenant.company_name,
            "logo_url": tenant.logo_url,
            "created_at": tenant.created_at
        } if tenant else None
    }

@router.post("/logout")
def logout():
    """Logout user (client-side token removal)."""
    return {"msg": "Logout successful"}

@router.get("/providers")
def get_social_providers():
    """Get available social login providers."""
    return {
        "providers": [
            {
                "name": "google",
                "display_name": "Google",
                "icon": "google"
            },
            {
                "name": "github", 
                "display_name": "GitHub",
                "icon": "github"
            },
            {
                "name": "facebook",
                "display_name": "Facebook", 
                "icon": "facebook"
            }
        ]
    } 