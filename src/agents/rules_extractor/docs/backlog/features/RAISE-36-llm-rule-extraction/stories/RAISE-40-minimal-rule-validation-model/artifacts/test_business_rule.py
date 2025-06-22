"""
Pruebas unitarias para el modelo BusinessRule.

Este archivo contiene pruebas para verificar que las validaciones
del modelo BusinessRule funcionan correctamente.
"""

import unittest
from pydantic import ValidationError
from rules_extractor.models.business_rule import (
    BusinessRule, BaseRule, ValidationRule, DecisionRule, CalculationRule, WorkflowRule,
    RuleType, SourceReference, ComparisonCondition, ComparisonOperator, LogicalCondition,
    LogicalOperator, Action, ActionType, ErrorLevel, load_rule_from_dict
)

class BusinessRuleBaseTest(unittest.TestCase):
    """Pruebas para el modelo base de reglas de negocio."""
    
    def test_valid_base_rule(self):
        """Verifica que una regla base con campos válidos se crea correctamente."""
        rule = BaseRule(
            id="RULE-TEST-1",
            type=RuleType.OTHER,
            description="Regla de prueba válida",
            source_reference=SourceReference(
                program="TESTPGM.SQLRPGLE",
                lines="100-120"
            ),
            confidence=0.85,
            system_version="TEST_SYSTEM_V1"
        )
        self.assertEqual(rule.id, "RULE-TEST-1")
        self.assertEqual(rule.type, RuleType.OTHER)
        self.assertEqual(rule.description, "Regla de prueba válida")
        self.assertEqual(rule.confidence, 0.85)
    
    def test_missing_required_fields(self):
        """Verifica que se lancen excepciones cuando faltan campos obligatorios."""
        # Falta descripción
        with self.assertRaises(ValidationError):
            BaseRule(
                id="RULE-TEST-2",
                type=RuleType.OTHER,
                source_reference=SourceReference(
                    program="TESTPGM.SQLRPGLE",
                    lines="100-120"
                ),
                confidence=0.85,
                system_version="TEST_SYSTEM_V1"
            )
        
        # Falta source_reference
        with self.assertRaises(ValidationError):
            BaseRule(
                id="RULE-TEST-3",
                type=RuleType.OTHER,
                description="Regla de prueba sin source_reference",
                confidence=0.85,
                system_version="TEST_SYSTEM_V1"
            )
    
    def test_confidence_range_validation(self):
        """Verifica que el valor de confidence esté en el rango 0-1."""
        # Confidence fuera de rango (muy alto)
        with self.assertRaises(ValidationError):
            BaseRule(
                id="RULE-TEST-4",
                type=RuleType.OTHER,
                description="Regla de prueba con confidence inválido",
                source_reference=SourceReference(
                    program="TESTPGM.SQLRPGLE",
                    lines="100-120"
                ),
                confidence=1.5,  # Debe ser <= 1.0
                system_version="TEST_SYSTEM_V1"
            )
        
        # Confidence fuera de rango (negativo)
        with self.assertRaises(ValidationError):
            BaseRule(
                id="RULE-TEST-5",
                type=RuleType.OTHER,
                description="Regla de prueba con confidence inválido",
                source_reference=SourceReference(
                    program="TESTPGM.SQLRPGLE",
                    lines="100-120"
                ),
                confidence=-0.2,  # Debe ser >= 0.0
                system_version="TEST_SYSTEM_V1"
            )


class BusinessRuleTypesTest(unittest.TestCase):
    """Pruebas para los diferentes tipos de reglas de negocio."""
    
    def test_validation_rule(self):
        """Verifica que una regla de validación se cree correctamente."""
        condition = ComparisonCondition(
            field="AMOUNT",
            operator=ComparisonOperator.GT,
            value=1000
        )
        
        action = Action(
            type=ActionType.ERROR_HANDLING,
            level=ErrorLevel.ERROR,
            message_template="El monto excede el límite permitido"
        )
        
        rule = ValidationRule(
            id="RULE-V001",
            description="Validar límite de monto",
            source_reference=SourceReference(
                program="VALCHECK.SQLRPGLE",
                lines="50-55"
            ),
            confidence=0.9,
            system_version="TEST_SYSTEM_V1",
            conditions=condition,
            action=action
        )
        
        self.assertEqual(rule.type, RuleType.VALIDATION)
        self.assertEqual(rule.conditions.field, "AMOUNT")
        self.assertEqual(rule.action.type, ActionType.ERROR_HANDLING)
    
    def test_calculation_rule(self):
        """Verifica que una regla de cálculo se cree correctamente."""
        rule = CalculationRule(
            id="RULE-C001",
            description="Calcular total con impuestos",
            source_reference=SourceReference(
                program="CALC.SQLRPGLE",
                lines="100-110"
            ),
            confidence=0.95,
            system_version="TEST_SYSTEM_V1",
            formula="TOTAL = SUBTOTAL * (1 + TAX_RATE)",
            target_field="TOTAL",
            source_fields=["SUBTOTAL", "TAX_RATE"]
        )
        
        self.assertEqual(rule.type, RuleType.CALCULATION)
        self.assertEqual(rule.formula, "TOTAL = SUBTOTAL * (1 + TAX_RATE)")
        self.assertEqual(rule.target_field, "TOTAL")
        self.assertEqual(len(rule.source_fields), 2)
    
    def test_decision_rule(self):
        """Verifica que una regla de decisión se cree correctamente."""
        condition = ComparisonCondition(
            field="CUSTOMER_TYPE",
            operator=ComparisonOperator.EQ,
            value="PREMIUM"
        )
        
        rule = DecisionRule(
            id="RULE-D001",
            description="Decidir descuento por tipo de cliente",
            source_reference=SourceReference(
                program="DISCOUNT.SQLRPGLE",
                lines="200-220"
            ),
            confidence=0.85,
            system_version="TEST_SYSTEM_V1",
            conditions=condition,
            outcomes=[
                {"when": "premium", "result": 0.15},
                {"when": "regular", "result": 0.05}
            ],
            outcome_type="discount_rate"
        )
        
        self.assertEqual(rule.type, RuleType.DECISION)
        self.assertEqual(len(rule.outcomes), 2)
        self.assertEqual(rule.outcome_type, "discount_rate")


class ComplexConditionsTest(unittest.TestCase):
    """Pruebas para condiciones lógicas complejas."""
    
    def test_complex_logical_condition(self):
        """Verifica que se puedan crear condiciones lógicas complejas."""
        cond1 = ComparisonCondition(
            field="AGE",
            operator=ComparisonOperator.GT,
            value=18
        )
        
        cond2 = ComparisonCondition(
            field="MEMBER_YEARS",
            operator=ComparisonOperator.GE,
            value=2
        )
        
        and_condition = LogicalCondition(
            operator=LogicalOperator.AND,
            operands=[cond1, cond2]
        )
        
        self.assertEqual(and_condition.operator, LogicalOperator.AND)
        self.assertEqual(len(and_condition.operands), 2)
        
        # Verificar validación de operandos para NOT
        with self.assertRaises(ValidationError):
            LogicalCondition(
                operator=LogicalOperator.NOT,
                operands=[cond1, cond2]  # NOT requiere exactamente un operando
            )


class LoadFromDictTest(unittest.TestCase):
    """Pruebas para la función helper load_rule_from_dict."""
    
    def test_load_validation_rule(self):
        """Verifica la carga de una regla de validación desde un diccionario."""
        data = {
            "id": "RULE-V002",
            "type": "validation",
            "description": "Validar código postal",
            "source_reference": {
                "program": "VALIDATE.SQLRPGLE",
                "lines": "300-310"
            },
            "confidence": 0.88,
            "system_version": "TEST_SYSTEM_V1",
            "conditions": {
                "type": "comparison",
                "field": "POSTAL_CODE",
                "operator": "==",
                "value": "12345"
            },
            "action": {
                "type": "error_handling",
                "level": "error",
                "message_template": "Código postal inválido"
            }
        }
        
        rule = load_rule_from_dict(data)
        self.assertIsInstance(rule, ValidationRule)
        self.assertEqual(rule.id, "RULE-V002")
        self.assertEqual(rule.conditions.field, "POSTAL_CODE")
    
    def test_unknown_rule_type(self):
        """Verifica que se lance una excepción para un tipo de regla desconocido."""
        data = {
            "id": "RULE-X001",
            "type": "unknown_type",  # Tipo inválido
            "description": "Regla de tipo desconocido",
            "source_reference": {
                "program": "TEST.SQLRPGLE",
                "lines": "1-10"
            },
            "confidence": 0.5,
            "system_version": "TEST_SYSTEM_V1"
        }
        
        with self.assertRaises(ValueError):
            load_rule_from_dict(data)


if __name__ == "__main__":
    unittest.main() 