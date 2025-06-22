"""Pydantic models for representing extracted business rules."""

from pydantic import BaseModel, Field, validator, root_validator, model_validator
from typing import List, Optional, Dict, Union, Literal, Any, Tuple
from enum import Enum
import re
from uuid import uuid4
from datetime import datetime

# --- Enums for Controlled Vocabularies ---

class RuleType(str, Enum):
    """Enumeration for the types of business rules."""
    VALIDATION = "validation"
    DECISION = "decision"
    CALCULATION = "calculation"
    WORKFLOW = "workflow"
    OTHER = "other"

class ComparisonOperator(str, Enum):
    """Comparison operators used in conditions."""
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    IN = "IN"
    NOT_IN = "NOT IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"

class LogicalOperator(str, Enum):
    """Logical operators for combining conditions."""
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

class ValueSourceType(str, Enum):
    """Types of sources for dynamic values in comparisons."""
    LOOKUP = "lookup"
    FIELD_REFERENCE = "field_reference"
    CALCULATION_REF = "calculation_ref"

class ActionType(str, Enum):
    """Types of actions performed by rules (esp. validation)."""
    ERROR_HANDLING = "error_handling"
    LOGGING = "logging"
    STATE_CHANGE = "state_change"
    ASSIGNMENTS = "assignments" # Added for Decision outcomes

class ErrorLevel(str, Enum):
    """Severity levels for error handling actions."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

# --- Detailed Field Structures ---

class SourceReference(BaseModel):
    """Reference to the origin in the legacy source code."""
    program: str = Field(..., description="Name of the source file or program.")
    section: Optional[str] = Field(None, description="Optional specific section, paragraph, or subroutine.")
    lines: str = Field(..., description="Line number range (e.g., '100-120' or '100').")
    snippet_hash: Optional[str] = Field(None, description="Optional SHA hash of the code snippet.")

    @validator('lines')
    def validate_line_format(cls, v):
        """Validates that the line format is 'N' or 'N-M'."""
        if not re.match(r'^\d+(-\d+)?$', v):
            raise ValueError("Line format must be 'N' or 'N-M'")
        return v

    def get_line_range(self) -> Tuple[int, int]:
        """Returns the line range as a (start, end) tuple (1-indexed)."""
        if '-' in self.lines:
            start, end = map(int, self.lines.split('-'))
            if start > end:
                raise ValueError(f"Start line {start} cannot be greater than end line {end} in range '{self.lines}'")
            return start, end
        else:
            line = int(self.lines)
            return line, line

class ValueSource(BaseModel):
    """Defines a dynamic source for a comparison value."""
    type: ValueSourceType = Field(..., description="Type of value source.")
    # Fields conditional on type
    field: Optional[str] = Field(None, description="Field used as key for lookup.")
    lookup_table_ref: Optional[str] = Field(None, description="Reference to lookup data source.")
    referenced_field: Optional[str] = Field(None, description="Another field whose value is used.")
    calculation_id: Optional[str] = Field(None, description="ID of a calculation rule providing the value.")
    concept: Optional[str] = Field(None, description="Optional glossary/KG concept link.")

    @model_validator(mode='after')
    def check_conditional_fields(self) -> 'ValueSource':
        if self.type == ValueSourceType.LOOKUP:
            if not self.field or not self.lookup_table_ref:
                raise ValueError("Lookup value source requires 'field' and 'lookup_table_ref'.")
        elif self.type == ValueSourceType.FIELD_REFERENCE:
            if not self.referenced_field:
                raise ValueError("Field reference value source requires 'referenced_field'.")
        elif self.type == ValueSourceType.CALCULATION_REF:
            if not self.calculation_id:
                raise ValueError("Calculation reference value source requires 'calculation_id'.")
        return self

# Forward references for Conditions
class ComparisonCondition(BaseModel):
    pass
class LogicalCondition(BaseModel):
    pass

Condition = Union[ComparisonCondition, LogicalCondition]

class ComparisonCondition(BaseModel):
    """Represents a simple comparison condition."""
    type: Literal["comparison"] = Field("comparison")
    field: str = Field(..., description="The legacy field being evaluated.")
    operator: ComparisonOperator = Field(..., description="The comparison operator.")
    value: Optional[Any] = Field(None, description="Literal value for comparison.")
    value_source: Optional[ValueSource] = Field(None, description="Dynamic source for comparison value.")
    concept: Optional[str] = Field(None, description="Optional glossary/KG concept for the field.")
    label: Optional[str] = Field(None, description="Optional label for this condition.")

    @model_validator(mode='after')
    def check_value_or_source(self) -> 'ComparisonCondition':
        if self.value is None and self.value_source is None:
            raise ValueError("Either 'value' or 'value_source' must be provided for a comparison.")
        if self.value is not None and self.value_source is not None:
            raise ValueError("Provide either 'value' or 'value_source', not both.")
        # Further validation based on operator (e.g., value type for IN/NOT IN) could go here
        if self.operator in [ComparisonOperator.IN, ComparisonOperator.NOT_IN] and not isinstance(self.value, list):
             raise ValueError(f"Operator {self.operator} requires 'value' to be a list.")
        if self.operator in [ComparisonOperator.IS_NULL, ComparisonOperator.IS_NOT_NULL] and (self.value is not None or self.value_source is not None):
             raise ValueError(f"Operator {self.operator} does not use 'value' or 'value_source'.")
        return self

class LogicalCondition(BaseModel):
    """Represents a combination of conditions using AND, OR, NOT."""
    type: Literal["logical_combination"] = Field("logical_combination")
    operator: LogicalOperator = Field(..., description="Logical operator (AND, OR, NOT).")
    operands: List[Condition] = Field(..., min_items=1, description="List of conditions to combine.")

    @validator('operands')
    def check_operand_count_for_not(cls, v, values):
        op = values.get('operator')
        if op == LogicalOperator.NOT and len(v) != 1:
            raise ValueError("Logical operator NOT requires exactly one operand.")
        if op != LogicalOperator.NOT and len(v) < 2:
             raise ValueError(f"Logical operator {op} requires at least two operands.")
        return v

# Update forward references
ComparisonCondition.update_forward_refs()
LogicalCondition.update_forward_refs()


class Action(BaseModel):
    """Defines an action taken by a rule (e.g., on validation failure)."""
    type: ActionType = Field(..., description="Type of action.")
    # Conditional fields based on type
    level: Optional[ErrorLevel] = Field(None, description="Severity level for error handling.")
    message_template: Optional[str] = Field(None, description="Message template (for logging/error).")
    error_code: Optional[str] = Field(None, description="Specific error code.")
    target_field: Optional[str] = Field(None, description="Target field for state change or assignment.")
    new_value: Optional[Any] = Field(None, description="New value for state change.")
    # For multi-assignment in decisions
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="List of assignments (target_field, value).")

    @model_validator(mode='after')
    def check_action_fields(self) -> 'Action':
        if self.type == ActionType.ERROR_HANDLING:
            if self.level is None or self.message_template is None:
                raise ValueError("Error handling action requires 'level' and 'message_template'.")
        elif self.type == ActionType.LOGGING:
            if self.message_template is None:
                raise ValueError("Logging action requires 'message_template'.")
        elif self.type == ActionType.STATE_CHANGE:
            if self.target_field is None or not hasattr(self, 'new_value'):
                raise ValueError("State change action requires 'target_field' and 'new_value'.")
        elif self.type == ActionType.ASSIGNMENTS:
             if self.actions is None:
                 raise ValueError("Assignments action requires 'actions' list.")
             # Could add validation for structure within 'actions' list items
        return self

# --- Base and Specialized Rule Models ---

class BaseRule(BaseModel):
    """Base model for all extracted business rules."""
    id: str = Field(default_factory=lambda: f"RULE-TEMP-{uuid4().hex[:6].upper()}", description="Unique rule identifier.")
    type: RuleType = Field(..., description="Type of the business rule.")
    description: str = Field(..., description="Human-readable description of the rule.")
    source_reference: SourceReference = Field(..., description="Reference to the source code origin.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0).")
    extracted_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of extraction (UTC).")
    system_version: str = Field(..., description="Version identifier of the legacy codebase.")
    # Optional metadata
    concepts: Optional[List[str]] = Field(None, description="List of related business concepts.")
    tags: Optional[List[str]] = Field(None, description="List of tags for categorization.")
    notes: Optional[str] = Field(None, description="Additional human-readable notes.")

    @validator('description')
    def description_must_be_meaningful(cls, v):
        if not v or len(v.strip()) < 5: # Arbitrary minimum length
            raise ValueError("Description must be provided and meaningful.")
        return v.strip()
        
    @validator('extracted_timestamp', pre=True)
    def handle_placeholder_timestamp(cls, v):
        """Replace placeholder timestamp formats with current timestamp."""
        if isinstance(v, str):
            # Check for common placeholder patterns
            placeholder_patterns = [
                r'YYYY-MM-DDTHH:MM:SSZ',
                r'YYYY-MM-DD',
                r'(\d{4}-\d{2}-\d{2}T00:00:00Z)',  # Date with zeros for time
            ]
            
            for pattern in placeholder_patterns:
                if re.match(pattern, v, re.IGNORECASE) or v.startswith('YYYY'):
                    return datetime.utcnow()
            
            # If it's a string but not a placeholder, let Pydantic try to parse it
        
        return v

    @validator('id', pre=True, always=True)
    def set_id_based_on_type(cls, v, values):
        # If ID is the default temporary one, try to make it slightly more specific
        if v is None or v.startswith("RULE-TEMP-"):
             rule_type_char = values.get('type', 'X').upper()[0]
             # A better approach might involve hashing parts of the rule, but this is simple
             return f"RULE-{rule_type_char}{uuid4().hex[:7].upper()}"
        return v # Keep provided ID if it's not the default

    @validator('system_version', pre=True)
    def handle_placeholder_system_version(cls, v):
        """Provide a default system version for placeholder values."""
        if isinstance(v, str):
            # Check for placeholder patterns 
            placeholder_patterns = [
                r'UNKNOWN[-_]?V\d+',  # UNKNOWN_V1, UNKNOWN-V1, UNKNOWNV1
                r'N/A',
                r'PLACEHOLDER'
            ]
            
            for pattern in placeholder_patterns:
                if re.match(pattern, v, re.IGNORECASE):
                    return "MVP_EXTRACTOR_V1"
        
        return v

class ValidationRule(BaseRule):
    """Model for a validation rule."""
    type: Literal[RuleType.VALIDATION] = Field(RuleType.VALIDATION)
    conditions: Condition = Field(..., description="Condition(s) triggering validation failure.")
    action: Action = Field(..., description="Action taken on validation failure.")

class DecisionOutcome(BaseModel):
    """Represents a possible outcome of a decision rule."""
    when: Optional[str] = Field(None, description="Label identifying the condition(s) leading to this outcome.")
    result: Union[Any, Action] = Field(..., description="The result of the decision (e.g., a value, assignment action).")

class DecisionRule(BaseRule):
    """Model for a decision rule."""
    type: Literal[RuleType.DECISION] = Field(RuleType.DECISION)
    conditions: Condition = Field(..., description="Condition(s) governing the decision.")
    outcomes: List[DecisionOutcome] = Field(..., min_items=1, description="Possible outcomes of the decision.")
    outcome_type: Optional[str] = Field(None, description="Nature of the outcome (e.g., 'assignment', 'status_code').")

class CalculationRule(BaseRule):
    """Model for a calculation rule."""
    type: Literal[RuleType.CALCULATION] = Field(RuleType.CALCULATION)
    formula: Union[str, Dict] = Field(..., description="Formula or structured algorithm.")
    target_field: str = Field(..., description="Business field where the result is stored.")
    source_fields: List[str] = Field(..., min_items=1, description="Input fields for the calculation.")
    conditions: Optional[Condition] = Field(None, description="Optional condition(s) for when this calculation applies.")

class WorkflowRule(BaseRule):
    """Model for a workflow or process rule."""
    type: Literal[RuleType.WORKFLOW] = Field(RuleType.WORKFLOW)
    trigger: Union[str, Dict] = Field(..., description="Event or state that initiates this step.")
    conditions: Optional[Condition] = Field(None, description="Optional condition(s) evaluated for this step.")
    action: Union[str, Action] = Field(..., description="Resulting workflow action or next step reference.")


# --- Union Type for Dispatching ---

BusinessRule = Union[ValidationRule, DecisionRule, CalculationRule, WorkflowRule, BaseRule]


# --- Helper Function (Example) ---

def load_rule_from_dict(data: Dict) -> BusinessRule:
    """Loads and validates a business rule from a dictionary, dispatching to the correct type."""
    rule_type = data.get('type')
    if not rule_type:
        raise ValueError("Missing 'type' field in rule data.")

    # Map type string to model class
    type_map = {
        RuleType.VALIDATION: ValidationRule,
        RuleType.DECISION: DecisionRule,
        RuleType.CALCULATION: CalculationRule,
        RuleType.WORKFLOW: WorkflowRule,
        RuleType.OTHER: BaseRule # Fallback to BaseRule if type is 'other'
    }

    model_class = type_map.get(rule_type)
    if model_class:
        # Ensure the type matches if it's not 'other'
        if rule_type != RuleType.OTHER and data.get('type') != model_class.__fields__['type'].default:
             raise ValueError(f"Type field '{data.get('type')}' conflicts with expected type for {model_class.__name__}")
        return model_class.parse_obj(data)
    else:
        # If type is unknown but present, treat as BaseRule or raise error
        # return BaseRule.parse_obj(data) # Option 1: Treat as BaseRule
        raise ValueError(f"Unknown rule type: {rule_type}") # Option 2: Strict error 