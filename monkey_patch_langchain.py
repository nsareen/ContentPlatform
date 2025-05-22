#!/usr/bin/env python
"""
Direct monkey patching script for LangChain Core to work with Pydantic v2.
Run this script before starting the backend server.
"""

import sys
import importlib
import types
from functools import wraps

def get_pydantic_version():
    """Get the major version of installed Pydantic."""
    import pydantic
    version = getattr(pydantic, "__version__", "1.0.0")
    major_version = int(version.split('.')[0])
    return major_version

def monkey_patch_langchain():
    """Apply runtime monkey patches to make LangChain work with Pydantic v2."""
    try:
        # Check Pydantic version
        pydantic_v2 = get_pydantic_version() >= 2
        if not pydantic_v2:
            print("Using Pydantic v1, no patching needed")
            return True
        
        print("Using Pydantic v2, applying monkey patches...")
        
        # Import the problematic module
        import langchain_core.example_selectors.length_based
        from langchain_core.example_selectors.length_based import LengthBasedExampleSelector
        
        # Create a new post_init method that works with Pydantic v2
        original_post_init = LengthBasedExampleSelector.post_init
        
        # Define a replacement for the post_init method
        def patched_post_init(self):
            """Patched validator that works with Pydantic v2."""
            if self.example_text_lengths:
                return self
            string_examples = [self.example_prompt.format(**eg) for eg in self.examples]
            self.example_text_lengths = [self.get_text_length(eg) for eg in string_examples]
            return self
        
        # Replace the original method with our patched version
        LengthBasedExampleSelector.post_init = patched_post_init
        
        # Monkey patch the model_validator decorator
        from pydantic import model_validator
        
        # Get the decorator from the class
        original_decorator = None
        for name, method in vars(LengthBasedExampleSelector).items():
            if name == 'post_init' and hasattr(method, '__wrapped__'):
                original_decorator = method.__wrapped__
                break
        
        # Apply the correct decorator for Pydantic v2
        if original_decorator:
            # Remove the original decorated method
            delattr(LengthBasedExampleSelector, 'post_init')
            
            # Add the method with the correct decorator
            setattr(LengthBasedExampleSelector, 'post_init', 
                   model_validator(mode="after")(patched_post_init))
        
        print("Successfully patched LengthBasedExampleSelector for Pydantic v2")
        return True
    except Exception as e:
        print(f"Error patching LangChain: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = monkey_patch_langchain()
    if success:
        print("Patching completed successfully")
    else:
        print("Patching failed")
        sys.exit(1)
