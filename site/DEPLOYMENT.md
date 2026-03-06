# Website Deployment

## Overview
The RaiSE website (raiseframework.ai) deploys to Cloudflare Pages from the `site/` directory.

## Automatic Deployment
- Pushes to `main` that modify `site/**` trigger the GitHub Actions workflow
- Workflow: `.github/workflows/deploy-site.yml`
- Build: `npm run build` (Astro 5 + Starlight)
- Deploy: `wrangler pages deploy` via cloudflare/wrangler-action

## Prerequisites (one-time setup)

### 1. Cloudflare API Token
1. Go to Cloudflare Dashboard > My Profile > API Tokens
2. Create token with permissions: Cloudflare Pages (Edit), D1 (Edit)
3. Add as GitHub secret: `CLOUDFLARE_API_TOKEN`

### 2. Cloudflare Account ID
1. Go to Cloudflare Dashboard > any domain > Overview
2. Copy Account ID from the right sidebar
3. Add as GitHub secret: `CLOUDFLARE_ACCOUNT_ID`

### 3. Repoint Cloudflare Pages (from raise-gtm)
1. Go to Cloudflare Pages > raise-website project
2. Settings > Builds & deployments
3. Change repository from `raise-gtm` to `raise-commons`
4. Set build output directory to `site/dist`
5. Set root directory to `site`
6. Or: disconnect the Git integration and rely on the GitHub Actions workflow with `wrangler pages deploy`

## D1 Database (Waitlist)
- Database: `raise-waitlist` (ID in `wrangler.jsonc`)
- Schema: `site/db/schema.sql`
- The database already exists in Cloudflare — no migration needed
- The waitlist API endpoint (`/api/waitlist`) uses D1 bindings configured in `wrangler.jsonc`

## Manual Deploy
```bash
cd site
npm install
npm run build
npx wrangler pages deploy dist --project-name=raise-website
```

## Troubleshooting
- **Build fails**: Check Node version (requires 22+), run `npm ci` before build
- **Deploy fails**: Verify CLOUDFLARE_API_TOKEN has Pages edit permission
- **D1 not working**: Verify database binding in wrangler.jsonc matches your account's D1 database
- **Workflow not triggering**: Check that changes are in `site/**` path and pushing to `main`
