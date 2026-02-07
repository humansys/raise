# Artifacts

> The document hierarchy in RaiSE

---

## What are Artifacts?

**Artifacts** are the documents and assets produced by following katas. They are the tangible outputs of governed work—the "receipts" that prove work was done properly.

## The Three-Level Hierarchy

RaiSE organizes artifacts in a three-level hierarchy:

```
                    SOLUTION
                   (the system)
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      PROJECT A    PROJECT B    PROJECT C
     (initiative)  (initiative) (initiative)
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
  Feat  Feat  Feat
   1     2     3
```

### Level 1: Solution

**Scope:** The entire system or product

**Location:** `governance/`

**Artifacts:**
| Artifact | Purpose |
|----------|---------|
| `business_case.md` | Why we're building this |
| `vision.md` | What we're building, high-level approach |
| `guardrails.md` | Rules that govern all work |
| `ecosystem.md` | External dependencies and integrations |

### Level 2: Project

**Scope:** A specific initiative, epic, or milestone

**Location:** `governance/`

**Artifacts:**
| Artifact | Purpose |
|----------|---------|
| `prd.md` | Requirements for this project |
| `vision.md` | Project-specific vision (optional) |
| `design.md` | Technical design |
| `backlog.md` | Prioritized work items |

### Level 3: Feature

**Scope:** Individual features, user stories, work items

**Location:** `work/stories/{name}/`

**Artifacts:**
| Artifact | Purpose |
|----------|---------|
| `spec.md` | Feature specification |
| `plan.md` | Implementation plan |
| `tasks.md` | Task breakdown |

## Governance vs Work

Artifacts live in two places:

```
governance/              work/
───────────              ─────
Approved artifacts       Work in progress
Source of truth          Drafts and experiments
Promoted via gates       Not yet validated
```

**Promotion flow:**
```
work/stories/{name}/     governance/
       draft.md      ──[gate]──→      approved.md
```

## Artifact Lifecycle

```
1. CREATE      Kata produces initial draft
      ↓
2. DRAFT       Lives in work/, being refined
      ↓
3. VALIDATE    Gate checks quality criteria
      ↓
4. PROMOTE     Moves to governance/ (source of truth)
      ↓
5. MAINTAIN    Updated as understanding evolves
```

## Traceability

Artifacts reference each other, creating traceability:

```
business_case.md
      ↓ derives
vision.md
      ↓ derives
project/prd.md
      ↓ derives
project/design.md
      ↓ derives
project/backlog.md
      ↓ implements
feature/spec.md
      ↓ implements
actual code
```

Every artifact knows:
- What it derives from (parent)
- What derives from it (children)
- When it was approved
- Who approved it

## Finding Artifacts

The `governance/index.yaml` manifest tracks all approved artifacts:

```yaml
artifacts:
  - path: vision.md
    type: vision
    level: solution
    status: approved
    approved_date: 2026-01-15

  - path: design.md
    type: design
    level: project
    status: approved
    approved_date: 2026-01-20
```

---

## Key Takeaways

1. **Three levels** — Solution → Project → Feature
2. **Two locations** — governance/ (truth) vs work/ (drafts)
3. **Promotion via gates** — Work becomes governance after validation
4. **Full traceability** — Every artifact linked to its context

---

*See also: [Governance](./governance.md) | [Gates](./gates.md)*
