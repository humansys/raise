import httpx
import os
import logging
from typing import Optional, Dict, Any
import json

class OpenRouterClient:
    def extract_rules(self, formatted_prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Sends the formatted prompt to the OpenRouter API and returns the response."""
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            logging.error("OPENROUTER_API_KEY environment variable not set.")
            raise ValueError("API key is missing. Set the OPENROUTER_API_KEY environment variable.")

        target_model = model or self.default_model
        logging.info(f"Sending request to OpenRouter model: {target_model}")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost", # Example referrer
            "X-Title": "Raise Rule Extractor MVP", # Example title
        }

        data = {
            "model": target_model,
            "messages": [
                {"role": "user", "content": formatted_prompt}
            ]
        }

        try:
            response = self.client.post(self.api_url, headers=headers, json=data, timeout=self.timeout)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            # --- Start Debugging Addition ---
            if os.environ.get("DEBUG_LLM_RESPONSE", "False").lower() == "true":
                print("\n--- LLM Raw Response Start ---")
                try:
                    # Attempt pretty printing if JSON, otherwise raw text
                    print(json.dumps(response.json(), indent=2))
                except json.JSONDecodeError:
                    print(response.text) # Print raw text if not valid JSON
                print("--- LLM Raw Response End ---\n")
            # --- End Debugging Addition ---

            return response.json()

        except httpx.TimeoutException as e:
            logging.error(f"Request timed out: {e}")
            raise ConnectionError(f"Request timed out after {self.timeout} seconds.") from e
        except httpx.RequestError as e:
            logging.error(f"An error occurred while requesting {e.request.url!r}: {e}")
            raise ConnectionError(f"HTTP request failed: {e}") from e
        except httpx.HTTPStatusError as e:
            logging.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
            logging.error(f"Response body: {e.response.text}")
            raise ConnectionError(f"HTTP error {e.response.status_code}: {e.response.text}") from e
        except Exception as e:
            logging.exception("An unexpected error occurred during API call.") # Log full traceback
            raise RuntimeError(f"An unexpected error occurred: {e}") from e 