# Architecture Options: Collective Intelligence Infrastructure

> Scout report for RES-LINEAGE-001
> Date: 2026-02-02

---

## TL;DR

| Option | Monthly Cost | Complexity | Best For |
|--------|-------------|------------|----------|
| **Git-native** | $0 | Low | Bootstrap, open source purity |
| **Minimal SaaS** | $5-50 | Medium | Early traction, control |
| **Full SaaS** | $200-2000+ | High | Scale, enterprise features |

**Recommendation:** Start Git-native, graduate to Minimal SaaS when you have 100+ users.

---

## Option 1: Git-Native (No Server)

**How it works:**
- Shared patterns live in a public Git repo (e.g., `raise-patterns`)
- Users opt-in to push anonymized patterns via PR or direct push
- Rai pulls from the repo on session start
- Lineage tracked via Git history

**Architecture:**
```
User's .rai/memory/     ──(opt-in export)──►   github.com/humansys/raise-patterns
       │                                                    │
       │                                                    │
       └────────────────(pull on session start)─────────────┘
```

**Costs:**
- Infrastructure: **$0** (GitHub/GitLab free tier)
- Maintenance: ~2 hrs/week (review PRs, curate)

**Pros:**
- Zero infrastructure cost
- Fully transparent (patterns are public)
- Lineage is Git history
- Works offline
- Open source ethos

**Cons:**
- No real-time sync
- Public only (no private sharing)
- Manual curation needed
- Doesn't scale past ~1000 contributors without tooling

**Prior art:** [Quit Store](https://arxiv.org/abs/1805.03721) — Git-based knowledge management

---

## Option 2: Minimal SaaS (Serverless Backend)

**How it works:**
- Lightweight API receives pattern submissions
- Serverless Postgres stores patterns with lineage
- CLI pulls aggregated patterns on session start
- Dashboard for transparency

**Architecture:**
```
User's .rai/memory/     ──(HTTPS POST)──►   api.raise.dev/patterns
       │                                          │
       │                                    [Serverless Function]
       │                                          │
       │                                    [Neon/Xata Postgres]
       │                                          │
       └────────────(GET on session start)────────┘
```

**Costs (estimated):**

| Component | Service | Monthly |
|-----------|---------|---------|
| Database | Neon free → $5 paid | $0-5 |
| API | Vercel/Cloudflare Workers | $0-20 |
| Storage | Included or S3 | $0-5 |
| Domain | raise.dev | $1 |
| **Total** | | **$5-30/month** |

At 1,000 users with light usage: ~$30-50/month
At 10,000 users: ~$100-200/month

**Pros:**
- Real-time sync
- Private + anonymous options
- Aggregation and analytics possible
- API enables future integrations

**Cons:**
- Infrastructure to maintain
- Monthly costs (small but non-zero)
- Privacy/trust requirements
- You become a data controller

**Prior art:** PostHog, Plausible (privacy-focused analytics)

---

## Option 3: Full SaaS (Hosted Rai)

**How it works:**
- Complete hosted experience
- User accounts, teams, permissions
- Pattern marketplace / library
- Analytics dashboard
- Enterprise features (SSO, audit logs)

**Architecture:**
```
┌─────────────────────────────────────────┐
│            app.raise.dev                │
├─────────────────────────────────────────┤
│  Auth │ Teams │ Patterns │ Analytics   │
├─────────────────────────────────────────┤
│           API Gateway                    │
├─────────────────────────────────────────┤
│  Postgres │ Redis │ S3 │ Search        │
└─────────────────────────────────────────┘
            │
            ▼
      User's local Rai
```

**Costs (estimated):**

| Component | Monthly |
|-----------|---------|
| Compute (API, workers) | $50-200 |
| Database (managed) | $25-100 |
| Auth (Clerk/Auth0) | $0-100 |
| Storage | $10-50 |
| Monitoring | $0-50 |
| **Total** | **$100-500/month** (early) |
| **At scale** | **$500-2000+/month** |

**Pros:**
- Full product experience
- Team features
- Revenue potential (freemium)
- Enterprise-ready

**Cons:**
- Significant investment to build
- Ongoing maintenance burden
- Support overhead
- Need users before value compounds

---

## Cost Drivers Deep Dive

### What makes collective intelligence expensive?

1. **Storage** — Patterns are small (KB), but with lineage metadata they grow
   - 10,000 patterns × 10KB = 100MB (negligible)
   - Lineage history multiplies this 5-10x

2. **Compute** — Aggregation, search, recommendations
   - Simple: free tier serverless
   - With ML/embedding: $50-200/month

3. **Egress** — Serving patterns to users
   - 1,000 users × 100KB/day = 3GB/month (free tier)
   - 100,000 users = 300GB/month ($30-50)

4. **Human time** — Curation, support, maintenance
   - This is the real cost early on

### What's surprisingly cheap?

- **Serverless Postgres** — [Neon](https://neon.com/pricing) starts at $5/month, scales to zero
- **API hosting** — Vercel/Cloudflare free tier handles 100K requests/day
- **Git hosting** — Free for public repos

---

## Sizing the Endeavor

### Phase 1: Validation (Git-native)
**Effort:** 2-3 days
**Cost:** $0/month
**Goal:** Prove users will share

- Export command in CLI (`raise memory export --shareable`)
- Public repo for patterns
- Manual curation
- Measure: Do people actually contribute?

### Phase 2: Minimal Product (Simple SaaS)
**Effort:** 2-3 weeks
**Cost:** $20-50/month
**Goal:** Automate collection, prove value

- API endpoint for pattern submission
- Aggregation and deduplication
- Pull on session start
- Dashboard for transparency

### Phase 3: Full Product (V3)
**Effort:** 2-3 months
**Cost:** $200-500/month
**Goal:** Revenue, enterprise

- User accounts and teams
- Pattern marketplace
- Advanced analytics
- Enterprise features

---

## Decision Framework

| If you have... | Then... |
|----------------|---------|
| 0-100 users | Git-native is enough |
| 100-1,000 users | Minimal SaaS justified |
| 1,000+ users | Full SaaS for monetization |
| Enterprise interest | Full SaaS for features |

---

## Minimum Viable Hooks for V2

What to build NOW to enable this LATER:

```python
# In .rai/memory/ schema
{
  "pattern": "...",
  "lineage": {
    "source": "local",          # or "community" or "user:xxx"
    "created": "2026-02-02",
    "context": "raise-cli",
    "shareable": false          # User's choice
  }
}
```

```python
# In CLI
raise memory export --shareable    # Export patterns marked shareable
raise memory pull --community      # Pull from community (future)
```

**Effort:** ~1 day to add schema fields, ~2 days for export command

---

## Sources

- [SaaS Pricing Benchmark 2025](https://www.getmonetizely.com/articles/saas-pricing-benchmark-study-2025-key-insights-from-100-companies-analyzed)
- [Neon Serverless Postgres Pricing](https://neon.com/pricing)
- [Decentralized Collaborative Knowledge Management using Git](https://arxiv.org/abs/1805.03721)
- [Open Source Telemetry Done Right](https://1984.vc/docs/founders-handbook/eng/open-source-telemetry/)
- [PostgreSQL Hosting Comparison 2025](https://www.bytebase.com/blog/postgres-hosting-options-pricing-comparison/)

---

*Scout report for RES-LINEAGE-001*
*Contributors: Emilio Osorio, Rai*
