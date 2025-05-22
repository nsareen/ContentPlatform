#!/usr/bin/env python
"""
Monkey patch for LangChain Core to work with Pydantic v2.
This script directly modifies the LengthBasedExampleSelector class at runtime.

Usage:
    python fix_langchain.py
"""

import sys
import os
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
        
        # First, make sure the module is not already imported
        module_name = 'langchain_core.example_selectors.length_based'
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # Create a custom implementation that doesn't use the problematic decorator
        from pydantic import BaseModel, Field
        from typing import Callable, List, Dict, Any
        import re
        from langchain_core.example_selectors.base import BaseExampleSelector
        from langchain_core.prompts.prompt import PromptTemplate
        
        # Get the original module
        original_module = importlib.import_module(module_name)
        
        # Create a new module to replace the original
        new_module = types.ModuleType(module_name)
        
        # Copy all attributes from the original module
        for attr_name in dir(original_module):
            if not attr_name.startswith('__'):
                setattr(new_module, attr_name, getattr(original_module, attr_name))
        
        # Define the replacement for _get_length_based
        def _get_length_based(text: str) -> int:
            return len(re.split(r"\n| ", text))
        
        # Set this function in the new module
        setattr(new_module, '_get_length_based', _get_length_based)
        
        # Create a replacement class
        class PatchedLengthBasedExampleSelector(BaseExampleSelector, BaseModel):
            """Select examples based on length."""
            
            examples: List[Dict[str, Any]]
            """A list of the examples that the prompt template expects."""
            
            example_prompt: PromptTemplate
            """Prompt template used to format the examples."""
            
            get_text_length: Callable[[str], int] = _get_length_based
            """Function to measure prompt length. Defaults to word count."""
            
            max_length: int = 2048
            """Max length for the prompt, beyond which examples are cut."""
            
            example_text_lengths: List[int] = Field(default_factory=list)
            """Length of each example."""
            
            def model_post_init(self):
                """Initialize example text lengths if not already set."""
                if not self.example_text_lengths and self.examples:
                    string_examples = [self.example_prompt.format(**eg) for eg in self.examples]
                    self.example_text_lengths = [self.get_text_length(eg) for eg in string_examples]
            
            def add_example(self, example: Dict[str, str]) -> None:
                """Add new example to list."""
                self.examples.append(example)
                string_example = self.example_prompt.format(**example)
                self.example_text_lengths.append(self.get_text_length(string_example))
            
            async def aadd_example(self, example: Dict[str, str]) -> None:
                """Async add new example to list."""
                self.add_example(example)
            
            def select_examples(self, input_variables: Dict[str, str]) -> List[Dict[str, str]]:
                """Select which examples to use based on the input lengths."""
                inputs = " ".join(input_variables.values())
                remaining_length = self.max_length - self.get_text_length(inputs)
                i = 0
                examples = []
                while remaining_length > 0 and i < len(self.examples):
                    new_length = remaining_length - self.example_text_lengths[i]
                    if new_length < 0:
                        break
                    examples.append(self.examples[i])
                    remaining_length = new_length
                    i += 1
                return examples
            
            async def aselect_examples(self, input_variables: Dict[str, str]) -> List[Dict[str, str]]:
                """Async select which examples to use based on the input lengths."""
                return self.select_examples(input_variables)
        
        # Replace the class in the new module
        setattr(new_module, 'LengthBasedExampleSelector', PatchedLengthBasedExampleSelector)
        
        # Update exports
        if hasattr(original_module, '__all__'):
            setattr(new_module, '__all__', original_module.__all__)
        
        # Replace the module in sys.modules
        sys.modules[module_name] = new_module
        
        print(f"Successfully patched {module_name}")
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
        sys.exit(0)
    else:
        print("Patching failed")
        sys.exit(1)
