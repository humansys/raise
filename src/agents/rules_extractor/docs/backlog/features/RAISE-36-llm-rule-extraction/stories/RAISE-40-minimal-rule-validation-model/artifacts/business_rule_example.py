"""
Ejemplo de uso del modelo BusinessRule para validación de reglas extraídas.

Este archivo muestra cómo utilizar el modelo BusinessRule para validar estructuras
de datos JSON que representan reglas de negocio extraídas de código AS/400.
"""

from rules_extractor.models.business_rule import (
    BusinessRule, BaseRule, ValidationRule, DecisionRule, CalculationRule, WorkflowRule,
    RuleType, SourceReference, ComparisonCondition, ComparisonOperator, Action, ActionType,
    ErrorLevel, LogicalCondition, LogicalOperator, load_rule_from_dict
)
from datetime import datetime
import json
from pydantic import ValidationError

# Ejemplo 1: Creación básica de una regla con los campos mínimos requeridos
def example_basic_rule():
    """Ejemplo de creación de una regla básica."""
    try:
        rule = BaseRule(
            id="RULE-1234",
            type=RuleType.OTHER,
            description="Regla de ejemplo que muestra la validación básica",
            source_reference=SourceReference(
                program="PROGRAM1.SQLRPGLE",
                lines="100-120"
            ),
            confidence=0.85,
            system_version="MVP_EXTRACTOR_V1"
        )
        print("✅ Regla básica creada exitosamente:")
        print(rule.model_dump_json(indent=2))
        return rule
    except ValidationError as e:
        print("❌ Error de validación:")
        print(e)
        return None

# Ejemplo 2: Validar un JSON incompleto (campos obligatorios faltantes)
def example_invalid_rule_missing_fields():
    """Ejemplo que muestra la validación cuando faltan campos obligatorios."""
    invalid_data = {
        "id": "RULE-INVALID",
        "type": "other",
        # Falta el campo 'description'
        "source_reference": {
            "program": "PROGRAM2.SQLRPGLE",
            "lines": "200-220"
        },
        # Falta el campo 'confidence'
        "system_version": "MVP_EXTRACTOR_V1"
    }
    
    try:
        rule = BaseRule.model_validate(invalid_data)
        print("✅ Regla validada correctamente (no debería ocurrir):")
        print(rule.model_dump_json(indent=2))
        return rule
    except ValidationError as e:
        print("❌ Error de validación (esperado):")
        print(e)
        return None

# Ejemplo 3: Regla de validación completa
def example_validation_rule():
    """Ejemplo de una regla de validación con condiciones y acciones."""
    try:
        # Crear una condición de comparación simple
        condition = ComparisonCondition(
            field="CUSTOMER_BALANCE",
            operator=ComparisonOperator.GT,
            value=1000.0
        )
        
        # Crear una acción para cuando la validación falla
        action = Action(
            type=ActionType.ERROR_HANDLING,
            level=ErrorLevel.ERROR,
            message_template="El balance del cliente excede el límite permitido de $1000"
        )
        
        # Crear la regla de validación
        rule = ValidationRule(
            id="RULE-V001",
            description="Validar que el balance del cliente no exceda $1000",
            source_reference=SourceReference(
                program="CUSTCHECK.SQLRPGLE",
                section="ValidateCustomerBalance",
                lines="150-155"
            ),
            confidence=0.95,
            system_version="MVP_EXTRACTOR_V1",
            conditions=condition,
            action=action,
            tags=["customer", "balance", "validation"]
        )
        
        print("✅ Regla de validación creada exitosamente:")
        print(rule.model_dump_json(indent=2))
        return rule
    except ValidationError as e:
        print("❌ Error de validación:")
        print(e)
        return None

# Ejemplo 4: Cargar una regla desde un diccionario (simulando JSON recibido del LLM)
def example_load_from_dict():
    """Ejemplo de carga de una regla desde un diccionario (JSON)."""
    # Este podría ser el output de un LLM
    llm_output = {
        "id": "RULE-C002",
        "type": "calculation",
        "description": "Calcular el total de la factura incluyendo impuestos",
        "source_reference": {
            "program": "INVOICE.SQLRPGLE",
            "section": "CalculateTotalWithTax",
            "lines": "300-320"
        },
        "confidence": 0.88,
        "system_version": "MVP_EXTRACTOR_V1",
        "formula": "TOTAL = SUBTOTAL * (1 + TAX_RATE)",
        "target_field": "TOTAL",
        "source_fields": ["SUBTOTAL", "TAX_RATE"]
    }
    
    try:
        # Usar el helper para cargar el tipo correcto basado en 'type'
        rule = load_rule_from_dict(llm_output)
        print("✅ Regla cargada exitosamente desde diccionario:")
        print(rule.model_dump_json(indent=2))
        
        # Verificar que el tipo es correcto
        print(f"Tipo de la regla: {type(rule).__name__}")
        return rule
    except ValidationError as e:
        print("❌ Error de validación:")
        print(e)
        return None
    except ValueError as e:
        print("❌ Error de valor:")
        print(e)
        return None

# Ejemplo 5: Regla con condiciones lógicas complejas
def example_complex_logical_conditions():
    """Ejemplo de una regla con condiciones lógicas complejas (AND, OR, NOT)."""
    try:
        # Condición 1: Si el cliente es nuevo (menos de 6 meses)
        cond1 = ComparisonCondition(
            field="CUSTOMER_MONTHS",
            operator=ComparisonOperator.LT,
            value=6
        )
        
        # Condición 2: Si el monto de la compra es mayor a $500
        cond2 = ComparisonCondition(
            field="PURCHASE_AMOUNT",
            operator=ComparisonOperator.GT,
            value=500
        )
        
        # Condición 3: Si el cliente no tiene historial de pagos atrasados
        cond3 = ComparisonCondition(
            field="HAS_LATE_PAYMENTS",
            operator=ComparisonOperator.EQ,
            value=False
        )
        
        # Combinación lógica: Cliente nuevo Y (Compra grande O Sin pagos atrasados)
        inner_or = LogicalCondition(
            operator=LogicalOperator.OR,
            operands=[cond2, cond3]
        )
        
        complex_condition = LogicalCondition(
            operator=LogicalOperator.AND,
            operands=[cond1, inner_or]
        )
        
        # Crear regla de decisión
        rule = DecisionRule(
            id="RULE-D003",
            description="Determinar si se aplica descuento especial para nuevos clientes",
            source_reference=SourceReference(
                program="DISCOUNT.SQLRPGLE",
                section="ApplySpecialDiscount",
                lines="400-450"
            ),
            confidence=0.90,
            system_version="MVP_EXTRACTOR_V1",
            conditions=complex_condition,
            outcomes=[
                {"when": "condition_met", "result": "APPLY_DISCOUNT"},
                {"when": "condition_not_met", "result": "NO_DISCOUNT"}
            ],
            outcome_type="discount_status"
        )
        
        print("✅ Regla con condiciones lógicas complejas creada exitosamente:")
        print(rule.model_dump_json(indent=2))
        return rule
    except ValidationError as e:
        print("❌ Error de validación:")
        print(e)
        return None

if __name__ == "__main__":
    print("\n==== Ejemplo 1: Regla Básica ====")
    example_basic_rule()
    
    print("\n==== Ejemplo 2: Regla Inválida (campos faltantes) ====")
    example_invalid_rule_missing_fields()
    
    print("\n==== Ejemplo 3: Regla de Validación ====")
    example_validation_rule()
    
    print("\n==== Ejemplo 4: Cargar desde Diccionario ====")
    example_load_from_dict()
    
    print("\n==== Ejemplo 5: Condiciones Lógicas Complejas ====")
    example_complex_logical_conditions() 