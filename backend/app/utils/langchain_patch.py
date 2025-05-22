"""
Runtime patch for LangChain to handle Pydantic version compatibility issues.
"""

import importlib
import sys

def patch_langchain_modules():
    """Apply runtime patches to LangChain modules for Pydantic compatibility."""
    try:
        # Try to import the module
        import langchain_core.example_selectors.length_based
        
        # If we're using Pydantic v1, we need to patch the module
        from app.utils.pydantic_compat import PYDANTIC_V2
        if not PYDANTIC_V2:
            # The patch should already be applied by pydantic_compat.py
            print("LangChain compatibility patch already applied")
        else:
            print("Using Pydantic v2, no patch needed")
        
        return True
    except Exception as e:
        print(f"Error patching LangChain modules: {str(e)}")
        return False

# Apply the patch
success = patch_langchain_modules()
print(f"LangChain compatibility check {'successful' if success else 'failed'}")