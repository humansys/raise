# High-Level Backlog (SAFe) for AS/400 Rule Extraction MVP

Below is a high-level backlog in SAFe terminology, focusing on **Features** and **User Stories** that make up the **Minimal Viable Product (MVP)** for an LLM-based AS/400 business rule extraction pipeline. Each feature supports the core MVP goals: ingest sample legacy code, extract rules via LLM, validate minimally, and output a structured result.

---

## [RAISE-30]: Basic Code Preprocessing

### Description
Provide a lightweight mechanism to read and segment the legacy COBOL/RPG code into manageable chunks for LLM consumption. Keep it simple—no heavy parsers at this stage.

### Benefit Hypothesis
Enables the Large Language Model to handle code in portions it can process effectively, establishing the foundation for extracting business rules.

### Acceptance Criteria
- Code can be ingested and split into text chunks of a reasonable size (e.g., 300–500 lines).
- Basic filtering of boilerplate (e.g., comment blocks, blank lines) without losing essential logic.

### User Stories

1. **[RAISE-31] Read source code file**  
   **As** a developer working on the MVP,  
   **I want** to read a given COBOL or RPG source file from a local directory,  
   **so that** the pipeline can programmatically access code lines for further processing.

   **Acceptance Criteria**  
   - Source file is read from a file path (hardcoded or minimal config).
   - Script outputs a list/array of code lines in memory (or a text buffer).
   - Handles encoding conversion if needed (EBCDIC to ASCII).

2. **[RAISE-32] Chuck source code files**  
   **As** an LLM integrator,  
   **I need** a script to chunk the code lines into separate text blocks,  
   **so that** each chunk is small enough for the LLM's context window.

   **Acceptance Criteria**  
   - Configurable chunk size (line-based or character-based).
   - Outputs separate chunk files or in-memory arrays for easy iteration.
   - Logs chunk boundaries for traceability.

---

## [RAISE-36*] LLM-Based Rule Extraction

### Description
Use a powerful LLM (e.g., GPT-4 or Claude) to identify business rules from each chunk. Return the results as structured JSON adhering to a minimal Pydantic schema.

### Benefit Hypothesis
Automating rule identification removes the burden of manually parsing legacy code, accelerating modernization efforts.

### Acceptance Criteria
- JSON output for each chunk containing candidate rules.
- Minimal required fields (e.g., `id`, `description`, `type`, `source_reference`, `confidence`).

### User Stories

1. **[RAISE-37] List business rule candidates**  
   **As** a code analyst,  
   **I want** to prompt the LLM with a short example + the chunked code,  
   **so that** it returns a list of business rule candidates in JSON format.

   **Acceptance Criteria**  
   - LLM prompt includes a "system role" and example snippet.
   - Output is captured in a Python structure (dictionary/list).
   - The script can handle failures (e.g., empty or malformed output) gracefully.

2. **[RAISE-40] Minimal Rule Validation Model**  
   **As** the MVP developer,  
   **I need** a minimal Pydantic model named `BusinessRule`,  
   **so that** the JSON returned by the LLM is automatically validated.

   **Acceptance Criteria**  
   - A `BusinessRule` model with at least `id`, `description`, `type`, `source_reference`, `confidence`.
   - Invalid or missing fields raise exceptions, prompting re-check or re-prompt.
   - Unit test verifying that a valid JSON example passes schema validation.

---

## [RAISE-41]: Lightweight Rule Validation

### Description
Perform a secondary check—an LLM "judge" pass or basic checks—on each extracted rule to confirm plausibility and assign confidence. Avoid deep formal methods at this stage.

### Benefit Hypothesis
Prevents excessive hallucinations or incorrect rule statements, increasing stakeholder trust in the MVP outputs.

### Acceptance Criteria
- Each rule is assigned a final confidence score after validation.
- Low-confidence or questionable rules are flagged.

### User Stories

1. **[RAISE-42] Rule validator Agent**  
   **As** the product owner,  
   **I want** a second LLM prompt that compares the proposed rule to the original code chunk,  
   **so that** it generates a simple confidence score (0–100) or "valid/invalid" classification.

   **Acceptance Criteria**  
   - The pipeline calls the LLM again with "Here is the code snippet and the extracted rule—rate accuracy."  
   - The returned score is merged into the final rule object.  
   - If the LLM judge says "high mismatch," rule is flagged for human review.

2. **[RAISE-43] Story F3-S2**  
   **As** a developer,  
   **I want** a quick script that logs or color-codes rules under a certain confidence threshold,  
   **so that** the SME knows which ones to double-check.

   **Acceptance Criteria**  
   - Confidence threshold is configurable (default 0.7 or 0.8).  
   - Flagged rules are listed separately for easy review in a console output or file.

---

## [RAISE-49]: Output and Auto-Documentation

### Description
Store the extracted, validated rules in a consolidated JSON/YAML file and generate a human-readable Markdown summary. This forms the MVP's final deliverable.

### Benefit Hypothesis
Allows both machines (downstream systems/agents) and human stakeholders (SMEs) to quickly consume and understand the results.

### Acceptance Criteria
- A single "rules_output.json" or "rules_output.yaml" file with all extracted rules.
- An auto-generated Markdown file listing each rule, referencing source lines.

### User Stories

1. **[RAISE-51] Output yaml rules file**  
   **As** a modernization SME,  
   **I want** a single "rules_output.yaml" file after the run,  
   **so that** I have a standardized, machine-readable view of all rules in one place.

   **Acceptance Criteria**  
   - Each rule object includes ID, description, type, source reference, final confidence.
   - If parsing multiple code chunks, all rules are merged into one output file.

2. **[RAISE-52] Markdown Report**  
   **As** a lead developer,  
   **I want** a Markdown report that lists each rule in a table or bullet format,  
   **so that** I can quickly share it with business users.

   **Acceptance Criteria**  
   - `rules_report.md` or similar, with each rule on a new line or section.  
   - Optional link back to the snippet or at least line references.  
   - Quick summary of how many rules found, how many flagged as low confidence.

---

## [RAISE-53]: MVP Enablers

### Description
Provide the foundational technical components, design, and tooling necessary to support the efficient implementation of the AS/400 Rule Extraction MVP. These enablers establish the architecture, development environment, and agent capabilities required for rule extraction.

### Benefit Hypothesis
Establishing clear technical design and tooling upfront accelerates development, reduces technical debt, and ensures consistent implementation of the rule extraction process.

### Acceptance Criteria
- Technical design document outlining architecture, components, and data flow
- Cursor IDE agent for rule extraction and analysis
- Rule generation framework supporting the extraction process

### User Stories

1. **[RAISE-54] MVP Base Technical Design**  
   **As** a technical lead,  
   **I want** a clear architectural design for the rule extraction pipeline,  
   **so that** the team has a consistent technical direction for implementation.

   **Acceptance Criteria**  
   - Component diagram showing major system parts and interactions
   - Data flow description from input code to rule output
   - Technology stack decisions documented with rationale
   - Interface definitions for key components
   - Performance and scalability considerations addressed

2. **[RAISE-62] Cursor Rules Agent**  
   **As** a developer,  
   **I want** a specialized Cursor IDE agent for code analysis and rule extraction,  
   **so that** I can efficiently interact with the legacy code and extracted rules.

   **Acceptance Criteria**  
   - Agent capable of analyzing code directly within Cursor IDE
   - Prompt templates optimized for business rule extraction
   - Integration with the rule validation process
   - User-friendly interface for reviewing and refining extracted rules
   - Agent performance measured and optimized for AS/400 code

3. **[RAISE-55] Cursor Rules Generation**  
   **As** an LLM integrator,  
   **I want** a framework for consistent rule generation from code analysis,  
   **so that** the extraction process produces standardized, high-quality rule definitions.

   **Acceptance Criteria**  
   - Rule generation templates supporting different rule types
   - Schema enforcement during rule creation
   - Consistent rule formatting and structure
   - Support for rule relationships and dependencies
   - Validation hooks to verify rule accuracy

---

## Additional Notes on SAFe Alignment

- **Program Increment (PI) Planning**: These features can be allocated to an initial PI of short duration (e.g., 2–3 sprints) to deliver the MVP.  
- **Enablers**: Technical tasks like "dockerize the Python script" or "integrate logging" can be treated as enabler stories inside each feature or in a separate backlog item.  
- **Iterations**: Each sprint can deliver a subset of user stories within these features, ensuring incremental progress.

---

## Summary

This backlog reflects a **KISS** approach to quickly build an **MVP** for automated rule extraction from AS/400 code:

1. **Feature 1** handles minimal code preprocessing.  
2. **Feature 2** extracts rules using the LLM + Pydantic validation.  
3. **Feature 3** validates confidence to reduce errors.  
4. **Feature 4** consolidates and documents output in both JSON/YAML (machine) and Markdown (human).

By completing these features, the team proves feasibility, demonstrating tangible outputs (structured rules + a short doc) for a small sample of legacy code. Further expansions (multi-agent, knowledge graph, etc.) can be introduced in subsequent increments once the MVP is validated.
