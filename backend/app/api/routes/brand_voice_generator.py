"""
API routes for brand voice generator.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.models import User, BrandVoice, UserRole, BrandVoiceStatus
from app.agents.brand_voice_generator import invoke_generator

router = APIRouter(
    prefix="/brand-voice-generator",
    tags=["brand-voice-generator"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/generate/", response_model=Dict[str, Any])
async def generate_brand_voice_from_content(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a brand voice profile from sample content.
    
    This endpoint uses the LangGraph agent to analyze content and generate a comprehensive
    brand voice profile with personality traits, tonality, and guidelines.
    """
    # Extract request data
    content = request.get("content")
    brand_name = request.get("brand_name")
    industry = request.get("industry")
    target_audience = request.get("target_audience")
    options = request.get("options", {})
    
    # Validate required fields
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required"
        )
    
    # Invoke the generator agent
    result = invoke_generator(
        content=content,
        brand_name=brand_name,
        industry=industry,
        target_audience=target_audience,
        options=options,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    
    # Check for errors
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "An error occurred during brand voice generation")
        )
    
    return result


@router.post("/save/", response_model=Dict[str, Any])
async def save_generated_brand_voice(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Save a generated brand voice profile to the database.
    
    This endpoint takes the output from the generate endpoint and creates a new brand voice
    record in the database.
    """
    # Extract request data
    brand_voice_components = request.get("brand_voice_components")
    generation_metadata = request.get("generation_metadata", {})
    source_content = request.get("source_content")
    name = request.get("name")
    description = request.get("description", "")
    tenant_id = request.get("tenant_id", current_user.tenant_id)
    
    # Validate required fields
    if not brand_voice_components:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand voice components are required"
        )
    
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required"
        )
    
    # Check if user belongs to the tenant or is an admin
    if current_user.tenant_id != tenant_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create a brand voice for this tenant"
        )
    
    # Extract components
    personality_traits = brand_voice_components.get("personality_traits", [])
    tonality = brand_voice_components.get("tonality", "")
    identity = brand_voice_components.get("identity", "")
    dos = brand_voice_components.get("dos", [])
    donts = brand_voice_components.get("donts", [])
    sample_content = brand_voice_components.get("sample_content", "")
    
    # Prepare voice metadata
    voice_metadata = {
        "personality": ", ".join(personality_traits),
        "tonality": tonality,
        "identity": identity
    }
    
    # Create new brand voice
    new_brand_voice = BrandVoice(
        tenant_id=tenant_id,
        name=name,
        description=description,
        voice_metadata=voice_metadata,
        dos="\n".join([f"• {do_item}" for do_item in dos]),
        donts="\n".join([f"• {dont_item}" for dont_item in donts]),
        status=BrandVoiceStatus.DRAFT,
        created_by_id=current_user.id,
        source_content=source_content,
        generation_metadata=generation_metadata
    )
    
    # Add to database
    db.add(new_brand_voice)
    db.commit()
    db.refresh(new_brand_voice)
    
    # Return the created brand voice
    return {
        "success": True,
        "brand_voice": {
            "id": new_brand_voice.id,
            "name": new_brand_voice.name,
            "description": new_brand_voice.description,
            "voice_metadata": new_brand_voice.voice_metadata,
            "dos": new_brand_voice.dos,
            "donts": new_brand_voice.donts,
            "status": new_brand_voice.status,
            "tenant_id": new_brand_voice.tenant_id,
            "created_by_id": new_brand_voice.created_by_id,
            "created_at": new_brand_voice.created_at
        }
    }


@router.post("/refine/", response_model=Dict[str, Any])
async def refine_brand_voice_generation(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Refine a generated brand voice based on user feedback.
    
    This endpoint allows users to provide feedback on specific components of a generated
    brand voice and get an improved version.
    """
    # Extract request data
    brand_voice_components = request.get("brand_voice_components")
    feedback = request.get("feedback", {})
    content = request.get("content")
    brand_name = request.get("brand_name")
    industry = request.get("industry")
    target_audience = request.get("target_audience")
    options = request.get("options", {})
    
    # Validate required fields
    if not brand_voice_components:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand voice components are required"
        )
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required"
        )
    
    # Add feedback to options
    options["feedback"] = feedback
    options["refinement"] = True
    
    # Invoke the generator agent with the feedback
    result = invoke_generator(
        content=content,
        brand_name=brand_name,
        industry=industry,
        target_audience=target_audience,
        options=options,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    
    # Check for errors
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "An error occurred during brand voice refinement")
        )
    
    return result
