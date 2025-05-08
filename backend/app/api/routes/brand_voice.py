from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import os

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.models import BrandVoice, User, UserRole, BrandVoiceStatus
from app.schemas.schemas import BrandVoiceCreate, BrandVoiceResponse, BrandVoiceUpdate

router = APIRouter(
    prefix="/voices",
    tags=["brand voices"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=BrandVoiceResponse, status_code=status.HTTP_201_CREATED)
def create_brand_voice(
    voice: BrandVoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if we're in development mode
    is_dev = os.environ.get("ENV") == "development"
    
    # In development mode, be more permissive with tenant access
    if is_dev:
        print(f"[DEBUG] Create brand voice - Development mode")
        print(f"[DEBUG] User role: {current_user.role}")
        print(f"[DEBUG] User tenant_id: {current_user.tenant_id}")
        print(f"[DEBUG] Requested voice tenant_id: {voice.tenant_id}")
        
        # For development, if the user is admin, allow creating for any tenant
        if current_user.role == UserRole.ADMIN:
            print(f"[DEBUG] User is admin, checking tenant_id")
            # If no tenant_id is provided, use the user's tenant_id
            if not voice.tenant_id:
                print(f"[DEBUG] No tenant_id provided, using user's tenant_id: {current_user.tenant_id}")
                voice.tenant_id = current_user.tenant_id
        else:
            print(f"[DEBUG] User is not admin, enforcing tenant matching")
            # For non-admin users, enforce tenant matching
            if current_user.tenant_id != voice.tenant_id:
                print(f"[DEBUG] Tenant mismatch: {current_user.tenant_id} != {voice.tenant_id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to create brand voices for this tenant"
                )
    else:
        # In production, strictly enforce tenant access
        if current_user.role not in [UserRole.BUSINESS_USER, UserRole.ADMIN] or current_user.tenant_id != voice.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create brand voices for this tenant"
            )
    
    # Create new brand voice
    db_voice = BrandVoice(**voice.dict(), created_by_id=current_user.id)
    db.add(db_voice)
    db.commit()
    db.refresh(db_voice)
    return db_voice

@router.get("/", response_model=List[BrandVoiceResponse])
def read_brand_voices(
    skip: int = 0,
    limit: int = 100,
    tenant_id: str = None,
    status: BrandVoiceStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # If tenant_id is provided, check if user belongs to that tenant
    if tenant_id and current_user.tenant_id != tenant_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access brand voices for this tenant"
        )
    
    # Use the user's tenant_id if none provided
    if not tenant_id:
        tenant_id = current_user.tenant_id
    
    # Build query
    query = db.query(BrandVoice).filter(BrandVoice.tenant_id == tenant_id)
    
    # Filter by status if provided
    if status:
        query = query.filter(BrandVoice.status == status)
    
    voices = query.offset(skip).limit(limit).all()
    return voices

@router.get("/{voice_id}", response_model=BrandVoiceResponse)
def read_brand_voice(
    voice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_voice = db.query(BrandVoice).filter(BrandVoice.id == voice_id).first()
    if db_voice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand voice not found"
        )
    
    # Check if user belongs to the tenant
    if current_user.tenant_id != db_voice.tenant_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this brand voice"
        )
    
    return db_voice

@router.put("/{voice_id}", response_model=BrandVoiceResponse)
def update_brand_voice(
    voice_id: str,
    voice: BrandVoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_voice = db.query(BrandVoice).filter(BrandVoice.id == voice_id).first()
    if db_voice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand voice not found"
        )
    
    # Check if user belongs to the tenant and is a business user or admin
    if (current_user.tenant_id != db_voice.tenant_id or 
        current_user.role not in [UserRole.BUSINESS_USER, UserRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this brand voice"
        )
    
    # Update brand voice fields
    voice_data = voice.dict(exclude_unset=True)
    
    # If status is changing to PUBLISHED, set published_at timestamp
    if "status" in voice_data and voice_data["status"] == BrandVoiceStatus.PUBLISHED:
        voice_data["published_at"] = datetime.now()
        
        # Check if required fields are present
        if not db_voice.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot publish: Brand voice name is required"
            )
    
    # Update version if this is a significant change
    if any(key in voice_data for key in ["name", "description", "voice_metadata", "dos", "donts"]):
        voice_data["version"] = db_voice.version + 1
    
    for key, value in voice_data.items():
        setattr(db_voice, key, value)
    
    db.commit()
    db.refresh(db_voice)
    return db_voice

@router.post("/{voice_id}/analyze", response_model=Dict[str, Any])
def analyze_brand_voice(
    voice_id: str,
    corpus: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_voice = db.query(BrandVoice).filter(BrandVoice.id == voice_id).first()
    if db_voice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand voice not found"
        )
    
    # Check if user belongs to the tenant and is a business user or admin
    if (current_user.tenant_id != db_voice.tenant_id or 
        current_user.role not in [UserRole.BUSINESS_USER, UserRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this brand voice"
        )
    
    # Check corpus length
    if len(corpus.split()) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corpus exceeds maximum length of 500 words"
        )
    
    # In a real implementation, this would call an LLM service to analyze the corpus
    # For now, we'll return a dummy response
    analysis = {
        "personality": "Bold, expressive, and effortlessly stylish",
        "tonality": "Confident, energetic, sophisticated",
        "dos": [
            "Maintain an Empowering and Confident Tone",
            "Keep the Language Fun and Playful",
            "Appeal to the Desire for Convenience and Effortlessness"
        ],
        "donts": [
            "Don't Overload with Technical Details",
            "Avoid Formal, Stiff Language",
            "Steer Clear of Overused Beauty Clichés"
        ]
    }
    
    return analysis
