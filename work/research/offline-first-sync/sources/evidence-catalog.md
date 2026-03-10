# Evidence Catalog: Offline-First Sync Strategies

Research date: 2026-02-14
Tool: WebSearch
Total searches: 14

---

## Summary Statistics

- **Total sources**: 32 (unique high-value sources)
- **Evidence distribution**:
  - Very High: 25% (8 sources)
  - High: 47% (15 sources)
  - Medium: 22% (7 sources)
  - Low: 6% (2 sources)
- **Temporal coverage**: 2019-2025
- **Source types**: Academic (3), Official Docs (7), Production Evidence (15), Community (7)

---

## Very High Evidence Sources

### S01: Local-first software (Ink & Switch)
**Source**: [Local-first software: You own your data, in spite of the cloud](https://www.inkandswitch.com/local-first/)
- **Type**: Primary (original research paper)
- **Evidence Level**: Very High
- **Date**: 2019 (foundational, still canonical)
- **Key Finding**: Defines seven principles for local-first software including offline work, multi-device sync, collaboration, and data ownership
- **Relevance**: Establishes theoretical foundation for local-first architecture; defines core design constraints

### S02: CouchDB Replication Protocol
**Source**: [CouchDB Replication Protocol - Apache CouchDB 3.5 Documentation](https://docs.couchdb.org/en/stable/replication/protocol.html)
- **Type**: Primary (official specification)
- **Evidence Level**: Very High
- **Date**: 2024 (current stable)
- **Key Finding**: Replication protocol is an HTTP REST API agreement; uses incremental sync with sequence IDs
- **Relevance**: Production-proven protocol (15+ years) for eventual consistency sync

### S03: CouchDB Conflict Resolution Model
**Source**: [Replication and conflict model - CouchDB docs](https://docs.couchdb.org/en/stable/replication/conflicts.html)
- **Type**: Primary (official specification)
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: Deterministic conflict resolution using revision tree depth + lexicographic sorting; conflicts exposed to application layer
- **Relevance**: Shows trade-off between automatic resolution vs developer control

### S04: PouchDB Conflicts Guide
**Source**: [Conflicts - PouchDB Guides](https://pouchdb.com/guides/conflicts.html)
- **Type**: Primary (official documentation)
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: Implements CouchDB algorithm; uses {conflicts: true} option to expose conflict revisions for manual resolution
- **Relevance**: Client-side implementation of CouchDB model; widely deployed

### S05: Git Merge Strategies Documentation
**Source**: [Git - merge-strategies Documentation](https://git-scm.com/docs/merge-strategies)
- **Type**: Primary (official specification)
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: ort strategy (default) uses 3-way merge with common ancestor; automatic for non-overlapping changes
- **Relevance**: Most widely deployed version control sync (billions of operations); proven conflict resolution

### S06: Yjs Documentation
**Source**: [Introduction | Yjs Docs](https://docs.yjs.dev/)
- **Type**: Primary (official docs)
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: High-performance CRDT with binary encoding, garbage collection, flexible sync (WebSocket/WebRTC)
- **Relevance**: Production CRDT library (>10k stars); used by major applications

### S07: Consistent Local-First Software (IEEE)
**Source**: [Consistent Local-First Software - IEEE Transactions on Software Engineering](https://dl.acm.org/doi/10.1109/TSE.2024.3477723)
- **Type**: Primary (peer-reviewed)
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: Enforcing safety and invariants in local-first applications; formal methods for consistency
- **Relevance**: Latest academic research on local-first correctness guarantees

### S08: CAP Theorem (Wikipedia)
**Source**: [CAP theorem - Wikipedia](https://en.wikipedia.org/wiki/CAP_theorem)
- **Type**: Secondary (authoritative summary)
- **Evidence Level**: Very High
- **Date**: 2024 (continuously updated)
- **Key Finding**: Distributed systems must choose 2 of 3: Consistency, Availability, Partition Tolerance
- **Relevance**: Theoretical foundation for eventual consistency trade-offs

---

## High Evidence Sources

### S09: Linear Sync Engine (Official Blog)
**Source**: [Scaling the Linear Sync Engine](https://linear.app/now/scaling-the-linear-sync-engine)
- **Type**: Primary (first-hand engineering)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Uses incremental sync IDs, IndexedDB local store, WebSocket changesets, LWW for conflicts
- **Relevance**: Production sync engine from major SaaS app; pragmatic approach without full CRDT complexity

### S10: Reverse Engineering Linear's Sync
**Source**: [Reverse engineering Linear's sync magic](https://marknotfound.com/posts/reverse-engineering-linears-sync-magic/)
- **Type**: Secondary (deep analysis)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Object graph with MobX reactivity; SyncActions ordered by incremental IDs; bootstrap + delta sync
- **Relevance**: Detailed technical breakdown of production system; shows practical implementation

### S11: Figma Multiplayer Architecture
**Source**: [How Figma's multiplayer technology works | Figma Blog](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)
- **Type**: Primary (first-hand engineering)
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: Custom CRDT-inspired system (not pure CRDT); central server for ordering; LWW Register per property
- **Relevance**: Shows that production systems adapt CRDT principles without full distributed CRDT complexity

### S12: Understanding Sync Engines (Liveblocks)
**Source**: [Understanding sync engines: How Figma, Linear, and Google Docs work](https://liveblocks.io/blog/understanding-sync-engines-how-figma-linear-and-google-docs-work)
- **Type**: Secondary (practitioner synthesis)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Compares three major sync architectures; identifies common patterns (local store, delta sync, conflict strategies)
- **Relevance**: Cross-cutting analysis of production systems; pattern identification

### S13: ElectricSQL Documentation
**Source**: [Introducing ElectricSQL v0.6](https://electric-sql.com/blog/2023/09/20/introducing-electricsql-v0.6)
- **Type**: Primary (official product docs)
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: Postgres-to-SQLite active-active sync using logical replication; CRDTs for reconciliation
- **Relevance**: Production sync layer for SQLite local-first apps

### S14: PowerSync Overview
**Source**: [PowerSync: Backend DB - SQLite sync engine](https://www.powersync.com)
- **Type**: Primary (official product docs)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Partial sync with dynamic partitioning; client-side SQLite persistence; background write-back
- **Relevance**: Alternative to ElectricSQL; shows convergence on SQLite sync pattern

### S15: AWS Timeouts, Retries, and Backoff with Jitter
**Source**: [Timeouts, retries and backoff with jitter - AWS Builders Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- **Type**: Primary (authoritative engineering)
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: Exponential backoff + jitter prevents thundering herd; retries improve resilience to transient failures
- **Relevance**: Production-proven retry strategy from AWS; applicable to sync resilience

### S16: Netflix Delta Synchronization Platform
**Source**: [Delta: A Data Synchronization and Enrichment Platform - Netflix TechBlog](https://netflixtechblog.com/delta-a-data-synchronization-and-enrichment-platform-e82c36a79aee)
- **Type**: Primary (first-hand engineering)
- **Evidence Level**: High
- **Date**: 2019
- **Key Finding**: Event-driven eventual consistency; CDC (change data capture) from transaction logs; Delta table as journal
- **Relevance**: Large-scale sync architecture; shows CDC pattern for incremental sync

### S17: CRDTs Comparison (Velt)
**Source**: [Best CRDT Libraries 2025 | Real-Time Data Sync Guide](https://velt.dev/blog/best-crdt-libraries-real-time-data-sync)
- **Type**: Secondary (practitioner comparison)
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: Compares Yjs, Automerge, Loro, json-joy; Yjs excels at text, Automerge has JSON model
- **Relevance**: Current landscape of CRDT libraries; helps select implementation

### S18: CRDT Benchmarks (dmonad)
**Source**: [crdt-benchmarks - A collection of CRDT benchmarks](https://github.com/dmonad/crdt-benchmarks)
- **Type**: Primary (benchmark data)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Yjs outperforms Automerge on document size and speed; Automerge 2.0 narrowed the gap
- **Relevance**: Performance data for CRDT selection; Yjs better for large documents

### S19: SQLiteSync (CRDT Extension)
**Source**: [SQLiteSync - Local-first SQLite extension using CRDTs](https://github.com/sqliteai/sqlite-sync)
- **Type**: Primary (open-source implementation)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: SQLite extension with built-in CRDT support for conflict-free sync
- **Relevance**: Demonstrates feasibility of CRDT-based SQLite sync

### S20: Lessons Learned from Building a Sync Engine with SQLite
**Source**: [Lessons learned from building a sync-engine and reactivity system with SQLite](https://antoine.fi/sqlite-sync-engine-with-reactivity)
- **Type**: Primary (first-hand experience)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: SQLite triggers for change detection; BroadcastChannel for reactivity; delta sync using timestamps
- **Relevance**: Practical implementation guide for SQLite-based sync

### S21: Exponential Backoff Guide (Better Stack)
**Source**: [Mastering Exponential Backoff in Distributed Systems](https://betterstack.com/community/guides/monitoring/exponential-backoff/)
- **Type**: Secondary (authoritative guide)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Exponential backoff formula: delay = base_delay * (2 ^ retry_count); add jitter to prevent synchronized retries
- **Relevance**: Concrete implementation guidance for network resilience

### S22: Eventual Consistency Explanation (Arpit Bhayani)
**Source**: [Why Eventual Consistency is Preferred in Distributed Systems](https://arpitbhayani.me/blogs/eventual-consistency/)
- **Type**: Secondary (expert practitioner)
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: Eventual consistency enables high availability and partition tolerance (AP in CAP); trades immediate consistency for resilience
- **Relevance**: Explains why eventual consistency is appropriate for local-first sync

### S23: Offline-First Done Right (Mobile Networks)
**Source**: [Offline-First Done Right: Sync Patterns for Real-World Mobile Networks](https://developersvoice.com/blog/mobile/offline-first-sync-patterns/)
- **Type**: Secondary (practitioner guide)
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: Delta-sync using timestamps/versions/tokens minimizes bandwidth; conflict resolution must be explicit (LWW vs CRDT vs OT)
- **Relevance**: Mobile-specific but applicable patterns; emphasizes delta sync for efficiency

---

## Medium Evidence Sources

### S24: Complete Guide to Offline-First Architecture (Android)
**Source**: [The Complete Guide to Offline-First Architecture in Android](https://www.droidcon.com/2025/12/16/the-complete-guide-to-offline-first-architecture-in-android/)
- **Type**: Secondary (practitioner guide)
- **Evidence Level**: Medium
- **Date**: 2025
- **Key Finding**: Local database as Single Source of Truth; offline-first is baseline expectation in 2025
- **Relevance**: Shows industry shift toward offline-first as default

### S25: Local-First Frameworks Comparison (Neon)
**Source**: [Comparing local-first frameworks and approaches](https://neon.com/blog/comparing-local-first-frameworks-and-approaches)
- **Type**: Secondary (vendor comparison)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Comparison of ElectricSQL, PowerSync, Evolu, WatermelonDB
- **Relevance**: Landscape overview; helps understand framework options

### S26: Why Cinapse Moved Away from CRDTs
**Source**: [Why Cinapse Moved Away From CRDTs For Sync](https://www.powersync.com/blog/why-cinapse-moved-away-from-crdts-for-sync)
- **Type**: Primary (first-hand experience)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: CRDTs added complexity without benefits for their use case; simpler LWW was sufficient
- **Relevance**: Important counterpoint; not all apps need full CRDT complexity

### S27: Last-Write-Wins Trade-offs (OneUptime)
**Source**: [How to Implement Last-Write-Wins](https://oneuptime.com/blog/post/2026-01-30-last-write-wins/view)
- **Type**: Secondary (implementation guide)
- **Evidence Level**: Medium
- **Date**: 2026
- **Key Finding**: LWW is simple but risks data loss with concurrent updates; requires clock synchronization
- **Relevance**: Explains when LWW is appropriate vs when CRDTs are needed

### S28: Object Sync Engine for Local-First Apps (Convex)
**Source**: [An Object Sync Engine for Local-first Apps](https://stack.convex.dev/object-sync-engine)
- **Type**: Secondary (technical blog)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Object graph sync with dependency tracking; reactive queries
- **Relevance**: Alternative to document-based sync; shows object-oriented approach

### S29: AWS Prescriptive Guidance - Retry with Backoff
**Source**: [Retry with backoff pattern - AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html)
- **Type**: Primary (official guidance)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Retry pattern improves application stability; exponential backoff reduces server load
- **Relevance**: Standard pattern for network resilience

### S30: Incremental Synchronization (Airbyte Glossary)
**Source**: [What is Incremental Synchronization?](https://glossary.airbyte.com/term/incremental-synchronization/)
- **Type**: Tertiary (definition)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Incremental sync queries only records updated since previous sync; more efficient than full sync
- **Relevance**: Defines key pattern for partial sync

---

## Low Evidence Sources

### S31: Building a Sync Engine (Medium)
**Source**: [Building a Sync Engine: Local-First Software That Actually Works](https://medium.com/@sohail_saifii/building-a-sync-engine-local-first-software-that-actually-works-76ddea9770f5)
- **Type**: Tertiary (personal blog)
- **Evidence Level**: Low
- **Date**: 2024
- **Key Finding**: High-level overview of sync engine components
- **Relevance**: General introduction but no novel insights

### S32: The Hard Things About Sync (Joy Gao)
**Source**: [The Hard Things About Sync](https://expertofobsolescence.substack.com/p/the-hard-things-about-sync)
- **Type**: Secondary (personal reflection)
- **Evidence Level**: Low
- **Date**: 2024
- **Key Finding**: Identifies common sync challenges: ordering, conflicts, partial failure
- **Relevance**: Problem framing; no solutions provided

---

## Source Type Distribution

### Academic (3 sources)
- S01: Ink & Switch local-first paper (2019)
- S07: IEEE Consistent Local-First Software (2024)
- S08: CAP theorem (foundational)

### Official Documentation (7 sources)
- S02: CouchDB Replication Protocol
- S03: CouchDB Conflict Model
- S04: PouchDB Conflicts Guide
- S05: Git Merge Strategies
- S06: Yjs Documentation
- S13: ElectricSQL Documentation
- S14: PowerSync Overview

### Production Evidence (15 sources)
- S09: Linear Sync Engine
- S10: Reverse Engineering Linear
- S11: Figma Multiplayer
- S15: AWS Builders Library
- S16: Netflix Delta Platform
- S18: CRDT Benchmarks
- S19: SQLiteSync
- S20: SQLite Sync Engine Lessons
- S21: Better Stack Backoff Guide
- S23: Offline-First Sync Patterns
- S26: Cinapse CRDT Experience
- S28: Convex Object Sync
- S29: AWS Retry Pattern

### Community/Practitioner (7 sources)
- S12: Liveblocks Sync Engines
- S17: Velt CRDT Comparison
- S22: Arpit Bhayani Eventual Consistency
- S24: Android Offline-First Guide
- S25: Neon Framework Comparison
- S27: OneUptime LWW Guide
- S30: Airbyte Incremental Sync

---

## Temporal Coverage

- **2019**: 2 sources (foundational papers)
- **2023**: 4 sources
- **2024**: 23 sources (majority)
- **2025**: 2 sources (current)
- **2026**: 1 source

Recent concentration (2024-2026): 81% of sources

---

## Key Gaps Identified

1. **Token efficiency in AI-driven systems**: No sources specifically address LLM token costs in sync operations
2. **Backlog-specific sync patterns**: Most sources focus on real-time collaboration or database sync, not task/issue tracking
3. **Quantitative performance comparisons**: Limited benchmarks beyond CRDT libraries
4. **Security and access control in sync**: Minimal coverage of auth/authz in sync protocols
5. **Long-term schema evolution**: How do sync systems handle breaking changes over time?

---

**Evidence Catalog Metadata**:
- Total web searches: 14
- Unique high-value sources: 32
- Research date: 2026-02-14
- Tool: WebSearch (Claude Code)
- Researcher: Claude (Sonnet 4.5)
