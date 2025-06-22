# Documentación del Modelo BusinessRule

## Introducción

El modelo `BusinessRule` es un componente central del sistema de extracción de reglas de negocio para código AS/400. Implementado con Pydantic, este modelo proporciona validación automática de las estructuras de datos que representan reglas de negocio extraídas del código legado.

## Estructura del Modelo

El sistema utiliza un enfoque de jerarquía de clases donde todas las reglas heredan de una clase base común y luego se especializan según su tipo:

```
BaseRule
  ├── ValidationRule
  ├── DecisionRule
  ├── CalculationRule
  └── WorkflowRule
```

### Clase Base

`BaseRule` implementa los campos comunes requeridos por todas las reglas:

```python
class BaseRule(BaseModel):
    id: str                          # Identificador único de la regla
    type: RuleType                   # Tipo de regla de negocio
    description: str                 # Descripción legible por humanos
    source_reference: SourceReference # Referencia al código fuente original
    confidence: float                # Nivel de confianza (0-1)
    extracted_timestamp: datetime    # Marca de tiempo de la extracción
    system_version: str              # Versión del sistema legado o extractor
    concepts: Optional[List[str]]    # Conceptos de negocio relacionados (opcional)
    tags: Optional[List[str]]        # Etiquetas para categorización (opcional)
    notes: Optional[str]             # Notas adicionales (opcional)
```

### Tipos de Reglas

El modelo soporta cuatro tipos principales de reglas de negocio:

1. **ValidationRule**: Representa reglas que validan datos según condiciones específicas.
2. **DecisionRule**: Representa reglas de toma de decisiones basadas en condiciones.
3. **CalculationRule**: Representa fórmulas y algoritmos de cálculo.
4. **WorkflowRule**: Representa reglas de flujo de trabajo o proceso.

### Estructuras de Soporte

El modelo también define varias estructuras auxiliares:

- **SourceReference**: Referencia al código fuente original (programa, sección, líneas).
- **ComparisonCondition**: Condición de comparación simple (campo, operador, valor).
- **LogicalCondition**: Combinación lógica de condiciones (AND, OR, NOT).
- **Action**: Acción a tomar como resultado de una regla (error, logging, cambio de estado).

## Uso del Modelo

### Importación

```python
from rules_extractor.models.business_rule import (
    BusinessRule, BaseRule, ValidationRule, DecisionRule, CalculationRule, WorkflowRule,
    RuleType, SourceReference, ComparisonCondition, ComparisonOperator, Action, ActionType,
    ErrorLevel, LogicalCondition, LogicalOperator, load_rule_from_dict
)
```

### Creación de una Regla Básica

```python
rule = BaseRule(
    id="RULE-1234",
    type=RuleType.OTHER,
    description="Ejemplo de regla básica",
    source_reference=SourceReference(
        program="PROGRAM.SQLRPGLE",
        lines="100-120"
    ),
    confidence=0.85,
    system_version="MVP_EXTRACTOR_V1"
)
```

### Creación de una Regla de Validación

```python
condition = ComparisonCondition(
    field="CUSTOMER_BALANCE",
    operator=ComparisonOperator.GT,
    value=1000.0
)

action = Action(
    type=ActionType.ERROR_HANDLING,
    level=ErrorLevel.ERROR,
    message_template="El balance del cliente excede el límite permitido de $1000"
)

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
```

### Cargar desde JSON/Diccionario

El modelo proporciona una función helper `load_rule_from_dict` para cargar y validar reglas desde un diccionario (por ejemplo, JSON recibido de un LLM):

```python
llm_output = {
    "id": "RULE-C002",
    "type": "calculation",
    "description": "Calcular total con impuestos",
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

rule = load_rule_from_dict(llm_output)
```

## Validación

El modelo Pydantic validará automáticamente:

1. La presencia de todos los campos obligatorios
2. El formato/tipo correcto de cada campo
3. Restricciones adicionales (por ejemplo, `confidence` entre 0 y 1)
4. Validaciones condicionales basadas en el tipo de regla o valores de otros campos

Si la validación falla, Pydantic lanzará una `ValidationError` con detalles sobre el error.

## Funciones de Validación Personalizadas

El modelo implementa varias funciones de validación personalizadas:

- **Validación de formato de líneas**: Asegura que el formato de líneas sea "N" o "N-M"
- **Validación de campos condicionales**: Verifica campos requeridos según el tipo
- **Validación de consistencia**: Asegura que, por ejemplo, las condiciones lógicas NOT tengan exactamente un operando

## Prácticas Recomendadas

1. **Utilice los tipos específicos**: Prefiera `ValidationRule`, `DecisionRule`, etc. en lugar de `BaseRule` cuando conozca el tipo específico.
2. **Maneje las excepciones de validación**: Capture las `ValidationError` para proporcionar retroalimentación útil.
3. **Utilice la función helper**: Utilice `load_rule_from_dict` para cargar reglas desde JSON/diccionarios.
4. **Proporcione descripciones significativas**: La descripción debe ser clara y explicar el propósito de la regla.

## Integración con el Pipeline de Extracción

El modelo BusinessRule se utiliza en varios componentes del pipeline de extracción:

1. **Response Parser**: Convierte la respuesta del LLM en objetos BusinessRule validados.
2. **Validator**: Añade información de confianza/validación a las reglas extraídas.
3. **Output Formatter**: Serializa las reglas validadas a YAML/JSON y Markdown.

## Extensiones Futuras

El modelo está diseñado para ser extensible. Posibles extensiones incluyen:

- Relaciones explícitas entre reglas (dependencias, contradicciones)
- Metadatos adicionales como datos de traceabilidad
- Tipos de reglas adicionales específicos del dominio
- Soporte para diferentes idiomas/formatos de salida

## Ejemplos 

Ver los archivos:
- `business_rule_example.py`: Ejemplos de uso del modelo
- `test_business_rule.py`: Pruebas unitarias que muestran validaciones 