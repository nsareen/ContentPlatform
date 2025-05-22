"""
Custom example selectors compatible with Pydantic v2
"""

import re
from typing import Callable, Dict, List, Any

from pydantic import BaseModel, Field
from langchain_core.example_selectors.base import BaseExampleSelector
from langchain_core.prompts.prompt import PromptTemplate

def _get_length_based(text: str) -> int:
    """Get the length of text based on word count."""
    return len(re.split(r"\n| ", text))

class CustomLengthBasedExampleSelector(BaseExampleSelector, BaseModel):
    """Select examples based on length, compatible with Pydantic v2."""

    examples: List[Dict[str, Any]] = Field(default_factory=list)
    """A list of the examples that the prompt template expects."""

    example_prompt: PromptTemplate
    """Prompt template used to format the examples."""

    get_text_length: Callable[[str], int] = _get_length_based
    """Function to measure prompt length. Defaults to word count."""

    max_length: int = 2048
    """Max length for the prompt, beyond which examples are cut."""

    example_text_lengths: List[int] = Field(default_factory=list)
    """Length of each example."""

    def add_example(self, example: Dict[str, str]) -> None:
        """Add new example to list."""
        self.examples.append(example)
        string_example = self.example_prompt.format(**example)
        self.example_text_lengths.append(self.get_text_length(string_example))

    async def aadd_example(self, example: Dict[str, str]) -> None:
        """Async add new example to list."""
        self.add_example(example)

    def model_post_init(self, __context: Any) -> None:
        """Initialize example text lengths if not already set."""
        if not self.example_text_lengths and self.examples:
            string_examples = [self.example_prompt.format(**eg) for eg in self.examples]
            self.example_text_lengths = [self.get_text_length(eg) for eg in string_examples]

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
