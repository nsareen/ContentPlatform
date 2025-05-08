"""
Test script to directly invoke the rich content agent with detailed logging.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.rich_content_agent import invoke_rich_content_agent

def test_rich_content_agent_direct():
    """Test the rich content agent directly with detailed logging."""
    print("Testing rich content agent directly...")
    
    # Test parameters
    message = "Create a marketing flyer for a new eco-friendly water bottle that keeps drinks cold for 24 hours"
    user_id = "test-user-id"
    tenant_id = "test-tenant-id"
    content_type = "flyer"
    
    # Force the intent to generate_rich_content
    context = {
        "force_intent": "generate_rich_content",
        "content_type": content_type
    }
    
    try:
        print(f"Invoking rich content agent with message: {message}")
        print(f"Context: {context}")
        
        # Invoke the agent
        result = invoke_rich_content_agent(
            message=message,
            user_id=user_id,
            tenant_id=tenant_id,
            content_type=content_type,
            context=context
        )
        
        print("\nAgent invocation result:")
        print(f"Status: {result.get('status')}")
        print(f"Action: {result.get('action')}")
        
        # Check if we got rich content
        if result.get('action') == 'generate_rich_content' and 'result' in result:
            rich_result = result['result']
            print("\nRich content generated successfully!")
            
            # Print text content
            if 'text_content' in rich_result:
                print("\nText content:")
                print("-" * 50)
                print(rich_result['text_content'][:500] + "..." if len(rich_result['text_content']) > 500 else rich_result['text_content'])
                print("-" * 50)
            
            # Print image information
            if 'images' in rich_result:
                images = rich_result['images']
                print(f"\nGenerated {len(images)} images:")
                for i, image in enumerate(images):
                    print(f"Image {i+1}: {image.get('url', 'No URL')[:100]}...")
        else:
            print("\nNo rich content in result. Full result:")
            print(result)
        
        return result
    except Exception as e:
        print(f"Exception during agent invocation: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_rich_content_agent_direct()
