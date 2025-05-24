"""
Test script for the Brand Voice Generator Agent.

This script tests the functionality of the brand voice generator agent
by invoking it with sample content and validating the output structure.
"""
import sys
import os
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agents.brand_voice_generator import invoke_generator
from app.agents.brand_voice_generator.state import GenerationDepth

# Sample content for testing
SAMPLE_CONTENT = """
At Eco-Friendly Solutions, we believe that small changes can make a big impact. 
Our sustainable products are designed with the planet in mind, using only 
recyclable materials and ethical manufacturing processes. 
We're committed to reducing waste and helping our customers live more 
environmentally conscious lives. Join us in our mission to create a greener future!
"""

def test_generator_basic_depth():
    """Test the brand voice generator with basic depth."""
    print("Testing brand voice generator with basic depth...")
    
    result = invoke_generator(
        content=SAMPLE_CONTENT,
        brand_name="Eco-Friendly Solutions",
        industry="retail",
        options={"generation_depth": GenerationDepth.BASIC.value}
    )
    
    # Validate the result structure
    validate_generator_result(result)
    print("✅ Basic depth test passed")
    return result

def test_generator_standard_depth():
    """Test the brand voice generator with standard depth."""
    print("Testing brand voice generator with standard depth...")
    
    result = invoke_generator(
        content=SAMPLE_CONTENT,
        brand_name="Eco-Friendly Solutions",
        industry="retail",
        options={"generation_depth": GenerationDepth.STANDARD.value}
    )
    
    # Validate the result structure
    validate_generator_result(result)
    print("✅ Standard depth test passed")
    return result

def test_generator_detailed_depth():
    """Test the brand voice generator with detailed depth."""
    print("Testing brand voice generator with detailed depth...")
    
    result = invoke_generator(
        content=SAMPLE_CONTENT,
        brand_name="Eco-Friendly Solutions",
        industry="retail",
        options={"generation_depth": GenerationDepth.DETAILED.value}
    )
    
    # Validate the result structure
    validate_generator_result(result)
    print("✅ Detailed depth test passed")
    return result

def validate_generator_result(result: Dict[str, Any]):
    """Validate the structure of the generator result."""
    # Check if the result is a dictionary
    assert isinstance(result, dict), "Result should be a dictionary"
    
    # Check if the result has the expected keys
    assert "success" in result, "Result should have a 'success' key"
    assert result["success"] is True, "Result should be successful"
    
    # Check if brand_voice_components exists and has the expected structure
    assert "brand_voice_components" in result, "Result should have brand_voice_components"
    components = result["brand_voice_components"]
    
    # Validate components
    assert "personality_traits" in components, "Missing personality_traits"
    assert isinstance(components["personality_traits"], list), "personality_traits should be a list"
    assert len(components["personality_traits"]) > 0, "personality_traits should not be empty"
    
    assert "tonality" in components, "Missing tonality"
    assert isinstance(components["tonality"], str), "tonality should be a string"
    assert len(components["tonality"]) > 0, "tonality should not be empty"
    
    assert "identity" in components, "Missing identity"
    assert isinstance(components["identity"], str), "identity should be a string"
    assert len(components["identity"]) > 0, "identity should not be empty"
    
    assert "dos" in components, "Missing dos"
    assert isinstance(components["dos"], list), "dos should be a list"
    assert len(components["dos"]) > 0, "dos should not be empty"
    
    assert "donts" in components, "Missing donts"
    assert isinstance(components["donts"], list), "donts should be a list"
    assert len(components["donts"]) > 0, "donts should not be empty"
    
    # Check for sample content if it's included
    if "sample_content" in components:
        assert isinstance(components["sample_content"], str), "sample_content should be a string"
        assert len(components["sample_content"]) > 0, "sample_content should not be empty"
    
    # Check if generation_metadata exists
    assert "generation_metadata" in result, "Result should have generation_metadata"
    metadata = result["generation_metadata"]
    assert "timestamp" in metadata, "Metadata should have a timestamp"
    assert "generation_depth" in metadata, "Metadata should have generation_depth"

if __name__ == "__main__":
    print("Running Brand Voice Generator Agent Tests")
    print("----------------------------------------")
    
    try:
        # Run the tests
        basic_result = test_generator_basic_depth()
        standard_result = test_generator_standard_depth()
        detailed_result = test_generator_detailed_depth()
        
        # Print a sample of the results
        print("\nSample Results:")
        print("Basic depth personality traits:", basic_result["brand_voice_components"]["personality_traits"])
        print("Standard depth tonality (excerpt):", standard_result["brand_voice_components"]["tonality"][:100] + "...")
        print("Detailed depth dos (first 3):", detailed_result["brand_voice_components"]["dos"][:3])
        
        print("\nAll tests passed! ✅")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
