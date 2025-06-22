"""Module for interacting with LLMs via the OpenRouter API."""

import os
import json
import logging
from typing import Optional, Dict, Any

# Note: Requires an external HTTP client library like 'requests' or 'httpx'
# Add 'requests' or 'httpx' to your requirements.txt
try:
    # Using httpx for potential async benefits later, but requests is also fine
    import httpx
except ImportError:
    httpx = None # Indicate that the library is missing

logger = logging.getLogger(__name__)

DEFAULT_OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-3-opus" # As requested
DEFAULT_TIMEOUT = 60 # seconds

class OpenRouterClient:
    """Client for making requests to the OpenRouter API (OpenAI-compatible)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        api_base: str = DEFAULT_OPENROUTER_API_BASE,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """Initializes the OpenRouter client.

        Args:
            api_key: OpenRouter API key. Defaults to OPENROUTER_API_KEY env var.
            model: The model identifier to use (e.g., 'anthropic/claude-3-opus').
            api_base: The base URL for the OpenRouter API.
            timeout: Request timeout in seconds.
        """
        if httpx is None:
            raise ImportError("The 'httpx' library is required for OpenRouterClient. Please install it.")

        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided and OPENROUTER_API_KEY environment variable not set.")

        self.model = model
        self.api_base = api_base
        self.timeout = timeout
        self.api_url = f"{self.api_base.rstrip('/')}/chat/completions"

        # Optional: Add headers for site identification (good practice for OpenRouter)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # "HTTP-Referer": "YOUR_SITE_URL", # Optional: Replace with your app URL
            # "X-Title": "YOUR_APP_NAME", # Optional: Replace with your app name
        }

    def get_completion(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.1) -> str:
        """Sends a prompt to the OpenRouter API and returns the completion text.

        Args:
            prompt: The complete prompt string.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (lower means more deterministic).

        Returns:
            The content of the LLM's response message.

        Raises:
            ValueError: If the API returns an error.
            IOError: If there is a network or request issue.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            # Add other parameters like top_p, frequency_penalty etc. if needed
        }

        try:
            logger.debug(f"Sending request to OpenRouter: {self.api_url} with model {self.model}")
            # Using synchronous httpx client here
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                )

            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            response_data = response.json()
            
            # Debug: Print the complete raw response if DEBUG_LLM_RESPONSE is enabled
            if os.environ.get("DEBUG_LLM_RESPONSE", "False").lower() == "true":
                print("\n--- Raw LLM API Response ---")
                print(json.dumps(response_data, indent=2))
                print("--- End Raw LLM API Response ---\n")
            
            logger.debug(f"Received response from OpenRouter: {response_data}")

            # Extract the content from the response
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                message = response_data["choices"][0].get("message")
                if message and message.get("content"):
                    content = message["content"].strip()
                    
                    # Debug: Print the extracted content if DEBUG_LLM_RESPONSE is enabled
                    if os.environ.get("DEBUG_LLM_RESPONSE", "False").lower() == "true":
                        print("\n--- Extracted LLM Response Content ---")
                        print(content)
                        print("--- End Extracted LLM Response Content ---\n")
                    
                    return content
                else:
                    raise ValueError("Invalid response format: 'content' not found in message.")
            else:
                raise ValueError("Invalid response format: 'choices' array is missing or empty.")

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API Error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"OpenRouter API Error: {e.response.status_code} - {e.response.text}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error contacting OpenRouter: {e}")
            raise IOError(f"Network error contacting OpenRouter: {e}") from e
        except json.JSONDecodeError as e:
             logger.error(f"Failed to decode JSON response from OpenRouter: {e}")
             raise ValueError(f"Failed to decode JSON response from OpenRouter: {e}") from e
        except Exception as e:
            logger.exception("An unexpected error occurred in get_completion")
            raise

# Example Usage (for testing - requires OPENROUTER_API_KEY env var)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # Ensure httpx is installed: pip install httpx

    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Skipping LLM Client test: OPENROUTER_API_KEY environment variable not set.")
    elif httpx is None:
        print("Skipping LLM Client test: httpx library not installed.")
    else:
        try:
            client = OpenRouterClient()
            # Simple test prompt (replace with a formatted one for real use)
            test_prompt = "SYSTEM: You are a helpful assistant.\nUSER: What is the capital of France?"

            print(f"Sending test prompt to {client.model}...")
            completion = client.get_completion(test_prompt, max_tokens=50)
            print("--- LLM Response ---")
            print(completion)
            print("-------------------")

        except (ValueError, IOError, ImportError) as e:
            print(f"Error during LLM Client testing: {e}")
        except Exception as e:
             print(f"An unexpected error occurred during testing: {e}") 