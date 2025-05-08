import os
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.db.database import get_db
from app.schemas.schemas import Token

# Check if we're in development mode
DEV_MODE = os.environ.get("ENV", "development") == "development"

router = APIRouter(tags=["authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Special case for development mode with test credentials
    if DEV_MODE and form_data.username == "admin@example.com" and form_data.password == "password123":
        print("Using development mode authentication with test credentials")
        # Create a mock token that will be recognized by our system
        access_token_expires = timedelta(days=1)  # Longer expiry for development
        access_token = create_access_token(
            data={"sub": "user-123", "tenant_id": "tenant-123", "role": "admin"},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    # Normal authentication flow
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "tenant_id": user.tenant_id, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Development-only endpoint for getting a token without credentials
# This would NEVER be included in a production system
@router.get("/dev-token", response_model=Token)
async def get_development_token():
    if not DEV_MODE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    print("Providing development token via dev-token endpoint")
    access_token_expires = timedelta(days=1)  # Longer expiry for development
    access_token = create_access_token(
        data={"sub": "user-123", "tenant_id": "tenant-123", "role": "admin"},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
