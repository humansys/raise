# RAISE-663 — Analysis

## 5 Whys

Problem: `rai backlog get` shows Python dict repr instead of description text.

Why 1: `description` is stored as ADF (Atlassian Document Format) — a nested JSON dict.
Why 2: `_parse_issue_detail` calls `str(fields.get("description", ""))` on the ADF dict.
Why 3: `str()` on a dict produces Python repr, not human-readable text.
Why 4: No ADF→text conversion function exists in the adapter.
Why 5: The adapter was written assuming description would always be a plain string.

**Root cause:** `acli_jira.py:220` uses `str()` on the ADF description dict, producing a Python repr. The 500-char hard-cap in `backlog.py:231` compounds the problem by truncating this already-unreadable output.

## Fix Approach

1. Add `_adf_to_text(value: object) -> str` module-level function in `acli_jira.py`:
   - If value is a dict (ADF doc), walk the node tree extracting text content
   - If value is a string, return as-is (handles plain-text descriptions)
   - Handles: paragraph, heading, text, bulletList, orderedList, listItem, codeBlock, blockquote

2. Replace `str(fields.get("description", ""))` → `_adf_to_text(fields.get("description", ""))` at line 220.

3. Remove hard-cap 500 chars in `backlog.py:231` — it was a workaround for the repr overflow, not a feature.
