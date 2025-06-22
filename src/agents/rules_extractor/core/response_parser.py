"""Module for parsing and validating LLM responses containing business rules."""

import yaml
import logging
from typing import List, Optional, Dict, Any
from pydantic import ValidationError
import re

# Change from absolute to relative import
from ..models.business_rule import BusinessRule, load_rule_from_dict

logger = logging.getLogger(__name__)

class ResponseParser:
    """Parses and validates YAML strings from LLM responses into BusinessRule objects."""

    def __init__(self):
        """Initializes the parser."""
        # Could add configuration options later if needed
        pass

    def _extract_yaml_content(self, raw_response: str) -> Optional[str]:
        """Extracts YAML content, potentially removing code block fences."""
        if not raw_response or raw_response.strip() == '':
            logger.warning("Received empty raw response from LLM.")
            return None

        # First check if the entire response is just an empty list
        if raw_response.strip() == '[]':
            logger.info("LLM indicated no business rules found (returned '[]').")
            return '[]'  # Return it so it parses correctly to an empty list later

        # Debug the raw response
        logger.debug(f"Raw response first 100 chars: {raw_response[:100]}")
        if len(raw_response) > 500:
            logger.debug(f"... and last 100 chars: {raw_response[-100:]}")

        # Look for any YAML content blocks (with or without language markers)
        yaml_blocks = []
        
        # Pattern for ```yaml ... ``` blocks
        yaml_pattern = re.compile(r"```(?:yaml)?\s*\n(.*?)\n\s*```", re.DOTALL)
        yaml_matches = yaml_pattern.findall(raw_response)
        if yaml_matches:
            yaml_blocks.extend(yaml_matches)
            logger.debug(f"Found {len(yaml_matches)} YAML code blocks with explicit fences.")
            
        # If we found YAML blocks, use the first one that seems valid
        for block in yaml_blocks:
            content = block.strip()
            if content and (content.startswith('-') or content.startswith('id:') or
                          content.startswith('[') or '{' in content):
                logger.debug("Using YAML content extracted from code block.")
                return content
                
        # If no valid YAML blocks were found, try treating the whole response as YAML
        # after stripping any trailing backticks
        content = raw_response.strip()
        # Remove any trailing backticks and surrounding whitespace
        if content.endswith('```'):
            content = content[:content.rindex('```')].strip()
            
        # Final check if content looks like YAML
        if content and (content.startswith('-') or content.startswith('id:') or
                      content.startswith('[') or '{' in content):
            logger.debug("Using entire response as YAML after cleanup.")
            return content
            
        logger.warning(f"Response content does not appear to be valid YAML: {content[:100]}...")
        return None

    def parse_response(self, llm_output: str) -> List[BusinessRule]:
        """Parses the raw LLM output string into a list of BusinessRule objects.

        Args:
            llm_output: The raw string response from the LLM.

        Returns:
            A list of validated BusinessRule objects. Returns an empty list if
            no rules are found, the YAML is invalid, validation fails, or the
            input is empty.
        """
        extracted_yaml = self._extract_yaml_content(llm_output)

        if extracted_yaml is None:
            # Warning already logged in _extract_yaml_content
            return []

        try:
            # Load the YAML content
            parsed_data = yaml.safe_load(extracted_yaml)

            # Check for the explicit empty list case after parsing
            if isinstance(parsed_data, list) and not parsed_data:
                logger.info("Successfully parsed empty list from LLM response.")
                return []

            # Determine if the output is a single rule object or a list of rules
            if isinstance(parsed_data, dict):
                # Single rule object
                rules_data = [parsed_data]
                logger.debug("Parsed a single rule object from YAML.")
            elif isinstance(parsed_data, list):
                # List of rule objects
                rules_data = parsed_data
                logger.debug(f"Parsed a list of {len(rules_data)} potential rule objects from YAML.")
            else:
                logger.warning(f"Parsed YAML is not a dictionary or list, but type '{type(parsed_data).__name__}'. Content: {str(parsed_data)[:100]}...")
                return []

            # Validate each rule dictionary against the Pydantic models
            validated_rules: List[BusinessRule] = []
            for i, rule_data in enumerate(rules_data):
                if not isinstance(rule_data, dict):
                    logger.warning(f"Item #{i+1} in the parsed list is not a dictionary (rule object), skipping.")
                    continue # Skip non-dictionary items in the list
                try:
                    # Use the helper function from the models module for validation and type dispatching
                    validated_rule = load_rule_from_dict(rule_data)
                    validated_rules.append(validated_rule)
                    logger.debug(f"Successfully validated rule object #{i+1} with ID {validated_rule.id}")
                except ValidationError as e:
                    logger.warning(f"Pydantic validation failed for rule object #{i+1}: {e}. Rule data: {str(rule_data)[:200]}...")
                    # Continue to the next rule, skipping the invalid one
                except ValueError as e:
                     logger.warning(f"Error loading rule object #{i+1} (likely unknown type or structure issue): {e}. Rule data: {str(rule_data)[:200]}...")
                     # Continue to the next rule

            if validated_rules:
                 logger.info(f"Successfully parsed and validated {len(validated_rules)} business rules.")
            elif rules_data: # Parsed data but nothing validated
                 logger.warning("Parsed YAML data, but no rules passed validation.")
            # If rules_data was empty initially, already logged.

            return validated_rules

        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML from LLM response: {e}. Content: {extracted_yaml[:200]}...")
            return []
        except Exception as e:
            # Catch any other unexpected errors during parsing/validation
            logger.exception(f"An unexpected error occurred during response parsing: {e}")
            return []

# Example Usage (for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = ResponseParser()

    # --- Test Cases ---
    test_cases = [
        {
            "name": "Single Valid Rule (YAML fences)",
            "input": "```yaml\nid: RULE-D001\ntype: decision\ndescription: Test rule\nsource_reference:\n  program: TESTPGM\n  lines: \"10-12\"\nconfidence: 0.9\nextracted_timestamp: \"2024-01-01T12:00:00Z\"\nsystem_version: \"V1\"\nconditions:\n  type: comparison\n  field: X\n  operator: ==\n  value: 1\noutcomes:\n  - result: \"OK\"\n```",
            "expected_count": 1
        },
        {
            "name": "List of Valid Rules (No fences)",
            "input": "- id: RULE-V001\n  type: validation\n  description: Rule 1\n  source_reference: {program: PGM1, lines: \"5\"}\n  confidence: 0.8\n  extracted_timestamp: \"2024-01-01T12:00:00Z\"\n  system_version: \"V1\"\n  conditions: {type: comparison, field: Y, operator: <, value: 0}\n  action: {type: error_handling, level: error, message_template: \"Y too low\"}\n- id: RULE-C001\n  type: calculation\n  description: Rule 2\n  source_reference: {program: PGM1, lines: \"20\"}\n  confidence: 0.95\n  extracted_timestamp: \"2024-01-01T12:00:00Z\"\n  system_version: \"V1\"\n  formula: \"Z = A + B\"\n  target_field: Z\n  source_fields: [A, B]",
            "expected_count": 2
        },
        {
            "name": "Malformed YAML",
            "input": "```yaml\nid: RULE-X001\ntype: oops\ndescription: Bad YAML\n  missing_indent: true\n```",
            "expected_count": 0
        },
        {
            "name": "Invalid Pydantic Data (Missing required field)",
            "input": "```yaml\nid: RULE-V002\ntype: validation\n# description: is missing\nsource_reference: {program: PGM2, lines: \"1\"}\nconfidence: 0.7\nextracted_timestamp: \"2024-01-01T12:00:00Z\"\nsystem_version: \"V1\"\nconditions: {type: comparison, field: A, operator: ==, value: 1}\naction: {type: error_handling, level: warning, message_template: \"A=1\"}\n```",
            "expected_count": 0
        },
                {
            "name": "Empty List Response (No rules found)",
            "input": "[]",
            "expected_count": 0
        },
        {
            "name": "Empty List Response (YAML fences)",
            "input": "```yaml\n[]\n```",
            "expected_count": 0
        },
        {
            "name": "Empty String Response",
            "input": "",
            "expected_count": 0
        },
        {
            "name": "Non-YAML String",
            "input": "Sorry, I couldn't find any rules.",
            "expected_count": 0
        },
        {
            "name": "Mixed Valid/Invalid Rules in List",
            "input": "- id: RULE-V003\n  type: validation\n  description: Valid Rule\n  source_reference: {program: PGM3, lines: \"1\"}\n  confidence: 0.9\n  extracted_timestamp: \"2024-01-01T12:00:00Z\"\n  system_version: \"V1\"\n  conditions: {type: comparison, field: C, operator: !=, value: 0}\n  action: {type: logging, message_template: \"C not zero\"}\n- id: RULE-I001\n  type: invalid_type\n  description: Invalid Rule Type\n  source_reference: {program: PGM3, lines: \"10\"}\n  confidence: 0.5\n  extracted_timestamp: \"2024-01-01T12:00:00Z\"\n  system_version: \"V1\"",
           "expected_count": 1 # Only the valid one should be returned
        }

    ]

    print("--- Running Parser Test Cases ---")
    for case in test_cases:
        print(f"\nTesting: {case['name']}")
        result = parser.parse_response(case['input'])
        print(f"  Input: {case['input'][:80]}..."
              f"  Expected Count: {case['expected_count']}, Got Count: {len(result)}")
        if len(result) == case['expected_count']:
            print("  Result: PASS")
        else:
            print("  Result: FAIL")
            # Optionally print the rules found for debugging
            # for rule in result:
            #     print(f"    - Rule ID: {rule.id}, Type: {rule.type}")
    print("\n--- Test Cases Complete ---") 