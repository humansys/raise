# Impact Analysis Skill

> **Purpose**: Analyze what needs updating when governance artifacts change

---

## Overview

This skill performs change impact analysis before modifying governance artifacts. It answers: "If I change X, what else needs to change?"

## Trigger

- Before editing any governance artifact
- When proposing ADRs that affect existing artifacts
- During framework version upgrades

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `artifact_path` | string | Yes | Path to artifact being changed |
| `change_type` | enum | Yes | `modify`, `rename`, `delete`, `add` |
| `change_description` | string | No | Description of the change |

## Analysis Types

### 1. Direct Dependencies

Find artifacts that directly reference the changed artifact:

```
Query index.yaml relationships where:
  - 'to' == artifact_path

Query all governance/ files for:
  - References to artifact filename
  - References to concepts defined in artifact
```

**Output**: List of directly dependent artifacts

### 2. Transitive Dependencies

Follow dependency chain:

```
For each direct dependency:
  - Find its dependents
  - Recurse until no more dependencies
```

**Output**: Full dependency tree

### 3. Concept Impact

For terminology/glossary changes:

```
If artifact defines terms:
  - Find all uses of those terms across governance/
  - Find all uses in .raise/ (katas, gates, templates)
  - Find all uses in work/
```

**Output**: List of files using affected terms

### 4. External Impact

For changes that affect consumer projects:

```
If artifact is part of injected framework:
  - Identify breaking changes
  - Identify migration requirements
  - Flag for migration guide update
```

**Output**: Migration impact assessment

## Steps

### 1. Parse Change Request

```
- Identify artifact being changed
- Determine change type and scope
- Load artifact content for analysis
```

**Verification**: Change request understood

> **Si no puedes continuar**: Artifact not found → Check path. Invalid change type → Use valid enum.

### 2. Build Dependency Graph

```
- Load governance/index.yaml
- Load framework/index.yaml (if raise-commons)
- Build in-memory graph of relationships
```

**Verification**: Graph built with all artifacts

### 3. Analyze Impact

```
- Run all relevant analysis types
- Collect affected artifacts
- Determine severity for each
```

**Verification**: Analysis complete

### 4. Generate Impact Report

```markdown
# Impact Analysis Report
Artifact: {path}
Change Type: {type}
Date: {date}

## Direct Impact
{list of directly affected artifacts}

## Transitive Impact
{dependency tree visualization}

## Concept Impact
{list of files using affected terms}

## Migration Impact
{breaking changes and migration requirements}

## Recommended Actions
1. {action 1}
2. {action 2}
...

## Estimated Effort
- Files to update: {count}
- Complexity: {low|medium|high}
```

**Verification**: Report generated with all sections

## Output

- Impact analysis report
- List of files to update
- Recommended action sequence

## Example Usage

```bash
# Analyze impact of modifying glossary
/dev/impact-analysis \
  --artifact framework/context/glossary.md \
  --change-type modify \
  --change-description "Rename 'Solution Vision' to 'Project Vision' at project level"

# Analyze impact of deleting an ADR
/dev/impact-analysis \
  --artifact framework/decisions/adr-005.md \
  --change-type delete
```

## Integration with Other Skills

```
Typical workflow:
1. /dev/impact-analysis --artifact X --change-type modify
2. Review impact report
3. Make changes to X and all affected artifacts
4. /dev/governance-audit --scope full
5. /dev/governance-sync (if promoting from work/)
```

---

*Internal tool for framework maintainers. Not part of injected framework.*
