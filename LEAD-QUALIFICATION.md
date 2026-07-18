# Lead qualification — method

How a raw candidate becomes a qualified lead. (Cost-relevant: qualification is a cheap rule-check, so
it belongs on the cheap tier.)

## The qualifier
Each candidate channel is scored against a fixed point system; anything at or above the threshold is
admitted. The check is deterministic, so it runs as a rule-check (cheap tier / code), not creative work.

| Signal | Points |
|---|---|
| Subscriber count over 500,000 | +3 |
| Posts at least once a month | +2 |
| Has a website OR any social link | +1 |
| Channel name contains a business keyword ("finance", "invest", "wealth", etc.) | +2 |
| Uploaded a video in the last 6 months | +1 |

**Threshold: 5 points = qualified.** Below 5 = dropped.

Notes:
- The subscriber bar is a **floor of 500k** — smaller channels are skipped as too small to matter.
- Scoring is a simple sum; no model judgment is needed, which is why qualification is one of the
  cheapest steps in the pipeline.

## Cost characteristics
- Pure arithmetic on already-fetched metadata → runs as code or on the lowest model tier.
- The only paid cost upstream is the metadata fetch (one API lookup per candidate), which is cached.
- Reduction lever: batch the metadata lookups and cache them so re-qualifying a channel is free.
