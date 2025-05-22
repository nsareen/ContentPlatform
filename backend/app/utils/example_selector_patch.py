"""
Targeted patch for LengthBasedExampleSelector to work with Pydantic v2.
This patch only modifies the specific class that's causing issues.
"""

import importlib
import sys
from types import ModuleType

def patch_length_based_example_selector():
    """
    Apply a targeted patch to LengthBasedExampleSelector to make it work with Pydantic v2.
    This is much more focused than trying to patch all of LangChain.
    """
    try:
        # Import the module that contains the problematic class
        module_name = 'langchain_core.example_selectors.length_based'
        
        # Check if the module is already loaded
        if module_name in sys.modules:
            # Get the module
            module = sys.modules[module_name]
            
            # Get the class
            if hasattr(module, 'LengthBasedExampleSelector'):
                # Create a custom implementation that doesn't use the problematic decorator
                from pydantic import BaseModel, Field
                from typing import Callable, List, Dict, Any
                import re
                from langchain_core.example_selectors.base import BaseExampleSelector
                from langchain_core.prompts.prompt import PromptTemplate
                
                def _get_length_based(text: str) -> int:
                    return len(re.split(r"\n| ", text))
                
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
                    
                    def __init__(self, **data):
                        super().__init__(**data)
                        # Initialize example text lengths if not already set
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
                
                # Replace the original class with our patched version
                module.LengthBasedExampleSelector = PatchedLengthBasedExampleSelector
                
                # Also update the exports
                if hasattr(module, '__all__') and 'LengthBasedExampleSelector' in module.__all__:
                    pass  # The name is already in __all__, no need to change it
                
                print("Successfully patched LengthBasedExampleSelector")
                return True
            else:
                print("Could not find LengthBasedExampleSelector in the module")
                return False
        else:
            # Import the module first, then patch it
            module = importlib.import_module(module_name)
            # Recursively call this function now that the module is loaded
            return patch_length_based_example_selector()
    
    except Exception as e:
        print(f"Error patching LengthBasedExampleSelector: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Apply the patch when this module is imported
success = patch_length_based_example_selector()
if success:
    print("LengthBasedExampleSelector patched successfully")
else:
    print("Failed to patch LengthBasedExampleSelector")
