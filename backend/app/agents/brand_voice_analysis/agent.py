"""
Brand Voice Analysis Agent using LangGraph.

This module implements a LangGraph-based agent for analyzing content against brand voice guidelines.
It provides detailed analysis, scoring, and suggestions for improving content alignment with brand voice.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple, Callable

from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agents.config import get_llm
from app.agents.brand_voice_analysis.state import BrandVoiceAnalysisState
from app.agents.brand_voice_analysis.nodes import (
    ContentAnalyzerNode,
    EvidenceCollectorNode,
    ScoreCalculatorNode,
    SuggestionGeneratorNode,
    AnalysisReportNode
)


def create_brand_voice_analysis_agent(llm=None) -> StateGraph:
    """Create a brand voice analysis agent using LangGraph.
    
    Args:
        llm: Optional language model to use. If not provided, will use the default from config.
    
    Returns:
        A LangGraph StateGraph for brand voice analysis.
    """
    # Initialize the language model
    llm = llm or get_llm()
    
    # Initialize nodes
    content_analyzer = ContentAnalyzerNode(llm)
    evidence_collector = EvidenceCollectorNode(llm)
    score_calculator = ScoreCalculatorNode(llm)
    suggestion_generator = SuggestionGeneratorNode(llm)
    analysis_report = AnalysisReportNode(llm)
    
    # Create the graph
    workflow = StateGraph(BrandVoiceAnalysisState)
    
    # Add nodes
    workflow.add_node("content_analyzer", content_analyzer)
    workflow.add_node("evidence_collector", evidence_collector)
    workflow.add_node("score_calculator", score_calculator)
    workflow.add_node("suggestion_generator", suggestion_generator)
    workflow.add_node("analysis_report", analysis_report)
    
    # Define edges
    workflow.add_edge("content_analyzer", "evidence_collector")
    workflow.add_edge("evidence_collector", "score_calculator")
    workflow.add_edge("score_calculator", "suggestion_generator")
    workflow.add_edge("suggestion_generator", "analysis_report")
    workflow.add_edge("analysis_report", END)
    
    # Set the entry point
    workflow.set_entry_point("content_analyzer")
    
    # Compile the graph
    return workflow.compile()


async def invoke_analysis_agent(
    content: str,
    brand_voice: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None
) -> Dict[str, Any]:
    """Invoke the brand voice analysis agent to analyze content against brand voice guidelines.
    
    Args:
        content: The content to analyze
        brand_voice: The brand voice to analyze against
        options: Optional analysis options
        user_id: Optional user ID for tracking
        tenant_id: Optional tenant ID for tracking
    
    Returns:
        Analysis results including scores, issues, suggestions, and a report
    """
    # Create default options if not provided
    if options is None:
        options = {
            "analysis_depth": "standard",
            "include_suggestions": True,
            "highlight_issues": True,
            "max_suggestions": 5,
            "generate_report": True
        }
    
    # Create the agent
    agent = create_brand_voice_analysis_agent()
    
    # Create initial state
    initial_state: BrandVoiceAnalysisState = {
        "content": content,
        "brand_voice": brand_voice,
        "options": options,
        "user_id": user_id or "",
        "tenant_id": tenant_id or "",
        "analysis_stage": "initialized",
        "messages": []
    }
    
    try:
        # Invoke the agent
        result = await agent.ainvoke(initial_state)
        
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
            "error": f"Error invoking brand voice analysis agent: {str(e)}",
            "analysis_result": None
        }
