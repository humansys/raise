"""Common test fixtures and configuration for the Rules Extractor component."""

import os
import pytest
from pathlib import Path

@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"

@pytest.fixture
def sample_rpgle_code() -> str:
    """Return a sample RPGLE code snippet for testing."""
    return """
    // Check if user is valid and password matches
    Exec SQL
      Select PASSWORD Into :password1
        From USERS
        Where username = :USRNME;

    If (SQLCode = 0 AND PWD = password1);
       passbys1.returncode = 000;
       passbys1.username1 = usrnme;
    ElseIf (SQLCode = 0 AND PWD <> password1);
       passbys1.returncode = 100;
       LogMSG = 'Incorrect password';
    Else;
       passbys1.returncode = 100;
       LogMsg = 'User does not exist';
    EndIf;
    """

@pytest.fixture
def mock_openrouter_response() -> dict:
    """Return a mock OpenRouter API response."""
    return {
        "id": "test-response",
        "choices": [{
            "message": {
                "content": "[]"  # Empty rules list
            }
        }]
    }

@pytest.fixture
def test_env_vars(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DEBUG_LLM_RESPONSE", "True") 