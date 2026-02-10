# S17.1: Fix TS/TSX Scanner — Design

> **Story:** S17.1 | **Epic:** E17 | **Size:** M | **Complexity:** Moderate
> **Module:** mod-discovery (domain layer)

---

## What & Why

**Problem:** The TypeScript scanner misses 84% of source files in real Next.js projects. Two bugs: (1) `.tsx` files are excluded from the glob pattern, and (2) `enum`, `const`, and `type` exports are not extracted even from scanned files.

**Value:** Fixes a blocking bug for TypeScript discovery and lays the foundation (new SymbolKinds, exclude-based hierarchy) for PHP and Svelte extractors in S17.2/S17.3.

---

## Approach

Four changes in `scanner.py`, one in `analyzer.py`, one in `discover.py` formatter:

1. **Fix TS glob** — `DEFAULT_LANGUAGE_PATTERNS["typescript"]` from `"**/*.ts"` to `"**/*.{ts,tsx}"` (or two-pattern approach if glob doesn't support brace expansion)
2. **TSX parser dispatch** — `_get_ts_parser()` accepts file extension; `.tsx` → `language_tsx()`, `.ts` → `language_typescript()`
3. **Expand SymbolKind** — Add `"enum"`, `"type_alias"`, `"constant"`, `"trait"`, `"component"`
4. **Extract new node types** — In `_extract_ts_js_symbols()`, handle `enum_declaration`, `type_alias_declaration`, `export_statement` with `variable_declaration` (const exports)
5. **Exclude-based hierarchy** — In `build_hierarchy()`, flip routing: class→fold, method→fold into parent, everything else→standalone
6. **Formatter counts** — Add summary lines for new symbol kinds in `_format_scan_summary()`

### Components Affected

| Component | File | Change |
|-----------|------|--------|
| SymbolKind | `scanner.py:27` | Expand Literal type |
| DEFAULT_LANGUAGE_PATTERNS | `scanner.py:536` | Fix TS glob |
| `_get_ts_parser()` | `scanner.py:228` | Accept extension, dispatch TSX |
| `extract_typescript_symbols()` | `scanner.py:313` | Pass extension to parser |
| `_extract_ts_js_symbols()` | `scanner.py:373` | Add enum/type_alias/const extraction |
| `_extract_ts_signature()` | `scanner.py:274` | Add signatures for new node types |
| `build_hierarchy()` | `analyzer.py:379` | Exclude-based routing |
| `_format_scan_summary()` | `discover.py:56` | New kind counts |

---

## Examples

### TSX file extraction (Bug 1 fix)

```typescript
// src/context/UserContext.tsx
import React, { createContext, useContext } from 'react';

interface UserContextType {
  user: User | null;
}

export const UserContext = createContext<UserContextType>({ user: null });

export default function UserProvider({ children }: Props) {
  return <UserContext.Provider value={{ user }}>{children}</UserContext.Provider>;
}
```

**Expected symbols:**
```python
[
    Symbol(name="UserContextType", kind="interface", file="src/context/UserContext.tsx", line=4),
    Symbol(name="UserContext", kind="constant", file="src/context/UserContext.tsx", line=8),
    Symbol(name="UserProvider", kind="function", file="src/context/UserContext.tsx", line=10),
]
```

### Enum/const/type extraction (Bug 2 fix)

```typescript
// src/config/roles.ts
export enum UserRole {
  Admin = 'admin',
  User = 'user',
}

export type ReportAction = 'view' | 'edit' | 'delete';

export const SESSION_CONFIG = {
  timeout: 30000,
  maxRetries: 3,
} as const;
```

**Expected symbols:**
```python
[
    Symbol(name="UserRole", kind="enum", file="src/config/roles.ts", line=1),
    Symbol(name="ReportAction", kind="type_alias", file="src/config/roles.ts", line=6),
    Symbol(name="SESSION_CONFIG", kind="constant", file="src/config/roles.ts", line=8),
]
```

### Exclude-based hierarchy

```python
# Before (include-based): new kinds silently dropped
if s.kind in ("function", "module"):  # enum, type_alias, constant → LOST

# After (exclude-based): only class/method are special
if s.kind not in ("class", "method"):  # everything else → standalone
```

---

## Acceptance Criteria

**MUST:**
- `.tsx` files found and parsed by `scan_directory(language="typescript")`
- `.tsx` files use `language_tsx()` parser; `.ts` files use `language_typescript()`
- `enum_declaration` extracted as `kind="enum"`
- `type_alias_declaration` extracted as `kind="type_alias"`
- Exported `const` declarations extracted as `kind="constant"`
- `build_hierarchy()` routes new kinds as standalone (not dropped)
- All existing Python scanner tests pass (regression)

**SHOULD:**
- Formatter shows counts for enums, type aliases, constants when present
- Signature extraction for enum and type_alias nodes

**MUST NOT:**
- Break existing Python or JavaScript extraction
- Change behavior of class/method/function/interface extraction
- Add PHP or Svelte support (S17.2/S17.3)

---

*Created: 2026-02-09*
