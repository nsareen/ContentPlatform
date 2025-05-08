"""
Test script for testing the image description extraction functionality.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import the necessary functions and classes
from app.agents.rich_content_agent import GenerateRichContentTool, GenerateImageTool

def test_image_description_extraction():
    """Test the image description extraction functionality."""
    print("Testing image description extraction...")
    
    # Create an instance of the GenerateRichContentTool
    tool = GenerateRichContentTool()
    
    # Sample content with different image description formats
    test_contents = [
        # Test case 1: Simple image description
        """
        I've generated the following content for your flyer:

        **Headline:**
        Welcome to our store!

        **Body:**
        Check out our latest products.

        **Image Description:**
        A beautiful storefront with customers walking in and out.
        """,
        
        # Test case 2: Numbered image descriptions
        """
        I've generated the following content for your flyer:

        **Headline:**
        Summer Sale!

        **Body:**
        Don't miss our biggest sale of the year.

        **Image Descriptions:**
        1. A beach scene with people enjoying the sun.
        2. A display of summer products on sale.
        """,
        
        # Test case 3: Image descriptions with "Image X:" format
        """
        I've generated the following content for your flyer:

        **Flyer Title: Unleash the Joy of Play!**

        **Marketing Copy:**
        Get ready to dive into a world where playtime is pure magic.

        **Image Descriptions:**

        1. **Image 1:** A group of children laughing and playing in a sunlit park. They are wearing bright, colorful outfits.
        2. **Image 2:** A close-up of a child wearing a stylish, patterned jacket.
        3. **Image 3:** A scene of kids sitting together on a picnic blanket, sharing snacks and giggles.
        """,
        
        # Test case 4: Multiple image description sections
        """
        I've generated the following content for your flyer:

        **Front of Flyer:**

        **Headline:**
        New Collection Arrived!

        **Image Description:**
        A model wearing our latest fashion collection.

        **Back of Flyer:**

        **Headline:**
        Visit Our Store Today!

        **Image Description:**
        Our store interior showing the new collection display.
        """
    ]
    
    # Test each content sample
    for i, content in enumerate(test_contents):
        print(f"\nTest case {i+1}:")
        print("-" * 40)
        print(f"Content sample: {content[:100]}...")
        
        # Extract image descriptions
        image_descriptions = tool._extract_image_descriptions(content)
        
        # Print results
        print(f"Extracted {len(image_descriptions)} image descriptions:")
        for j, desc in enumerate(image_descriptions):
            print(f"  {j+1}. {desc[:100]}...")
    
    # Return success
    return True

def test_image_generation():
    """Test the image generation functionality."""
    print("\nTesting image generation...")
    
    # Create an instance of the GenerateImageTool
    image_tool = GenerateImageTool()
    
    # Test descriptions
    test_descriptions = [
        "A simple blue circle on a white background",
        "A cartoon cat sitting on a windowsill watching birds outside"
    ]
    
    # Test with both DALL-E 3 and GPT Image models
    models = ["dall-e-3", "gpt-image-1"]
    
    results = []
    
    for model in models:
        print(f"\nTesting with model: {model}")
        
        for i, desc in enumerate(test_descriptions):
            print(f"Generating image {i+1} with description: {desc[:50]}...")
            
            try:
                # Generate image
                image_result = image_tool._run(
                    description=desc,
                    model=model,
                    quality="standard" if model == "dall-e-3" else "medium",
                    size="1024x1024",
                    format="url"
                )
                
                # Check result
                if "error" not in image_result:
                    print(f"Successfully generated image with {model}")
                    image_url = image_result.get("image_data", "")
                    print(f"Image URL: {image_url[:50]}...")
                    
                    results.append({
                        "model": model,
                        "description": desc,
                        "success": True,
                        "url": image_url
                    })
                else:
                    error_msg = image_result.get("error", "Unknown error")
                    print(f"Error generating image with {model}: {error_msg}")
                    
                    results.append({
                        "model": model,
                        "description": desc,
                        "success": False,
                        "error": error_msg
                    })
            except Exception as e:
                print(f"Exception generating image: {str(e)}")
                
                results.append({
                    "model": model,
                    "description": desc,
                    "success": False,
                    "error": str(e)
                })
    
    # Save results to a file
    with open("image_generation_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
        print("\nFull results saved to image_generation_test_results.json")
    
    # Check if any images were successfully generated
    success_count = sum(1 for result in results if result["success"])
    print(f"\nSuccessfully generated {success_count} out of {len(results)} images")
    
    return success_count > 0

def test_rich_content_with_frontend_input():
    """Test the rich content generation with input similar to what would come from the frontend."""
    print("\nTesting rich content generation with frontend-like input...")
    
    # Import the invoke_rich_content_agent function
    from app.agents.rich_content_agent import invoke_rich_content_agent
    
    # Sample frontend input
    frontend_input = {
        "prompt": "Create a flyer for a kids clothing brand that emphasizes bold and playful styles",
        "content_type": "flyer",
        "brand_voice_id": None  # Simulate no brand voice ID
    }
    
    print(f"Frontend input: {frontend_input}")
    
    # Invoke the agent
    result = invoke_rich_content_agent(
        message=frontend_input["prompt"],
        user_id="test-user",
        tenant_id="test-tenant",
        brand_voice_id=frontend_input["brand_voice_id"],
        content_type=frontend_input["content_type"],
        context={
            "force_intent": "generate_rich_content",
            "content_type": frontend_input["content_type"],
            "image_model": "dall-e-3",
            "image_quality": "standard",
            "image_size": "1024x1024",
            "image_style": "natural"
        }
    )
    
    # Save the result to a file
    with open("frontend_simulation_result.json", "w") as f:
        json.dump(result, f, indent=2)
        print("\nFull result saved to frontend_simulation_result.json")
    
    # Check if text content was generated
    if "result" in result and "text_content" in result["result"]:
        print("\nText content generated successfully")
        text_content = result["result"]["text_content"]
        print(f"Text content preview: {text_content[:200]}...")
        
        # Check if image descriptions were extracted
        image_descriptions = result["result"].get("image_descriptions", [])
        print(f"\nExtracted {len(image_descriptions)} image descriptions:")
        for i, desc in enumerate(image_descriptions):
            print(f"  {i+1}. {desc[:100]}...")
        
        # Check if images were generated
        images = result["result"].get("images", [])
        print(f"\nGenerated {len(images)} images:")
        for i, img in enumerate(images):
            print(f"Image {i+1}:")
            print(f"  Model: {img.get('model', 'unknown')}")
            print(f"  URL: {img.get('url', 'No URL')[:50]}...")
            print(f"  Description: {img.get('description', 'No description')[:50]}...")
        
        # Check for image generation error
        if "image_generation_error" in result["result"]:
            print(f"\nImage generation error: {result['result']['image_generation_error']}")
    else:
        print("\nFailed to generate text content")
    
    return result

if __name__ == "__main__":
    # Run the tests
    print("Running image description extraction test...")
    extraction_result = test_image_description_extraction()
    
    print("\nRunning image generation test...")
    generation_result = test_image_generation()
    
    print("\nRunning frontend simulation test...")
    frontend_result = test_rich_content_with_frontend_input()
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Image description extraction: {'SUCCESS' if extraction_result else 'FAILURE'}")
    print(f"Image generation: {'SUCCESS' if generation_result else 'FAILURE'}")
    print(f"Frontend simulation: {'SUCCESS' if frontend_result.get('status') == 'success' else 'FAILURE'}")
    
    # Check if any images were generated in the frontend simulation
    if frontend_result.get("result", {}).get("images", []):
        print("Frontend simulation generated images: YES")
    else:
        print("Frontend simulation generated images: NO")
        if "image_generation_error" in frontend_result.get("result", {}):
            print(f"Error: {frontend_result['result']['image_generation_error']}")
