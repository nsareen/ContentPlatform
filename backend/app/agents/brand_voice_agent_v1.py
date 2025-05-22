"""
Brand Voice Agent - Main agent for handling brand voice operations
Using LangGraph patterns compatible with Pydantic v1
"""

from typing import Dict, List, Any, TypedDict, Literal, Union, Optional, Tuple
import json
import inspect
from datetime import datetime

from langchain.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.tools.base import BaseTool, Tool
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from langchain.memory import ConversationBufferMemory

from app.db.database import SessionLocal
from app.models.models import BrandVoice, BrandVoiceStatus
from app.agents.config import get_llm, BRAND_VOICE_AGENT_PROMPT, CONTENT_GENERATOR_PROMPT, ANALYZER_PROMPT


# Define state types
class AgentState(dict):
    """State for the brand voice agent workflow."""
    def __init__(self, 
                 messages: List[Dict[str, Any]],
                 user_id: str,
                 tenant_id: str,
                 current_brand_voice_id: str = "",
                 intent: str = "",
                 context: Dict[str, Any] = None):
        super().__init__()
        self["messages"] = messages
        self["user_id"] = user_id
        self["tenant_id"] = tenant_id
        self["current_brand_voice_id"] = current_brand_voice_id
        self["intent"] = intent
        self["context"] = context or {}


# Define structured tools using the Tool class
def create_brand_voice(name: str, description: str, personality: str = None, 
                       tonality: str = None, dos: str = None, donts: str = None) -> Dict[str, Any]:
    """Create a new brand voice with the given parameters."""
    print(f"Creating brand voice with name: {name}")
    
    # Get tenant_id and user_id from the current state
    tenant_id = "default-tenant"
    created_by_id = "default-user"
    
    # Try to get the state from the calling frame
    frame = inspect.currentframe()
    try:
        if frame and frame.f_back and 'state' in frame.f_back.f_locals:
            state = frame.f_back.f_locals['state']
            if isinstance(state, dict):
                tenant_id = state.get('tenant_id', tenant_id)
                created_by_id = state.get('user_id', created_by_id)
                print(f"Using tenant_id: {tenant_id} and user_id: {created_by_id} from state")
    finally:
        del frame  # Avoid reference cycles
    
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
            created_by_id=created_by_id
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


def generate_content(prompt: str, brand_voice_id: str = None, content_type: str = None) -> Dict[str, Any]:
    """Generate content using the specified brand voice."""
    print(f"Generating content with prompt: {prompt[:50]}...")
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
        return generate_fallback_content(prompt)
    
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
            return generate_fallback_content(prompt)
        
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
            ("system", CONTENT_GENERATOR_PROMPT),
            ("human", """
            Brand Voice: {brand_voice}
            
            Content Type: {content_type}
            
            Generate content for the following prompt:
            {prompt}
            """)
        ])
        
        # Format the prompt with the brand voice data and user prompt
        formatted_prompt = content_prompt.format_messages(
            brand_voice=json.dumps(brand_voice_data, indent=2),
            content_type=content_type or "general",
            prompt=prompt
        )
        
        # Get the LLM
        llm = get_llm()
        
        # Generate the content
        response = llm.invoke(formatted_prompt)
        generated_content = response.content
        
        print(f"Generated content: {generated_content[:100]}...")
        
        # Return the generated content
        return {
            "content": generated_content,
            "brand_voice_id": brand_voice_id,
            "brand_voice_name": db_voice.name,
            "content_type": content_type or "general"
        }
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        return generate_fallback_content(prompt)
    finally:
        db.close()


def analyze_content(content: str) -> Dict[str, Any]:
    """Analyze the provided content to extract brand voice characteristics."""
    print(f"Analyzing content: {content[:50]}...")
    
    try:
        # Create the prompt for the analyzer
        analyzer_prompt = ChatPromptTemplate.from_messages([
            ("system", ANALYZER_PROMPT),
            ("human", """
            Analyze the following content and extract brand voice characteristics:
            
            {content}
            """)
        ])
        
        # Format the prompt with the content
        formatted_prompt = analyzer_prompt.format_messages(
            content=content
        )
        
        # Get the LLM
        llm = get_llm()
        
        # Generate the analysis
        response = llm.invoke(formatted_prompt)
        analysis = response.content
        
        print(f"Analysis: {analysis[:100]}...")
        
        # Try to parse the analysis as JSON
        try:
            analysis_dict = json.loads(analysis)
            return analysis_dict
        except json.JSONDecodeError:
            # If parsing fails, return the raw analysis
            return {
                "raw_analysis": analysis,
                "personality": "",
                "tonality": "",
                "dos": "",
                "donts": ""
            }
    except Exception as e:
        print(f"Error analyzing content: {str(e)}")
        return {
            "error": f"Failed to analyze content: {str(e)}",
            "personality": "",
            "tonality": "",
            "dos": "",
            "donts": ""
        }


# Helper function for fallback content generation
def generate_fallback_content(prompt_text: str) -> Dict[str, Any]:
    """Generate fallback content when brand voice data is not available or LLM fails."""
    try:
        llm = get_llm()
        response = llm.invoke(f"Generate content for: {prompt_text}")
        return {
            "content": response.content,
            "brand_voice_id": None,
            "brand_voice_name": "Generic",
            "content_type": "general"
        }
    except Exception as e:
        return {
            "content": f"I'm sorry, I couldn't generate content at this time. Error: {str(e)}",
            "error": str(e)
        }


# Intent classification function
def classify_intent(message: str) -> str:
    """Classify the user's intent based on their message."""
    print(f"Classifying intent for message: {message[:50]}...")
    
    # Create a prompt for intent classification
    intent_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an intent classifier for a brand voice system. Your job is to determine the user's intent
        based on their message. The possible intents are:
        
        1. create_brand_voice - User wants to create a new brand voice
        2. generate_content - User wants to generate content using a brand voice
        3. analyze_content - User wants to analyze content to extract brand voice characteristics
        4. conversation - User is just having a conversation or asking a question
        
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
        valid_intents = ["create_brand_voice", "generate_content", "analyze_content", "conversation"]
        if intent not in valid_intents:
            intent = "conversation"
        
        print(f"Classified intent: {intent}")
        return intent
    except Exception as e:
        print(f"Error classifying intent: {str(e)}")
        return "conversation"


# Create tools
create_brand_voice_tool = Tool(
    name="create_brand_voice",
    description="Create a new brand voice based on the provided information.",
    func=create_brand_voice
)

generate_content_tool = Tool(
    name="generate_content",
    description="Generate content that adheres to a specific brand voice.",
    func=generate_content
)

analyze_content_tool = Tool(
    name="analyze_content",
    description="Analyze content to extract brand voice characteristics.",
    func=analyze_content
)

# List of tools
tools = [
    create_brand_voice_tool,
    generate_content_tool,
    analyze_content_tool
]


# Function to invoke the agent
def invoke_brand_voice_agent(
    message: str,
    user_id: str,
    tenant_id: str,
    brand_voice_id: str = None,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Invoke the brand voice agent with a user message."""
    print(f"Invoking brand voice agent with message: {message[:50]}...")
    print(f"Brand voice ID: {brand_voice_id}")
    print(f"Context: {context}")
    
    # Classify the intent
    intent = classify_intent(message)
    
    # Create the state
    state = AgentState(
        messages=[{"role": "user", "content": message}],
        user_id=user_id,
        tenant_id=tenant_id,
        current_brand_voice_id=brand_voice_id or "",
        intent=intent,
        context=context or {}
    )
    
    try:
        # Process based on intent
        if intent == "create_brand_voice":
            # Create a prompt to extract brand voice details
            extract_prompt = ChatPromptTemplate.from_messages([
                ("system", """
                Extract the details for creating a brand voice from the user's message.
                Return a JSON object with the following fields:
                - name: The name of the brand voice
                - description: A description of the brand voice
                - personality: (optional) The personality traits of the brand voice
                - tonality: (optional) The tone of the brand voice
                - dos: (optional) Things the brand voice should do
                - donts: (optional) Things the brand voice should not do
                
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
                
                # Create the brand voice
                result = create_brand_voice(
                    name=details.get("name", "Untitled Brand Voice"),
                    description=details.get("description", ""),
                    personality=details.get("personality"),
                    tonality=details.get("tonality"),
                    dos=details.get("dos"),
                    donts=details.get("donts")
                )
                
                # Add the result to the state
                state["create_brand_voice_result"] = result
                
                # Create a response message
                response_message = f"I've created a brand voice named '{details.get('name', 'Untitled Brand Voice')}' for you."
                state["messages"].append({"role": "assistant", "content": response_message})
                
                return {
                    "status": "success",
                    "action": "create_brand_voice",
                    "result": result,
                    "message": response_message
                }
            except json.JSONDecodeError:
                error_msg = "I couldn't parse the brand voice details. Please provide a name and description for your brand voice."
                state["messages"].append({"role": "assistant", "content": error_msg})
                return {
                    "status": "error",
                    "message": error_msg
                }
        
        elif intent == "generate_content":
            # Create a prompt to extract content generation details
            extract_prompt = ChatPromptTemplate.from_messages([
                ("system", """
                Extract the details for generating content from the user's message.
                Return a JSON object with the following fields:
                - prompt: The prompt for generating content
                - content_type: (optional) The type of content to generate (e.g., blog, social media, email)
                
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
                
                # Generate the content
                result = generate_content(
                    prompt=details.get("prompt", message),
                    brand_voice_id=brand_voice_id,
                    content_type=details.get("content_type")
                )
                
                # Add the result to the state
                state["generate_content_result"] = result
                
                # Create a response message
                response_message = result.get("content", "I've generated content for you.")
                state["messages"].append({"role": "assistant", "content": response_message})
                
                return {
                    "status": "success",
                    "action": "generate_content",
                    "result": result,
                    "message": response_message
                }
            except json.JSONDecodeError:
                # If parsing fails, use the original message as the prompt
                result = generate_content(
                    prompt=message,
                    brand_voice_id=brand_voice_id
                )
                
                # Add the result to the state
                state["generate_content_result"] = result
                
                # Create a response message
                response_message = result.get("content", "I've generated content for you.")
                state["messages"].append({"role": "assistant", "content": response_message})
                
                return {
                    "status": "success",
                    "action": "generate_content",
                    "result": result,
                    "message": response_message
                }
        
        elif intent == "analyze_content":
            # Create a prompt to extract content for analysis
            extract_prompt = ChatPromptTemplate.from_messages([
                ("system", """
                Extract the content to analyze from the user's message.
                Return a JSON object with the following field:
                - content: The content to analyze
                
                If the content is not provided, use the entire message as the content.
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
                
                # Analyze the content
                result = analyze_content(
                    content=details.get("content", message)
                )
                
                # Add the result to the state
                state["analyze_content_result"] = result
                
                # Create a response message
                if "raw_analysis" in result:
                    response_message = result["raw_analysis"]
                else:
                    response_message = f"""
                    I've analyzed the content and here are the brand voice characteristics:
                    
                    Personality: {result.get('personality', '')}
                    Tonality: {result.get('tonality', '')}
                    
                    Do's:
                    {result.get('dos', '')}
                    
                    Don'ts:
                    {result.get('donts', '')}
                    """
                
                state["messages"].append({"role": "assistant", "content": response_message})
                
                return {
                    "status": "success",
                    "action": "analyze_content",
                    "result": result,
                    "message": response_message
                }
            except json.JSONDecodeError:
                # If parsing fails, use the original message as the content
                result = analyze_content(message)
                
                # Add the result to the state
                state["analyze_content_result"] = result
                
                # Create a response message
                if "raw_analysis" in result:
                    response_message = result["raw_analysis"]
                else:
                    response_message = f"""
                    I've analyzed the content and here are the brand voice characteristics:
                    
                    Personality: {result.get('personality', '')}
                    Tonality: {result.get('tonality', '')}
                    
                    Do's:
                    {result.get('dos', '')}
                    
                    Don'ts:
                    {result.get('donts', '')}
                    """
                
                state["messages"].append({"role": "assistant", "content": response_message})
                
                return {
                    "status": "success",
                    "action": "analyze_content",
                    "result": result,
                    "message": response_message
                }
        
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
        return {"status": "error", "message": f"Error running brand voice agent: {str(e)}"}
