# RaiSE JSON Schemas

This directory contains the JSON Schemas that define the data contracts between RaiSE components.

## Overview

RaiSE uses three core schemas to ensure consistent data exchange between the SAR (extraction) and CTX (context delivery) components:

| Schema | Purpose | Producer | Consumer |
|--------|---------|----------|----------|
| `rule-schema.json` | Individual governance rule | SAR | CTX, Validate |
| `graph-schema.json` | Relationship graph between rules | SAR | CTX |
| `mvc-schema.json` | Minimum Viable Context output | CTX | LLM Agents |

## Schema Descriptions

### rule-schema.json

Defines the structure for individual governance rules extracted by SAR from codebase analysis.

**Key fields:**
- `id`: Unique identifier in slugified format (e.g., `ts-service-suffix`)
- `confidence`: Adoption rate in codebase (0.0-1.0)
- `enforcement`: How strictly to enforce (`hard`, `strong`, `moderate`, `advisory`, `none`)
- `pattern`: Detection pattern (ast-grep, regex, or structural)
- `examples`: Positive (correct) and negative (violation) code examples
- `provenance`: Origin metadata (source, tool version, evidence count)

### graph-schema.json

Defines the relationship graph between rules, stored separately from individual rules per [ADR-004](../adrs/adr-004-separate-graph.md).

**Relationship types:**
- `requires`: Rule A requires Rule B to be followed
- `conflicts_with`: Rules cannot both be enforced
- `supersedes`: Rule A replaces deprecated Rule B
- `related_to`: Rules are conceptually related

### mvc-schema.json

Defines the output format of `raise ctx get` - the Minimum Viable Context delivered to LLM agents.

**Key sections:**
- `query`: Original query parameters (task, scope, min_confidence)
- `primary_rules`: Full rule content for directly applicable rules
- `context_rules`: Summary-only references for related rules
- `warnings`: Conflicts, deprecations, low-confidence alerts
- `graph_context`: Relevant subgraph showing rule relationships
- `metadata`: Token estimate, retrieval time, match count

## Usage

### Validating YAML Files

Rules are stored as YAML files (per [ADR-003](../adrs/adr-003-yaml-rule-format.md)) but validated against these JSON Schemas.

```bash
# Using ajv-cli
npx ajv validate -s rule-schema.json -d path/to/rule.yaml

# Using python jsonschema
python -m jsonschema -i rule.yaml rule-schema.json
```

### Programmatic Validation (TypeScript)

```typescript
import Ajv from 'ajv';
import ruleSchema from './rule-schema.json';

const ajv = new Ajv();
const validate = ajv.compile(ruleSchema);

const rule = loadYamlFile('rules/ts-service-suffix.yaml');
if (!validate(rule)) {
  console.error(validate.errors);
}
```

## Examples

The `examples/` directory contains realistic examples for each schema:

| File | Schema | Description |
|------|--------|-------------|
| `rule-example-naming.yaml` | rule-schema | TypeScript service naming convention |
| `rule-example-architecture.yaml` | rule-schema | Repository pattern architecture rule |
| `graph-example.yaml` | graph-schema | Rule relationship graph |
| `mvc-example.yaml` | mvc-schema | CTX output for auth service task |

## Design Principles

1. **Lean**: Only fields necessary for governance, no over-engineering
2. **Explicit**: Every field has a `description`
3. **Validable**: Enums for fixed values, patterns for formats
4. **Strict**: `additionalProperties: false` prevents schema drift
5. **Versioned**: Schema evolution via semver in `$id`

## Schema Version

All schemas follow [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/schema).

Current version: **1.0.0**

## Related Documentation

- [ADR-003: YAML Rule Format](../adrs/adr-003-yaml-rule-format.md)
- [ADR-004: Separate Graph](../adrs/adr-004-separate-graph.md)
- [Design Document](../design.md) - Data contracts section
- [CTX Vision](../ctx/vision.md) - MVC concept explanation
