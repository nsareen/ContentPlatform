from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    BUSINESS_USER = "business_user"
    CONTENT_SPECIALIST = "content_specialist"

class BrandVoiceStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNDER_REVIEW = "under_review"
    INACTIVE = "inactive"

class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    CLOSED = "closed"

# Base schemas
class TenantBase(BaseModel):
    name: str
    config: Optional[Dict[str, Any]] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole

class BrandVoiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    voice_metadata: Optional[Dict[str, Any]] = None
    dos: Optional[str] = None
    donts: Optional[str] = None

class ContentProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    schema_def: Optional[Dict[str, Any]] = None
    voice_id: Optional[str] = None

class TaskBase(BaseModel):
    type: str
    input_data: Dict[str, Any]
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None

class FeedbackBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None

# Create schemas
class TenantCreate(TenantBase):
    pass

class UserCreate(UserBase):
    password: str
    tenant_id: str

class BrandVoiceCreate(BrandVoiceBase):
    tenant_id: str

class ContentProjectCreate(ContentProjectBase):
    tenant_id: str

class TaskCreate(TaskBase):
    project_id: str

class FeedbackCreate(FeedbackBase):
    task_id: str

# Update schemas
class TenantUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class BrandVoiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    voice_metadata: Optional[Dict[str, Any]] = None
    dos: Optional[str] = None
    donts: Optional[str] = None
    status: Optional[BrandVoiceStatus] = None

class ContentProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    schema_def: Optional[Dict[str, Any]] = None
    voice_id: Optional[str] = None

class TaskUpdate(BaseModel):
    type: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    assignee_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None

# Response schemas
class TenantResponse(TenantBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class BrandVoiceResponse(BrandVoiceBase):
    id: str
    tenant_id: str
    version: int
    status: BrandVoiceStatus
    created_by_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ContentProjectResponse(ContentProjectBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class TaskResponse(TaskBase):
    id: str
    project_id: str
    output_data: Optional[Dict[str, Any]] = None
    status: TaskStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class FeedbackResponse(FeedbackBase):
    id: str
    task_id: str
    created_at: datetime

    class Config:
        orm_mode = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    role: Optional[UserRole] = None
