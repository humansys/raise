"""Module responsible for formatting prompts for the LLM."""

import os
from pathlib import Path
from typing import Dict, Any
import yaml

from ..models.business_rule import BusinessRule # Using relative import

# Define project root relative to this file's location
# Assumes this file is at rules_extractor/core/prompt_formatter.py
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Define default paths relative to the project root
DEFAULT_PROMPT_DIR = PROJECT_ROOT / "rules_extractor" / "prompts"
DEFAULT_SYSTEM_MESSAGE_FILE = DEFAULT_PROMPT_DIR / "system_message.md"
DEFAULT_EXAMPLE_INPUT_FILE = PROJECT_ROOT / "rules_extractor/docs/backlog/features/RAISE-36-llm-rule-extraction/stories/RAISE-37-list-business-rule-candidates/examples/one-shot-example-input.rpgle"
DEFAULT_EXAMPLE_OUTPUT_FILE = PROJECT_ROOT / "rules_extractor/docs/backlog/features/RAISE-36-llm-rule-extraction/stories/RAISE-37-list-business-rule-candidates/examples/one-shot-example-output.yml"


class PromptFormatter:
    """Formats the complete prompt to be sent to the LLM for rule extraction."""

    def __init__(
        self,
        system_message_path: Path = DEFAULT_SYSTEM_MESSAGE_FILE,
        example_input_path: Path = DEFAULT_EXAMPLE_INPUT_FILE,
        example_output_path: Path = DEFAULT_EXAMPLE_OUTPUT_FILE,
    ):
        """Initializes the formatter, loading template components."""
        self.system_message = self._load_text_file(system_message_path)
        self.example_input_code = self._load_text_file(example_input_path)
        self.example_output_yaml = self._load_text_file(example_output_path)

        # Validate that the example output can be parsed (optional but recommended)
        try:
            example_data = yaml.safe_load(self.example_output_yaml)
            # Optionally, fully validate against Pydantic model if needed here
            # BusinessRule.parse_obj(example_data) # Or the specific rule type
            if not isinstance(example_data, dict):
                raise ValueError("Example output YAML does not represent a single rule object.")
        except (yaml.YAMLError, ValueError) as e:
            raise ValueError(f"Failed to load or parse example output YAML {example_output_path}: {e}")
        except Exception as e:
             # Catch other potential errors like Pydantic validation
             raise ValueError(f"Error processing example output YAML {example_output_path}: {e}")

    def _load_text_file(self, file_path: Path) -> str:
        """Loads content from a text file."""
        # Now directly check the provided (likely absolute or project-relative) path
        if not file_path.is_file():
             raise FileNotFoundError(f"Prompt component file not found at {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading prompt component file {file_path}: {e}")

    def format_prompt(self, code_chunk: str) -> str:
        """Constructs the final prompt string for a given code chunk."""
        # Basic structure using f-strings. Could use Jinja2 for more complex templating.
        prompt = f"""\
{self.system_message}

--- EXAMPLE --- 

**Input Code Snippet:**
```rpgle
{self.example_input_code}
```

**Desired Output (YAML format):**
```yaml
{self.example_output_yaml}
```

--- END EXAMPLE ---

--- TASK ---

Analyze the following code snippet and extract any potential business rules in the same YAML format as the example above. If no rules are found, return an empty list `[]`.

**Input Code Snippet:**
```
{code_chunk}
```

**Output:**
```yaml
"""
        return prompt

# Example Usage (for testing)
if __name__ == '__main__':
    try:
        # Create dummy files if they don't exist for basic testing
        if not DEFAULT_SYSTEM_MESSAGE_FILE.exists():
            DEFAULT_SYSTEM_MESSAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
            DEFAULT_SYSTEM_MESSAGE_FILE.write_text("SYSTEM MESSAGE PLACEHOLDER: Analyze code, extract rules.", encoding='utf-8')
        if not DEFAULT_EXAMPLE_INPUT_FILE.exists():
             DEFAULT_EXAMPLE_INPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
             DEFAULT_EXAMPLE_INPUT_FILE.write_text("   IF KONTO-STATUS = 'A' THEN MOVE 'ACTIVE' TO STATUS-OUT.", encoding='utf-8')
        if not DEFAULT_EXAMPLE_OUTPUT_FILE.exists():
             DEFAULT_EXAMPLE_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
             DEFAULT_EXAMPLE_OUTPUT_FILE.write_text(
                 "id: RULE-D000\ntype: decision\ndescription: Set status based on KONTO-STATUS.\nconditions:\n  type: comparison\n  field: KONTO-STATUS\n  operator: ==\n  value: \"'A\'\"\noutcomes:\n  - result:\n      type: assignments\n      actions:\n        - target_field: STATUS-OUT\n          value: \"'ACTIVE\'\"\nsource_reference:\n  program: DUMMY\n  lines: \"1\"\nconfidence: 1.0\nextracted_timestamp: \"2024-01-01T00:00:00Z\"\nsystem_version: \"DUMMY_V1\"",
                 encoding='utf-8'
             )

        formatter = PromptFormatter()
        test_code = "   COMPUTE TOTAL = QTY * PRICE.\n   IF TOTAL > 1000 THEN PERFORM APPLY_SURCHARGE."
        final_prompt = formatter.format_prompt(test_code)
        print("--- Generated Prompt ---")
        print(final_prompt)
        print("----------------------")

    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Error during PromptFormatter initialization or usage: {e}") 