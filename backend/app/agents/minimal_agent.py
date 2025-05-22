"""
Minimal Brand Voice Agent - Simplified version that works with Pydantic v2
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import os

from pydantic import BaseModel, Field
import openai

from app.db.database import SessionLocal
from app.models.models import BrandVoice, BrandVoiceStatus
from app.agents.config import get_llm, BRAND_VOICE_AGENT_PROMPT, CONTENT_GENERATOR_PROMPT, ANALYZER_PROMPT

# Get OpenAI API key from environment
import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

class BrandVoiceRequest(BaseModel):
    """Request model for brand voice operations."""
    message: str
    user_id: str
    tenant_id: str
    brand_voice_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class BrandVoiceResponse(BaseModel):
    """Response model for brand voice operations."""
    status: str
    action: Optional[str] = None
    message: str
    result: Optional[Dict[str, Any]] = None

def create_brand_voice(
    name: str, 
    description: str, 
    tenant_id: str,
    user_id: str,
    personality: Optional[str] = None,
    tonality: Optional[str] = None,
    dos: Optional[str] = None,
    donts: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new brand voice."""
    print(f"Creating brand voice with name: {name}")
    
    # Create a database session
    db = SessionLocal()
    try:
        # Create a new brand voice object
        voice_metadata = {
            "personality": personality,
            "tonality": tonality
        }
        
        # Create the brand voice in the database
        db_voice = BrandVoice(
            name=name,
            description=description,
            voice_metadata=voice_metadata,
            dos=dos,
            donts=donts,
            status=BrandVoiceStatus.DRAFT,
            tenant_id=tenant_id,
            created_by_id=user_id
        )
        
        # Add to database and commit
        db.add(db_voice)
        db.commit()
        db.refresh(db_voice)
        
        print(f"Successfully created brand voice with ID: {db_voice.id}")
        
        # Return the created brand voice
        return {
            "id": db_voice.id,
            "name": db_voice.name,
            "description": db_voice.description,
            "status": db_voice.status.value,
            "version": db_voice.version,
            "created_at": db_voice.created_at.isoformat() if db_voice.created_at else None,
            "voice_metadata": db_voice.voice_metadata,
            "dos": db_voice.dos,
            "donts": db_voice.donts
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating brand voice: {str(e)}")
        return {"error": f"Failed to create brand voice: {str(e)}"}
    finally:
        db.close()

def generate_content(
    prompt: str, 
    brand_voice_id: Optional[str] = None,
    content_type: Optional[str] = None
) -> Dict[str, Any]:
    """Generate content using a brand voice."""
    print(f"Generating content for brand voice ID: {brand_voice_id}")
    print(f"Prompt: {prompt}")
    
    # Get brand voice data from the database
    db = SessionLocal()
    try:
        if not brand_voice_id:
            print("No brand voice ID provided, using default content generation")
            brand_voice = None
        else:
            # Query the database for the brand voice
            db_brand_voice = db.query(BrandVoice).filter(BrandVoice.id == brand_voice_id).first()
            
            if not db_brand_voice:
                print(f"Brand voice with ID {brand_voice_id} not found")
                return {"error": f"Brand voice with ID {brand_voice_id} not found"}
            
            # Convert database model to dictionary for use in prompt
            brand_voice = {
                "id": db_brand_voice.id,
                "name": db_brand_voice.name,
                "description": db_brand_voice.description,
                "voice_metadata": db_brand_voice.voice_metadata,
                "dos": db_brand_voice.dos,
                "donts": db_brand_voice.donts
            }
        
        # Construct the system prompt
        system_prompt = "You are a content generator that writes in a specific brand voice."
        
        if brand_voice:
            system_prompt += f"\n\nBrand Voice: {brand_voice['name']}\n"
            system_prompt += f"Description: {brand_voice['description']}\n"
            
            if brand_voice.get('voice_metadata'):
                metadata = brand_voice['voice_metadata']
                if metadata.get('personality'):
                    system_prompt += f"Personality: {metadata['personality']}\n"
                if metadata.get('tonality'):
                    system_prompt += f"Tonality: {metadata['tonality']}\n"
            
            if brand_voice.get('dos'):
                system_prompt += f"\nDos:\n{brand_voice['dos']}\n"
            
            if brand_voice.get('donts'):
                system_prompt += f"\nDon'ts:\n{brand_voice['donts']}\n"
        
        # Add content type if provided
        if content_type:
            system_prompt += f"\nGenerate content in the format of a {content_type}.\n"
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract the generated content
        generated_content = response['choices'][0]['message']['content']
        
        return {
            "content": generated_content,
            "brand_voice_id": brand_voice_id if brand_voice else None,
            "prompt": prompt,
            "content_type": content_type
        }
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        return {"error": f"Failed to generate content: {str(e)}"}
    finally:
        db.close()

def analyze_content(content: str) -> Dict[str, Any]:
    """Analyze content to extract brand voice characteristics."""
    print(f"Analyzing content: {content[:100]}...")
    
    try:
        # Construct the system prompt
        system_prompt = """
        You are a content analyzer that extracts brand voice characteristics from text.
        Analyze the provided content and extract the following:
        - Personality traits
        - Tone of voice
        - Writing style
        - Key phrases or expressions
        - Dos and don'ts
        
        Format your response as a JSON object with these keys.
        """
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract the analysis
        analysis_text = response['choices'][0]['message']['content']
        
        # Try to parse as JSON
        try:
            # Extract JSON if it's wrapped in markdown code blocks
            if "```json" in analysis_text:
                json_str = analysis_text.split("```json")[1].split("```")[0].strip()
                analysis = json.loads(json_str)
            else:
                # Otherwise try to parse the whole response
                analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # If parsing fails, return the raw text
            analysis = {
                "raw_analysis": analysis_text,
                "note": "Could not parse as JSON"
            }
        
        return analysis
    except Exception as e:
        print(f"Error analyzing content: {str(e)}")
        return {"error": f"Failed to analyze content: {str(e)}"}

def invoke_brand_voice_agent(
    message: str,
    user_id: str,
    tenant_id: str,
    brand_voice_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Invoke the brand voice agent with a user message."""
    context = context or {}
    print(f"Invoking brand voice agent with message: {message[:50]}...")
    print(f"Brand voice ID: {brand_voice_id}")
    print(f"Context: {context}")
    
    # Check if there's a forced intent in the context
    forced_intent = context.get("force_intent")
    
    if forced_intent == "generate_content":
        # Direct content generation
        result = generate_content(
            prompt=message,
            brand_voice_id=brand_voice_id,
            content_type=context.get("content_type")
        )
        
        return {
            "status": "success" if "error" not in result else "error",
            "action": "generate_content",
            "result": result,
            "message": result.get("content", result.get("error", "Content generation completed"))
        }
    
    elif forced_intent == "analyze_content":
        # Direct content analysis
        full_content = context.get("full_content", message)
        result = analyze_content(full_content)
        
        return {
            "status": "success" if "error" not in result else "error",
            "action": "analyze_content",
            "result": result,
            "message": "Content analysis completed"
        }
    
    else:
        # Classify intent using OpenAI
        system_prompt = """
        You are an intent classifier for a brand voice system. Classify the user's message into one of these categories:
        - create_brand_voice: User wants to create a new brand voice
        - generate_content: User wants to generate content using a brand voice
        - analyze_content: User wants to analyze content to extract brand voice characteristics
        - unknown: None of the above
        
        Respond with ONLY the intent category name.
        """
        
        try:
            # Call OpenAI API for intent classification
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                max_tokens=20
            )
            
            # Extract the intent
            intent = response['choices'][0]['message']['content'].strip().lower()
            
            # Process based on intent
            if intent == "create_brand_voice":
                # Extract parameters using OpenAI
                param_prompt = """
                Extract the following parameters for creating a brand voice from the user's message:
                - name: The name of the brand voice
                - description: A description of the brand voice
                - personality: The personality traits (optional)
                - tonality: The tone of voice (optional)
                - dos: Things to do in this brand voice (optional)
                - donts: Things to avoid in this brand voice (optional)
                
                Format your response as a JSON object with these keys.
                """
                
                param_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": param_prompt},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                
                # Extract the parameters
                param_text = param_response['choices'][0]['message']['content']
                
                # Try to parse as JSON
                try:
                    # Extract JSON if it's wrapped in markdown code blocks
                    if "```json" in param_text:
                        json_str = param_text.split("```json")[1].split("```")[0].strip()
                        params = json.loads(json_str)
                    else:
                        # Otherwise try to parse the whole response
                        params = json.loads(param_text)
                except json.JSONDecodeError:
                    # If parsing fails, use default values
                    params = {
                        "name": "New Brand Voice",
                        "description": "Brand voice created from user message"
                    }
                
                # Create the brand voice
                result = create_brand_voice(
                    name=params.get("name", "New Brand Voice"),
                    description=params.get("description", "Brand voice created from user message"),
                    tenant_id=tenant_id,
                    user_id=user_id,
                    personality=params.get("personality"),
                    tonality=params.get("tonality"),
                    dos=params.get("dos"),
                    donts=params.get("donts")
                )
                
                return {
                    "status": "success" if "error" not in result else "error",
                    "action": "create_brand_voice",
                    "result": result,
                    "message": f"Created brand voice: {params.get('name', 'New Brand Voice')}"
                }
            
            elif intent == "generate_content":
                # Generate content
                result = generate_content(
                    prompt=message,
                    brand_voice_id=brand_voice_id,
                    content_type=context.get("content_type")
                )
                
                return {
                    "status": "success" if "error" not in result else "error",
                    "action": "generate_content",
                    "result": result,
                    "message": result.get("content", result.get("error", "Content generation completed"))
                }
            
            elif intent == "analyze_content":
                # Analyze content
                result = analyze_content(message)
                
                return {
                    "status": "success" if "error" not in result else "error",
                    "action": "analyze_content",
                    "result": result,
                    "message": "Content analysis completed"
                }
            
            else:
                # Unknown intent, generate a conversational response
                conv_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant for a brand voice system."},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                # Extract the response
                response_text = conv_response['choices'][0]['message']['content']
                
                return {
                    "status": "success",
                    "action": "conversation",
                    "result": {"content": response_text},
                    "message": response_text
                }
                
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing message: {str(e)}"
            }
