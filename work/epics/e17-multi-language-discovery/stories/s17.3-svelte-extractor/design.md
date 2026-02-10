# Design: S17.3 — Svelte Extractor

## What & Why

**Problem:** `raise discover scan` cannot extract symbols from `.svelte` files. zambezi-concierge uses Svelte for its frontend — these components are invisible to discovery.

**Value:** Completes M2 (Demo Ready) — discovery works across Python, TS/JS, PHP, and Svelte in polyglot repos.

## Architectural Context

- **Module:** discovery/scanner.py (domain layer, leaf)
- **Pattern:** Two-pass extraction — tree-sitter-svelte parses structure, tree-sitter-JS/TS parses `<script>` content
- **Constraint:** All analysis is deterministic — no AI inference in scanner

## Approach

Svelte files have three sections: `<script>`, template HTML, and `<style>`. tree-sitter-svelte treats `<script>` content as opaque `raw_text` — it doesn't parse the JS/TS inside. This requires a **two-pass** approach:

1. **Pass 1:** Parse `.svelte` with tree-sitter-svelte, find `script_element` nodes
2. **Detect language:** Check `<script lang="ts">` attribute → TypeScript, else JavaScript
3. **Pass 2:** Re-parse the `raw_text` content with the appropriate JS/TS parser
4. **Component symbol:** Register the `.svelte` file as a `"component"` kind symbol

### Components Modified

| Component | Change |
|-----------|--------|
| `scanner.py` — `_get_svelte_parser()` | Create — tree-sitter-svelte parser |
| `scanner.py` — `_extract_svelte_script_info()` | Create — extract script content + detect lang |
| `scanner.py` — `extract_svelte_symbols()` | Create — two-pass: svelte parse → JS/TS parse |
| `scanner.py` — `extract_symbols()` | Modify — add `"svelte"` case |

**IMPORTANT:** `tree_sitter_svelte.language()` (not `language_svelte()`).

### Line Offset

Script content starts at an offset within the `.svelte` file. Symbols extracted from the JS/TS parse will have line numbers relative to the script block. Must add the script block's start line to get correct file-level line numbers.

## Examples

### Input (JS)
```svelte
<script>
  import { onMount } from 'svelte';

  export let name = 'world';

  function greet(msg) {
    return 'Hello ' + msg;
  }

  class UserService {
    getName() {
      return this.name;
    }
  }
</script>

<h1>Hello {name}!</h1>
```

### Expected Output
```python
[
    Symbol(kind="component", name="Greeting", file="Greeting.svelte", line=1,
           signature="component Greeting"),
    Symbol(kind="function", name="greet", file="Greeting.svelte", line=6,
           signature="function greet(msg)"),
    Symbol(kind="class", name="UserService", file="Greeting.svelte", line=10,
           signature="class UserService"),
    Symbol(kind="method", name="getName", file="Greeting.svelte", line=11,
           signature="getName()", parent="UserService"),
]
```

### Input (TypeScript)
```svelte
<script lang="ts">
  interface User {
    name: string;
  }

  export function getUser(): User {
    return { name: 'test' };
  }
</script>
```

### Expected Output
```python
[
    Symbol(kind="component", name="UserCard", file="UserCard.svelte", line=1,
           signature="component UserCard"),
    Symbol(kind="interface", name="User", file="UserCard.svelte", line=2,
           signature="interface User"),
    Symbol(kind="function", name="getUser", file="UserCard.svelte", line=6,
           signature="function getUser(): User"),
]
```

### No Script Block
```svelte
<div>Static content only</div>
```

### Expected Output
```python
[
    Symbol(kind="component", name="Static", file="Static.svelte", line=1,
           signature="component Static"),
]
```

## Acceptance Criteria

**MUST:**
- Extract functions, classes, methods, interfaces, enums from `<script>` blocks
- Detect `lang="ts"` and use TypeScript parser when present, JavaScript otherwise
- Register `.svelte` file as `"component"` symbol
- Correct line numbers (offset from script block start)
- Wire into `extract_symbols()` dispatcher
- All tests pass, ruff clean, pyright clean

**SHOULD:**
- Handle `<script context="module">` blocks (extract from both if present)
- Handle files with no `<script>` block (component-only symbol)

**MUST NOT:**
- Parse template HTML for symbols
- Parse `<style>` blocks
- Add Svelte-specific category logic (that's S17.4)
