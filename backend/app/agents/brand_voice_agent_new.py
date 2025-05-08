"""
Brand Voice Agent - Main agent for handling brand voice operations
Using modern LangGraph patterns
"""

from typing import Dict, List, Any, TypedDict, Literal, Union, Optional
import json
from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.db.database import SessionLocal
from app.models.models import BrandVoice, BrandVoiceStatus
from app.agents.config import get_llm, BRAND_VOICE_AGENT_PROMPT, CONTENT_GENERATOR_PROMPT, ANALYZER_PROMPT


# Define state types
class AgentState(TypedDict):
    """State for the brand voice agent workflow."""
    messages: List[Dict[str, Any]]
    user_id: str
    tenant_id: str
    current_brand_voice_id: str
    intent: str
    context: Dict[str, Any]


# Define tool input schemas
class BrandVoiceCreateInput(BaseModel):
    """Input for creating a brand voice."""
    name: str = Field(..., description="Name of the brand voice")
    description: str = Field(..., description="Description of the brand voice")
    personality: Optional[str] = Field(None, description="Personality traits of the brand voice")
    tonality: Optional[str] = Field(None, description="Tonality aspects of the brand voice")
    dos: Optional[str] = Field(None, description="Writing practices to follow")
    donts: Optional[str] = Field(None, description="Writing practices to avoid")


# Define tools using the @tool decorator
@tool
def create_brand_voice(
    name: str, 
    description: str, 
    personality: Optional[str] = None, 
    tonality: Optional[str] = None, 
    dos: Optional[str] = None, 
    donts: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new brand voice based on the provided information."""
    # Get tenant_id and user_id from the current frame's locals
    import inspect
    
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


@tool
def generate_content(
    prompt: str,
    brand_voice_id: Optional[str] = None,
    content_type: Optional[str] = None
) -> Dict[str, Any]:
    """Generate content that adheres to a specific brand voice."""
    # Try to get brand_voice_id from state if not provided
    import inspect
    
    # Try to get the state from the calling frame
    frame = inspect.currentframe()
    try:
        if frame and frame.f_back and 'state' in frame.f_back.f_locals:
            state = frame.f_back.f_locals['state']
            if isinstance(state, dict) and not brand_voice_id and state.get('current_brand_voice_id'):
                brand_voice_id = state.get('current_brand_voice_id')
                print(f"Using brand voice ID from state: {brand_voice_id}")
    finally:
        del frame  # Avoid reference cycles
    
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
                "description": db_brand_voice.description or "",
                "voice_metadata": db_brand_voice.voice_metadata or {},
                "dos": db_brand_voice.dos or "",
                "donts": db_brand_voice.donts or ""
            }
            print(f"Successfully loaded brand voice: {brand_voice['name']}")
    finally:
        db.close()
    
    # Generate sample content based on the prompt
    content_type = content_type or "general"
    
    # If we have a valid brand voice, use it for content generation
    if brand_voice:
        # Use the LLM with the brand voice guidelines
        try:
            # Extract personality and tonality from voice_metadata
            personality = brand_voice['voice_metadata'].get('personality', '') if brand_voice['voice_metadata'] else ''
            tonality = brand_voice['voice_metadata'].get('tonality', '') if brand_voice['voice_metadata'] else ''
            
            # Create the prompt for the LLM
            prompt_template = ChatPromptTemplate.from_messages([
                SystemMessage(content=CONTENT_GENERATOR_PROMPT),
                HumanMessage(content=f"""
            Brand Voice: {brand_voice['name']}
            Description: {brand_voice['description']}
            Personality: {personality}
            Tonality: {tonality}
            Dos:
            {brand_voice['dos']}
            Don'ts:
            {brand_voice['donts']}
            
            Content Request: {prompt}
            Content Type: {content_type}
            
            Generate content that follows this brand voice:
                """)
            ])
            
            llm = get_llm()
            response = llm.invoke(prompt_template)
            content = response.content
            print(f"Generated content using LLM and brand voice: {content[:50]}...")
        except Exception as e:
            print(f"Error generating content with LLM: {str(e)}")
            # Fallback to sample content if LLM fails
            content = generate_fallback_content(prompt)
    else:
        # No brand voice provided, use fallback content
        content = generate_fallback_content(prompt)
    
    return {
        "content": content,
        "brand_voice_id": brand_voice_id,
        "prompt": prompt,
        "content_type": content_type
    }


@tool
def analyze_content(content: str) -> Dict[str, Any]:
    """Analyze content to extract brand voice characteristics."""
    print(f"Analyzing content: {content[:50]}...")
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=ANALYZER_PROMPT),
        HumanMessage(content=f"""
Analyze the following content to extract brand voice characteristics:

{content}

Provide a detailed analysis of the personality, tonality, dos, and don'ts.
        """)
    ])
    
    llm = get_llm()
    response = llm.invoke(prompt)
    
    # In a real implementation, you might want to parse the response
    # into a structured format
    return {
        "analysis": response.content,
        "content": content
    }


# Helper function for fallback content generation
def generate_fallback_content(prompt_text: str) -> str:
    """Generate fallback content when brand voice data is not available or LLM fails."""
    if "product" in prompt_text.lower():
        return f"Introducing our latest innovation that effortlessly elevates your experience! Our product doesn't just deliver results—it transforms your routine into something you'll actually look forward to. With its sleek design and intuitive functionality, you'll wonder how you ever lived without it!"
    elif "social" in prompt_text.lower() or "post" in prompt_text.lower():
        return f"✨ Life's too short for boring routines! Our new collection lets you express yourself without trying too hard. Swipe up to discover your new favorites that work as hard as you play! #StyleWithoutEffort #LiveBoldly"
    elif "email" in prompt_text.lower():
        return f"Hey there,\n\nExcited to share something amazing with you! We've been working on something special that we know you'll love. It's all about making your life easier while keeping things fun and fresh.\n\nCan't wait for you to experience it!\n\nCheers,\nThe Team"
    else:
        return f"We believe in creating experiences that spark joy and make life easier. Our approach combines bold innovation with playful design, ensuring everything we create is not just functional, but genuinely delightful to use. We don't bog you down with technical jargon—instead, we focus on what really matters: how our products make you feel."


# Intent classification function
def classify_intent(state: AgentState) -> AgentState:
    """Classify the user's intent based on their message."""
    messages = state["messages"]
    if not messages:
        state["intent"] = "unknown"
        return state
    
    last_message = messages[-1]["content"]
    
    # Create a prompt for intent classification
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are an intent classifier for a brand voice management system.
Classify the user's message into one of the following intents:
- create_brand_voice: User wants to create a new brand voice
- generate_content: User wants to generate content using a brand voice
- analyze_content: User wants to analyze content to extract brand voice characteristics
- refine_brand_voice: User wants to refine an existing brand voice
- get_brand_voice: User wants to retrieve information about a brand voice
- unknown: The intent is unclear or not related to brand voice management

Respond with ONLY the intent name, nothing else."""),
        HumanMessage(content=last_message)
    ])
    
    llm = get_llm(temperature=0)
    response = llm.invoke(prompt)
    
    state["intent"] = response.content.strip().lower()
    return state


# Router function
def route_by_intent(state: AgentState) -> str:
    """Route the workflow based on the classified intent."""
    intent = state["intent"]
    print(f"Routing based on intent: {intent}")
    return intent


# Create the workflow graph
def create_brand_voice_agent() -> StateGraph:
    """Create the brand voice agent workflow graph."""
    # Initialize the workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("intent_classifier", classify_intent)
    workflow.add_node("router", route_by_intent)
    
    # Add tool nodes
    workflow.add_node("create_brand_voice", ToolNode(create_brand_voice))
    workflow.add_node("generate_content", ToolNode(generate_content))
    workflow.add_node("analyze_content", ToolNode(analyze_content))
    
    # Add conditional edges based on the intent
    workflow.add_edge("intent_classifier", "router")
    
    # Use conditional edges to route based on intent
    workflow.add_conditional_edges(
        "router",
        lambda state: state["intent"],
        {
            "create_brand_voice": "create_brand_voice",
            "generate_content": "generate_content",
            "analyze_content": "analyze_content",
            "unknown": END,
            "refine_brand_voice": END,  # Not implemented yet
            "get_brand_voice": END,     # Not implemented yet
        }
    )
    
    # Connect tool nodes back to the end
    workflow.add_edge("create_brand_voice", END)
    workflow.add_edge("generate_content", END)
    workflow.add_edge("analyze_content", END)
    
    # Set the entry point
    workflow.set_entry_point("intent_classifier")
    
    return workflow


# Initialize the agent
try:
    brand_voice_agent = create_brand_voice_agent().compile()
    print("Brand voice agent initialized successfully")
except Exception as e:
    print(f"Error initializing brand voice agent: {str(e)}")
    brand_voice_agent = None


# Function to invoke the agent
def invoke_brand_voice_agent(
    message: str,
    user_id: str,
    tenant_id: str,
    brand_voice_id: str = None,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Invoke the brand voice agent with a user message."""
    global brand_voice_agent
    
    print(f"Invoking brand voice agent with message: {message[:50]}...")
    print(f"Brand voice ID: {brand_voice_id}")
    print(f"Context: {context}")
    
    # Initialize the agent if needed
    if brand_voice_agent is None:
        try:
            print("Initializing brand voice agent")
            brand_voice_agent = create_brand_voice_agent().compile()
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            return {"status": "error", "message": f"Failed to initialize brand voice agent: {str(e)}"}
    
    # Handle direct intent specification through context
    # This allows API endpoints to specify exactly what they want the agent to do
    forced_intent = None
    if context and context.get("force_intent"):
        forced_intent = context.get("force_intent")
        print(f"Using forced intent from context: {forced_intent}")
    
    # Initialize the state
    state = AgentState(
        messages=[{"role": "user", "content": message}],
        user_id=user_id,
        tenant_id=tenant_id,
        current_brand_voice_id=brand_voice_id or "",
        intent=forced_intent or "",  # Use forced intent if provided
        context=context or {}
    )
    
    try:
        # Run the agent
        print("Running agent workflow")
        result = brand_voice_agent.invoke(state)
        print(f"Agent result: {result}")
    except Exception as e:
        print(f"Error running agent: {str(e)}")
        return {"status": "error", "message": f"Error running brand voice agent: {str(e)}"}
    
    # Process the result
    if isinstance(result, dict) and "error" in result:
        return {"status": "error", "message": result["error"]}
    
    # Extract the final result
    final_state = result
    
    # Determine the response based on the executed node
    if final_state.get("create_brand_voice"):
        return {
            "status": "success",
            "action": "create_brand_voice",
            "result": final_state["create_brand_voice"]
        }
    elif final_state.get("generate_content"):
        return {
            "status": "success",
            "action": "generate_content",
            "result": final_state["generate_content"]
        }
    elif final_state.get("analyze_content"):
        return {
            "status": "success",
            "action": "analyze_content",
            "result": final_state["analyze_content"]
        }
    else:
        return {
            "status": "success",
            "action": "conversation",
            "result": {
                "message": "I understand your request, but I'm not sure how to help with that specific brand voice task."
            }
        }
