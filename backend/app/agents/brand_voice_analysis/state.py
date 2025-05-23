"""
State definitions for the Brand Voice Analysis agent.
"""

from typing import Dict, List, Any, Optional, TypedDict, Union
from pydantic import BaseModel, Field
from enum import Enum


class AnalysisDepth(str, Enum):
    """Depth of analysis to perform."""
    BASIC = "basic"       # Quick analysis, high-level feedback
    STANDARD = "standard" # Comprehensive analysis
    DETAILED = "detailed" # In-depth analysis with extensive suggestions


class IssueType(str, Enum):
    """Types of issues that can be identified in content."""
    PERSONALITY_MISMATCH = "personality_mismatch"
    TONALITY_MISMATCH = "tonality_mismatch"
    DOS_VIOLATION = "dos_violation"
    DONTS_VIOLATION = "donts_violation"
    STYLE_INCONSISTENCY = "style_inconsistency"
    GENERAL = "general"


class SuggestionCategory(str, Enum):
    """Categories of suggestions for content improvement."""
    PERSONALITY = "personality"
    TONALITY = "tonality"
    DOS = "dos"
    DONTS = "donts"
    STYLE = "style"
    GENERAL = "general"


class ContentIssue(BaseModel):
    """An issue identified in the content."""
    start_index: int
    end_index: int
    text: str
    issue_type: IssueType
    explanation: str
    severity: float = Field(default=0.5, ge=0.0, le=1.0)


class ContentSuggestion(BaseModel):
    """A suggestion for improving content."""
    id: str
    original_text: str
    suggested_text: str
    explanation: str
    category: SuggestionCategory
    priority: int = Field(default=1, ge=1, le=3)  # 1=high, 2=medium, 3=low


class AnalysisOptions(BaseModel):
    """Options for content analysis."""
    analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD
    include_suggestions: bool = True
    highlight_issues: bool = True
    max_suggestions: int = 5


class BrandVoiceAnalysisState(TypedDict, total=False):
    """State for the brand voice analysis agent workflow."""
    # Input data
    content: str
    brand_voice: Dict[str, Any]
    options: Dict[str, Any]
    user_id: str
    tenant_id: str
    
    # Processing state
    analysis_stage: str
    messages: List[Dict[str, Any]]
    
    # Analysis results
    issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    scores: Dict[str, float]
    evidence: Dict[str, List[str]]
    
    # Final output
    analysis_result: Dict[str, Any]
    error: Optional[str]
