"""
API routes for the rich content generation system.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.models import User, BrandVoice
from app.agents.rich_content_agent import invoke_rich_content_agent

router = APIRouter(
    prefix="/rich-content",
    tags=["rich-content"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/generate", response_model=Dict[str, Any])
async def generate_rich_content(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate rich content (text and images) for marketing materials.
    
    This endpoint creates marketing content with both text and images based on the prompt.
    """
    brand_voice_id = request.get("brand_voice_id")
    prompt = request.get("prompt")
    content_type = request.get("content_type", "flyer")
    
    # Get image generation parameters if provided
    image_model = request.get("image_model", "dall-e-3")  # dall-e-3 or gpt-image-1
    image_quality = request.get("image_quality", "standard")  # standard/hd for DALL-E 3, low/medium/high for GPT-Image
    image_size = request.get("image_size", "1024x1024")  # 1024x1024, 1024x1536, 1536x1024
    image_style = request.get("image_style", "natural")  # vivid or natural (for DALL-E 3)
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt is required"
        )
    
    # Check if the brand voice exists and belongs to the user's tenant
    if brand_voice_id:
        brand_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
        if not brand_voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand voice not found"
            )
        if brand_voice.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this brand voice"
            )
    
    # Create context with image generation parameters
    context = {
        "force_intent": "generate_rich_content",
        "content_type": content_type,
        "image_model": image_model,
        "image_quality": image_quality,
        "image_size": image_size,
        "image_style": image_style
    }
    
    # Invoke the rich content agent
    result = invoke_rich_content_agent(
        message=prompt,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        brand_voice_id=brand_voice_id,
        content_type=content_type,
        context=context
    )
    
    return result


@router.post("/templates", response_model=List[Dict[str, Any]])
async def list_templates(
    current_user: User = Depends(get_current_active_user)
):
    """
    List available marketing material templates.
    """
    # This would typically come from a database, but for now we'll hardcode some templates
    templates = [
        {
            "id": "flyer",
            "name": "Product Flyer",
            "description": "A single-page flyer to promote a product or service",
            "image_count": 1
        },
        {
            "id": "social-post",
            "name": "Social Media Post",
            "description": "Content optimized for social media platforms",
            "image_count": 1
        },
        {
            "id": "email-campaign",
            "name": "Email Campaign",
            "description": "Content for an email marketing campaign",
            "image_count": 1
        },
        {
            "id": "product-launch",
            "name": "Product Launch Announcement",
            "description": "Content for announcing a new product or service",
            "image_count": 2
        }
    ]
    
    return templates
