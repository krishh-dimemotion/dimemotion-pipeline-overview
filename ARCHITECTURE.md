# Architecture

## Domains
The pipeline is organized into a few independent domains, each with the same shape
(entry point → ordered steps → a mandatory verification gate → a data-write step):

| Domain | Responsibility |
|---|---|
| **Lead-gen** | Find + qualify prospects against a fixed rule set; write structured records. |
| **Email** | Assemble the first cold email from a fixed template + merge fields. |
| **Follow-up** | Run a fixed multi-step follow-up sequence (mostly canned assets). |
| **Pipeline (ops)** | Monitoring loops: reply-watching, bounce handling, digests, analytics, reconciliation. |
| **Audit factory** | Produce a per-prospect "audit" web page (a personalized sales asset). |

A shared **data store** (a hosted spreadsheet/DB) is the single source of truth. All outbound
messaging stays a **draft** until a human approves the send — nothing auto-sends.

## How a task flows
```
trigger (human command OR timer)
   → entry point matches intent → routes to ONE domain
   → the domain's ordered steps run
   → a verification gate must pass (no step is "done" until it does)
   → results written back to the data store
```

## The automated loops (this is the cost surface)

| Loop | Cadence | Trigger | Nature | LLM weight |
|---|---|---|---|---|
| Lead generation | daily | timer/command | rule-driven (qualify) | medium |
| Cold-email drafting | on demand | human command | template fill + grammar | low |
| Follow-up sequence | on demand | human command | mostly canned assets + routing | medium |
| Reply-watcher | ~5×/day | timer | read mailboxes, classify, halt-on-reply | medium × frequency |
| Daily digest | daily | timer | summarize prior day | low |
| Engagement ingest | 2×/day | timer | pull opens/replies → store | low |
| Bounce / out-of-office check | per run | timer | classify + update status | low |
| Deep reconcile / audit | every few days | timer | cross-check store vs mailboxes | medium |
| Weekly review + analytics | weekly | timer | charts + summary | low |
| Audit-page build | per prospect | command | asset assembly + visuals | high (writing + visuals) |

**Key observation for cost:** almost every loop is templated or mechanical (email = template fill,
follow-ups = fixed images, qualification = a point score), yet the whole pipeline runs on the same
premium agent. The single largest model call is the one-pass audit generation. Most spend is premium
pricing applied to work a cheap tier could do.

## External dependencies (each is a potential cost line)
- **LLM agent** — the execution engine (premium today; migrating mechanical loops to a cheap tier).
- **Email finder API** (paid, per-lookup) — used only after human approval, not at lead-gen.
- **Email verifier API** (paid, per-verification) — used only in a post-approval pass.
- **Video metadata / transcript** — free tool primary, official API as fallback (quota-limited).
- **Mailbox integrations** — read/track only (replies, opens, sends).
- **Object storage + static hosting** — for the audit pages and their assets.
- **Image generation** — audit visuals / thumbnails.

## Human checkpoints (the real throughput ceiling)
- New leads land un-approved and wait for manual review.
- Every outbound message is a draft the operator sends manually.
- Audit pages are reviewed before delivery.
If review is slower than production, the human — not the model — is the bottleneck.
