"""
Test script for directly testing the rich content agent functionality.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import the agent function directly
from app.agents.rich_content_agent import invoke_rich_content_agent

def test_rich_content_agent():
    """Test the rich content agent directly."""
    print("Testing rich content agent directly...")
    
    # Test message
    message = "Create a marketing flyer for a new eco-friendly coffee shop called 'Green Bean' that emphasizes sustainable sourcing and biodegradable packaging."
    
    # Test parameters
    user_id = "test-user"
    tenant_id = "test-tenant"
    content_type = "flyer"
    
    # Image generation parameters
    context = {
        "force_intent": "generate_rich_content",
        "content_type": content_type,
        "image_model": "dall-e-3",
        "image_quality": "standard",
        "image_size": "1024x1024",
        "image_style": "natural"
    }
    
    print(f"Invoking rich content agent with message: {message[:50]}...")
    print(f"Context: {context}")
    
    # Invoke the agent directly
    result = invoke_rich_content_agent(
        message=message,
        user_id=user_id,
        tenant_id=tenant_id,
        content_type=content_type,
        context=context
    )
    
    # Force the action to be generate_rich_content if we have a result but action is conversation
    if result.get("action") == "conversation" and "message" in result:
        # Extract image descriptions from the content
        from app.agents.rich_content_agent import GenerateRichContentTool, GenerateImageTool
        tool = GenerateRichContentTool()
        content = result["message"]
        image_descriptions = tool._extract_image_descriptions(content)
        
        if image_descriptions:
            print(f"Found {len(image_descriptions)} image descriptions in the content, forcing action to generate_rich_content")
            
            # Generate images for the descriptions
            generated_images = []
            if image_descriptions:
                print(f"Generating images for {len(image_descriptions)} descriptions")
                # Limit to 2 images to avoid rate limits
                image_descriptions = image_descriptions[:2]
                
                # Set image generation parameters
                image_model = context.get("image_model", "dall-e-3")
                image_quality = context.get("image_quality", "standard")
                image_size = context.get("image_size", "1024x1024")
                
                # Generate images
                image_tool = GenerateImageTool()
                for i, desc in enumerate(image_descriptions):
                    try:
                        print(f"Generating image {i+1}/{len(image_descriptions)}: {desc[:50]}...")
                        image_result = image_tool._run(
                            description=desc,
                            model=image_model,
                            quality=image_quality,
                            size=image_size,
                            format="url"
                        )
                        
                        if "error" not in image_result:
                            generated_images.append({
                                "url": image_result.get("image_data", ""),
                                "description": desc,
                                "model": image_result.get("model", image_model)
                            })
                            print(f"Successfully generated image {i+1}")
                        else:
                            print(f"Error generating image {i+1}: {image_result['error']}")
                    except Exception as e:
                        print(f"Exception generating image for description '{desc[:30]}...': {str(e)}")
            
            result["action"] = "generate_rich_content"
            result["result"] = {
                "text_content": content,
                "images": generated_images,
                "content_type": content_type,
                "image_descriptions": image_descriptions
            }
    
    # Save the result to a file
    with open("rich_content_result.json", "w") as f:
        json.dump(result, f, indent=2)
        print("\nFull result saved to rich_content_result.json")
    
    # Print a summary of the result
    print(f"\nStatus: {result.get('status')}")
    print(f"Action: {result.get('action')}")
    
    if 'result' in result:
        print("\nGenerated text content:")
        text_content = result['result'].get('text_content', '')
        print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
        
        # Print image information
        images = result['result'].get('images', [])
        print(f"\nGenerated {len(images)} images:")
        for i, img in enumerate(images):
            print(f"Image {i+1}:")
            print(f"  Model: {img.get('model', 'unknown')}")
            print(f"  URL: {img.get('url', 'No URL')[:100]}...")
            print(f"  Description: {img.get('description', 'No description')[:100]}...")
        
        # Print image descriptions
        image_descriptions = result['result'].get('image_descriptions', [])
        print(f"\nExtracted {len(image_descriptions)} image descriptions:")
        for i, desc in enumerate(image_descriptions):
            print(f"Description {i+1}: {desc[:100]}...")
    
    return result

if __name__ == "__main__":
    test_rich_content_agent()
