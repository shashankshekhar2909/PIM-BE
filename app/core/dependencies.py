from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.security import decode_access_token
from app.models.user import User
import logging

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    logging.warning(f"[AUTH] Token received: {token}")
    payload = decode_access_token(token)
    logging.warning(f"[AUTH] Decoded payload: {payload}")
    if payload is None or "sub" not in payload:
        logging.error("[AUTH] Invalid token or missing 'sub' in payload.")
        raise credentials_exception
    user = db.query(User).filter(User.id == payload["sub"]).first()
    logging.warning(f"[AUTH] User lookup by id {payload['sub']}: {user}")
    if user is None:
        logging.error(f"[AUTH] No user found for id {payload['sub']}")
        raise credentials_exception
    return user 