# RAISE-1063 Analysis

## Method: Document directly

## Root Cause

Auth refactor renamed OrgContext→MemberContext, verify_api_key→verify_member,
ApiKey→ApiKeyRow. Tests in raise-pro/tests/rai_server/ still reference old names.
DB models also added members/licenses tables and new ApiKeyRow columns.

## Fix Approach

1. test_auth.py: Rewrite to use MemberContext/verify_member with correct mock chain
2. test_api_*.py: Update _override_auth helpers (3 files, identical pattern)
3. test_db_models.py: ApiKey→ApiKeyRow, update column expectations, add table list entries
