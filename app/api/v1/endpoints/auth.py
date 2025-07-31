from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import get_password_hash, verify_password, create_access_token
from sqlalchemy.exc import IntegrityError
import logging

router = APIRouter()

@router.post("/signup")
def signup(
    email: str = Body(...),
    password: str = Body(...),
    company_name: str = Body(...),
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        # Create tenant
        tenant = Tenant(company_name=company_name)
        db.add(tenant)
        db.flush()  # get tenant.id
        
        # Create user
        user = User(email=email, password_hash=get_password_hash(password), tenant_id=tenant.id, role="admin")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Generate token with 'sub' as string
        token = create_access_token({"sub": str(user.id)})
        
        return {
            "msg": "Signup successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "tenant_id": user.tenant_id,
                "role": user.role
            },
            "access_token": token
        }
    except IntegrityError as e:
        db.rollback()
        # Check if it's a unique constraint violation on email
        if "UNIQUE constraint failed: users.email" in str(e):
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            raise HTTPException(status_code=400, detail="Failed to create company. Please try again.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create company. Please try again.")

@router.post("/login")
def login(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Generate token with 'sub' as string
    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "tenant_id": user.tenant_id,
            "role": user.role
        }
    }

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
    # No server-side logout for JWT; client should delete token
    return {"msg": "Logout successful"} 