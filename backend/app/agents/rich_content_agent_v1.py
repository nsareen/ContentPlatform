"""
Rich Content Agent - Agent for generating rich media content (text + images)
Using patterns compatible with Pydantic v1
"""

from typing import Dict, List, Any, Union, Optional, Tuple
import json
import inspect
from datetime import datetime
import base64
import os
import re

from langchain.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.tools.base import BaseTool, Tool
from langchain.agents import AgentExecutor, LLMSingleActionAgent
import openai

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
class RichAgentState(dict):
    """State for the rich content agent workflow."""
    def __init__(self, 
                 messages: List[Dict[str, Any]],
                 user_id: str,
                 tenant_id: str,
                 current_brand_voice_id: str = "",
                 intent: str = "",
                 context: Dict[str, Any] = None,
                 generated_images: List[Dict[str, Any]] = None):
        super().__init__()
        self["messages"] = messages
        self["user_id"] = user_id
        self["tenant_id"] = tenant_id
        self["current_brand_voice_id"] = current_brand_voice_id
        self["intent"] = intent
        self["context"] = context or {}
        self["generated_images"] = generated_images or []


# Define tool functions
def generate_image(
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
        
        # Set the OpenAI API key
        openai.api_key = OPENAI_API_KEY
        
        # Prepare parameters based on the model
        params = {
            "prompt": description,
            "size": size,
            "n": 1
        }
        
        # Add model-specific parameters
        if model == "dall-e-3":
            params["model"] = "dall-e-3"
            params["quality"] = quality
            params["style"] = style
        else:
            # For older OpenAI version, we can only use dall-e-2
            params["model"] = "dall-e-2"
        
        # Log the request parameters
        print(f"Generating image with parameters: {params}")
        
        # Make the API call
        response = openai.Image.create(**params)
        
        # Process the response
        if 'data' in response and len(response['data']) > 0:
            image_data = response['data'][0]
            
            result = {
                "description": description,
                "model": params["model"],
                "size": size
            }
            
            # Add the image data based on the requested format
            if 'url' in image_data:
                result["url"] = image_data['url']
            elif 'b64_json' in image_data:
                result["b64_json"] = image_data['b64_json']
            else:
                print(f"WARNING: Unexpected response format: {image_data}")
                return {"error": "Unexpected response format from image generation API"}
            
            print(f"Successfully generated image: {result.get('url', 'b64_json data')[:30]}...")
            return result
        else:
            print("ERROR: No image data returned from API")
            return {"error": "No image data returned from API"}
    
    except Exception as e:
        print(f"ERROR generating image: {str(e)}")
        return {"error": f"Failed to generate image: {str(e)}"}


def generate_rich_content(prompt: str, brand_voice_id: str = None, content_type: str = "flyer") -> Dict[str, Any]:
    """Generate rich content using the specified brand voice."""
    print(f"Generating rich content with prompt: {prompt[:50]}...")
    print(f"Brand voice ID: {brand_voice_id}")
    print(f"Content type: {content_type}")
    
    # Get tenant_id from the current state
    tenant_id = "default-tenant"
    
    # Try to get the state from the calling frame
    frame = inspect.currentframe()
    try:
        if frame and frame.f_back and 'state' in frame.f_back.f_locals:
            state = frame.f_back.f_locals['state']
            if isinstance(state, dict):
                tenant_id = state.get('tenant_id', tenant_id)
                # If brand_voice_id is not provided, try to get it from the state
                if not brand_voice_id and state.get('current_brand_voice_id'):
                    brand_voice_id = state.get('current_brand_voice_id')
                    print(f"Using brand_voice_id from state: {brand_voice_id}")
    finally:
        del frame  # Avoid reference cycles
    
    # If no brand voice ID is provided, generate generic content
    if not brand_voice_id:
        return {"error": "Brand voice ID is required for rich content generation"}
    
    # Create a database session
    db = SessionLocal()
    try:
        # Get the brand voice from the database without tenant filtering
        # This allows admin users to access brand voices from any tenant
        db_voice = db.query(BrandVoice).filter(
            BrandVoice.id == brand_voice_id
        ).first()
        
        if not db_voice:
            print(f"Brand voice not found with ID: {brand_voice_id}")
            return {"error": f"Brand voice not found with ID: {brand_voice_id}"}
        
        # Prepare the brand voice data for the prompt
        brand_voice_data = {
            "name": db_voice.name,
            "description": db_voice.description,
            "personality": db_voice.voice_metadata.get("personality", "") if db_voice.voice_metadata else "",
            "tonality": db_voice.voice_metadata.get("tonality", "") if db_voice.voice_metadata else "",
            "dos": db_voice.dos or "",
            "donts": db_voice.donts or ""
        }
        
        # Create the prompt for the content generator
        content_prompt = ChatPromptTemplate.from_messages([
            ("system", RICH_CONTENT_GENERATOR_PROMPT),
            ("human", """
            Generate rich content for the following:
            
            Content Type: {content_type}
            Prompt: {prompt}
            """)
        ])
        
        # Format the prompt with the brand voice data and user prompt
        formatted_prompt = content_prompt.format_messages(
            brand_voice_details=json.dumps(brand_voice_data, indent=2),
            content_type=content_type,
            prompt=prompt
        )
        
        # Get the LLM
        llm = get_llm()
        
        # Generate the content
        response = llm.invoke(formatted_prompt)
        generated_content = response.content
        
        print(f"Generated content: {generated_content[:100]}...")
        
        # Extract image descriptions from the content
        image_descriptions = _extract_image_descriptions(generated_content)
        
        # Return the generated content
        return {
            "text_content": generated_content,
            "brand_voice_id": brand_voice_id,
            "brand_voice_name": db_voice.name,
            "content_type": content_type,
            "image_descriptions": image_descriptions
        }
    except Exception as e:
        print(f"Error generating rich content: {str(e)}")
        return {"error": f"Failed to generate rich content: {str(e)}"}
    finally:
        db.close()


def _extract_image_descriptions(content: str) -> List[str]:
    """Extract image descriptions from the generated content."""
    print("Extracting image descriptions from content...")
    
    # List to store extracted image descriptions
    image_descriptions = []
    
    # Pattern 1: Look for sections labeled as image descriptions
    pattern1 = r"(?i)(?:image|img)(?:\s+description|\s+desc)?(?:\s*\d*\s*)?:\s*([^\n]+)"
    matches1 = re.findall(pattern1, content)
    
    # Pattern 2: Look for markdown image syntax
    pattern2 = r"!\[([^\]]+)\]\([^)]*\)"
    matches2 = re.findall(pattern2, content)
    
    # Pattern 3: Look for numbered image descriptions
    pattern3 = r"(?i)(?:image|img)\s*\d+\s*:\s*([^\n]+)"
    matches3 = re.findall(pattern3, content)
    
    # Pattern 4: Look for sections enclosed in triple backticks with image or img in the label
    pattern4 = r"```(?:image|img)[^`]*```"
    matches4 = re.findall(pattern4, content)
    
    # Process matches from pattern 4
    for match in matches4:
        # Remove the backticks and the label
        clean_match = match.replace("```image", "").replace("```img", "").replace("```", "").strip()
        if clean_match:
            image_descriptions.append(clean_match)
    
    # Pattern 5: Look for HTML-like image tags
    pattern5 = r"<(?:image|img)[^>]*>([^<]+)</(?:image|img)>"
    matches5 = re.findall(pattern5, content)
    
    # Combine all matches
    all_matches = matches1 + matches2 + matches3 + matches5
    
    # Add unique matches to the image_descriptions list
    for match in all_matches:
        match = match.strip()
        if match and match not in image_descriptions:
            image_descriptions.append(match)
    
    # If no matches were found, look for sections that might be image descriptions
    if not image_descriptions:
        # Look for lines that might be image descriptions
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # Check if the line contains keywords that suggest it's an image description
            if (len(line) > 20 and  # Reasonably long
                ('image' in line.lower() or 'visual' in line.lower() or 'picture' in line.lower()) and
                not line.startswith('#') and  # Not a heading
                not line.startswith('>')):  # Not a quote
                image_descriptions.append(line)
    
    # If still no matches, use the first paragraph as an image description
    if not image_descriptions:
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if paragraphs:
            first_para = paragraphs[0]
            # Only use if it's a reasonable length
            if 20 <= len(first_para) <= 1000:
                image_descriptions.append(first_para)
    
    # Log the extracted descriptions
    print(f"Extracted {len(image_descriptions)} image descriptions:")
    for i, desc in enumerate(image_descriptions):
        print(f"  {i+1}. {desc[:50]}...")
    
    return image_descriptions


# Intent classification function
def classify_intent(message: str) -> str:
    """Classify the user's intent based on their message."""
    print(f"Classifying intent for message: {message[:50]}...")
    
    # For rich content agent, we only have one intent: generate_rich_content
    # But we'll keep the intent classification for consistency with other agents
    
    # Create a prompt for intent classification
    intent_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an intent classifier for a rich content system. Your job is to determine the user's intent
        based on their message. The possible intents are:
        
        1. generate_rich_content - User wants to generate rich content (text + images)
        2. conversation - User is just having a conversation or asking a question
        
        Respond with ONLY the intent name, nothing else.
        """),
        ("human", "{message}")
    ])
    
    # Format the prompt with the message
    formatted_prompt = intent_prompt.format_messages(
        message=message
    )
    
    # Get the LLM
    llm = get_llm()
    
    try:
        # Classify the intent
        response = llm.invoke(formatted_prompt)
        intent = response.content.strip().lower()
        
        # Map to valid intents
        valid_intents = ["generate_rich_content", "conversation"]
        if intent not in valid_intents:
            intent = "generate_rich_content"  # Default to rich content generation
        
        print(f"Classified intent: {intent}")
        return intent
    except Exception as e:
        print(f"Error classifying intent: {str(e)}")
        return "generate_rich_content"  # Default to rich content generation


# Create tools
generate_image_tool = Tool(
    name="generate_image",
    description="Generate an image based on a description using OpenAI's image generation models.",
    func=generate_image
)

generate_rich_content_tool = Tool(
    name="generate_rich_content",
    description="Generate rich content (text and image descriptions) for marketing materials.",
    func=generate_rich_content
)

# List of tools
tools = [
    generate_image_tool,
    generate_rich_content_tool
]


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
    print(f"Invoking rich content agent with message: {message[:50]}...")
    print(f"Brand voice ID: {brand_voice_id}")
    print(f"Content type: {content_type}")
    print(f"Context: {context}")
    
    # Classify the intent
    intent = classify_intent(message)
    
    # Create the state
    state = RichAgentState(
        messages=[{"role": "user", "content": message}],
        user_id=user_id,
        tenant_id=tenant_id,
        current_brand_voice_id=brand_voice_id or "",
        intent=intent,
        context=context or {},
        generated_images=[]
    )
    
    try:
        # Process based on intent
        if intent == "generate_rich_content":
            # Create a prompt to extract content generation details
            extract_prompt = ChatPromptTemplate.from_messages([
                ("system", """
                Extract the details for generating rich content from the user's message.
                Return a JSON object with the following fields:
                - prompt: The prompt for generating content
                - content_type: (optional) The type of content to generate (e.g., flyer, social media post, email)
                
                If any field is not provided, leave it as null.
                """),
                ("human", "{message}")
            ])
            
            # Format the prompt with the message
            formatted_prompt = extract_prompt.format_messages(
                message=message
            )
            
            # Get the LLM
            llm = get_llm()
            
            # Extract the details
            response = llm.invoke(formatted_prompt)
            details_text = response.content
            
            try:
                # Parse the details
                details = json.loads(details_text)
                
                # Generate the rich content
                result = generate_rich_content(
                    prompt=details.get("prompt", message),
                    brand_voice_id=brand_voice_id,
                    content_type=details.get("content_type", content_type)
                )
                
                # Add the result to the state
                state["generate_rich_content_result"] = result
                
                # Check if there was an error
                if "error" in result:
                    error_msg = result["error"]
                    state["messages"].append({"role": "assistant", "content": f"Error: {error_msg}"})
                    return {
                        "status": "error",
                        "message": error_msg
                    }
                
                # Generate images for each image description
                generated_images = []
                image_descriptions = result.get("image_descriptions", [])
                
                for description in image_descriptions:
                    # Generate the image
                    image_result = generate_image(
                        description=description,
                        model="gpt-image-1"  # Use GPT-Image model
                    )
                    
                    # Check if there was an error
                    if "error" in image_result:
                        print(f"Error generating image: {image_result['error']}")
                        continue
                    
                    # Add the image to the list
                    generated_images.append(image_result)
                
                # Add the generated images to the state
                state["generated_images"] = generated_images
                
                # Create a response message
                response_message = result.get("text_content", "I've generated rich content for you.")
                state["messages"].append({"role": "assistant", "content": response_message})
                
                # If no images were generated, add a detailed error message
                if not generated_images and image_descriptions:
                    print("\n" + "!" * 80)
                    print("WARNING: IMAGE GENERATION FAILED")
                    print("!" * 80)
                    print("No images were generated. This might be due to API key limitations.")
                    print("Project-based API keys (sk-proj-...) may not have access to image generation APIs.")
                    print("Consider using a standard API key (sk-...) for image generation.")
                    print("!" * 80 + "\n")
                    
                    # Add a detailed error message to the result
                    state["image_generation_error"] = "Failed to generate images. Your API key may not have access to image generation APIs. Project-based API keys (sk-proj-...) typically don't work with DALL-E or GPT Image generation."
                
                # Return the result
                result_dict = {
                    "status": "success",
                    "action": "generate_rich_content",
                    "result": {
                        "text_content": result.get("text_content", ""),
                        "images": generated_images,
                        "content_type": result.get("content_type", "flyer"),
                        "image_descriptions": image_descriptions
                    },
                    "message": response_message
                }
                
                # Add image generation error if present
                if "image_generation_error" in state:
                    result_dict["result"]["image_generation_error"] = state["image_generation_error"]
                
                return result_dict
            
            except json.JSONDecodeError:
                # If parsing fails, use the original message as the prompt
                result = generate_rich_content(
                    prompt=message,
                    brand_voice_id=brand_voice_id,
                    content_type=content_type
                )
                
                # Add the result to the state
                state["generate_rich_content_result"] = result
                
                # Check if there was an error
                if "error" in result:
                    error_msg = result["error"]
                    state["messages"].append({"role": "assistant", "content": f"Error: {error_msg}"})
                    return {
                        "status": "error",
                        "message": error_msg
                    }
                
                # Generate images for each image description
                generated_images = []
                image_descriptions = result.get("image_descriptions", [])
                
                for description in image_descriptions:
                    # Generate the image
                    image_result = generate_image(
                        description=description,
                        model="gpt-image-1"  # Use GPT-Image model
                    )
                    
                    # Check if there was an error
                    if "error" in image_result:
                        print(f"Error generating image: {image_result['error']}")
                        continue
                    
                    # Add the image to the list
                    generated_images.append(image_result)
                
                # Add the generated images to the state
                state["generated_images"] = generated_images
                
                # Create a response message
                response_message = result.get("text_content", "I've generated rich content for you.")
                state["messages"].append({"role": "assistant", "content": response_message})
                
                # If no images were generated, add a detailed error message
                if not generated_images and image_descriptions:
                    print("\n" + "!" * 80)
                    print("WARNING: IMAGE GENERATION FAILED")
                    print("!" * 80)
                    print("No images were generated. This might be due to API key limitations.")
                    print("Project-based API keys (sk-proj-...) may not have access to image generation APIs.")
                    print("Consider using a standard API key (sk-...) for image generation.")
                    print("!" * 80 + "\n")
                    
                    # Add a detailed error message to the result
                    state["image_generation_error"] = "Failed to generate images. Your API key may not have access to image generation APIs. Project-based API keys (sk-proj-...) typically don't work with DALL-E or GPT Image generation."
                
                # Return the result
                result_dict = {
                    "status": "success",
                    "action": "generate_rich_content",
                    "result": {
                        "text_content": result.get("text_content", ""),
                        "images": generated_images,
                        "content_type": result.get("content_type", "flyer"),
                        "image_descriptions": image_descriptions
                    },
                    "message": response_message
                }
                
                # Add image generation error if present
                if "image_generation_error" in state:
                    result_dict["result"]["image_generation_error"] = state["image_generation_error"]
                
                return result_dict
        
        else:  # conversation
            # Create a prompt for general conversation
            conversation_prompt = ChatPromptTemplate.from_messages([
                ("system", BRAND_VOICE_AGENT_PROMPT),
                ("human", "{message}")
            ])
            
            # Format the prompt with the message
            formatted_prompt = conversation_prompt.format_messages(
                message=message
            )
            
            # Get the LLM
            llm = get_llm()
            
            # Generate the response
            response = llm.invoke(formatted_prompt)
            response_message = response.content
            
            # Add the response to the state
            state["messages"].append({"role": "assistant", "content": response_message})
            
            return {
                "status": "success",
                "action": "conversation",
                "message": response_message
            }
    
    except Exception as e:
        print(f"Error running agent: {str(e)}")
        return {"status": "error", "message": f"Error running rich content agent: {str(e)}"}
