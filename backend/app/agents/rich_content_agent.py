"""
Rich Content Agent - Agent for generating rich media content (text + images)
Using modern LangGraph patterns with structured tools
"""

from typing import Dict, List, Any, TypedDict, Literal, Union, Optional, Tuple
import json
import inspect
from datetime import datetime
import base64
import os
import re

from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import BaseTool, StructuredTool, tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from openai import OpenAI

from app.db.database import SessionLocal
from app.models.models import BrandVoice, BrandVoiceStatus
from app.agents.config import get_llm, BRAND_VOICE_AGENT_PROMPT

# Define the system prompt for the rich content generator
RICH_CONTENT_GENERATOR_PROMPT = """You are a marketing content creator specialized in generating rich media content.
Your task is to create compelling marketing materials that combine text and images.

For the given brand voice and prompt, you will:
1. Generate appropriate marketing copy that follows the brand voice guidelines
2. Create image descriptions that will be used to generate visuals
3. Format the content in a way that's suitable for the requested marketing material type

Brand Voice Details:
{brand_voice_details}

Content Type: {content_type}
User Prompt: {prompt}

Remember to maintain the brand's tone, personality, and adhere to the dos and don'ts.
"""

# Define state types
class RichAgentState(TypedDict):
    """State for the rich content agent workflow."""
    messages: List[Dict[str, Any]]
    user_id: str
    tenant_id: str
    current_brand_voice_id: str
    intent: str
    context: Dict[str, Any]
    generated_images: List[Dict[str, Any]]


# Define structured tools using the StructuredTool class
class GenerateImageTool(BaseTool):
    name: str = "generate_image"
    description: str = "Generate an image based on a description using OpenAI's image generation models."
    
    def _run(
        self, 
        description: str, 
        style: str = "natural", 
        size: str = "1024x1024",
        quality: str = "standard",
        model: str = "gpt-image-1",
        format: str = "url",
        background: str = "opaque"
    ) -> Dict[str, Any]:
        """Generate an image based on the provided description.
        
        Args:
            description: Text description of the desired image
            style: For DALL-E 3, must be 'vivid' or 'natural'. For GPT-Image, ignored.
            size: Image dimensions (e.g., '1024x1024', '1024x1536')
            quality: Rendering quality ('standard'/'hd' for DALL-E 3, 'low'/'medium'/'high' for GPT-Image)
            model: Model to use ('dall-e-3' or 'gpt-image-1' if available)
            format: Response format ('url' or 'b64_json')
            background: Background type ('opaque' or 'transparent' - transparent only works with png format)
        """
        print(f"Generating image with description: {description[:50]}...")
        
        try:
            # Import the API key from config.py
            from app.agents.config import OPENAI_API_KEY
            
            # Check if we have a valid API key
            if not OPENAI_API_KEY:
                print("ERROR: OpenAI API key not found in config")
                return {"error": "OpenAI API key not found in configuration"}
                
            print(f"Using OpenAI API key from config: {OPENAI_API_KEY[:5]}...")
            
            # Initialize OpenAI client with the API key from config
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Prepare parameters based on the model
            params = {
                "model": model,
                "prompt": description,
                "size": size,
                "n": 1,
                "response_format": format
            }
            
            # Add model-specific parameters
            if model == "dall-e-3":
                if style in ["vivid", "natural"]:
                    params["style"] = style
                params["quality"] = "hd" if quality == "high" else "standard"
            elif model == "gpt-image-1":
                # Remove response_format for gpt-image-1 as it's not supported
                if "response_format" in params:
                    del params["response_format"]
                
                # Map standard/hd to medium/high for gpt-image-1
                if quality == "standard":
                    params["quality"] = "medium"
                elif quality == "high" or quality == "hd":
                    params["quality"] = "high"
                elif quality == "low":
                    params["quality"] = "low"
                else:
                    # Default to medium quality
                    params["quality"] = "medium"
                    
                # Handle transparent background
                if background == "transparent" and format in ["png", "webp"]:
                    params["background"] = "transparent"
            
            # Generate image
            print("\n" + "=" * 80)
            print("IMAGE GENERATION - FULL PARAMETERS:")
            print("=" * 80)
            print(f"Model: {model}")
            print(f"Size: {size}")
            print(f"Quality: {quality if 'quality' in params else 'N/A'}")
            print(f"Style: {style if 'style' in params else 'N/A'}")
            print(f"Format: {format if 'response_format' in params else 'N/A'}")
            print("\nFULL PROMPT:")
            print("-" * 80)
            print(description)
            print("-" * 80)
            print("\nAPI CALL PARAMETERS:")
            for key, value in params.items():
                if key != 'prompt':  # Skip printing the prompt again
                    print(f"{key}: {value}")
            print("=" * 80 + "\n")
            
            # Make the API call
            print(f"Calling OpenAI images.generate API...")
            response = client.images.generate(**params)
            
            # Process response based on format
            if format == "url":
                image_data = response.data[0].url
                # Log the URL for debugging
                print(f"Generated image URL: {image_data}")
            else:  # b64_json
                image_data = response.data[0].b64_json
            
            print(f"Successfully generated image with model {model}")
            
            return {
                "image_data": image_data,
                "format": format,
                "description": description,
                "style": style,
                "size": size,
                "model": model
            }
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return {"error": f"Failed to generate image: {str(e)}"}
    
    async def _arun(
        self, 
        description: str, 
        style: str = "natural", 
        size: str = "1024x1024",
        quality: str = "standard",
        model: str = "gpt-image-1",
        format: str = "url",
        background: str = "opaque"
    ) -> Dict[str, Any]:
        """Async implementation of generate_image."""
        return self._run(description, style, size, quality, model, format, background)


class GenerateRichContentTool(BaseTool):
    name: str = "generate_rich_content"
    description: str = "Generate rich content (text and image descriptions) for marketing materials."
    
    def _run(self, prompt: str, brand_voice_id: str = None, content_type: str = "flyer") -> Dict[str, Any]:
        """Generate rich content using the specified brand voice."""
        print(f"Generating rich content with prompt: {prompt[:50]}...")
        
        # Get tenant_id and user_id from the current state
        tenant_id = "default-tenant"
        user_id = "default-user"
        
        # Try to get the state from the calling frame
        frame = inspect.currentframe()
        try:
            if frame and frame.f_back and 'state' in frame.f_back.f_locals:
                state = frame.f_back.f_locals['state']
                if isinstance(state, dict):
                    if 'tenant_id' in state and state['tenant_id']:
                        tenant_id = state['tenant_id']
                    if 'user_id' in state and state['user_id']:
                        user_id = state['user_id']
                    print(f"Using tenant_id: {tenant_id} and user_id: {user_id} from state")
        except Exception as e:
            print(f"Error getting state from frame: {str(e)}")
        
        # Initialize the LLM
        llm = get_llm()
        
        # Create a database session
        db = SessionLocal()
        try:
            # Get the brand voice from the database
            brand_voice = None
            if brand_voice_id:
                brand_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
            
            # Prepare brand voice details for the prompt
            brand_voice_details = "No specific brand voice selected."
            if brand_voice:
                brand_voice_details = f"""
                Name: {brand_voice.name}
                Description: {brand_voice.description}
                Personality: {brand_voice.voice_metadata.get('personality', 'Not specified')}
                Tonality: {brand_voice.voice_metadata.get('tonality', 'Not specified')}
                Dos: {brand_voice.dos or 'Not specified'}
                Don'ts: {brand_voice.donts or 'Not specified'}
                """
            
            # Create the prompt for the LLM
            formatted_prompt = RICH_CONTENT_GENERATOR_PROMPT.format(
                brand_voice_details=brand_voice_details,
                content_type=content_type,
                prompt=prompt
            )
            
            # Log the full system prompt and user message
            print("\n" + "=" * 80)
            print("RICH CONTENT GENERATION - SYSTEM PROMPT:")
            print("=" * 80)
            print(formatted_prompt)
            print("=" * 80)
            
            print("\n" + "=" * 80)
            print("RICH CONTENT GENERATION - USER MESSAGE:")
            print("=" * 80)
            print(prompt)
            print("=" * 80 + "\n")
            
            # Log the user prompt
            print("\n" + "=" * 80)
            print("RICH CONTENT GENERATION - USER PROMPT:")
            print("=" * 80)
            print(prompt)
            print("=" * 80 + "\n")
            
            # Get the LLM
            llm = get_llm()
            
            # Generate content with better error handling
            try:
                print("Calling LLM to generate rich content...")
                response = llm.invoke([SystemMessage(content=formatted_prompt), 
                                      HumanMessage(content=prompt)])
                
                # Debug the response type
                print(f"LLM response type: {type(response)}")
                
                # Check if response is a string (which would cause the error)
                if isinstance(response, str):
                    print("WARNING: LLM returned a string instead of a message object")
                    content = response
                else:
                    # Try to access the content attribute safely
                    if hasattr(response, 'content'):
                        content = response.content
                        print(f"Successfully extracted content from response: {content[:50]}...")
                        
                        # Log the full LLM response
                        print("\n" + "=" * 80)
                        print("RICH CONTENT GENERATION - LLM RESPONSE:")
                        print("=" * 80)
                        print(content)
                        print("=" * 80 + "\n")
                    else:
                        # If response doesn't have content attribute, convert to string
                        content = str(response)
                        print(f"Converted response to string: {content[:50]}...")
                        
                        # Log the full LLM response
                        print("\n" + "=" * 80)
                        print("RICH CONTENT GENERATION - LLM RESPONSE (CONVERTED):")
                        print("=" * 80)
                        print(content)
                        print("=" * 80 + "\n")
            except Exception as e:
                print(f"Exception during LLM invocation: {str(e)}")
                raise e
            
            # More robust parsing logic to extract image descriptions
            text_content = content
            image_descriptions = self._extract_image_descriptions(content)
            
            # Log the extracted image descriptions
            print("\n" + "=" * 80)
            print("EXTRACTED IMAGE DESCRIPTIONS:")
            print("=" * 80)
            print(f"Total extracted: {len(image_descriptions)}")
            for i, desc in enumerate(image_descriptions):
                print(f"\nIMAGE DESCRIPTION #{i+1}:")
                print("-" * 60)
                print(desc)
                print("-" * 60)
            print("=" * 80 + "\n")
            
            print(f"Extracted {len(image_descriptions)} image descriptions")
            for i, desc in enumerate(image_descriptions):
                print(f"  {i+1}: {desc[:100]}...")
                
            # Keep the full text content as is
            return {
                "text_content": text_content,
                "image_descriptions": image_descriptions,
                "content_type": content_type,
                "brand_voice_id": brand_voice_id if brand_voice_id else None
            }
        except Exception as e:
            print(f"Error generating rich content: {str(e)}")
            return {"error": f"Failed to generate rich content: {str(e)}"}
        finally:
            db.close()
    
    def _extract_image_descriptions(self, content: str) -> List[str]:
        """Extract image descriptions from the generated content."""
        image_descriptions = []
        
        # Define regex patterns to extract image descriptions
        patterns = [
            # Pattern 1: **Image Description:** text
            r"\*\*(?:Image|Main Image|Feature Image|Lifestyle Image) Description(?:s)?:\*\*\s*([^\n]+(?:\n[^\n*]+)*)",
            
            # Pattern 1.1: **Image Description:** followed by numbered list
            r"\*\*Image Description(?:s)?:\*\*\s*\n\s*(\d+\.\s*[^\n]+(?:\n\s*\d+\.\s*[^\n]+)*)",
            
            # Pattern 1.2: **Image Descriptions:** section with numbered items
            r"\*\*Image Descriptions?:\*\*\s*\n\n((?:\d+\. \*\*Image \d+:\*\* [^\n]+\n\n)+)",
            
            # Pattern 2: **Image Descriptions:** followed by numbered list
            r"\*\*Image Descriptions?:\*\*\s*\n\s*\d+\.\s*([^\n]+(?:\n[^\n*]+)*)",
            
            # Pattern 3: **Main Image:** text (numbered image descriptions)
            r"\*\*(?:Main|Feature|Lifestyle) Image:\*\*\s*([^\n]+(?:\n[^\n*]+)*)",
            
            # Pattern 4: 1. **Main Image:** text (numbered with asterisks)
            r"\d+\.\s*\*\*(?:Main|Feature|Lifestyle) Image:\*\*\s*([^\n]+(?:\n[^\n*]+)*)",
            
            # Pattern 5: 1. **Image:** text (generic numbered images)
            r"\d+\.\s*\*\*Image:\*\*\s*([^\n]+(?:\n[^\n*]+)*)",
            
            # Pattern 6: Look for any text between **Image Description** and the next **
            r"\*\*Image Description\*\*\s*([^*]+)\*\*",
            
            # Pattern 7: **Image Descriptions:** followed by numbered list with **
            r"\*\*Image Descriptions?:\*\*\s*\n\s*\d+\.\s*\*\*[^:]+:\*\*\s*([^\n]+(?:\n[^\n-]+)*)",
            
            # Pattern 8: **[Image Description]** text
            r"\*\*\[(?:Image|Main Image|Feature Image|Lifestyle Image) Description\]\*\*\s*([^\n]+(?:\n[^\n*]+)*)",
            
            # Pattern 9: **[Text Overlay on Image]** text
            r"\*\*\[Text Overlay on Image\]\*\*\s*([^\n]+(?:\n[^\n*]+)*)",
            
            # Pattern 10: Numbered image with description
            r"\d+\.\s*\*\*Image \d+:\*\*\s*([^\n]+(?:\n[^\n*]+)*)",
            
            # Pattern 11: Simple numbered list after Image Descriptions section
            r"\*\*Image Descriptions?:\*\*[^\n]*\n\n((?:\d+\. [^\n]+\n\n?)+)"
        ]
        
        # Try each pattern
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                print(f"Found {len(matches)} image descriptions with pattern {i+1}")
                
                # For patterns that return a single string with multiple numbered items
                if i in [2, 10] or "\n1. " in ''.join(matches):
                    print(f"Processing numbered list from pattern {i+1}")
                    for match in matches:
                        # Extract individual numbered items
                        numbered_items = re.findall(r"\d+\.\s*(?:\*\*Image \d+:\*\*\s*)?([^\n]+)", match)
                        if numbered_items:
                            print(f"Extracted {len(numbered_items)} individual items from numbered list")
                            image_descriptions.extend(numbered_items)
                else:
                    image_descriptions.extend(matches)
        
        # If no matches found with regex, try a more aggressive approach
        if not image_descriptions:
            print("No matches found with regex patterns, trying alternative approach")
            # Look for any section that might contain image descriptions
            image_sections = []
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if re.search(r'\*\*.*[Ii]mage.*\*\*', line):
                    # Found a potential image description section
                    section_start = i
                    section_end = i + 1
                    # Find the end of this section (next ** or end of content)
                    for j in range(i + 1, len(lines)):
                        if '**' in lines[j] and not lines[j].strip().startswith('-'):
                            section_end = j
                            break
                        section_end = j + 1
                    
                    # Extract the section content
                    section = '\n'.join(lines[section_start+1:section_end]).strip()
                    if section and len(section) > 10:  # Minimum length to be considered valid
                        image_sections.append(section)
            
            if image_sections:
                print(f"Found {len(image_sections)} potential image sections with alternative approach")
                image_descriptions.extend(image_sections)
        
        # If we still don't have image descriptions, try to extract from numbered lists
        if not image_descriptions:
            # Look for numbered lists after "Image Description:"
            sections = re.split(r"\*\*[^*]+\*\*", content)
            for i, section in enumerate(sections):
                if i > 0 and "Image Description" in sections[i-1]:
                    # Extract numbered items
                    numbered_items = re.findall(r"\d+\.\s*(?:\*\*Image \d+:\*\*\s*)?([^\n]+)", section)
                    if numbered_items:
                        print(f"Found {len(numbered_items)} numbered image descriptions")
                        image_descriptions.extend(numbered_items)
                    
            # Last resort: try to find a section that looks like image descriptions
            if not image_descriptions:
                # Look for sections with "Image" in the title followed by numbered lists
                image_section_match = re.search(r"\*\*[^*]*Image[^*]*\*\*([^*]+)\*\*", content, re.IGNORECASE | re.DOTALL)
                if image_section_match:
                    section_content = image_section_match.group(1)
                    # Extract numbered items from this section
                    numbered_items = re.findall(r"\d+\.\s*(?:\*\*Image \d+:\*\*\s*)?([^\n]+)", section_content)
                    if numbered_items:
                        print(f"Found {len(numbered_items)} image descriptions in dedicated section")
                        image_descriptions.extend(numbered_items)
    
        # Clean up the descriptions
        cleaned_descriptions = []
        for desc in image_descriptions:
            # Remove any markdown formatting
            desc = desc.strip()
            desc = re.sub(r"\*\*|\*|__|\_", "", desc)
            desc = re.sub(r"\n+", " ", desc)
            desc = re.sub(r"\s+", " ", desc)
            # Remove leading numbers (e.g., "1. ")
            desc = re.sub(r"^\d+\.\s*", "", desc)
            
            if desc and len(desc) > 10:  # Ensure minimum length
                cleaned_descriptions.append(desc)
        
        # Remove duplicates while preserving order
        unique_descriptions = []
        for desc in cleaned_descriptions:
            if desc not in unique_descriptions:
                unique_descriptions.append(desc)
        
        print(f"Extracted {len(unique_descriptions)} image descriptions")
        return unique_descriptions
    
    async def _arun(self, prompt: str, brand_voice_id: str = None, content_type: str = "flyer") -> Dict[str, Any]:
        """Async implementation of generate_rich_content."""
        return self._run(prompt, brand_voice_id, content_type)


# Intent classification function
def classify_intent(state: RichAgentState) -> RichAgentState:
    """Classify the user's intent based on their message."""
    print("Classifying intent...")
    
    # Check if intent is forced through context
    if state["context"] and "force_intent" in state["context"]:
        forced_intent = state["context"]["force_intent"]
        print(f"Using forced intent from context: {forced_intent}")
        state["intent"] = forced_intent
        return state
    
    # Get the last user message
    last_message = None
    for msg in reversed(state["messages"]):
        if msg.get("role") == "user":
            last_message = msg.get("content")
            break
    
    if not last_message:
        print("No user message found, defaulting to 'unknown' intent")
        state["intent"] = "unknown"
        return state
    
    # Simple keyword-based intent classification
    # In a real implementation, you'd want to use a more sophisticated approach
    message_lower = last_message.lower()
    
    if "generate" in message_lower and ("image" in message_lower or "picture" in message_lower):
        state["intent"] = "generate_image"
    elif "create" in message_lower and ("flyer" in message_lower or "marketing" in message_lower or "content" in message_lower):
        state["intent"] = "generate_rich_content"
    else:
        state["intent"] = "generate_rich_content"  # Default to rich content generation
    
    print(f"Classified intent: {state['intent']}")
    return state


# Router function
def route_by_intent(state: RichAgentState) -> RichAgentState:
    """Process the state based on the classified intent.
    Note: This function must return the state, not just the intent.
    The actual routing is handled by the conditional edge in the graph.
    """
    print(f"Processing intent: {state['intent']}")
    # We could do additional state processing here if needed
    return state


# Function wrappers for tool nodes to avoid tuple issues with LangGraph
def generate_image_node(state: RichAgentState) -> RichAgentState:
    """Function wrapper for the generate_image tool."""
    print("Executing generate_image_node")
    
    # Get the last user message
    last_message = None
    for msg in reversed(state["messages"]):
        if msg.get("role") == "user":
            last_message = msg.get("content")
            break
    
    if not last_message:
        state["messages"].append({"role": "assistant", "content": "I couldn't understand your request. Please provide a description for the image you want to generate."})
        return state
    
    # Get image preferences from context if available
    model = "dall-e-3"  # Default model
    quality = "standard"  # Default quality
    size = "1024x1024"  # Default size
    style = "natural"  # Default style
    format = "url"  # Default format
    
    if "context" in state:
        context = state["context"]
        if "image_model" in context:
            model = context["image_model"]
        if "image_quality" in context:
            quality = context["image_quality"]
        if "image_size" in context:
            size = context["image_size"]
        if "image_style" in context:
            style = context["image_style"]
    
    # Initialize the tool
    tool = GenerateImageTool()
    
    try:
        # Call the tool with enhanced parameters
        result = tool._run(
            description=last_message,
            style=style,
            size=size,
            quality=quality,
            model=model,
            format=format,
            background="opaque"
        )
        
        # Add the result to the state
        state["generate_image_result"] = result
        
        # Add a response message
        if "error" in result:
            state["messages"].append({"role": "assistant", "content": f"Error generating image: {result['error']}"})  
        else:
            # The URL is now in image_data field if format is 'url'
            image_url = result.get('image_data', '')
            model_name = result.get('model', model)
            state["messages"].append({
                "role": "assistant", 
                "content": f"I've generated an image based on your description using the {model_name} model. You can view it at {image_url}"
            })  
    except Exception as e:
        print(f"Error in generate_image_node: {str(e)}")
        state["messages"].append({"role": "assistant", "content": f"I encountered an error while generating the image: {str(e)}"})  
    
    # Ensure the state has the correct intent
    state["intent"] = "generate_image"
    
    return state


def generate_rich_content_node(state: RichAgentState) -> RichAgentState:
    """Function wrapper for the generate_rich_content tool."""
    print("Executing generate_rich_content_node")
    
    # Get the last user message
    last_message = None
    for msg in reversed(state["messages"]):
        if msg.get("role") == "user":
            last_message = msg.get("content")
            break
    
    if not last_message:
        state["messages"].append({"role": "assistant", "content": "I couldn't understand your request. Please provide a prompt for the content you want to generate."})
        return state
    
    # Get content type from context if available
    content_type = "flyer"
    if "context" in state and "content_type" in state["context"]:
        content_type = state["context"]["content_type"]
    
    # Initialize the tool
    tool = GenerateRichContentTool()
    
    try:
        # Call the tool
        result = tool._run(
            prompt=last_message,
            brand_voice_id=state.get("current_brand_voice_id", None),
            content_type=content_type
        )
        
        # Add the result to the state - CRITICAL: This must be set for the agent to return the correct action
        state["generate_rich_content_result"] = result
        print(f"Set generate_rich_content_result in state with {len(result.get('image_descriptions', []))} image descriptions")
        
        # Add a response message
        if "error" in result:
            state["messages"].append({"role": "assistant", "content": f"Error generating rich content: {result['error']}"})  
        else:
            response = f"I've generated the following content for your {content_type}:\n\n{result['text_content']}"
            if "image_descriptions" in result and result["image_descriptions"]:
                response += "\n\nI've also prepared image descriptions that will be used to generate visuals for your content."
            
            state["messages"].append({"role": "assistant", "content": response})  
    except Exception as e:
        print(f"Error in generate_rich_content_node: {str(e)}")
        state["messages"].append({"role": "assistant", "content": f"I encountered an error while generating rich content: {str(e)}"})  
    
    # Ensure the state has the correct intent
    state["intent"] = "generate_rich_content"
    
    return state


# Create the workflow graph
def create_rich_content_agent():
    """Create the rich content agent workflow graph."""
    # Create the workflow
    workflow = StateGraph(RichAgentState)
    
    # Add nodes
    workflow.add_node("intent_classifier", classify_intent)
    workflow.add_node("router", route_by_intent)
    workflow.add_node("generate_image", generate_image_node)
    workflow.add_node("generate_rich_content", generate_rich_content_node)
    
    # Define the edges
    workflow.add_edge("intent_classifier", "router")
    
    # Add conditional edges with proper string values
    workflow.add_conditional_edges(
        "router",
        lambda x: x["intent"],
        {
            "generate_image": "generate_image",
            "generate_rich_content": "generate_rich_content",
            "unknown": END
        }
    )
    
    # Connect tool nodes back to the end
    workflow.add_edge("generate_image", END)
    workflow.add_edge("generate_rich_content", END)
    
    # Set the entry point
    workflow.set_entry_point("intent_classifier")
    
    return workflow


# Initialize the agent
try:
    rich_content_agent = create_rich_content_agent().compile()
    print("Rich content agent initialized successfully")
except Exception as e:
    print(f"Error initializing rich content agent: {str(e)}")
    rich_content_agent = None


# Function to invoke the agent
def invoke_rich_content_agent(
    message: str,
    user_id: str,
    tenant_id: str,
    brand_voice_id: str = None,
    content_type: str = "flyer",
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Invoke the rich content agent with a user message.
    
    This function logs the entire workflow from initial request to final response,
    making it easy to debug and understand the rich content generation process.
    """
    # Log the invocation details
    print("\n" + "*" * 100)
    print("INVOKING RICH CONTENT AGENT")
    print("*" * 100)
    print(f"Invoking rich content agent with message: {message[:50]}...")
    print(f"Brand voice ID: {brand_voice_id}")
    print(f"Content type: {content_type}")
    print(f"Context: {context}")
    print("*" * 100 + "\n")
    global rich_content_agent
    
    print(f"Invoking rich content agent with message: {message[:50]}...")
    print(f"Brand voice ID: {brand_voice_id}")
    print(f"Content type: {content_type}")
    print(f"Context: {context}")
    
    # Initialize the agent if needed
    if rich_content_agent is None:
        try:
            rich_content_agent = create_rich_content_agent().compile()
            print("Rich content agent initialized successfully")
        except Exception as e:
            print(f"Error initializing rich content agent: {str(e)}")
            return {"status": "error", "message": f"Failed to initialize agent: {str(e)}"}
    
    # Create the initial state
    state = {
        "messages": [{"role": "user", "content": message}],
        "user_id": user_id,
        "tenant_id": tenant_id,
        "current_brand_voice_id": brand_voice_id,
        "intent": "",
        "context": context or {},
        "generated_images": []
    }
    
    # Invoke the agent
    try:
        print("Invoking agent...")
        final_state = rich_content_agent.invoke(state)
        print("Agent invocation complete")
        print(f"Final state intent: {final_state.get('intent', 'unknown')}")
        
        # Get the last assistant message
        response_message = ""
        for msg in reversed(final_state.get("messages", [])):
            if msg.get("role") == "assistant":
                response_message = msg.get("content", "")
                break
        
        # Handle generate_rich_content intent
        if final_state.get("intent") == "generate_rich_content":
            print("DEBUG: Handling result based on intent")
            print(f"DEBUG: Intent = {final_state.get('intent')}")
            print(f"DEBUG: Keys in final_state = {final_state.keys()}")
            
            # Get the result from the state
            if "generate_rich_content_result" in final_state:
                result = final_state["generate_rich_content_result"]
                print("DEBUG: Found generate_rich_content_result in final_state")
            else:
                # Create a result from the context if not present
                print("DEBUG: generate_rich_content_result not found in final_state, creating from context")
                result = {
                    "text_content": response_message,
                    "content_type": final_state.get("context", {}).get("content_type", "flyer"),
                    "image_descriptions": []
                }
                
                # Extract image descriptions from the response message
                if response_message:
                    tool = GenerateRichContentTool()
                    extracted_descriptions = tool._extract_image_descriptions(response_message)
                    if extracted_descriptions:
                        print(f"DEBUG: Extracted {len(extracted_descriptions)} image descriptions from response")
                        result["image_descriptions"] = extracted_descriptions
                
                # Old method of extracting image descriptions (keeping as fallback)
                if "Image Descriptions:" in response_message:
                    print("DEBUG: Extracting image descriptions from response message")
                    try:
                        # Extract the image descriptions section
                        image_section = response_message.split("Image Descriptions:")[1].split("---")[0].strip()
                        # Extract individual descriptions
                        descriptions = []
                        for line in image_section.split("\n"):
                            if line.strip() and ":**" not in line and not line.startswith("---"):
                                descriptions.append(line.strip())
                        
                        if descriptions:
                            result["image_descriptions"] = descriptions[:3]  # Limit to 3 descriptions
                            print(f"DEBUG: Extracted {len(descriptions)} image descriptions from response")
                    except Exception as e:
                        print(f"DEBUG: Error extracting image descriptions: {str(e)}")
            
            print(f"DEBUG: Result keys: {result.keys()}")
            print(f"DEBUG: Image descriptions: {result.get('image_descriptions', [])}")
            
            
            # Generate images for the image descriptions
            generated_images = []
            print(f"DEBUG: Result keys: {result.keys()}")
            print(f"DEBUG: Context: {context}")
            
            if "image_descriptions" in result and result["image_descriptions"]:
                print(f"Found {len(result['image_descriptions'])} image descriptions to generate")
                # Limit to 2 images to avoid rate limits
                image_descriptions = result["image_descriptions"][:2]
                print(f"Will generate images for these descriptions: {image_descriptions}")
                
                # Extract image descriptions directly from the text content
                tool = GenerateRichContentTool()
                extracted_descriptions = tool._extract_image_descriptions(result["text_content"])
                
                # Update the result with the extracted image descriptions
                result["image_descriptions"] = extracted_descriptions
                
                # Set image generation parameters
                # Use DALL-E 3 since we confirmed it works with the project-based API key
                image_model = "dall-e-3"  # Use DALL-E 3
                image_quality = "standard"  # standard quality for DALL-E 3
                image_size = context.get("image_size", "1024x1024")
                
                print(f"DEBUG: Image generation parameters set: model={image_model}, quality={image_quality}, size={image_size}")
                
                # Generate images
                print("DEBUG: Creating GenerateImageTool instance")
                image_tool = GenerateImageTool()
                print("DEBUG: GenerateImageTool instance created successfully")
                
                for i, desc in enumerate(image_descriptions):
                    # Skip empty or invalid descriptions
                    if not desc or desc == "**":
                        print(f"Skipping invalid description: {desc}")
                        continue
                    
                    # Try with DALL-E 3 first
                    try:
                        print(f"Generating image {i+1}/{len(image_descriptions)} with {image_model}: {desc[:50]}...")
                        image_result = image_tool._run(
                            description=desc,
                            model=image_model,
                            quality=image_quality,
                            size=image_size,
                            format="url"
                        )
                        
                        if "error" not in image_result:
                            image_url = image_result.get("image_data", "")
                            # Log the image URL for debugging
                            print(f"Adding image URL to result: {image_url}")
                            generated_images.append({
                                "url": image_url,
                                "description": desc,
                                "model": image_result.get("model", image_model)
                            })
                            print(f"Successfully generated image {i+1} with {image_model}")
                        else:
                            error_msg = image_result.get('error', 'Unknown error')
                            print(f"Error generating image with {image_model}: {error_msg}")
                            
                            # If DALL-E 3 fails, try with GPT Image
                            if image_model == "dall-e-3":
                                try:
                                    print(f"Falling back to gpt-image-1 for image {i+1}")
                                    fallback_result = image_tool._run(
                                        description=desc,
                                        model="gpt-image-1",
                                        quality="medium",
                                        size=image_size,
                                        format="url"
                                    )
                                    
                                    if "error" not in fallback_result:
                                        image_url = fallback_result.get("image_data", "")
                                        print(f"Successfully generated fallback image with gpt-image-1")
                                        generated_images.append({
                                            "url": image_url,
                                            "description": desc,
                                            "model": "gpt-image-1"
                                        })
                                    else:
                                        print(f"Fallback to gpt-image-1 also failed: {fallback_result.get('error', 'Unknown error')}")
                                except Exception as fallback_error:
                                    print(f"Exception in fallback to gpt-image-1: {str(fallback_error)}")
                    except Exception as e:
                        print(f"Exception generating image for description '{desc[:30]}...': {str(e)}")
                        
                        # Try with GPT Image as fallback
                        try:
                            print(f"Falling back to gpt-image-1 after exception")
                            fallback_result = image_tool._run(
                                description=desc,
                                model="gpt-image-1",
                                quality="medium",
                                size=image_size,
                                format="url"
                            )
                            
                            if "error" not in fallback_result:
                                image_url = fallback_result.get("image_data", "")
                                print(f"Successfully generated fallback image with gpt-image-1")
                                generated_images.append({
                                    "url": image_url,
                                    "description": desc,
                                    "model": "gpt-image-1"
                                })
                            else:
                                print(f"Fallback to gpt-image-1 also failed after exception: {fallback_result.get('error', 'Unknown error')}")
                        except Exception as fallback_error:
                            print(f"Exception in fallback to gpt-image-1 after initial exception: {str(fallback_error)}")
                            
                # If no images were generated, add a detailed error message
                if not generated_images:
                    print("\n" + "!" * 80)
                    print("WARNING: IMAGE GENERATION FAILED")
                    print("!" * 80)
                    print("No images were generated. This might be due to API key limitations.")
                    print("Project-based API keys (sk-proj-...) may not have access to image generation APIs.")
                    print("Consider using a standard API key (sk-...) for image generation.")
                    print("!" * 80 + "\n")
                    
                    # Add a detailed error message to the result
                    state["image_generation_error"] = "Failed to generate images. Your API key may not have access to image generation APIs. Project-based API keys (sk-proj-...) typically don't work with DALL-E or GPT Image generation."
            
            print(f"Generated {len(generated_images)} images for rich content")
            # Include any image generation error message
            result_dict = {
                "status": "success",
                "action": "generate_rich_content",
                "result": {
                    "text_content": result.get("text_content", ""),
                    "images": generated_images,
                    "content_type": result.get("content_type", "flyer"),
                    "image_descriptions": result.get("image_descriptions", [])
                },
                "message": response_message
            }
            
            # Add image generation error if present
            if "image_generation_error" in final_state:
                result_dict["result"]["image_generation_error"] = final_state["image_generation_error"]
            
            # Log the final result
            print("\n" + "*" * 100)
            print("RICH CONTENT AGENT - FINAL RESULT")
            print("*" * 100)
            print(f"Status: {result_dict['status']}")
            print(f"Action: {result_dict['action']}")
            print(f"Text content length: {len(result_dict['result']['text_content'])} characters")
            print(f"Number of images: {len(result_dict['result']['images'])}")
            print(f"Number of image descriptions: {len(result_dict['result']['image_descriptions'])}")
            if 'image_generation_error' in result_dict['result']:
                print(f"Image generation error: {result_dict['result']['image_generation_error']}")
            print("*" * 100 + "\n")
            
            return result_dict
        elif "error" in final_state:
            return {
                "status": "error",
                "message": final_state["error"]
            }
        else:
            # If we have a generate_rich_content_result but the intent wasn't set correctly,
            # still return a rich content response
            if "generate_rich_content_result" in final_state:
                result = final_state["generate_rich_content_result"]
                print("Intent was not set to generate_rich_content but we have a result, fixing action")
                return {
                    "status": "success",
                    "action": "generate_rich_content",
                    "result": {
                        "text_content": result.get("text_content", ""),
                        "images": [],
                        "content_type": result.get("content_type", "flyer"),
                        "image_descriptions": result.get("image_descriptions", [])
                    },
                    "message": response_message
                }
            # Default response for conversation or unknown intent
            return {
                "status": "success",
                "action": "conversation",
                "message": response_message
            }
    except Exception as e:
        print(f"Error invoking agent: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to process request: {str(e)}"
        }
