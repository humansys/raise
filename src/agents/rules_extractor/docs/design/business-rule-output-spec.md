## 1. Business Rule Output Specification

This document specifies the standardized structure for representing extracted business rules in YAML/JSON format. The structure is designed to be machine-readable for automated processing (like code generation) while containing sufficient metadata for human understanding and traceability. Pydantic models should be used to validate this structure in Python implementations.

**Root Object:** Each rule is represented as a single object (or an entry in a list of rules).

**Base Rule Fields (Required for all rule types):**

| Field                 | Type        | Required | Description                                                                                                | Example                                        |
| :-------------------- | :---------- | :------- | :--------------------------------------------------------------------------------------------------------- | :--------------------------------------------- |
| `id`                  | String      | Yes      | A unique identifier for the rule. Should be stable across extractions if possible.                         | `"RULE-V003"`                                  |
| `type`                | String Enum | Yes      | The classification of the rule. Allowed values: `validation`, `decision`, `calculation`, `workflow`, `other`. | `"validation"`                                 |
| `description`         | String      | Yes      | A concise, human-readable description of the rule's purpose and logic.                                   | `"Customer discount must be within tier limits."` |
| `source_reference`    | Object      | Yes      | Metadata linking the rule back to its origin in the legacy source code. See details below.                 | `{ "program": "ORDENTRY", "lines": "450-485" }` |
| `confidence`          | Float       | Yes      | A score between 0.0 and 1.0 indicating the confidence in the accuracy of the extracted rule.                 | `0.95`                                         |
| `extracted_timestamp` | String (ISO)| Yes      | The timestamp (ISO 8601 format) when the rule was extracted or last updated.                             | `"2025-04-07T11:00:00Z"`                       |
| `system_version`      | String      | Yes      | Identifier for the version of the legacy codebase from which the rule was extracted.                       | `"AS400_PROD_2025_04_v1.1"`                    |

**Base Rule Fields (Optional):**

| Field     | Type          | Required | Description                                                                                                   | Example                      |
| :-------- | :------------ | :------- | :------------------------------------------------------------------------------------------------------------ | :--------------------------- |
| `concepts`| List[String]  | No       | List of key business concepts or terms from a glossary/KG that this rule relates to.                          | `["DiscountPolicy", "OrderValidation"]` |
| `tags`    | List[String]  | No       | Optional tags for categorization, filtering, or grouping rules (e.g., business domain, priority).           | `["pricing", "order_entry"]` |
| `notes`   | String        | No       | Any additional human-readable notes, justifications, or clarification about the rule or its extraction. | `"LLM initially missed the override flag."` |

**Detailed Field Structures:**

**`source_reference` Object:**

| Field          | Type   | Required | Description                                                                    | Example                               |
| :------------- | :----- | :------- | :----------------------------------------------------------------------------- | :------------------------------------ |
| `program`      | String | Yes      | Name of the source file or program (e.g., COBOL program name, RPG source member). | `"ORDENTRY"`                          |
| `section`      | String | No       | Optional name of the specific section, paragraph, or subroutine.             | `"VALIDATE_DISCOUNT_SUBRTN"`          |
| `lines`        | String | Yes      | Line number range (e.g., "450-485") or single line number ("450").           | `"450-485"`                           |
| `snippet_hash` | String | No       | Optional SHA hash of the exact code snippet corresponding to these lines.    | `"e5f8a1b3c7d9..."`                 |

**Rule-Type Specific Fields (Choose relevant structure based on `type`):**

1.  **For `type: validation`:**
    *   `conditions`: (Object | List[Object]) **Required**. Defines the condition(s) that trigger the validation *failure*. See Condition Structure below.
    *   `action`: (Object) **Required**. Defines what happens when the validation fails. See Action Structure below.

2.  **For `type: decision`:**
    *   `conditions`: (Object | List[Object]) **Required**. Defines the condition(s) governing the decision. See Condition Structure. Can be complex, representing inputs to a decision table.
    *   `outcomes`: (List[Object] | Object) **Required**. Defines the possible results of the decision, often linked to specific condition combinations. Structure depends on complexity (e.g., list of `{ "when": <condition_label>, "result": <value> }` or a more complex mapping).
    *   `outcome_type`: (String) **Optional**. Describes the nature of the outcome (e.g., `"assignment"`, `"workflow_trigger"`, `"interest_rate"`).

3.  **For `type: calculation`:**
    *   `formula`: (String | Object) **Required**. The formula or algorithm. Can be a simple string or a structured representation (e.g., expression tree).
    *   `target_field`: (String) **Required**. The business field where the result is stored.
    *   `source_fields`: (List[String]) **Required**. List of input fields used in the calculation.
    *   `conditions`: (Object | List[Object]) **Optional**. Conditions under which this calculation applies. See Condition Structure.

4.  **For `type: workflow`:**
    *   `trigger`: (String | Object) **Required**. Event or state that initiates this workflow step/rule.
    *   `conditions`: (Object | List[Object]) **Optional**. Conditions evaluated for this step. See Condition Structure.
    *   `action` / `next_step`: (String | Object) **Required**. The resulting workflow action or the next step in the process.

**Condition Structure (Used within `conditions` fields):**

Conditions can be simple comparisons or nested logical combinations.

*   **`comparison` Object:**
    | Field     | Type        | Required | Description                                                                                                                               | Example                    |
    | :-------- | :---------- | :------- | :---------------------------------------------------------------------------------------------------------------------------------------- | :------------------------- |
    | `type`    | String Enum | Yes      | Must be `"comparison"`.                                                                                                                 | `"comparison"`             |
    | `field`   | String      | Yes      | The field being evaluated (use legacy name).                                                                                              | `"CUST_DISCOUNT_PCT"`      |
    | `operator`| String Enum | Yes      | Comparison operator (e.g., `==`, `!=`, `<`, `<=`, `>`, `>=`, `IN`, `NOT IN`, `IS NULL`, `IS NOT NULL`). Case-insensitive recommended.        | `"<"`                      |
    | `value`   | String/Int/Float/Boolean/List | Yes (unless `value_source`) | The literal value to compare against. Use quotes for string literals (e.g., `"'Y'"`). For `IN`/`NOT IN`, use a List. | `0` or `"'ACTIVE'"`      |
    | `value_source` | Object | Yes (unless `value`) | Alternative source for the comparison value if not literal. See Value Source Structure below.                              | `{ "type": "lookup", ...}` |
    | `concept` | String      | No       | Optional link to glossary/KG concept for the `field`.                                                                                     | `"CustomerDiscountPercentage"` |
    | `label`   | String      | No       | Optional label for this condition, useful in decision tables (`when: <label>`).                                                            | `"DiscountTooLow"`         |

*   **`logical_combination` Object:**
    | Field     | Type        | Required | Description                                                                   | Example                                 |
    | :-------- | :---------- | :------- | :---------------------------------------------------------------------------- | :-------------------------------------- |
    | `type`    | String Enum | Yes      | Must be `"logical_combination"`.                                              | `"logical_combination"`                 |
    | `operator`| String Enum | Yes      | Logical operator (`AND`, `OR`, `NOT`). Case-insensitive recommended.          | `"AND"`                                 |
    | `operands`| List[Object]| Yes      | List of nested condition objects (can be `comparison` or `logical_combination`). For `NOT`, usually a single operand. | `[ { "type": "comparison", ... }, ... ]` |

*Note: For simple rules, `conditions` might be a single `comparison` object. For complex rules, it might be a single `logical_combination` object or a list of conditions implicitly ANDed together (convention needed).*

**Value Source Structure (Used within `comparison`):**

| Field              | Type        | Required | Description                                                                     | Example                                     |
| :----------------- | :---------- | :------- | :------------------------------------------------------------------------------ | :------------------------------------------ |
| `type`             | String Enum | Yes      | Type of source. Allowed: `"lookup"`, `"field_reference"`, `"calculation_ref"`. | `"lookup"`                                  |
| `field`            | String      | Yes (if `type: lookup`) | The field used as the key for the lookup.                             | `"CUSTOMER_TIER"`                           |
| `lookup_table_ref` | String      | Yes (if `type: lookup`) | Reference to the table/config/KG node where lookup data resides.        | `"TierMaxDiscountTable"`                    |
| `referenced_field` | String      | Yes (if `type: field_reference`) | Another field whose value is used for comparison.                 | `"PREVIOUS_ORDER_DISCOUNT"`               |
| `calculation_id`   | String      | Yes (if `type: calculation_ref`) | ID of another `calculation` rule whose result is used.           | `"RULE-C001"`                             |
| `concept`          | String      | No       | Optional link to glossary/KG concept for the value source.                      | `"MaxDiscountPolicy"`                       |

**Action Structure (Used for `validation` rules):**

| Field            | Type        | Required | Description                                                                    | Example                                           |
| :--------------- | :---------- | :------- | :----------------------------------------------------------------------------- | :------------------------------------------------ |
| `type`           | String Enum | Yes      | Type of action. Allowed: `"error_handling"`, `"logging"`, `"state_change"`.     | `"error_handling"`                                |
| `level`          | String Enum | Yes (if `type: error_handling`) | Severity level. Allowed: `"error"`, `"warning"`, `"info"`.                | `"error"`                                         |
| `message_template`| String      | Yes (if `type: error_handling` or `logging`) | Message text, can include placeholders like `{field_name}`.               | `"Invalid discount {CUST_DISCOUNT_PCT}%."`        |
| `error_code`     | String      | No (but recommended if `type: error_handling`) | Specific code for programmatic error handling.                             | `"DISC_ERR_002"`                                |
| `target_field`   | String      | Yes (if `type: state_change`) | The field whose state is changed by the action.                              | `"ORDER_STATUS"`                                |
| `new_value`      | String/Int/Float | Yes (if `type: state_change`) | The new value assigned to the `target_field`.                             | `"'REJECTED'"`                                  |

