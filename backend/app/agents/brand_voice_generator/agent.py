"""
Brand Voice Generator Agent using LangGraph.

This module implements a LangGraph-based agent for generating brand voice profiles from sample content.
It extracts personality traits, tonality, and guidelines to create a comprehensive brand voice.
"""

import json
from typing import Dict, List, Any, TypedDict, Literal, Union, Optional, Tuple

from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import BaseTool, StructuredTool, tool
from langgraph.graph import StateGraph, END

from app.agents.config import get_llm
from app.agents.brand_voice_generator.state import BrandVoiceGeneratorState
from app.agents.brand_voice_generator.nodes import (
    analyze_content,
    extract_personality_traits,
    define_tonality,
    generate_identity,
    generate_dos,
    generate_donts,
    generate_sample_content,
    assemble_brand_voice
)


def create_brand_voice_generator():
    """Create a brand voice generator workflow graph.
    
    Returns:
        A LangGraph StateGraph for brand voice generation.
    """
    # Create the workflow with a dict type for state
    workflow = StateGraph(Dict)
    
    # Add nodes
    workflow.add_node("analyze_content", analyze_content)
    workflow.add_node("extract_personality_traits", extract_personality_traits)
    workflow.add_node("define_tonality", define_tonality)
    workflow.add_node("generate_identity", generate_identity)
    workflow.add_node("generate_dos", generate_dos)
    workflow.add_node("generate_donts", generate_donts)
    workflow.add_node("generate_sample_content", generate_sample_content)
    workflow.add_node("assemble_brand_voice", assemble_brand_voice)
    
    # Define edges
    workflow.add_edge("analyze_content", "extract_personality_traits")
    workflow.add_edge("extract_personality_traits", "define_tonality")
    workflow.add_edge("define_tonality", "generate_identity")
    workflow.add_edge("generate_identity", "generate_dos")
    workflow.add_edge("generate_dos", "generate_donts")
    workflow.add_edge("generate_donts", "generate_sample_content")
    workflow.add_edge("generate_sample_content", "assemble_brand_voice")
    workflow.add_edge("assemble_brand_voice", END)
    
    # Set the entry point
    workflow.set_entry_point("analyze_content")
    
    return workflow


# Initialize the agent
try:
    brand_voice_generator = create_brand_voice_generator().compile()
    print("Brand voice generator initialized successfully")
except Exception as e:
    print(f"Error initializing brand voice generator: {str(e)}")
    brand_voice_generator = None


def invoke_generator(
    content: str,
    brand_name: Optional[str] = None,
    industry: Optional[str] = None,
    target_audience: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None
) -> Dict[str, Any]:
    """Invoke the brand voice generator to create a brand voice profile from sample content.
    
    Args:
        content: The sample content to analyze
        brand_name: Optional brand name
        industry: Optional industry
        target_audience: Optional target audience
        options: Optional generation options
        user_id: Optional user ID for tracking
        tenant_id: Optional tenant ID for tracking
    
    Returns:
        Generated brand voice components including personality traits, tonality, and guidelines
    """
    # Check if agent is initialized
    if brand_voice_generator is None:
        return {
            "success": False,
            "error": "Brand voice generator is not initialized",
            "brand_voice_components": None
        }
    
    # Create default options if not provided
    if options is None:
        options = {
            "generation_depth": "standard",
            "include_sample_content": True
        }
    
    # Create initial state
    initial_state = BrandVoiceGeneratorState(
        content=content,
        brand_name=brand_name,
        industry=industry,
        target_audience=target_audience,
        options=options,
        user_id=user_id or "",
        tenant_id=tenant_id or ""
    )
    
    # Convert to dict to ensure compatibility with LangGraph
    initial_state_dict = dict(initial_state)
    
    try:
        # Invoke the agent
        result = brand_voice_generator.invoke(initial_state_dict)
        
        # Check for errors
        if "error" in result and result["error"]:
            return {
                "success": False,
                "error": result["error"],
                "brand_voice_components": None
            }
        
        # Format the brand voice components for the response
        brand_voice_components = result.get("brand_voice_components", {})
        generation_metadata = result.get("generation_metadata", {})
        
        # Return the generation result
        return {
            "success": True,
            "brand_voice_components": brand_voice_components,
            "generation_metadata": generation_metadata,
            "messages": result.get("messages", [])
        }
    except Exception as e:
        # Handle any exceptions
        return {
            "success": False,
            "error": f"Error invoking brand voice generator: {str(e)}",
            "brand_voice_components": None
        }
