# RAISE-1278: Analysis

## Root Cause (XS — cause evident)

`write_record()` and `read_record()` in `memory/learning.py` use `record.work_id` / `work_id` parameter directly in path construction without case normalization. Since story branch regex is case-insensitive (`re.IGNORECASE`), agents may extract `s1051.6` or `S1051.6` depending on branch naming convention used at creation time.

On case-sensitive filesystems (Linux), this creates two distinct directories.

## Fix Approach

1. Add Pydantic `field_validator` on `LearningRecord.work_id` to normalize to uppercase at model construction time
2. Normalize `work_id` parameter in `read_record()` to uppercase before path lookup
3. Migration: rename existing lowercase directories to uppercase (one-shot, committed)
4. Delete the duplicate lowercase record (keep uppercase — it has richer data)
