from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.supabase import get_supabase_client, get_supabase_admin_client
from app.core.social_auth import SocialAuthService
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import create_access_token, verify_password
import logging
from datetime import datetime

class SupabaseAuthService:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.admin_supabase = get_supabase_admin_client()
    
    def signup_with_email(self, email: str, password: str, company_name: str, db: Session) -> Dict[str, Any]:
        """Sign up a new user with email and password using Supabase."""
        try:
            if not self.supabase:
                raise HTTPException(
                    status_code=503, 
                    detail="Supabase authentication is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
                )
            
            # Create user in Supabase
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if auth_response.user is None:
                raise HTTPException(status_code=400, detail="Failed to create user in Supabase")
            
            supabase_user_id = auth_response.user.id
            
            # Check if user already exists in our database
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                # If user exists but doesn't have supabase_user_id, update it
                if not existing_user.supabase_user_id:
                    existing_user.supabase_user_id = supabase_user_id
                    db.commit()
                    db.refresh(existing_user)
                    return self._create_auth_response(existing_user)
                else:
                    raise HTTPException(status_code=400, detail="Email already registered")
            
            # Create tenant
            tenant = Tenant(company_name=company_name)
            db.add(tenant)
            db.flush()
            
            # Create user in our database
            user = User(
                email=email,
                supabase_user_id=supabase_user_id,
                tenant_id=tenant.id,
                role="admin"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return self._create_auth_response(user)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logging.error(f"Signup error: {str(e)}")
            if "User already registered" in str(e):
                raise HTTPException(status_code=400, detail="Email already registered")
            raise HTTPException(status_code=500, detail="Failed to create user")
    
    def login_with_email(self, email: str, password: str, db: Session) -> Dict[str, Any]:
        """Login user with email and password using Supabase or local authentication."""
        try:
            # First, try to find user in our database
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found in system")
            
            # Check if user is blocked
            if user.is_blocked:
                raise HTTPException(status_code=403, detail="User account is blocked")
            
            # Try local authentication first (if user has password_hash)
            if user.password_hash and user.password_hash.strip():
                if verify_password(password, user.password_hash):
                    # Update last login
                    user.last_login = datetime.utcnow()
                    db.commit()
                    db.refresh(user)
                    return self._create_auth_response(user)
                else:
                    raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # If no local password, try Supabase authentication
            if not self.supabase:
                raise HTTPException(
                    status_code=503, 
                    detail="Supabase authentication is not configured and no local password found."
                )
            
            # Authenticate with Supabase
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user is None:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Update supabase_user_id if not set
            if not user.supabase_user_id:
                user.supabase_user_id = auth_response.user.id
                user.last_login = datetime.utcnow()
                db.commit()
                db.refresh(user)
            
            return self._create_auth_response(user)
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            if "Invalid login credentials" in str(e):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            raise HTTPException(status_code=500, detail="Login failed")
    
    def signup_with_social(self, provider: str, access_token: str, company_name: str, db: Session) -> Dict[str, Any]:
        """Sign up a new user with social login using Supabase."""
        try:
            if not self.supabase:
                raise HTTPException(
                    status_code=503, 
                    detail="Supabase authentication is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
                )
            
            # Get user information from the OAuth provider
            user_info = SocialAuthService.get_user_info(provider, access_token)
            if not user_info:
                raise HTTPException(status_code=400, detail="Failed to get user information from OAuth provider")
            
            email = user_info.get("email")
            if not email:
                raise HTTPException(status_code=400, detail="Email is required for social login")
            
            # Check if user already exists in our database
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                # If user exists, return auth response
                return self._create_auth_response(existing_user)
            
            # Create tenant
            tenant = Tenant(company_name=company_name)
            db.add(tenant)
            db.flush()
            
            # Create user in our database (with empty password_hash for social login)
            user = User(
                email=email,
                tenant_id=tenant.id,
                role="admin",
                password_hash=""  # Empty string for social login users
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return self._create_auth_response(user)
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logging.error(f"Social signup error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create user with social login")
    
    def verify_token(self, token: str, db: Session) -> Optional[User]:
        """Verify Supabase JWT token and return user."""
        try:
            if not self.supabase:
                return None
            
            # Verify token with Supabase
            user_response = self.supabase.auth.get_user(token)
            if not user_response.user:
                return None
            
            # Find user in our database
            user = db.query(User).filter(User.email == user_response.user.email).first()
            return user
            
        except Exception as e:
            logging.debug(f"Token verification failed: {str(e)}")
            return None
    
    def _create_auth_response(self, user: User) -> Dict[str, Any]:
        """Create authentication response with user data and token."""
        from datetime import timedelta
        from app.core.security import create_access_token
        
        # Create access token
        access_token_expires = timedelta(minutes=60 * 24)  # 24 hours
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        # Get tenant details if user has a tenant
        tenant_info = None
        if user.tenant_id:
            from app.models.tenant import Tenant
            tenant = user.tenant if hasattr(user, 'tenant') else None
            if tenant:
                tenant_info = {
                    "id": tenant.id,
                    "company_name": tenant.company_name,
                    "logo_url": tenant.logo_url
                }
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),  # Convert to string as you showed
                "email": user.email,
                "name": user.full_name or user.email,  # Use full_name or email as name
                "role": user.role,
                "isSetupComplete": True,  # Default to True for existing users
                "companyId": str(user.tenant_id) if user.tenant_id else "",
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_blocked": user.is_blocked,
                "tenant_id": user.tenant_id,
                "tenant": tenant_info
            }
        } 