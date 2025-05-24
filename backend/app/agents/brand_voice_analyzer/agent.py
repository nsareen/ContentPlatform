"""
Brand Voice Analyzer Agent using LangGraph.

This module implements a LangGraph-based agent for analyzing content against brand voice guidelines.
It provides detailed analysis, scoring, and suggestions for improving content alignment with brand voice.
"""

import json
from typing import Dict, List, Any, TypedDict, Literal, Union, Optional, Tuple

from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import BaseTool, StructuredTool, tool
from langgraph.graph import StateGraph, END
# Removed problematic import: from langgraph.prebuilt import ToolNode

from app.agents.config import get_llm
from app.agents.brand_voice_analyzer.state import BrandVoiceAnalyzerState
from app.agents.brand_voice_analyzer.nodes import (
    classify_intent,
    analyze_content,
    collect_evidence,
    calculate_scores,
    generate_suggestions,
    generate_report
)


def create_brand_voice_analyzer():
    """Create a brand voice analyzer workflow graph.
    
    Returns:
        A LangGraph StateGraph for brand voice analysis.
    """
    # Create the workflow with a dict type for state
    workflow = StateGraph(Dict)
    
    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("analyze_content", analyze_content)
    workflow.add_node("collect_evidence", collect_evidence)
    workflow.add_node("calculate_scores", calculate_scores)
    workflow.add_node("generate_suggestions", generate_suggestions)
    workflow.add_node("generate_report", generate_report)
    
    # Define edges
    workflow.add_edge("classify_intent", "analyze_content")
    workflow.add_edge("analyze_content", "collect_evidence")
    workflow.add_edge("collect_evidence", "calculate_scores")
    workflow.add_edge("calculate_scores", "generate_suggestions")
    workflow.add_edge("generate_suggestions", "generate_report")
    workflow.add_edge("generate_report", END)
    
    # Set the entry point
    workflow.set_entry_point("classify_intent")
    
    return workflow


# Initialize the agent
try:
    brand_voice_analyzer = create_brand_voice_analyzer().compile()
    print("Brand voice analyzer initialized successfully")
except Exception as e:
    print(f"Error initializing brand voice analyzer: {str(e)}")
    brand_voice_analyzer = None


def invoke_analyzer(
    content: str,
    brand_voice: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None
) -> Dict[str, Any]:
    """Invoke the brand voice analyzer to analyze content against brand voice guidelines.
    
    Args:
        content: The content to analyze
        brand_voice: The brand voice to analyze against
        options: Optional analysis options
        user_id: Optional user ID for tracking
        tenant_id: Optional tenant ID for tracking
    
    Returns:
        Analysis results including scores, issues, suggestions, and a report
    """
    # Check if agent is initialized
    if brand_voice_analyzer is None:
        return {
            "success": False,
            "error": "Brand voice analyzer is not initialized",
            "analysis_result": None
        }
    
    # Create default options if not provided
    if options is None:
        options = {
            "analysis_depth": "standard",
            "include_suggestions": True,
            "highlight_issues": True,
            "max_suggestions": 5,
            "generate_report": True
        }
    
    # Create initial state
    # Initialize with the expected structure for LangGraph
    initial_state = BrandVoiceAnalyzerState(
        content=content,
        brand_voice=brand_voice,
        options=options,
        user_id=user_id or "",
        tenant_id=tenant_id or ""
    )
    
    # Convert to dict to ensure compatibility with LangGraph
    initial_state_dict = dict(initial_state)
    
    try:
        # Invoke the agent
        result = brand_voice_analyzer.invoke(initial_state_dict)
        
        # Check for errors
        if "error" in result and result["error"]:
            return {
                "success": False,
                "error": result["error"],
                "analysis_result": None
            }
        
        # Return the analysis result
        return {
            "success": True,
            "analysis_result": result.get("analysis_result", {}),
            "messages": result.get("messages", [])
        }
    except Exception as e:
        # Handle any exceptions
        return {
            "success": False,
            "error": f"Error invoking brand voice analyzer: {str(e)}",
            "analysis_result": None
        }
