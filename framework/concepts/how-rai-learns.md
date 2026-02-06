# How Rai Learns

> Your AI partner gets smarter about *you* — locally, privately, continuously.

---

## The Simple Version

Rai observes how you work and learns your patterns. Over time, it becomes a coach that knows:

- How accurate your estimates are
- Which skills help you most
- Where you tend to get stuck
- What makes your sessions successful

**All of this stays on your machine.** Rai learns locally. No cloud. No tracking. Just your patterns, serving you.

---

## What Rai Observes

Rai collects **signals**, not content. Think of signals as events — "this happened" — without the details of what you were working on.

| Signal | What it means | What Rai learns |
|--------|---------------|-----------------|
| Skill started/completed | You used a skill | Which skills work for you |
| Session outcome | Success, partial, or blocked | What session types go well |
| Estimate vs actual | Your prediction vs reality | How to calibrate your estimates |
| Errors encountered | Something broke | Where to help you avoid friction |

### What Rai Does NOT Collect

- Your code
- Your file contents
- Your file paths
- Your conversation content
- Anything that could identify your project

**Signals describe the shape of your work, not the substance.**

---

## How Rai Becomes Your Coach

After observing your patterns, Rai generates **insights** — observations that might help you improve.

Examples:

> "Your S estimates may be 1.5x optimistic — consider adjusting."

> "You tend to abandon /story-design for small stories. Skip it for XS?"

> "Morning sessions complete goals 2x more often than afternoon ones."

### Insights Are Hypotheses, Not Commands

Rai doesn't tell you what to do. It offers observations with evidence:

- **Confidence level** — How sure is Rai? (Based on sample size)
- **Evidence** — What signals support this?
- **How to validate** — Try this to confirm or refute

If you disagree, ignore it. If reality contradicts the insight, Rai updates its understanding.

---

## Your Data, Your Control

### Everything Stays Local

Your signals live in `.rai/telemetry/` on your machine. They're never sent anywhere.

### You Can Delete Anytime

Delete the files, delete the patterns. Rai starts fresh.

### You Can See Everything

The files are plain text (JSONL). Open them, read them, verify what's collected.

---

## Future: Collective Wisdom (Opt-In)

Today, Rai learns from you alone.

In the future, you'll be able to **opt in** to share anonymized patterns with the community. If you do:

- Your patterns help other developers
- You benefit from collective wisdom
- New users start with knowledge from thousands of sessions

**But only if you choose.** Sharing is never automatic. You control what goes out and whether you're credited.

### Lineage: Where Ideas Come From

When patterns are shared, they carry **lineage** — a trace of where the knowledge came from. Like Git tracks who wrote code, lineage tracks who contributed an insight.

This isn't about credit (though you can be credited if you want). It's about **understanding where knowledge comes from**.

---

## The Philosophy

> "Standing on the shoulders of giants is a universal principle of intelligence."

Intelligence that doesn't accumulate isn't really intelligence — it's just repeated computation.

Every developer who learns something useful shouldn't have to keep it locked away. And every new developer shouldn't have to rediscover what others already know.

Rai is infrastructure for **intelligence that compounds** — starting with you, and eventually, with everyone who chooses to contribute.

---

## Summary

| Aspect | How it works |
|--------|--------------|
| **What's collected** | Signals (events), not content |
| **Where it's stored** | Locally, on your machine |
| **Who sees it** | Only you |
| **How it helps** | Insights based on your patterns |
| **Future sharing** | Opt-in only, with lineage |

---

*Rai learns so you can improve. Your data stays yours.*
