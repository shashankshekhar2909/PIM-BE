from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.auth_service import SupabaseAuthService
from app.models.user import User
from app.models.audit import AuditLog
import logging
from datetime import datetime
from typing import Optional, Dict

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_auth_service():
    return SupabaseAuthService()

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db),
    auth_service: SupabaseAuthService = Depends(get_auth_service)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    # First, try to verify as a custom JWT token
    try:
        from app.core.security import decode_access_token
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user = db.query(User).filter(User.id == payload["sub"]).first()
            if user:
                # Check if user is blocked
                if user.is_blocked:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="User account is blocked"
                    )
                return user
    except Exception as e:
        logging.debug(f"Custom JWT verification failed: {str(e)}")
    
    # If custom JWT fails, try Supabase verification
    try:
        user = auth_service.verify_token(token, db)
        if user:
            # Check if user is blocked
            if user.is_blocked:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is blocked"
                )
            return user
    except Exception as e:
        logging.debug(f"Supabase token verification failed: {str(e)}")
    
    # If both fail, raise credentials exception
    raise credentials_exception

def log_user_action(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    resource_name: Optional[str] = None,
    details: Optional[str] = None,
    request: Optional[Request] = None,
    metadata: Optional[Dict] = None
):
    """Log a user action for audit purposes"""
    try:
        # Get IP address and user agent from request
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            audit_metadata=metadata
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logging.error(f"Failed to log audit action: {str(e)}")

def require_superadmin(current_user: User):
    """Require superadmin role"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")

def require_superadmin_or_analyst(current_user: User):
    """Require superadmin or analyst role"""
    if not (current_user.is_superadmin or current_user.is_analyst):
        raise HTTPException(status_code=403, detail="Superadmin or analyst access required")

def require_tenant_access(current_user: User, tenant_id: int):
    """Require user to have access to the specified tenant"""
    if current_user.is_superadmin or current_user.is_analyst:
        return True  # Superadmin and analyst can access all tenants
    
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied to this tenant")
    
    return True 