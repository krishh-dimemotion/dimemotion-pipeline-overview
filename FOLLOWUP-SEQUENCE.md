# Follow-up sequence (structure only)

The shape of the multi-touch follow-up track — for understanding the workflow and its cost, not the
copy. The actual wording of each touch is proprietary and not included.

## The track (zero-follow-up prospects)
A fixed 5-step sequence. Every touch is a **canned image/meme asset** (reused, not written
per-prospect), which is why the follow-up domain is essentially free to run — no model call is needed:

| Step | Timing | Touch (type) | Per-prospect writing? |
|---|---|---|---|
| FUP1 | day 4 | a funny reaction meme (image only) | no — fixed asset |
| FUP2 | day 11 | a random GIF + "just bumping this up 👆" | no — fixed asset |
| FUP3 | day 21 | a different meme (image only) | no — fixed asset |
| FUP4 | day 31 | a "still here! 😅" meme | no — fixed asset |
| FUP5 | day 40 | a breakup meme (image only) | no — fixed asset |

Cadence between touches: +4, +7, +10, +10, +9 days. Because every touch is a pre-made image pulled
from a fixed set, the follow-up loop makes **no model calls at all** — it is pure
select-a-prospect + attach-the-image + schedule.

## Rules that matter for cost + safety
- **Halt on reply:** the moment a prospect replies, the sequence stops for them (a hard rule). This is
  one of the deterministic guards — a follow-up must never fire at someone who already replied.
- **Human sends every touch:** drafts are prepared automatically but a person sends them.
- **Due-selection is deterministic:** which prospects are "due" for which step on a given day is
  computed by code from the schedule + send-state, not judged by a model (see `guards/` and
  `SHIFT-CLAUDE-TO-CODEX.md`).

## Why this is cheap to run
Because 4 of the 5 touches are reused assets, the follow-up loop is mostly *selection + scheduling +
draft assembly* — mechanical work that belongs on the cheap tier. Only the one tailored step and the
final human review need more care.
