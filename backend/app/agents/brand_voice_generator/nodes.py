"""
Node implementations for the Brand Voice Generator.
"""

import json
import uuid
from typing import Dict, List, Any, Callable, Tuple, Optional

from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from app.agents.brand_voice_generator.state import (
    BrandVoiceGeneratorState,
    GenerationDepth,
    ContentType,
    BrandVoiceComponentType
)
from app.agents.brand_voice_generator.prompts import (
    CONTENT_ANALYZER_PROMPT,
    PERSONALITY_EXTRACTOR_PROMPT,
    TONALITY_DEFINER_PROMPT,
    IDENTITY_GENERATOR_PROMPT,
    DOS_GENERATOR_PROMPT,
    DONTS_GENERATOR_PROMPT,
    SAMPLE_CONTENT_GENERATOR_PROMPT,
    BRAND_VOICE_ASSEMBLER_PROMPT
)
from app.agents.config import get_llm


def analyze_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze content to identify brand voice characteristics."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract content and metadata
        content = state["content"]
        brand_name = state["brand_name"]
        industry = state["industry"]
        target_audience = state["target_audience"]
        options = state.get("options", {})
        analysis_depth = options.get("analysis_depth", "standard")
        
        # Create system prompt
        system_prompt = CONTENT_ANALYZER_PROMPT.format(
            brand_name=brand_name,
            industry=industry,
            target_audience=target_audience,
            analysis_depth=analysis_depth
        )
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please analyze this content: {content}")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Store the content analysis in state
        state["content_analysis"] = {
            "text": response.content,
            "content_type": detect_content_type(content, response.content)
        }
        
        # Update state
        state["generation_stage"] = "content_analyzed"
        
        # Add messages to state for debugging/logging
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append({
            "role": "system",
            "content": "Content analyzed successfully."
        })
        
        return state
    except Exception as e:
        # Handle errors
        state["error"] = f"Error in content analyzer: {str(e)}"
        state["messages"] = state.get("messages", []) + [{
            "role": "system",
            "content": f"Error in content analyzer: {str(e)}"
        }]
        return state


def detect_content_type(content: str, analysis: str) -> str:
    """Detect the type of content based on the content and analysis."""
    content_lower = content.lower()
    analysis_lower = analysis.lower()
    
    # Check for product description indicators
    if any(term in content_lower or term in analysis_lower for term in 
           ["product", "feature", "specification", "benefit", "use case"]):
        return ContentType.PRODUCT_DESCRIPTION
    
    # Check for marketing copy indicators
    elif any(term in content_lower or term in analysis_lower for term in 
             ["campaign", "promotion", "offer", "limited time", "exclusive"]):
        return ContentType.MARKETING_COPY
    
    # Check for website content indicators
    elif any(term in content_lower or term in analysis_lower for term in 
             ["website", "page", "about us", "mission", "vision", "company"]):
        return ContentType.WEBSITE_CONTENT
    
    # Check for social media indicators
    elif any(term in content_lower or term in analysis_lower for term in 
             ["post", "tweet", "instagram", "facebook", "linkedin", "follow", "like", "share"]):
        return ContentType.SOCIAL_MEDIA
    
    # Default to general
    else:
        return ContentType.GENERAL


def extract_personality_traits(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract personality traits from content analysis."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        content_analysis = state["content_analysis"]["text"]
        brand_name = state["brand_name"]
        industry = state["industry"]
        target_audience = state["target_audience"]
        
        # Create system prompt
        system_prompt = PERSONALITY_EXTRACTOR_PROMPT.format(
            content_analysis=content_analysis,
            brand_name=brand_name,
            industry=industry,
            target_audience=target_audience
        )
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Extract the personality traits from this content analysis.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Parse personality traits from response
        personality_traits = parse_personality_traits(response.content)
        
        # Update state
        state["brand_voice_components"]["personality_traits"] = personality_traits
        state["generation_stage"] = "personality_traits_extracted"
        
        # Add messages to state for debugging/logging
        state["messages"].append({
            "role": "system",
            "content": f"Extracted {len(personality_traits)} personality traits."
        })
        
        return state
    except Exception as e:
        # Handle errors
        state["error"] = f"Error in personality traits extractor: {str(e)}"
        state["messages"].append({
            "role": "system",
            "content": f"Error in personality traits extractor: {str(e)}"
        })
        return state


def parse_personality_traits(response_text: str) -> List[str]:
    """Parse personality traits from LLM response."""
    traits = []
    
    # Simple parsing logic - extract traits from response
    lines = response_text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for trait markers like numbers, bullets, or trait names followed by colons
        if (line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "•", "-", "*")) or 
            any(trait in line.lower() for trait in ["confident", "friendly", "professional", "casual", 
                                                   "formal", "playful", "serious", "authoritative", 
                                                   "approachable", "innovative", "traditional"])):
            # Extract the trait name (first word or phrase before any explanation)
            trait = line.split(":", 1)[0] if ":" in line else line
            # Clean up the trait by removing numbers, bullets, etc.
            trait = trait.lstrip("123456789.-•* ").strip()
            # If the trait is too long, it's probably not just the trait name
            if len(trait.split()) <= 3:
                traits.append(trait)
    
    # If no traits were found using the above method, try a simpler approach
    if not traits:
        # Look for single words that might be traits
        words = response_text.split()
        for word in words:
            word = word.strip().rstrip(",.;:").lower()
            if word in ["confident", "friendly", "professional", "casual", "formal", 
                        "playful", "serious", "authoritative", "approachable", 
                        "innovative", "traditional"]:
                traits.append(word)
    
    # Deduplicate traits
    traits = list(dict.fromkeys(traits))
    
    # Limit to 7 traits
    return traits[:7]


def define_tonality(state: Dict[str, Any]) -> Dict[str, Any]:
    """Define the brand voice tonality based on personality traits."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        personality_traits = state["brand_voice_components"]["personality_traits"]
        brand_name = state["brand_name"]
        industry = state["industry"]
        target_audience = state["target_audience"]
        
        # Create system prompt
        system_prompt = TONALITY_DEFINER_PROMPT.format(
            personality_traits=", ".join(personality_traits),
            brand_name=brand_name,
            industry=industry,
            target_audience=target_audience
        )
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Define the tonality for this brand voice.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Update state
        state["brand_voice_components"]["tonality"] = response.content.strip()
        state["generation_stage"] = "tonality_defined"
        
        # Add messages to state for debugging/logging
        state["messages"].append({
            "role": "system",
            "content": "Tonality defined successfully."
        })
        
        return state
    except Exception as e:
        # Handle errors
        state["error"] = f"Error in tonality definer: {str(e)}"
        state["messages"].append({
            "role": "system",
            "content": f"Error in tonality definer: {str(e)}"
        })
        return state


def generate_identity(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the brand identity description."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        personality_traits = state["brand_voice_components"]["personality_traits"]
        tonality = state["brand_voice_components"]["tonality"]
        brand_name = state["brand_name"]
        industry = state["industry"]
        target_audience = state["target_audience"]
        
        # Create system prompt
        system_prompt = IDENTITY_GENERATOR_PROMPT.format(
            personality_traits=", ".join(personality_traits),
            tonality=tonality,
            brand_name=brand_name,
            industry=industry,
            target_audience=target_audience
        )
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate the brand identity description.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Update state
        state["brand_voice_components"]["identity"] = response.content.strip()
        state["generation_stage"] = "identity_generated"
        
        # Add messages to state for debugging/logging
        state["messages"].append({
            "role": "system",
            "content": "Brand identity generated successfully."
        })
        
        return state
    except Exception as e:
        # Handle errors
        state["error"] = f"Error in identity generator: {str(e)}"
        state["messages"].append({
            "role": "system",
            "content": f"Error in identity generator: {str(e)}"
        })
        return state


def generate_dos(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the do's guidelines for the brand voice."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        personality_traits = state["brand_voice_components"]["personality_traits"]
        tonality = state["brand_voice_components"]["tonality"]
        identity = state["brand_voice_components"]["identity"]
        brand_name = state["brand_name"]
        industry = state["industry"]
        target_audience = state["target_audience"]
        
        # Create system prompt
        system_prompt = DOS_GENERATOR_PROMPT.format(
            personality_traits=", ".join(personality_traits),
            tonality=tonality,
            identity=identity,
            brand_name=brand_name,
            industry=industry,
            target_audience=target_audience
        )
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate the do's guidelines for this brand voice.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Parse do's from response
        dos = parse_guidelines(response.content)
        
        # Update state
        state["brand_voice_components"]["dos"] = dos
        state["generation_stage"] = "dos_generated"
        
        # Add messages to state for debugging/logging
        state["messages"].append({
            "role": "system",
            "content": f"Generated {len(dos)} do's guidelines."
        })
        
        return state
    except Exception as e:
        # Handle errors
        state["error"] = f"Error in do's generator: {str(e)}"
        state["messages"].append({
            "role": "system",
            "content": f"Error in do's generator: {str(e)}"
        })
        return state


def generate_donts(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate the don'ts guidelines for the brand voice."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        personality_traits = state["brand_voice_components"]["personality_traits"]
        tonality = state["brand_voice_components"]["tonality"]
        identity = state["brand_voice_components"]["identity"]
        brand_name = state["brand_name"]
        industry = state["industry"]
        target_audience = state["target_audience"]
        
        # Create system prompt
        system_prompt = DONTS_GENERATOR_PROMPT.format(
            personality_traits=", ".join(personality_traits),
            tonality=tonality,
            identity=identity,
            brand_name=brand_name,
            industry=industry,
            target_audience=target_audience
        )
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate the don'ts guidelines for this brand voice.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Parse don'ts from response
        donts = parse_guidelines(response.content)
        
        # Update state
        state["brand_voice_components"]["donts"] = donts
        state["generation_stage"] = "donts_generated"
        
        # Add messages to state for debugging/logging
        state["messages"].append({
            "role": "system",
            "content": f"Generated {len(donts)} don'ts guidelines."
        })
        
        return state
    except Exception as e:
        # Handle errors
        state["error"] = f"Error in don'ts generator: {str(e)}"
        state["messages"].append({
            "role": "system",
            "content": f"Error in don'ts generator: {str(e)}"
        })
        return state


def parse_guidelines(response_text: str) -> List[str]:
    """Parse guidelines (do's or don'ts) from LLM response."""
    guidelines = []
    
    # Simple parsing logic - extract guidelines from response
    lines = response_text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for guideline markers like numbers, bullets, etc.
        if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "•", "-", "*")):
            # Clean up the guideline by removing numbers, bullets, etc.
            guideline = line.lstrip("123456789.-•* ").strip()
            guidelines.append(guideline)
    
    # If no guidelines were found using the above method, try splitting by periods
    if not guidelines:
        sentences = response_text.split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and len(sentence) < 200:  # Reasonable length for a guideline
                guidelines.append(sentence)
    
    # Limit to 8 guidelines
    return guidelines[:8]


def generate_sample_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate sample content that exemplifies the brand voice."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        personality_traits = state["brand_voice_components"]["personality_traits"]
        tonality = state["brand_voice_components"]["tonality"]
        identity = state["brand_voice_components"]["identity"]
        dos = state["brand_voice_components"]["dos"]
        donts = state["brand_voice_components"]["donts"]
        brand_name = state["brand_name"]
        industry = state["industry"]
        target_audience = state["target_audience"]
        
        # Create system prompt
        system_prompt = SAMPLE_CONTENT_GENERATOR_PROMPT.format(
            personality_traits=", ".join(personality_traits),
            tonality=tonality,
            identity=identity,
            dos="\n".join([f"- {do_item}" for do_item in dos]),
            donts="\n".join([f"- {dont_item}" for dont_item in donts]),
            brand_name=brand_name,
            industry=industry,
            target_audience=target_audience
        )
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate sample content that exemplifies this brand voice.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Update state
        state["brand_voice_components"]["sample_content"] = response.content.strip()
        state["generation_stage"] = "sample_content_generated"
        
        # Add messages to state for debugging/logging
        state["messages"].append({
            "role": "system",
            "content": "Sample content generated successfully."
        })
        
        return state
    except Exception as e:
        # Handle errors
        state["error"] = f"Error in sample content generator: {str(e)}"
        state["messages"].append({
            "role": "system",
            "content": f"Error in sample content generator: {str(e)}"
        })
        return state


def assemble_brand_voice(state: Dict[str, Any]) -> Dict[str, Any]:
    """Assemble the complete brand voice profile and perform final validation."""
    try:
        # Get the LLM
        llm = get_llm()
        
        # Extract data from state
        personality_traits = state["brand_voice_components"]["personality_traits"]
        tonality = state["brand_voice_components"]["tonality"]
        identity = state["brand_voice_components"]["identity"]
        dos = state["brand_voice_components"]["dos"]
        donts = state["brand_voice_components"]["donts"]
        sample_content = state["brand_voice_components"]["sample_content"]
        brand_name = state["brand_name"]
        industry = state["industry"]
        target_audience = state["target_audience"]
        
        # Create system prompt
        system_prompt = BRAND_VOICE_ASSEMBLER_PROMPT.format(
            personality_traits=", ".join(personality_traits),
            tonality=tonality,
            identity=identity,
            dos="\n".join([f"- {do_item}" for do_item in dos]),
            donts="\n".join([f"- {dont_item}" for dont_item in donts]),
            sample_content=sample_content,
            brand_name=brand_name,
            industry=industry,
            target_audience=target_audience
        )
        
        # Create messages for LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Review and finalize this brand voice profile.")
        ]
        
        # Get response from LLM
        response = llm.invoke(messages)
        
        # Create the generation metadata
        generation_metadata = {
            "content_type": state["content_analysis"].get("content_type", ContentType.GENERAL),
            "brand_name": brand_name,
            "industry": industry,
            "target_audience": target_audience,
            "generation_assessment": response.content.strip(),
            "timestamp": str(uuid.uuid1())
        }
        
        # Update state
        state["generation_metadata"] = generation_metadata
        state["generation_stage"] = "completed"
        
        # Add messages to state for debugging/logging
        state["messages"].append({
            "role": "system",
            "content": "Brand voice profile assembled successfully."
        })
        
        return state
    except Exception as e:
        # Handle errors
        state["error"] = f"Error in brand voice assembler: {str(e)}"
        state["messages"].append({
            "role": "system",
            "content": f"Error in brand voice assembler: {str(e)}"
        })
        return state
