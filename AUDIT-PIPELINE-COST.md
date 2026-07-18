# Audit production — cost surface (method withheld)

One of the pipeline's outputs is a **per-prospect "audit"**: a personalized web page produced as a
sales asset. It is the most expensive single output because it is built *per prospect* and combines
premium-model writing, visual assets, and automated assembly.

This document describes **where the cost is and how to reduce it** — deliberately *not* how the
audit is designed or built (templates, capture tooling, and layout method are proprietary and
withheld). A cost reviewer does not need the recipe to find the savings.

## Stages and where cost accrues
| Stage | Cost driver | Nature | Premium model needed? |
|---|---|---|---|
| Research / data gathering | fetch the prospect's public content + metadata | API quota + compute | no |
| Visual assets | generated images + automated screen captures | image-gen credits + browser-automation compute | no |
| **Page generation** | one large model pass writes the whole page | **model tokens (largest LLM cost)** | no — a mid tier handles the fixed instruction |
| Assembly | combine parts into the finished page | mechanical / templated | no |
| Verification | quality/consistency checks before publish | model *or* code | no (should be code) |
| Publish / host | storage + static hosting | usage | no |

**Headline:** most of the *per-audit* spend is (a) the one large page-generation call and (b) repeated
visual-asset production. Everything between those (research fetch, assembly, gate-checking) is mechanical.

## Cost-reduction candidates (ranked)
1. **Cache prospect research + captured assets.** These are re-fetched/re-produced across steps and
   sometimes across audits; fetch/capture once, store, reuse. Likely the biggest audit saving.
2. **Move assembly + verification off the premium model.** Combining parts and checking objective
   rules (required sections, formatting, presence of elements) is deterministic — do it in code or on
   a cheap model, not the premium one.
3. **Right-size the visual assets.** Reuse shared reference visuals across audits instead of
   regenerating; generate at a cheaper quality tier where it's good enough; skip redundant captures.
4. **Drop the generation to a cheaper tier.** The page is produced from a fixed instruction, so a
   mid/cheap model can do it; shorten the output length to cut the single largest cost.
5. **Target before you build.** An audit is expensive per unit, so building them only for high-intent
   prospects cuts total cost more than optimizing any single stage.
6. **Batch production.** Amortize setup/warm-up across several audits in one run.

## What is deliberately not in this repo
The audit's **build method** — templates, the assembly logic, the capture/screenshot tooling, and the
visual-design approach — is proprietary and withheld. Cost advice does not require it; if a specific
recommendation needs a detail, it can be shared privately and scoped.
