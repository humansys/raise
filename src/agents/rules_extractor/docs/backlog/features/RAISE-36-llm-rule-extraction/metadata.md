# RAISE-36: LLM-Based Rule Extraction

## Description
Use a powerful LLM (e.g., GPT-4 or Claude) to identify business rules from each chunk. Return the results as structured JSON adhering to a minimal Pydantic schema.

## Benefit Hypothesis
Automating rule identification removes the burden of manually parsing legacy code, accelerating modernization efforts.

## Acceptance Criteria
- JSON output for each chunk containing candidate rules.
- Minimal required fields (e.g., `id`, `description`, `type`, `source_reference`, `confidence`).

## User Stories
- [RAISE-37] List business rule candidates
- [RAISE-40] Minimal Rule Validation Model

## Status
Pending

## Dependencies
- Python 3.8+
- pydantic
- OpenAI API / Anthropic API
- Basic Code Preprocessing (RAISE-30) 