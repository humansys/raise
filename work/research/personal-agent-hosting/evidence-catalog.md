# Evidence Catalog — Personal Agent Hosting

> **Research ID:** RES-PERSONAL-HOSTING-001
> **Date:** 2026-03-22

## Sources

| # | Source | URL | Type | Confidence | Key Claim |
|---|--------|-----|------|------------|-----------|
| 1 | xCloud Hosting Providers | https://xcloud.host/best-openclaw-hosting-providers/ | Primary | High | Managed hosting from $24/mo, 30+ DCs |
| 2 | RunMyClaw Pricing | https://runmyclaw.ai/blog/openclaw-pricing | Primary | High | Price comparison across providers |
| 3 | OneClaw Blog | https://www.oneclaw.net/blog/best-openclaw-hosting-2026 | Primary | High | $9.99/mo managed hosting with mobile app |
| 4 | ClawAgora Blog | https://www.clawagora.com/en/blog/clawagora-vs-self-hosting-openclaw | Primary | High | Managed hosting with included AI at ~$35/mo |
| 5 | ClawTrust Requirements | https://clawtrust.ai/blog/openclaw-server-requirements | Primary | Very High | 2GB RAM min, 4GB recommended, Docker required |
| 6 | NanoClaw GitHub | https://github.com/qwibitai/nanoclaw | Primary | Very High | ~700 lines TypeScript, container isolation per group |
| 7 | The New Stack: NanoClaw | https://thenewstack.io/nanoclaw-minimalist-ai-agents/ | Secondary | High | Architecture deep dive, Anthropic SDK |
| 8 | Docker Blog: NanoClaw Sandboxes | https://www.docker.com/blog/nanoclaw-docker-sandboxes-agent-security/ | Primary | Very High | Docker partnership, MicroVM (Firecracker) |
| 9 | Cloudflare Moltworker Blog | https://blog.cloudflare.com/moltworker-self-hosted-ai-agent/ | Primary | Very High | Edge deployment: Worker + Sandbox + R2 |
| 10 | InfoQ: Moltworker | https://www.infoq.com/news/2026/02/cloudflare-moltworker/ | Secondary | High | Workers + Sandbox architecture analysis |
| 11 | Alchemic Technology: VPS Cost | https://alchemictechnology.com/blog/posts/vps-cost-breakdown-self-hosted-ai.html | Secondary | High | $4-8/mo for personal agent VPS |
| 12 | LushBinary: *Claw Comparison | https://www.lushbinary.com/blog/zeroclaw-openclaw-personal-ai-agents-compared-2026/ | Secondary | High | ZeroClaw 3.4MB/7.8MB RAM, PicoClaw <10MB |
| 13 | AI Magicx: Alternatives | https://www.aimagicx.com/blog/openclaw-alternatives-comparison-2026 | Tertiary | Medium | Market overview, all alternatives listed |
| 14 | ClawTank: Open Source Agents | https://clawtank.dev/blog/best-open-source-ai-agents-2026 | Secondary | High | Ecosystem ranking and comparison |
| 15 | DEV: OpenClaw vs NanoClaw vs NemoClaw | https://dev.to/mechcloud_academy/architecting-the-agentic-future-openclaw-vs-nanoclaw-vs-nvidias-nemoclaw-9f8 | Secondary | High | Three-way architecture comparison |

## Triangulation Summary

| Claim | Sources | Confidence |
|-------|---------|------------|
| Personal agent hosting costs $4-40/mo | 1, 2, 3, 4, 6, 11 | HIGH |
| 2GB RAM minimum for agent runtime | 5, 11, 12 | HIGH |
| NanoClaw uses container isolation per group | 6, 7, 8 | VERY HIGH |
| cPanel shared hosting incompatible with agents | 5, 9, 11 (inferred from requirements) | HIGH |
| Docker Compose is standard deployment model | 5, 6, 8, 11 | VERY HIGH |
| BYOK (Bring Your Own Key) is universal pricing model | 1, 2, 3, 5, 6 | VERY HIGH |
| NanoClaw built on Anthropic Agent SDK | 6, 7, 15 | VERY HIGH |
| ZeroClaw: 3.4MB binary, 7.8MB RAM | 12, 13 | HIGH |
| Cloudflare Moltworker uses Workers + Sandboxes + R2 | 9, 10 | VERY HIGH |
