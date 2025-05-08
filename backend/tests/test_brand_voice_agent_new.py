"""
Test script for the new brand voice agent implementation to verify functionality.
"""

import sys
import os
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.brand_voice_agent_new import (
    invoke_brand_voice_agent,
    create_brand_voice,
    generate_content,
    analyze_content
)

# Test data
TEST_USER_ID = "test-user-123"
TEST_TENANT_ID = "1ece4109-616a-47b1-8466-e74ef48bb85e"  # Use the actual tenant ID from the database

def print_result(title: str, result: Dict[str, Any]) -> None:
    """Print test results in a formatted way."""
    print("\n" + "=" * 80)
    print(f"TEST: {title}")
    print("-" * 80)
    print(f"Status: {result.get('status', 'N/A')}")
    print(f"Action: {result.get('action', 'N/A')}")
    
    if result.get('result'):
        print("\nResult:")
        if isinstance(result['result'], dict):
            for key, value in result['result'].items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
        else:
            print(f"  {result['result']}")
    
    if result.get('message'):
        print(f"\nMessage: {result['message']}")
    
    print("=" * 80)

def test_direct_tool_calls():
    """Test direct calls to tool functions."""
    print("\nTesting direct tool calls...")
    
    # Test create_brand_voice
    print("Testing create_brand_voice...")
    # Create a frame variable to simulate the state
    import inspect
    frame = inspect.currentframe()
    frame.f_locals['state'] = {"tenant_id": TEST_TENANT_ID, "user_id": TEST_USER_ID}
    
    create_result = create_brand_voice(
        name="Test Brand Voice",
        description="A test brand voice for automated testing",
        personality="Bold, confident",
        tonality="Professional, friendly",
        dos="Use active voice. Be concise.",
        donts="Avoid jargon. Don't use passive voice."
    )
    print_result("Create Brand Voice (Direct)", {"result": create_result})
    
    # If brand voice was created successfully, use its ID for content generation
    brand_voice_id = create_result.get("id") if isinstance(create_result, dict) and "id" in create_result else None
    
    # Test generate_content
    print("Testing generate_content...")
    # Update the frame locals with brand_voice_id
    frame = inspect.currentframe()
    frame.f_locals['state'] = {
        "tenant_id": TEST_TENANT_ID, 
        "user_id": TEST_USER_ID,
        "current_brand_voice_id": brand_voice_id
    }
    
    generate_result = generate_content(
        prompt="Write a short product description for a new smartphone",
        brand_voice_id=brand_voice_id,
        content_type="product"
    )
    print_result("Generate Content (Direct)", {"result": generate_result})
    
    # Test analyze_content
    print("Testing analyze_content...")
    sample_content = """
    Introducing our revolutionary smartphone that doesn't just keep up with your life—it enhances it. 
    With cutting-edge technology wrapped in a sleek, sophisticated design, this device delivers 
    performance without compromise. The intuitive interface makes complex tasks simple, 
    while the all-day battery ensures you're always connected to what matters most.
    """
    
    analyze_result = analyze_content(content=sample_content)
    print_result("Analyze Content (Direct)", {"result": analyze_result})

def test_agent_workflow():
    """Test the full agent workflow through invoke_brand_voice_agent."""
    print("\nTesting agent workflow...")
    
    # Test create brand voice intent
    create_message = "I want to create a new brand voice called 'Tech Innovators' that is bold, forward-thinking, and uses simple language to explain complex concepts."
    create_result = invoke_brand_voice_agent(
        message=create_message,
        user_id=TEST_USER_ID,
        tenant_id=TEST_TENANT_ID
    )
    print_result("Create Brand Voice (Agent)", create_result)
    
    # Test generate content intent
    generate_message = "Generate content for a social media post about our new AI-powered app"
    generate_result = invoke_brand_voice_agent(
        message=generate_message,
        user_id=TEST_USER_ID,
        tenant_id=TEST_TENANT_ID,
        brand_voice_id=None  # The agent should handle this case
    )
    print_result("Generate Content (Agent)", generate_result)
    
    # Test analyze content intent
    analyze_message = "Analyze this content: Our cutting-edge solution revolutionizes how businesses approach data analytics, providing unprecedented insights with minimal effort."
    analyze_result = invoke_brand_voice_agent(
        message=analyze_message,
        user_id=TEST_USER_ID,
        tenant_id=TEST_TENANT_ID
    )
    print_result("Analyze Content (Agent)", analyze_result)
    
    # Test forced intent
    forced_generate_result = invoke_brand_voice_agent(
        message="Write a product description for a smart watch",
        user_id=TEST_USER_ID,
        tenant_id=TEST_TENANT_ID,
        context={"force_intent": "generate_content"}
    )
    print_result("Generate Content (Forced Intent)", forced_generate_result)

if __name__ == "__main__":
    print("Starting brand voice agent tests...")
    
    try:
        # Test direct tool calls first to isolate issues
        test_direct_tool_calls()
        
        # Test the agent workflow
        test_agent_workflow()
        
        print("\nAll tests completed.")
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        import traceback
        traceback.print_exc()
