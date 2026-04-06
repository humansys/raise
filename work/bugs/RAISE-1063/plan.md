# RAISE-1063 Plan

## Tasks

### T1: Fix _override_auth in test_api_agent, test_api_memory, test_api_graph
- OrgContext→MemberContext, verify_api_key→verify_member
- MemberContext has more fields (member_id, email, role, plan, features)

### T2: Rewrite test_auth.py
- Use verify_member instead of verify_api_key
- Mock must return (ApiKeyRow, MemberRow, Organization) tuple + LicenseRow
- Update all assertions

### T3: Fix test_db_models.py
- ApiKey→ApiKeyRow, update column set, update table registration list

### T4: Verify all tests pass
