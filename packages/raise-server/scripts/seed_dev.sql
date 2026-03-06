-- Seed data for local development / E2E testing.
-- Usage: docker compose exec postgres psql -U rai -d rai -f /dev/stdin < packages/rai-server/scripts/seed_dev.sql
--
-- Creates:
--   org "RaiSE Dev" (slug: raise-dev)
--   API key rsk_dev_test_key_12345
--
-- Raw key for env vars: RAI_API_KEY=rsk_dev_test_key_12345

INSERT INTO organizations (id, name, slug)
VALUES ('00000000-0000-4000-8000-000000000001', 'RaiSE Dev', 'raise-dev')
ON CONFLICT (slug) DO NOTHING;

-- Hash pre-computed with Python: hashlib.sha256(b'rsk_dev_test_key_12345').hexdigest()
INSERT INTO api_keys (id, org_id, key_hash, prefix, is_active)
VALUES (
    '00000000-0000-4000-8000-000000000002',
    '00000000-0000-4000-8000-000000000001',
    '8cbe0fafaba0937eb3470293b8c57f93c696580d619713c8ebfe33a27ef352c1',
    'rsk_dev_test',
    true
)
ON CONFLICT DO NOTHING;
