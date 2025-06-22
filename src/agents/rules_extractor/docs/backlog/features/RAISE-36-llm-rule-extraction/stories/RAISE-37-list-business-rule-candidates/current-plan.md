# RAISE-37: List Business Rule Candidates - Implementation Plan

## Overview
This plan outlines the steps to implement the functionality for prompting a Large Language Model (LLM) with code chunks and parsing the returned JSON to extract potential business rule candidates. The goal is to create a robust component that integrates with an LLM service, handles its responses, and manages potential errors gracefully.

## Components
1.  **LLM Prompt Formatter**: A module/class responsible for constructing the prompt string to be sent to the LLM. This includes adding the system message, the one-shot example, and the actual code chunk.
2.  **LLM Interaction Client**: A module/class to handle communication with the LLM API (specific API to be determined, potentially using a generic interface). It will send the formatted prompt and receive the response.
3.  **Response Parser**: A module/class to parse the JSON response from the LLM. It will validate the structure and extract the list of business rule candidates.
4.  **Error Handler**: Logic integrated within the client and parser to manage potential issues like network errors, API errors, invalid JSON, or empty responses.
5.  **Main Orchestration Script/Function**: A script or function that ties the above components together, taking a code chunk as input and returning a list of extracted rule candidates (or an empty list on failure).

## Implementation Approach
1.  **Define Data Structures**:
    -   Finalize the Python data structure for representing a business rule candidate (e.g., a simple list of strings, or a list of Pydantic models if more structure is needed later).
    -   Define the expected JSON structure from the LLM.
2.  **Develop LLM Prompt Formatter**:
    -   Implement logic to dynamically create the prompt using a template, incorporating the system message, example, and code chunk.
    -   Store the system message and example snippet (these might be configurable).
3.  **Implement LLM Interaction Client**:
    -   Choose an LLM provider/library (e.g., OpenAI, Anthropic, local model via Ollama/LM Studio).
    -   Create a client class/function to encapsulate API calls.
    -   Implement basic request/response handling.
4.  **Build Response Parser**:
    -   Implement JSON parsing logic.
    -   Add validation checks for the expected structure.
    -   Extract the relevant candidate list.
5.  **Integrate Error Handling**:
    -   Add `try-except` blocks for API calls (network issues, timeouts).
    -   Handle potential `JSONDecodeError` during parsing.
    -   Implement logic for empty or unexpected responses from the LLM based on Acceptance Criterion 3.
    -   Integrate logging for warnings and errors.
6.  **Create Orchestrator**:
    -   Write the main script/function (`extract_rules(code_chunk: str) -> List[str]`) that utilizes the formatter, client, and parser.
    -   Ensure it returns an empty list upon failure as per AC3.
7.  **Add Unit Tests**:
    -   Test the prompt formatter with different inputs.
    -   Mock the LLM client and test the orchestrator's handling of successful responses and various failure modes (API error, bad JSON, empty response).
    -   Test the response parser with valid and invalid JSON examples.

## Considerations
-   **LLM Choice**: The specific LLM and its API will influence the client implementation. Consider using an adapter pattern if flexibility is needed.
-   **Prompt Engineering**: The quality of the system message and example snippet is crucial for good results. Iteration might be needed.
-   **API Keys/Credentials**: Secure management of LLM API keys is necessary.
-   **Rate Limiting/Costs**: Be mindful of LLM API rate limits and costs during development and testing.
-   **Scalability**: While this story focuses on a single chunk, consider how this component might be used in a larger workflow processing many chunks.

## Dependencies
-   Python 3.9+
-   An LLM client library (e.g., `openai`, `anthropic`, `requests`)
-   Potentially `pydantic` if complex data structures are used for candidates. 