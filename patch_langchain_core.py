#!/usr/bin/env python
"""
Direct monkey patching script for LangChain Core to work with Pydantic v2.
Run this script before starting the backend server.
"""

import sys
import importlib
import importlib.util
import types
from functools import wraps

def get_pydantic_version():
    """Get the major version of installed Pydantic."""
    import pydantic
    version = getattr(pydantic, "__version__", "1.0.0")
    major_version = int(version.split('.')[0])
    return major_version

def patch_length_based_example_selector():
    """
    Directly patch the LengthBasedExampleSelector class in langchain_core
    to work with Pydantic v2.
    """
    try:
        # Import the module
        import langchain_core.example_selectors.length_based
        
        # Check if we need to patch (only for Pydantic v1)
        pydantic_v2 = get_pydantic_version() >= 2
        if pydantic_v2:
            print("Using Pydantic v2, no patching needed")
            return True
        
        # Get the class
        cls = langchain_core.example_selectors.length_based.LengthBasedExampleSelector
        
        # Find the post_init method and its decorator
        if hasattr(cls, 'post_init'):
            # Import the root_validator from pydantic v1
            from pydantic import root_validator
            
            # Get the original method
            original_method = cls.post_init
            
            # Remove the original method and its decorator
            delattr(cls, 'post_init')
            
            # Create a new method with the correct decorator
            @root_validator(pre=False)
            def patched_post_init(cls, values):
                """Patched validator that works with Pydantic v1."""
                if values.get("example_text_lengths"):
                    return values
                
                # Get the example_prompt and examples from values
                example_prompt = values.get("example_prompt")
                examples = values.get("examples", [])
                
                # Format examples and calculate lengths
                if example_prompt and examples:
                    string_examples = [example_prompt.format(**eg) for eg in examples]
                    get_text_length = values.get("get_text_length", lambda x: len(x.split()))
                    values["example_text_lengths"] = [get_text_length(eg) for eg in string_examples]
                
                return values
            
            # Add the patched method to the class
            setattr(cls, 'post_init', patched_post_init)
            
            print("Successfully patched LengthBasedExampleSelector.post_init")
            return True
        else:
            print("Could not find post_init method in LengthBasedExampleSelector")
            return False
    except Exception as e:
        print(f"Error patching LengthBasedExampleSelector: {str(e)}")
        return False

if __name__ == "__main__":
    success = patch_length_based_example_selector()
    if success:
        print("Patching completed successfully")
    else:
        print("Patching failed")
        sys.exit(1)
