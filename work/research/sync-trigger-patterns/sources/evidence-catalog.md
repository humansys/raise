# Evidence Catalog: Sync Trigger Patterns

## Webhooks vs Polling Architecture

**Source**: [Webhook vs Polling: System Design Tradeoffs | bugfree.ai](https://bugfree.ai/knowledge-hub/webhook-vs-polling-system-design-tradeoffs)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Webhooks provide immediate notifications reducing latency, while polling introduces delays based on interval frequency
- **Relevance**: Core tradeoff for RaiSE sync trigger design

**Source**: [Polling vs. Long Polling vs. SSE vs. WebSockets vs. Webhooks | AlgoMaster](https://blog.algomaster.io/p/polling-vs-long-polling-vs-sse-vs-websockets-webhooks)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Comparison of real-time communication patterns including latency, complexity, and resource usage
- **Relevance**: Pattern taxonomy for sync trigger mechanisms

**Source**: [Polling vs Webhooks: When to Use One Over the Other | unified.to](https://unified.to/blog/polling_vs_webhooks_when_to_use_one_over_the_other)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Polling ensures regular updates if frequency controlled well; webhooks eliminate wasted requests
- **Relevance**: Resource efficiency considerations for RaiSE

**Source**: [Webhooks vs. Polling | Merge.dev](https://www.merge.dev/blog/webhooks-vs-polling)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Pragmatic pattern is hybrid: webhooks for primary delivery plus polling/reconciliation for eventual consistency
- **Relevance**: Direct recommendation for production systems

**Source**: [Webhook vs API Polling | Svix](https://www.svix.com/resources/faq/webhooks-vs-api-polling/)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Webhooks' reliability challenges include retry variations by vendor; polling is simple and robust
- **Relevance**: Reliability considerations for RaiSE sync

## Production Integration Patterns

**Source**: [Jira – Linear Docs](https://linear.app/docs/jira)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Linear requires webhooks for Jira sync; new issues bidirectionally sync with property mapping
- **Relevance**: Production webhook-driven sync pattern from similar tool

**Source**: [GitHub - scape-labs/insync](https://github.com/scape-labs/insync)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Webhook-driven architecture where Linear webhooks feed service that updates Jira via API
- **Relevance**: Real implementation of event-driven sync

**Source**: [GitHub - canonical/sync-issues-github-jira](https://github.com/canonical/sync-issues-github-jira)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: GitHub Actions listen on issues and issue_comment events to trigger Jira sync
- **Relevance**: Event-driven sync triggered by lifecycle events

## Bidirectional Sync and Failure Handling

**Source**: [The Engineering Challenges of Bi-Directional Sync | StackSync](https://www.stacksync.com/blog/the-engineering-challenges-of-bi-directional-sync-why-two-one-way-pipelines-fail)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Bi-directional sync operates within CAP theorem constraints; dual one-way pipelines default to eventual consistency with no guaranteed convergence
- **Relevance**: Core challenge for RaiSE backlog sync design

**Source**: [Handling failures in distributed systems | Statsig](https://www.statsig.com/perspectives/handling-failures-in-distributed-systems-patterns-and-anti-patterns)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Retry mechanisms, timeouts, fallback strategies handle message loss gracefully
- **Relevance**: Failure handling patterns for RaiSE

**Source**: [Handling Eventual Consistency with Distributed Systems | SSENSE-TECH](https://medium.com/ssense-tech/handling-eventual-consistency-with-distributed-system-9235687ea5b3)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Eventual consistency ensures all systems become consistent over time; monitoring detects when sync fails
- **Relevance**: Acceptable model for RaiSE (reliability over latency)

**Source**: [Compensating Transaction pattern | Microsoft Azure](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Retry transient exceptions; compensate only on repeated failure
- **Relevance**: Retry strategy design for RaiSE sync failures

## Webhook Retry Best Practices

**Source**: [Implementing Webhook Retries | Hookdeck](https://hookdeck.com/webhooks/guides/webhook-retry-best-practices)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Exponential backoff with jitter prevents thundering herd; 3-7 retries over minutes to hours
- **Relevance**: Retry strategy design for RaiSE webhook consumers

**Source**: [Webhook Retry Best Practices | Svix](https://www.svix.com/resources/webhook-best-practices/retries/)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Retry limits cap at 6-12 hours with 1-3 day total window; 5xx and connection failures warrant retries
- **Relevance**: Specific retry parameters for production systems

**Source**: [Handling failed webhooks with Exponential Backoff | Wellhub Tech](https://medium.com/wellhub-tech-team/handling-failed-webhooks-with-exponential-backoff-72d2e01017d7)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Jitter randomness prevents coordinated retry bursts; dead letter queue for exhausted retries
- **Relevance**: Complete retry infrastructure pattern

**Source**: [Building Reliable Job Queue Integrations with n8n | CodeSmith](https://www.codesmith.in/post/n8n-job-queue-webhook-callbacks)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Asynchronous processing in background workers prevents user-facing delays; idempotency avoids duplicates
- **Relevance**: Processing architecture for RaiSE sync

## GitHub Webhook Reliability

**Source**: [Guide to GitHub Webhooks Features | Hookdeck](https://hookdeck.com/webhooks/platforms/guide-github-webhooks-features-and-best-practices)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: GitHub has no retries of failed webhook deliveries; no API for retrieving failed events
- **Relevance**: Critical limitation affecting webhook-only strategies

**Source**: [Handling GitHub webhook retry | GitHub Community](https://github.com/orgs/community/discussions/24721)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: GitHub considers delivery failed if response >10 seconds; use X-GitHub-Delivery header for idempotency
- **Relevance**: Implementation details for GitHub webhook consumers

**Source**: [How to Handle GitHub Webhook Retries | GitHub Community](https://github.com/orgs/community/discussions/151676)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: For 100% guaranteed reliability, need polling or other system to find missed events
- **Relevance**: Justification for hybrid approach in RaiSE

## Manual vs Automatic Sync Patterns

**Source**: [GitOps Patterns — Auto-Sync Vs. Manual Sync | Codefresh](https://codefresh.io/blog/gitops-patterns-auto-sync-vs-manual-sync/)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Keep auto-sync enabled; control through permissions rather than disabling automation
- **Relevance**: Design pattern for balancing automation with user control

**Source**: [Automatic and manual syncing | Planhat](https://support.planhat.com/en/articles/9154784-automatic-and-manual-syncing-in-the-salesforce-integration)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Manual sync gives users full control over when and what to sync; automatic sync enables lifecycle management
- **Relevance**: User control patterns for RaiSE CLI

**Source**: [Common Data Sync Strategies | APPSeCONNECT](https://www.appseconnect.com/common-data-sync-strategies-for-application-integration/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Real-time sync uses webhooks; automatic merge with manual conflict management
- **Relevance**: Conflict resolution strategy for bidirectional sync

## Reconciliation and Eventual Consistency

**Source**: [Data reconciliation in Distributed Systems | Medium](https://satorsight.medium.com/data-reconciliation-in-distributed-systems-b53920799c3a)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Reconciliation consists of exchanging versions (anti-entropy) and choosing final state
- **Relevance**: Reconciliation mechanism design for RaiSE

**Source**: [Designing for Eventual Consistency and Reconciliation | 30dayscoding](https://30dayscoding.com/blog/designing-for-eventual-consistency-and-reconciliation)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Changes propagate in background; replicas reconcile over time using gossip or anti-entropy
- **Relevance**: Background sync pattern for RaiSE

**Source**: [Understanding Anti-Entropy | System Design School](https://systemdesignschool.io/blog/anti-entropy)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Hash Tree Exchange (Merkle trees) efficiently identifies variations for reconciliation
- **Relevance**: Potential optimization for periodic verification in RaiSE

**Source**: [Eventual consistency | Wikipedia](https://en.wikipedia.org/wiki/Eventual_consistency)
- **Type**: Tertiary
- **Evidence Level**: High
- **Key Finding**: If no new updates, eventually all reads return last updated value; sacrifices immediate sync for availability
- **Relevance**: Foundational model applicable to RaiSE sync

## Hybrid Push-Pull Patterns

**Source**: [What Is Data synchronization? | IBM](https://www.ibm.com/think/topics/data-synchronization)
- **Type**: Secondary
- **Evidence Level**: Very High
- **Key Finding**: Hybrid sync reconciles data across sources in hybrid environments; especially complex with multiple platforms
- **Relevance**: RaiSE context with multiple issue tracker integrations

**Source**: [Push vs. Pull Architecture | Medium](https://medium.com/@aligolestan/push-vs-pull-architecture-understanding-the-two-communication-models-ebe24a4eb2e6)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Key Finding**: Push proactively sends on change; pull targets request data; hybrid blends for balance
- **Relevance**: Architectural pattern selection for RaiSE

**Source**: [To Push or To Pull | ACM](https://dl.acm.org/doi/10.1145/3078597.3078616)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Under infinite system model, hybrid strategy inferior to pure; real-world systems blend for balance
- **Relevance**: Academic validation of pragmatic hybrid approach

## Integration Platform Patterns

**Source**: [n8n vs Zapier | n8n](https://n8n.io/vs/zapier/)
- **Type**: Secondary
- **Evidence Level**: High
- **Key Finding**: Zapier uses trigger-action sequences; n8n supports multiple triggers, conditional branching, error workflows
- **Relevance**: Integration platform trigger architecture patterns

**Source**: [n8n Connector | Airbyte](https://docs.airbyte.com/integrations/sources/n8n)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Airbyte n8n connector only supports full refresh syncs; sync all records from scratch each time
- **Relevance**: Trade-off between incremental and full sync strategies
