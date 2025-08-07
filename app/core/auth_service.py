from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.supabase import get_supabase_client, get_supabase_admin_client
from app.core.social_auth import SocialAuthService
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import create_access_token
import logging

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
        """Login user with email and password using Supabase."""
        try:
            if not self.supabase:
                raise HTTPException(
                    status_code=503, 
                    detail="Supabase authentication is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
                )
            
            # Authenticate with Supabase
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user is None:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Find user in our database
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found in system")
            
            # Update supabase_user_id if not set
            if not user.supabase_user_id:
                user.supabase_user_id = auth_response.user.id
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
            
            if user_response.user is None:
                return None
            
            # Find user in our database
            user = db.query(User).filter(User.supabase_user_id == user_response.user.id).first()
            if not user:
                # Try to find by email as fallback
                user = db.query(User).filter(User.email == user_response.user.email).first()
                if user and not user.supabase_user_id:
                    # Update with supabase_user_id
                    user.supabase_user_id = user_response.user.id
                    db.commit()
                    db.refresh(user)
            
            return user
            
        except Exception as e:
            logging.error(f"Token verification error: {str(e)}")
            return None
    
    def _create_auth_response(self, user: User) -> Dict[str, Any]:
        """Create authentication response with user data and token."""
        # Create a custom JWT token for our system
        token_data = {"sub": str(user.id)}
        if user.supabase_user_id:
            token_data["supabase_user_id"] = user.supabase_user_id
        
        token = create_access_token(token_data)
        
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