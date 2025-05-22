"""
Pydantic compatibility layer to handle differences between v1 and v2.

This module provides compatibility functions and decorators to allow code written
for Pydantic v2 to work with Pydantic v1, focusing specifically on the validator
functions that have different names between versions.
"""
import functools
import inspect
import importlib.util
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, get_type_hints

# Check Pydantic version
def get_pydantic_version():
    """Get the major version of installed Pydantic."""
    import pydantic
    version = getattr(pydantic, "__version__", "1.0.0")
    major_version = int(version.split('.')[0])
    return major_version

PYDANTIC_V2 = get_pydantic_version() >= 2

# Import appropriate validators based on version
if PYDANTIC_V2:
    from pydantic import field_validator as _field_validator
    from pydantic import model_validator as _model_validator
    
    # Use the original validators directly
    field_validator = _field_validator
    
    # Create a wrapper for model_validator to handle mode parameter
    def model_validator(*args, **kwargs):
        # For v2, pass through all arguments including mode
        return _model_validator(*args, **kwargs)
else:
    # For v1, we need to adapt the validators
    from pydantic import validator as _field_validator
    from pydantic import root_validator as _root_validator
    
    # Create a wrapper for field_validator to ignore v2-specific parameters
    def field_validator(*args, **kwargs):
        # Remove v2-specific parameters
        kwargs.pop('mode', None)
        return _field_validator(*args, **kwargs)
    
    # For model_validator in Pydantic v1
    def model_validator(*args, **kwargs):
        # In v1, we need to handle differently based on the mode
        # For "after" mode in v2, use root_validator(pre=False) in v1
        # For "before" mode in v2, use root_validator(pre=True) in v1
        mode = kwargs.pop('mode', None)
        pre = True
        if mode == "after":
            pre = False
        return _root_validator(pre=pre, **kwargs)

# Monkey patch the LengthBasedExampleSelector to work with both v1 and v2
def patch_langchain_selectors():
    try:
        import langchain_core.example_selectors.length_based
        
        # Check if we need to patch
        if not PYDANTIC_V2:
            # Get the class
            cls = langchain_core.example_selectors.length_based.LengthBasedExampleSelector
            
            # Check if it has the problematic validator
            if hasattr(cls, 'post_init'):
                # Remove the model_validator decorator and replace with root_validator
                old_post_init = cls.post_init
                delattr(cls, 'post_init')
                
                # Add a new validator with the correct decorator for v1
                setattr(cls, 'post_init', _root_validator(pre=False)(old_post_init.__func__))
                
                print("Successfully patched LengthBasedExampleSelector for Pydantic v1")
        
        return True
    except Exception as e:
        print(f"Error patching LengthBasedExampleSelector: {str(e)}")
        return False

# Try to patch LangChain selectors
patch_success = patch_langchain_selectors()

# Export the appropriate validators
__all__ = ['field_validator', 'model_validator', 'PYDANTIC_V2']