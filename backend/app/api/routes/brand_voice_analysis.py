"""
API routes for brand voice analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.models import User, BrandVoice, UserRole
from app.agents.brand_voice_analysis import invoke_analysis_agent

router = APIRouter(
    prefix="/brand-voice-analysis",
    tags=["brand-voice-analysis"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_content_with_brand_voice(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze content against a specific brand voice using the LangGraph agent.
    
    This endpoint performs detailed analysis of content against brand voice guidelines,
    providing scores, highlighting issues, and suggesting improvements.
    """
    # Extract request data
    content = request.get("content")
    brand_voice_id = request.get("brand_voice_id")
    options = request.get("options", {})
    
    # Validate required fields
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required"
        )
    
    if not brand_voice_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand voice ID is required"
        )
    
    # Verify that the brand voice exists and the user has access
    db_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
    if not db_voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand voice not found"
        )
    
    # Check if user belongs to the tenant or is an admin
    if current_user.tenant_id != db_voice.tenant_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this brand voice"
        )
    
    # Convert database model to dictionary for the agent
    brand_voice_dict = {
        "id": db_voice.id,
        "name": db_voice.name,
        "description": db_voice.description,
        "voice_metadata": db_voice.voice_metadata,
        "dos": db_voice.dos,
        "donts": db_voice.donts,
        "tenant_id": db_voice.tenant_id
    }
    
    # Invoke the analysis agent
    result = await invoke_analysis_agent(
        content=content,
        brand_voice=brand_voice_dict,
        options=options,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id
    )
    
    # Check for errors
    if not result.get("success", False):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "An error occurred during analysis")
        )
    
    return result


@router.post("/compare", response_model=Dict[str, Any])
async def compare_content_with_brand_voices(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Compare content against multiple brand voices to find the best match.
    
    This endpoint analyzes content against multiple brand voices and returns
    a ranked list of matches with scores and analysis for each.
    """
    # Extract request data
    content = request.get("content")
    brand_voice_ids = request.get("brand_voice_ids", [])
    options = request.get("options", {})
    
    # Validate required fields
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required"
        )
    
    if not brand_voice_ids or not isinstance(brand_voice_ids, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one brand voice ID is required"
        )
    
    # Limit the number of brand voices to compare
    if len(brand_voice_ids) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum of 5 brand voices can be compared at once"
        )
    
    # Verify that all brand voices exist and the user has access
    brand_voices = []
    for bv_id in brand_voice_ids:
        db_voice = db.query(BrandVoice).filter(BrandVoice.id == bv_id).first()
        if not db_voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand voice with ID {bv_id} not found"
            )
        
        # Check if user belongs to the tenant or is an admin
        if current_user.tenant_id != db_voice.tenant_id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized to access brand voice with ID {bv_id}"
            )
        
        # Convert database model to dictionary for the agent
        brand_voices.append({
            "id": db_voice.id,
            "name": db_voice.name,
            "description": db_voice.description,
            "voice_metadata": db_voice.voice_metadata,
            "dos": db_voice.dos,
            "donts": db_voice.donts,
            "tenant_id": db_voice.tenant_id
        })
    
    # Set simplified options for comparison to speed up processing
    comparison_options = {
        "analysis_depth": options.get("analysis_depth", "basic"),
        "include_suggestions": False,
        "highlight_issues": True,
        "max_suggestions": 0,
        "generate_report": False
    }
    
    # Analyze content against each brand voice
    results = []
    for brand_voice in brand_voices:
        # Invoke the analysis agent
        result = await invoke_analysis_agent(
            content=content,
            brand_voice=brand_voice,
            options=comparison_options,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id
        )
        
        # Add to results if successful
        if result.get("success", False):
            analysis_result = result.get("analysis_result", {})
            results.append({
                "brand_voice_id": brand_voice["id"],
                "brand_voice_name": brand_voice["name"],
                "overall_score": analysis_result.get("overall_score", 0),
                "personality_score": analysis_result.get("personality_score", 0),
                "tonality_score": analysis_result.get("tonality_score", 0),
                "dos_alignment": analysis_result.get("dos_alignment", 0),
                "donts_alignment": analysis_result.get("donts_alignment", 0),
                "issue_count": len(analysis_result.get("highlighted_sections", [])),
                "highlighted_sections": analysis_result.get("highlighted_sections", [])[:3]  # Limit to top 3 issues
            })
    
    # Sort results by overall score (highest first)
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    
    return {
        "success": True,
        "comparison_results": results,
        "best_match": results[0] if results else None
    }


@router.post("/batch-analyze", response_model=Dict[str, Any])
async def batch_analyze_content(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze multiple content items against a brand voice.
    
    This endpoint is useful for analyzing a batch of content items (e.g., social media posts)
    against a single brand voice to ensure consistency.
    """
    # Extract request data
    content_items = request.get("content_items", [])
    brand_voice_id = request.get("brand_voice_id")
    options = request.get("options", {})
    
    # Validate required fields
    if not content_items or not isinstance(content_items, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one content item is required"
        )
    
    if not brand_voice_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand voice ID is required"
        )
    
    # Limit the number of content items to analyze
    if len(content_items) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum of 10 content items can be analyzed at once"
        )
    
    # Verify that the brand voice exists and the user has access
    db_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
    if not db_voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand voice not found"
        )
    
    # Check if user belongs to the tenant or is an admin
    if current_user.tenant_id != db_voice.tenant_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this brand voice"
        )
    
    # Convert database model to dictionary for the agent
    brand_voice_dict = {
        "id": db_voice.id,
        "name": db_voice.name,
        "description": db_voice.description,
        "voice_metadata": db_voice.voice_metadata,
        "dos": db_voice.dos,
        "donts": db_voice.donts,
        "tenant_id": db_voice.tenant_id
    }
    
    # Set simplified options for batch analysis to speed up processing
    batch_options = {
        "analysis_depth": options.get("analysis_depth", "basic"),
        "include_suggestions": options.get("include_suggestions", True),
        "highlight_issues": True,
        "max_suggestions": options.get("max_suggestions", 3),
        "generate_report": False
    }
    
    # Analyze each content item
    results = []
    for i, content_item in enumerate(content_items):
        # Extract content and metadata
        content = content_item.get("content", "")
        content_id = content_item.get("id", f"item_{i+1}")
        content_type = content_item.get("type", "text")
        
        if not content:
            results.append({
                "content_id": content_id,
                "success": False,
                "error": "Content is empty",
                "analysis_result": None
            })
            continue
        
        # Invoke the analysis agent
        result = await invoke_analysis_agent(
            content=content,
            brand_voice=brand_voice_dict,
            options=batch_options,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id
        )
        
        # Add to results
        results.append({
            "content_id": content_id,
            "content_type": content_type,
            "success": result.get("success", False),
            "error": result.get("error"),
            "analysis_result": result.get("analysis_result")
        })
    
    # Calculate aggregate statistics
    successful_analyses = [r for r in results if r.get("success", False)]
    avg_overall_score = sum(r.get("analysis_result", {}).get("overall_score", 0) for r in successful_analyses) / len(successful_analyses) if successful_analyses else 0
    
    return {
        "success": True,
        "batch_results": results,
        "summary": {
            "total_items": len(content_items),
            "successful_analyses": len(successful_analyses),
            "failed_analyses": len(content_items) - len(successful_analyses),
            "average_overall_score": avg_overall_score
        }
    }
