#!/usr/bin/env python3
"""
Script to patch LangChain files to work with Pydantic v2
"""
import os
import sys
import shutil

def patch_length_based_file():
    """Patch the length_based.py file to work with Pydantic v2"""
    # Path to the file to patch
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "content-platform-env/lib/python3.12/site-packages/langchain_core/example_selectors/length_based.py"
    )
    
    # Create a backup of the original file
    backup_path = file_path + ".bak"
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        print(f"Created backup at {backup_path}")
    
    # New content for the file
    new_content = """
"""Select examples based on length."""

import re
from typing import Callable, List, Dict, Any

from pydantic import BaseModel, Field
from typing_extensions import Self

from langchain_core.example_selectors.base import BaseExampleSelector
from langchain_core.prompts.prompt import PromptTemplate


def _get_length_based(text: str) -> int:
    return len(re.split("\\n| ", text))


class LengthBasedExampleSelector(BaseExampleSelector, BaseModel):
    """Select examples based on length."""

    examples: List[Dict[str, Any]]
    """A list of the examples that the prompt template expects."""

    example_prompt: PromptTemplate
    """Prompt template used to format the examples."""

    get_text_length: Callable[[str], int] = _get_length_based
    """Function to measure prompt length. Defaults to word count."""

    max_length: int = 2048
    """Max length for the prompt, beyond which examples are cut."""

    example_text_lengths: List[int] = Field(default_factory=list)  # :meta private:
    """Length of each example."""

    def add_example(self, example: Dict[str, Any]) -> None:
        """Add new example to list.

        Args:
            example: A dictionary with keys as input variables
                and values as their values.
        """
        self.examples.append(example)
        string_example = self.example_prompt.format(**example)
        self.example_text_lengths.append(self.get_text_length(string_example))

    async def aadd_example(self, example: Dict[str, Any]) -> None:
        """Async add new example to list.

        Args:
            example: A dictionary with keys as input variables
                and values as their values.
        """
        self.add_example(example)

    def post_init(self) -> Self:
        """Validate that the examples are formatted correctly."""
        if self.example_text_lengths:
            return self
        string_examples = [self.example_prompt.format(**eg) for eg in self.examples]
        self.example_text_lengths = [self.get_text_length(eg) for eg in string_examples]
        return self

    def select_examples(self, input_variables: Dict[str, str]) -> List[Dict[str, Any]]:
        """Select which examples to use based on the input lengths.

        Args:
            input_variables: A dictionary with keys as input variables
               and values as their values.

        Returns:
            A list of examples to include in the prompt.
        """
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

    async def aselect_examples(self, input_variables: Dict[str, str]) -> List[Dict[str, Any]]:
        """Async select which examples to use based on the input lengths.

        Args:
            input_variables: A dictionary with keys as input variables
               and values as their values.

        Returns:
            A list of examples to include in the prompt.
        """
        return self.select_examples(input_variables)
"""
    
    # Write the new content to the file
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"Successfully patched {file_path}")

if __name__ == "__main__":
    patch_length_based_file()
    print("Patching complete!")
