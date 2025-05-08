"""
API routes for the agentic AI system.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.models import User, BrandVoice
from app.agents.brand_voice_agent import invoke_brand_voice_agent

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
    dependencies=[Depends(get_current_active_user)]
)


class AgentRequest:
    """Request model for agent interactions."""
    message: str
    brand_voice_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@router.post("/chat", response_model=Dict[str, Any])
async def agent_chat(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Chat with the agentic AI system.
    
    The agent will:
    1. Identify the user's intent
    2. Execute the appropriate workflow
    3. Return the result
    
    This endpoint handles all conversational interactions with the brand voice system.
    """
    message = request.get("message")
    brand_voice_id = request.get("brand_voice_id")
    context = request.get("context", {})
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )
    
    # If brand_voice_id is provided, verify that it exists and the user has access
    if brand_voice_id:
        db_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
        if not db_voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand voice not found"
            )
        
        # Check if user belongs to the tenant
        if current_user.tenant_id != db_voice.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this brand voice"
            )
    
    # Invoke the agent
    result = invoke_brand_voice_agent(
        message=message,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        brand_voice_id=brand_voice_id,
        context=context
    )
    
    return result


@router.post("/generate", response_model=Dict[str, Any])
async def generate_content(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate content using a specific brand voice.
    
    This endpoint is a direct route to content generation, bypassing the intent classification.
    """
    brand_voice_id = request.get("brand_voice_id")
    prompt = request.get("prompt")
    content_type = request.get("content_type")
    
    if not brand_voice_id or not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand voice ID and prompt are required"
        )
    
    # Verify that the brand voice exists and the user has access
    db_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
    if not db_voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand voice not found"
        )
    
    # Check if user belongs to the tenant
    if current_user.tenant_id != db_voice.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this brand voice"
        )
    
    # Construct a message that will trigger content generation
    message = f"Generate content using brand voice {brand_voice_id}: {prompt}"
    if content_type:
        message += f" The content type is {content_type}."
    
    # Invoke the agent with a context that ensures content generation
    result = invoke_brand_voice_agent(
        message=message,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        brand_voice_id=brand_voice_id,
        context={
            "force_intent": "generate_content",
            "content_type": content_type
        }
    )
    
    return result


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_content(
    request: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze content to extract brand voice characteristics.
    
    This endpoint is a direct route to content analysis, bypassing the intent classification.
    """
    content = request.get("content")
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required"
        )
    
    # Construct a message that will trigger content analysis
    message = f"Analyze this content to extract brand voice characteristics: {content[:100]}..."
    
    # Invoke the agent with a context that ensures content analysis
    result = invoke_brand_voice_agent(
        message=message,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        context={
            "force_intent": "analyze_content",
            "full_content": content
        }
    )
    
    return result
