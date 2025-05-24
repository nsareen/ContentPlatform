"""
State definitions for the Brand Voice Generator.
"""

from typing import Dict, List, Any, Optional, TypedDict, Union
from enum import Enum


class GenerationDepth(str, Enum):
    """Depth of generation to perform."""
    BASIC = "basic"       # Basic brand voice generation
    STANDARD = "standard" # Standard brand voice generation with detailed components
    DETAILED = "detailed" # In-depth brand voice generation with extensive guidelines


class ContentType(str, Enum):
    """Types of content that can be used for brand voice generation."""
    PRODUCT_DESCRIPTION = "product_description"
    MARKETING_COPY = "marketing_copy"
    WEBSITE_CONTENT = "website_content"
    SOCIAL_MEDIA = "social_media"
    GENERAL = "general"


class BrandVoiceComponentType(str, Enum):
    """Components of a brand voice that can be generated."""
    PERSONALITY = "personality"
    TONALITY = "tonality"
    DOS = "dos"
    DONTS = "donts"
    IDENTITY = "identity"
    SAMPLE_CONTENT = "sample_content"


# Define the state as a dict subclass for LangGraph compatibility
class BrandVoiceGeneratorState(dict):
    """State for the brand voice generator workflow."""
    def __init__(self, 
                 content: str,
                 brand_name: Optional[str] = None,
                 industry: Optional[str] = None,
                 target_audience: Optional[str] = None,
                 options: Dict[str, Any] = None,
                 user_id: str = "",
                 tenant_id: str = ""):
        super().__init__()
        self["content"] = content
        self["brand_name"] = brand_name or ""
        self["industry"] = industry or ""
        self["target_audience"] = target_audience or ""
        self["options"] = options or {}
        self["user_id"] = user_id
        self["tenant_id"] = tenant_id
        self["generation_stage"] = "initialized"
        self["messages"] = []
        self["content_analysis"] = {}
        self["brand_voice_components"] = {
            "personality_traits": [],
            "tonality": "",
            "identity": "",
            "dos": [],
            "donts": [],
            "sample_content": ""
        }
        self["generation_metadata"] = {}
        self["error"] = None
