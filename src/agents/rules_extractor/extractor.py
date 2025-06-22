"""Main orchestration module for extracting business rules from code chunks."""

import logging
from typing import List, Optional
import os
import argparse

from rules_extractor.core.prompt_formatter import PromptFormatter
from rules_extractor.core.llm_client import OpenRouterClient
from rules_extractor.core.response_parser import ResponseParser
from rules_extractor.models.business_rule import BusinessRule

logger = logging.getLogger(__name__)

class RuleExtractor:
    """Orchestrates the process of extracting business rules from code chunks."""

    def __init__(
        self,
        formatter: Optional[PromptFormatter] = None,
        client: Optional[OpenRouterClient] = None,
        parser: Optional[ResponseParser] = None
    ):
        """Initializes the extractor with necessary components.

        If components are not provided, default instances will be created.
        This allows for dependency injection during testing or advanced configuration.
        """
        try:
            self.formatter = formatter or PromptFormatter()
            # Note: OpenRouterClient requires OPENROUTER_API_KEY env var by default
            self.client = client or OpenRouterClient()
            self.parser = parser or ResponseParser()
            logger.info("RuleExtractor initialized successfully.")
        except (FileNotFoundError, ValueError, ImportError) as e:
            logger.exception(f"Failed to initialize RuleExtractor components: {e}")
            # Depending on application design, might want to re-raise or handle differently
            raise RuntimeError(f"RuleExtractor initialization failed: {e}") from e

    def extract_rules(self, code_chunk: str) -> List[BusinessRule]:
        """Extracts business rules from a single code chunk.

        Args:
            code_chunk: A string containing the piece of legacy code to analyze.

        Returns:
            A list of validated BusinessRule objects extracted from the code.
            Returns an empty list if no rules are found or if errors occur
            during the process.
        """
        if not code_chunk or not code_chunk.strip():
            logger.warning("extract_rules called with empty code chunk. Returning empty list.")
            return []

        try:
            # 1. Format the prompt
            logger.debug(f"Formatting prompt for code chunk (length: {len(code_chunk)}).")
            prompt = self.formatter.format_prompt(code_chunk)
            logger.debug("Prompt formatted successfully.")

            # 2. Get completion from LLM
            logger.debug("Sending prompt to LLM...")
            raw_response = self.client.get_completion(prompt)
            logger.debug(f"Received raw response from LLM (length: {len(raw_response)}).")

            # 3. Parse the response
            logger.debug("Parsing LLM response...")
            rules = self.parser.parse_response(raw_response)
            logger.info(f"Extraction complete. Found {len(rules)} valid rule(s).")

            return rules

        except (ValueError, IOError) as e:
            # Errors during formatting, client interaction, or parsing
            logger.error(f"Error during rule extraction process: {e}")
            return [] # Return empty list on error as per requirements
        except Exception as e:
            # Catch any unexpected errors
            logger.exception(f"An unexpected error occurred during rule extraction: {e}")
            return []

# Example Usage (for testing)
if __name__ == '__main__':
    # Handle command line arguments
    parser = argparse.ArgumentParser(description="Extract business rules from code.")
    parser.add_argument('--file', type=str, help='Path to the file to process')
    args = parser.parse_args()
    
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        if load_dotenv(): # Returns True if a .env file was found and loaded
            print("Loaded environment variables from .env file.")
        else:
             print(".env file not found or empty, relying on system environment variables.")
    except ImportError:
        print("python-dotenv not installed, relying on system environment variables.")
        # Continue execution, OpenRouterClient will raise error if key isn't in env

    # Configure logging based on environment variable
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        print(f"Invalid log level: {log_level}. Defaulting to INFO.")
        numeric_level = logging.INFO
    
    logging.basicConfig(
        level=numeric_level, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if numeric_level <= logging.DEBUG:
        print(f"Log level set to {log_level}")
    
    try:
        print("--- Initializing Rule Extractor ---")
        # Requires OPENROUTER_API_KEY to be set in environment
        # Requires httpx and PyYAML to be installed
        extractor = RuleExtractor()
        print("--- Initialization Complete ---")
        
        if args.file:
            # Process the specified file
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    code_content = f.read()
                    
                print(f"\n--- Processing file: {args.file} ---")
                extracted_rules = extractor.extract_rules(code_content)
                print(f"\nExtracted {len(extracted_rules)} rules from file:")
                if extracted_rules:
                    for rule in extracted_rules:
                        # Convert Pydantic model to dict for cleaner printing
                        print(rule.model_dump_json(indent=2))
                        print("---")
                else:
                    print("(No rules extracted from file)")
                    
            except (IOError, UnicodeDecodeError) as e:
                print(f"Error reading file {args.file}: {e}")
                print("Try specifying the correct encoding if needed.")
                exit(1)
        else:
            # Run default test cases
            # Example code chunk (replace with more realistic RPG/COBOL if desired)
            test_code_rpgle = """
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

            test_code_no_rules = """
               // Just some technical code
               MOVE A TO B.
               ADD 1 TO COUNTER.
               WRITE OUTPUT-RECORD.
            """

            print("\n--- Testing extraction with RPGLE code chunk ---")
            extracted_rules = extractor.extract_rules(test_code_rpgle)
            print(f"\nExtracted {len(extracted_rules)} rules:")
            if extracted_rules:
                for rule in extracted_rules:
                    # Convert Pydantic model to dict for cleaner printing
                    print(rule.model_dump_json(indent=2))
                    print("---")
            else:
                print("(No rules extracted or error occurred)")

            print("\n--- Testing extraction with code containing no obvious rules ---")
            extracted_rules_none = extractor.extract_rules(test_code_no_rules)
            print(f"\nExtracted {len(extracted_rules_none)} rules:")
            if extracted_rules_none:
                 for rule in extracted_rules_none:
                     print(rule.model_dump_json(indent=2))
                     print("---")
            else:
                print("(No rules extracted - as expected)")

    except RuntimeError as e:
        print(f"Could not run test: {e}")
    except ImportError as e:
        print(f"Could not run test due to missing dependency: {e}. Please install requirements.")
    except Exception as e:
        print(f"An unexpected error occurred during testing: {e}") 