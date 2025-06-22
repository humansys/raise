"""Unit tests for the Rules Extractor module."""

import pytest
from rules_extractor.extractor import RuleExtractor
from rules_extractor.core.prompt_formatter import PromptFormatter
from rules_extractor.core.llm_client import OpenRouterClient
from rules_extractor.core.response_parser import ResponseParser

def test_extractor_initialization(test_env_vars):
    """Test that the RuleExtractor can be initialized correctly."""
    extractor = RuleExtractor()
    assert isinstance(extractor.formatter, PromptFormatter)
    assert isinstance(extractor.client, OpenRouterClient)
    assert isinstance(extractor.parser, ResponseParser)

def test_extract_rules_empty_input(test_env_vars):
    """Test that empty input returns an empty list."""
    extractor = RuleExtractor()
    assert extractor.extract_rules("") == []
    assert extractor.extract_rules("   ") == []
    assert extractor.extract_rules(None) == []

def test_extract_rules_with_sample_code(test_env_vars, sample_rpgle_code, mocker):
    """Test rule extraction with sample RPGLE code."""
    # Mock the LLM client to return a predefined response
    mock_response = {
        "id": "test",
        "choices": [{
            "message": {
                "content": """```yaml
- id: RULE-D001
  type: decision
  description: Test rule
  source_reference:
    program: TEST
    lines: "1-5"
  confidence: 0.95
  extracted_timestamp: "2024-04-06T00:00:00Z"
  system_version: "TEST_V1"
  tags: []
  concepts: []
```"""
            }
        }]
    }
    
    mock_client = mocker.Mock()
    mock_client.get_completion.return_value = mock_response
    
    extractor = RuleExtractor(client=mock_client)
    rules = extractor.extract_rules(sample_rpgle_code)
    
    assert len(rules) == 1
    assert rules[0].id == "RULE-D001"
    assert rules[0].type == "decision"
    assert rules[0].confidence == 0.95

def test_extract_rules_handles_errors(test_env_vars, mocker):
    """Test that the extractor handles errors gracefully."""
    mock_client = mocker.Mock()
    mock_client.get_completion.side_effect = Exception("API Error")
    
    extractor = RuleExtractor(client=mock_client)
    rules = extractor.extract_rules("some code")
    
    assert rules == []  # Should return empty list on error 