"""
State definitions for the Brand Voice Analyzer.
"""

from typing import Dict, List, Any, Optional, TypedDict, Union
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


# Define the state as a dict subclass for LangGraph compatibility
class BrandVoiceAnalyzerState(dict):
    """State for the brand voice analyzer workflow."""
    def __init__(self, 
                 content: str,
                 brand_voice: Dict[str, Any],
                 options: Dict[str, Any] = None,
                 user_id: str = "",
                 tenant_id: str = ""):
        super().__init__()
        self["content"] = content
        self["brand_voice"] = brand_voice
        self["options"] = options or {}
        self["user_id"] = user_id
        self["tenant_id"] = tenant_id
        self["analysis_stage"] = "initialized"
        self["messages"] = []
        self["issues"] = []
        self["suggestions"] = []
        self["scores"] = {}
        self["evidence"] = {}
        self["analysis_result"] = {}
        self["error"] = None
        self["intent"] = "analyze"
