"""
Integration test for the brand voice agent.
This script simulates the interaction between the frontend and the backend.
"""

import sys
import os
import asyncio
import json

# Add the parent directory to the path to import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.brand_voice_agent import invoke_brand_voice_agent
from app.models.models import BrandVoice
from app.db.database import get_db

async def test_playground_integration():
    """
    Test the integration between the frontend playground and the brand voice agent.
    This simulates the API call made by the PlaygroundPanel component.
    """
    # Get a database session
    db = next(get_db())
    
    # Get the first brand voice from the database
    brand_voice = db.query(BrandVoice).first()
    if not brand_voice:
        print("No brand voices found in the database. Please create one first.")
        return
    
    print(f"Testing with brand voice: {brand_voice.name} (ID: {brand_voice.id})")
    
    # Simulate the API call made by the PlaygroundPanel component
    prompt = "Generate a short tagline for a tech company"
    
    # This is equivalent to the API call to /api/agent/generate
    result = invoke_brand_voice_agent(
        message=f"Generate content using brand voice {brand_voice.id}: {prompt}",
        user_id="test-user",
        tenant_id=brand_voice.tenant_id,
        brand_voice_id=brand_voice.id,
        context={
            "force_intent": "generate_content",
            "content_type": "general"
        }
    )
    
    print("\nAPI Response:")
    print(json.dumps(result, indent=2))
    
    # Verify that the response contains the expected fields
    assert "status" in result, "Response should contain a status field"
    assert result["status"] == "success", "Status should be success"
    assert "action" in result, "Response should contain an action field"
    assert "message" in result, "Response should contain a message field"
    
    print("\nIntegration test passed! The brand voice agent is working correctly.")
    print("The PlaygroundPanel component will be able to display this content.")

if __name__ == "__main__":
    asyncio.run(test_playground_integration())
