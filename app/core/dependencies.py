from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.auth_service import SupabaseAuthService
from app.models.user import User
import logging

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
                return user
    except Exception as e:
        logging.debug(f"Custom JWT verification failed: {str(e)}")
    
    # If custom JWT fails, try Supabase verification
    try:
        user = auth_service.verify_token(token, db)
        if user:
            return user
    except Exception as e:
        logging.debug(f"Supabase token verification failed: {str(e)}")
    
    # If both fail, raise credentials exception
    raise credentials_exception 