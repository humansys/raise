# Rules Extractor API Documentation

## Overview

The Rules Extractor component provides functionality to extract business rules from legacy code using LLM-based analysis. This document describes the main classes and their APIs.

## Main Components

### RuleExtractor

The main class for extracting business rules from code.

```python
from rules_extractor.extractor import RuleExtractor

extractor = RuleExtractor()
rules = extractor.extract_rules(code_chunk)
```

#### Methods

- `extract_rules(code_chunk: str) -> List[BusinessRule]`
  - Extracts business rules from a code chunk
  - Returns a list of validated BusinessRule objects
  - Returns empty list if no rules found or on error

### BusinessRule

Pydantic model representing a business rule.

```python
from rules_extractor.models.business_rule import BusinessRule

rule = BusinessRule(
    id="RULE-001",
    type="decision",
    description="User authentication rule",
    confidence=0.95
)
```

#### Fields

- `id: str` - Unique identifier for the rule
- `type: str` - Type of rule (decision, validation, etc.)
- `description: str` - Clear description of the rule
- `source_reference: SourceReference` - Reference to source code
- `confidence: float` - Confidence score (0.0-1.0)
- `tags: List[str]` - Optional tags
- `concepts: List[str]` - Business concepts involved

### OpenRouterClient

Client for interacting with the OpenRouter LLM API.

```python
from rules_extractor.core.llm_client import OpenRouterClient

client = OpenRouterClient()
response = client.get_completion(prompt)
```

#### Configuration

Environment variables:
- `OPENROUTER_API_KEY` - API key for OpenRouter
- `LOG_LEVEL` - Logging level (DEBUG, INFO, etc.)
- `DEBUG_LLM_RESPONSE` - Show raw LLM responses

## Usage Examples

### Basic Usage

```python
from rules_extractor.extractor import RuleExtractor

# Initialize the extractor
extractor = RuleExtractor()

# Extract rules from code
code = """
    IF BALANCE < 0 THEN
        SET ACCOUNT-STATUS TO 'OVERDRAWN'
    END-IF
"""
rules = extractor.extract_rules(code)

# Process extracted rules
for rule in rules:
    print(f"Rule {rule.id}: {rule.description}")
```

### Command Line Usage

```bash
# Process a single file
./run_extractor.sh path/to/file.rpgle

# Run with default test cases
./run_extractor.sh
```

## Error Handling

The component uses Python's logging module for error reporting and debugging. All methods return empty lists or None on error rather than raising exceptions (except for initialization errors).

## Dependencies

- `pydantic` - Data validation
- `httpx` - HTTP client
- `pyyaml` - YAML processing
- `python-dotenv` - Environment variable management 