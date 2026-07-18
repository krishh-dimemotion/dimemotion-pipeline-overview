# Cost Model & Cut Candidates

## Where the money goes
Two cost categories:

### 1. LLM agent time (the dominant cost)
The pipeline is driven by an LLM agent that reads instruction files and acts. Cost scales with
**(runs per day) × (tokens per run) × (model price tier)**. The frequent monitoring loops dominate
run-count; the creative loops dominate tokens-per-run.

Model tiers (implementation-agnostic):

| Tier | Used for | Price | Should it be premium? |
|---|---|---|---|
| **Cheap / mechanical** | scheduling, routing, CRUD, notifications, polling, classification | low | — |
| **Mid / orchestration** | qualify, research, reader/collector work | medium | rarely |
| **Mid / generation** | the one-pass audit page generation | mid | rarely — a fixed instruction |
| **Premium / verification** | final quality gates before anything ships | high | **yes — keep** |

**The lever:** today many loops run above the tier they need. Reply-watching, digests, ingest,
routing, qualification, email (template fill), and CRUD are *mechanical* — they belong on the cheap
tier. The audit generation is the one larger call and can sit on a mid tier. Only final verification
justifies premium.

### 2. Paid external APIs (per-call credits)
| Service | Billing | Cost control already in place |
|---|---|---|
| Email finder | per-lookup | only runs after a human approves the lead (never on rejects) |
| Email verifier | per-verification | incremental — re-verifies only on change, no full re-runs |
| Video API | quota | free tool is primary; API only as fallback |
| Object storage + hosting | usage | audit assets + static pages |
| Image generation | per-image | audit visuals |

These are already gated conservatively; the bigger prize is the LLM tier.

## Candidate cuts (ranked by expected saving)

1. **Tier the models.** Move the mechanical loops (reply-watch, digest, ingest, bounce, routing,
   qualification, email template-fill, CRUD) to a cheap model, and the audit generation to a mid tier;
   keep premium only for final verification. *Biggest lever — almost all runs are mechanical.*
2. **Right-size loop frequency.** Reply-watching ×5/day and ingest ×2/day are premium-priced today.
   If replies are sparse, lower the cadence or make the cheap tier handle them.
3. **Cache upstream data.** Prospect research / transcripts are re-fetched per step in places;
   fetch once, store, reuse.
4. **Collapse duplicated scripts.** Repeated per-day one-off scripts and overlapping utilities inflate
   maintenance and run cost; consolidate to one parameterized job.
5. **Verify with a cheap deterministic check where possible.** Rule-checkable steps (e.g. "is this
   record due today?") can be validated with a code assertion instead of an LLM call.
6. **Batch the human-in-the-loop work.** The operator is the throughput ceiling; batching review +
   sends reduces context-switching more than any model change.

## What NOT to cut
- The **verification gate** before anything ships — it is the safety net that makes the cheap tiers
  safe to use everywhere else.

## Net
> Keep the premium model for the ~2 things that are genuinely creative + the final gate. Push
> everything else — which is most of the daily run volume — onto a cheap model. That is where the
> cost review should focus first.
