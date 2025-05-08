"""
Configuration for the agentic AI system.
"""

import os
import json
from typing import Any, List, Optional, Dict
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Try to load from the backend directory
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"No .env file found at {env_path}")
except ImportError:
    print("python-dotenv not installed, skipping .env loading")

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

# Default model configuration
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.2

# OpenAI API configuration
# Read API key directly from .env file if it exists
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
OPENAI_API_KEY = ""
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                OPENAI_API_KEY = line.strip().split('=', 1)[1]
                # Remove quotes if present
                if (OPENAI_API_KEY.startswith('\'') and OPENAI_API_KEY.endswith('\'')) or \
                   (OPENAI_API_KEY.startswith('"') and OPENAI_API_KEY.endswith('"')):
                    OPENAI_API_KEY = OPENAI_API_KEY[1:-1]
                print(f"Loaded API key directly from .env file: {OPENAI_API_KEY[:5]}...")
                break

# Fallback to environment variable if not found in .env
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    if OPENAI_API_KEY:
        print(f"Using API key from environment variable: {OPENAI_API_KEY[:5]}...")

# Mock LLM for testing
class MockChatModel(BaseChatModel):
    """Mock Chat Model for testing without API keys."""
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager = None, **kwargs: Any) -> ChatResult:
        """Mock response generation."""
        # Simple mock response based on the last message content
        last_message = messages[-1].content
        
        if "create brand voice" in last_message.lower():
            response = "I'll create a brand voice with the characteristics you described."
        elif "generate content" in last_message.lower():
            response = "Here's some content that matches your brand voice: Our innovative solution transforms how you interact with technology, making complex tasks simple and intuitive."
        elif "analyze" in last_message.lower():
            response = "Analysis: The content has a professional, confident tone with clear and concise language. It avoids jargon and focuses on benefits rather than features."
        else:
            response = "I understand your request and I'm here to help with your brand voice needs."
            
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=response))])
    
    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager = None, **kwargs: Any) -> ChatResult:
        """Async version of mock response generation."""
        return self._generate(messages, stop, run_manager, **kwargs)

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "mock-chat-model"

# Create LLM instances
def get_llm(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE, use_mock=False):
    """Get a configured LLM instance.
    
    Args:
        model: The model to use
        temperature: The temperature setting
        use_mock: Whether to use a mock LLM (for testing without API keys)
    """
    # Use mock LLM if requested or if no API key is available
    if use_mock or not OPENAI_API_KEY:
        print("Using mock LLM for testing")
        return MockChatModel()
    
    # Use real OpenAI API
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=OPENAI_API_KEY
    )

# Agent system prompts
BRAND_VOICE_AGENT_PROMPT = """You are an AI assistant specialized in brand voice management.
Your goal is to help users create, refine, and apply brand voices to their content.
You can understand user intents and execute the appropriate workflows.

Available actions:
1. Create a new brand voice based on user description
2. Refine an existing brand voice with additional guidelines
3. Generate content that adheres to a specific brand voice
4. Analyze content to extract brand voice characteristics
5. Provide feedback on how well content matches a brand voice

Always be helpful, concise, and focused on the user's goals.
"""

CONTENT_GENERATOR_PROMPT = """You are a specialized content generator that creates content
following specific brand voice guidelines. You will receive:

1. A brand voice description with personality, tonality, dos, and don'ts
2. A content request or prompt

Your job is to generate content that perfectly matches the brand voice while
fulfilling the content request. Be creative but stay true to the brand voice guidelines.
"""

ANALYZER_PROMPT = """You are a specialized content analyzer that can identify brand voice
characteristics from text. Given a piece of content, extract:

1. Personality traits (e.g., bold, friendly, professional)
2. Tonality aspects (e.g., conversational, formal, enthusiastic)
3. Key dos (writing practices that should be followed)
4. Key don'ts (writing practices that should be avoided)

Be specific and provide actionable insights that can help define a brand voice.
"""
