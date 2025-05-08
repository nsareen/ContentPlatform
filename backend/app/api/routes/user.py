from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.auth import get_current_active_user, get_password_hash
from app.db.database import get_db
from app.models.models import User, UserRole
from app.schemas.schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if user is admin or belongs to the tenant and is a business user
    if (current_user.role != UserRole.ADMIN and 
        (current_user.tenant_id != user.tenant_id or current_user.role != UserRole.BUSINESS_USER)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create users"
        )
    
    # Check if user with same email exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        tenant_id=user.tenant_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # If tenant_id is provided, check if user belongs to that tenant
    if tenant_id and current_user.tenant_id != tenant_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access users for this tenant"
        )
    
    # Use the user's tenant_id if none provided
    if not tenant_id and current_user.role != UserRole.ADMIN:
        tenant_id = current_user.tenant_id
    
    # Build query
    query = db.query(User)
    
    # Filter by tenant_id if provided or if user is not admin
    if tenant_id:
        query = query.filter(User.tenant_id == tenant_id)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user is admin or the user themselves or belongs to the same tenant and is a business user
    if (current_user.role != UserRole.ADMIN and 
        current_user.id != user_id and 
        (current_user.tenant_id != db_user.tenant_id or current_user.role != UserRole.BUSINESS_USER)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )
    
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user is admin or the user themselves or belongs to the same tenant and is a business user
    if (current_user.role != UserRole.ADMIN and 
        current_user.id != user_id and 
        (current_user.tenant_id != db_user.tenant_id or current_user.role != UserRole.BUSINESS_USER)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Update user fields
    user_data = user.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in user_data:
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
    
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user
