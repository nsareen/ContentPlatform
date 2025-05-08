from datetime import datetime, timedelta
from typing import Optional
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import TokenData

# In a production environment, these would be loaded from environment variables
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Fix the tokenUrl to match the actual endpoint path with the /api prefix
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Simple exception for authentication failures
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check for development environment
    is_dev = os.environ.get("ENV", "development") == "development"  # Default to development mode
    print(f"Current environment: {'development' if is_dev else 'production'}")
    
    # In development mode, always return a mock user for any token
    # This is ONLY for development and would be a security risk in production
    if is_dev:
        try:
            # Try to decode the token to get user info if available
            try:
                # First try to decode without verification
                unverified_payload = jwt.decode(token, options={"verify_signature": False})
                user_id = unverified_payload.get("sub", "user-123")
                tenant_id = unverified_payload.get("tenant_id", "tenant-123")
                role = unverified_payload.get("role", "admin")
                print(f"Development mode: Using token payload with user_id={user_id}")
            except Exception as e:
                # If token can't be decoded, use default values
                print(f"Development mode: Could not decode token, using default values. Error: {e}")
                user_id = "user-123"
                tenant_id = "tenant-123"
                role = "admin"
            
            # Look up the test user from the database
            user = db.query(User).filter(User.email == "admin@example.com").first()
            if user:
                print("Development mode: Using existing admin user from database")
                return user
            
            # If test user doesn't exist in DB, create a mock user object
            print("Development mode: Creating mock user")
            return User(
                id=user_id,
                email="admin@example.com",
                full_name="Test User",
                role=role,
                tenant_id=tenant_id,
                is_active=True
            )
        except Exception as e:
            print(f"Development mode error: {e}")
            # Even if something goes wrong, still return a mock user in development
            return User(
                id="user-123",
                email="admin@example.com",
                full_name="Test User",
                role="admin",
                tenant_id="tenant-123",
                is_active=True
            )
    
    # For production, perform proper token validation
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
        
        # Look up the user in the database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise credentials_exception
        
        return user
    except Exception:
        # In production, any error means invalid credentials
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
