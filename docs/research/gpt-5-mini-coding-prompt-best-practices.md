# Best Practices for GPT-5 Mini Coding Prompts

This document outlines best practices for crafting coding-specific system prompts for a GPT-5 Mini model. The core assumption is that this model is optimized for speed, efficiency, and direct instruction execution, rather than deep, abstract reasoning.

### 1. Be Direct and Imperative
Use clear, command-oriented language. Tell the model exactly what to do. Avoid ambiguity and conversational fluff.
- **Good**: "Implement the `createUser` function as specified in the plan."
- **Less Good**: "Could you please think about how you might go about creating the `createUser` function?"

### 2. Prioritize Atomic, Single-Responsibility Tasks
Break down coding tasks into the smallest possible logical steps. A "mini" model excels at executing a sequence of simple, well-defined tasks rather than a single, complex one.
- **Example**: Instead of "Build the user profile page," break it down into:
  1.  "Create the file `UserProfile.svelte`."
  2.  "Add the basic component structure with `<script>`, markup, and `<style>` tags."
  3.  "Implement the `fetchUserData` function to call the `/api/user/{id}` endpoint."
  4.  "Render the user's name and email in the markup."

### 3. Provide All Necessary Context Explicitly
Do not assume the model will infer context. Provide all required information, such as file paths, relevant code snippets, and specific rules, directly within the prompt for the current task.
- **Example**: "Modify the file `backend/api/routers/chatbot.py`. Here is the relevant function to update: `...` You must apply rule `210-fastapi-api-security.mdc`."

### 4. Enforce Strict Adherence to Plans
Instruct the model that it is an *executor*, not a *designer*. Its primary role is to translate a given plan (from a tech lead, for instance) into code with perfect fidelity. Deviations or creative interpretations should be explicitly forbidden unless it asks for clarification.
- **Example**: "Your task is to implement the provided plan exactly as written. Do not add, remove, or modify any logic that is not specified. If the plan is unclear, you must ask for clarification."

### 5. Demand Precise Tool Usage
Be explicit about how the model should use its available tools. Specify the exact commands to run or the precise format for file edits.
- **Example**: "Use `edit_file` on `path/to/your/file.js`. Ensure you use `// ... existing code ...` to preserve the parts of the file that are not being changed."

### 6. Focus on Verification
Since the model is optimized for execution speed, instruct it to always include a verification step. This builds a self-correction loop into the workflow.
- **Example**: "After writing the code, describe the command you would run to verify that your changes work as expected (e.g., running a specific unit test)."
