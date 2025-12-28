# Best Practices for GPT-5 High Prompt Engineering

This document outlines key strategies and best practices for crafting effective prompts for a GPT-5 High model, ensuring optimal performance, clarity, and depth of response. The principles outlined here are used to construct the system prompts for RaiSE agents within the Zambezi Concierge project.

### 1. Assign a Specific Role and Persona
Instruct the model to act as a specific persona or expert. This focuses the model's knowledge and generates outputs in the desired style and tone.
- **Example**: "You are a Tech Lead Agent, responsible for guiding software development teams..."

### 2. Provide Clear, Specific, and Delimited Instructions
Clearly articulate the desired outcome, context, length, format, and style. Use delimiters like `###` or `"""` to separate instructions from context, which helps the model distinguish between different parts of the prompt.
- **Example**:
  ```
  ### Context
  The user wants to add a new API endpoint for user profiles.

  ### Task
  Generate a technical design document outlining the required changes.
  ```

### 3. Break Down Complex Tasks into Manageable Steps
For intricate requests, instruct the model to think step-by-step or follow a specific sequence of actions. This prevents the model from missing details and encourages a more logical workflow.
- **Example**: "1. Analyze the requirements. 2. Propose three alternative solutions. 3. Select the best option and justify your choice. 4. Draft the implementation plan."

### 4. Use "Router Nudge" Phrases for Deeper Reasoning
Incorporate phrases that prompt the model to engage in deeper, more critical thinking. This leads to more detailed, nuanced, and well-reasoned responses.
- **Examples**: "Think hard about this.", "Analyze the trade-offs of this approach.", "Consider the security implications."

### 5. Mandate an Iterative Refinement and Self-Correction Loop
Instruct the model to generate an initial response, evaluate it against a defined standard or set of criteria, and then refine it. This leverages the model's ability to critique and improve its own work, leading to higher-quality outputs.
- **Example**: "After generating the design, review it against the SOLID principles and the project's coding standards. Refine it if any violations are found."

### 6. Provide Comprehensive Context and Hard Constraints
Offer sufficient background information and specify any non-negotiable limitations. This guides the model toward relevant, realistic, and compliant responses.
- **Example**: "The solution must be implemented using the existing tech stack (FastAPI, PostgreSQL) and must comply with the security rules defined in `210-fastapi-api-security.mdc`."

### 7. Leverage Advanced Features and Structured Output
Craft prompts that tap into advanced capabilities like data analysis, complex reasoning, and structured data generation (JSON, YAML). Clearly define the expected output format.
- **Example**: "Provide the final output as a JSON object with the following schema: `{ "component": "...", "changes": [...], "reasoning": "..." }`"
