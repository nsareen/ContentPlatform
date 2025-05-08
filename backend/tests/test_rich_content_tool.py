"""
Test script for the GenerateRichContentTool class in isolation.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.agents.rich_content_agent import GenerateRichContentTool

def test_generate_rich_content_tool():
    """Test the GenerateRichContentTool class directly."""
    print("Testing GenerateRichContentTool...")
    
    # Create an instance of the tool
    tool = GenerateRichContentTool()
    
    # Test the tool with a simple prompt
    prompt = "Create a marketing flyer for a new eco-friendly water bottle that keeps drinks cold for 24 hours"
    content_type = "flyer"
    
    try:
        print(f"Calling tool._run with prompt: {prompt[:50]}...")
        result = tool._run(prompt=prompt, content_type=content_type)
        
        print("\nTool execution successful!")
        print(f"Result type: {type(result)}")
        
        if isinstance(result, dict):
            if "error" in result:
                print(f"Tool returned error: {result['error']}")
            else:
                print("Tool returned success result:")
                for key, value in result.items():
                    if key == "text_content":
                        print(f"- {key}: {value[:100]}...")
                    elif key == "image_descriptions":
                        print(f"- {key}: {len(value)} descriptions")
                        for i, desc in enumerate(value):
                            print(f"  - Description {i+1}: {desc[:50]}...")
                    else:
                        print(f"- {key}: {value}")
        else:
            print(f"Unexpected result type: {type(result)}")
            print(f"Result: {result}")
        
        return True
    except Exception as e:
        print(f"Exception during tool execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_generate_rich_content_tool()
