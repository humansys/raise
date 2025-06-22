# RAISE-37: List Business Rule Candidates

## User Story

As a code analyst,
I want to automatically extract potential business rules from code chunks using an LLM,
so that I can quickly identify and document key logic within the codebase.

## Acceptance Criteria

1.  The prompt sent to the LLM includes a system message defining its role and task, along with a concise example of input code and desired output format.
2.  The LLM's JSON output containing the list of business rule candidates is successfully parsed into a Python list of strings (or a predefined data structure).
3.  If the LLM returns empty output, malformed JSON, or indicates a failure, the system logs a warning and returns an empty list of candidates without crashing.

## Status

Status: Not Started ❌