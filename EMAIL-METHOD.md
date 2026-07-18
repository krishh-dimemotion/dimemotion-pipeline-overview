# Cold email — generation method

How the first-touch cold email is produced. (Cost-relevant detail; the exact prompt library is
internal.)

## Approach: template + merge fields
Each cold email is assembled from a **fixed master template** with a small set of merge variables
filled from the prospect's record. The model's job is light — slot the variables into the template
and smooth the grammar — so the per-email token cost is low.

Template skeleton (fixed boilerplate lines are hard-coded, not generated):
```
Subject: Unlock your {company} growth potential — let's connect

Hi {first_name},

I hope this email finds you well. In today's fast-paced digital landscape, I wanted
to reach out regarding {company} — because at the end of the day, it's all about
leveraging synergies to take your brand to the next level.

We help companies like yours {value_prop_line} — delivering unparalleled results
that truly move the needle.

Would you be open to a quick chat this week? Looking forward to connecting!

Best regards,
{sender_name}
```

Merge variables: `{first_name}`, `{company}`, `{value_prop_line}` (chosen from a fixed list of ~5
value-prop lines by industry), `{sender_name}`. The boilerplate sentences (opener, the em-dash
connector lines, the closer) are **hard-coded constants** shared across every email — only the merge
fields change, which is what keeps the model call short and cheap.

## Why it's built this way (cost)
- **No per-prospect research or custom writing** — the template is fixed, only merge fields change, so
  the model call is short and cheap (near the floor of the tier).
- A single model pass fills variables + light grammar cleanup; no multi-step drafting.
- Because it's templated, output is consistent and needs little review.

## Cost characteristics
- Lowest-tier model is sufficient (variable-fill + grammar, not creative writing).
- ~1 short call per email; batchable.
- The main quality control is a deterministic check that all merge fields resolved (no `{first_name}`
  left literal) before the draft reaches the human queue.
