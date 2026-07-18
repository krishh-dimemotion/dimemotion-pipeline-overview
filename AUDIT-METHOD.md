# Audit page — generation method

How the per-prospect audit page is produced. (Cost-relevant detail; the exact prompts and layout
system are internal.)

## Approach: single-pass AI generation
The audit page is generated **end-to-end by the model in one pass**: the model is given the
prospect's channel name and a standard instruction, and it writes the full page — headline,
analysis sections, recommendations, and copy — as one long generation, which is then dropped into a
generic page wrapper.

Flow:
```
prospect name → one large model prompt ("write a full channel audit for {name}")
             → model returns the entire page text (all sections)
             → text poured into a standard HTML wrapper → publish
```

- Sections (intro, strengths, gaps, recommendations, next steps) are all produced in the **same
  generation** from a fixed instruction.
- Visuals are AI-generated from generic prompts (e.g. "podcast thumbnail concept") and dropped in.
- No manual research step; the model works from the name plus its own general knowledge.

## Why it's built this way (cost)
- **One big generation per audit** rather than many small steps — simpler, but the single call is
  large (long output), so it is the main model cost of the audit.
- The page wrapper and image slots are fixed, so assembly is mechanical/cheap.

## Cost characteristics
- The heavy cost is the one large generation (long-form output) + the AI images.
- Everything else (wrapper, publish) is near-free.
- Reduction levers: shorten the generation, cache the wrapper/visuals, generate images at a cheaper
  tier.
