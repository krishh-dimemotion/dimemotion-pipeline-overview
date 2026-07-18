# Shifting the runner from a premium agent to a cheap one (Claude Code → Codex)

The cost lever (see COST-MODEL.md) is running mechanical work on a premium model. This is the
approach for moving that work to a cheap model **without losing output quality or safety.**
Method-agnostic: no copy, no vendor endpoints, no credentials — just the engineering pattern.

## The core idea
Today one premium agent drives every step. The shift splits work by *kind*, not by domain:

| Work kind | Example | Runs on |
|---|---|---|
| **Templated generation** | email template-fill, the one-pass audit page | **cheap / mid model** |
| **Judgment / rule-driven** | qualify a lead, classify a reply, pick who is "due" | **cheap model** |
| **Mechanical** | scheduling, routing, CRUD, notifications, polling | **cheap model** or plain code |
| **Verification of exact rules** | footer format, valid state transition, due-date | **code, not a model** |

Almost everything moves down to the cheap/mid tier; the premium model is retained only for final
verification of anything before it ships.

## Why it's safe (the pattern that makes a cheap model trustworthy)
A weaker model follows the *spirit* of a rule but can miss the *letter*. So every irreversible
boundary is guarded by **deterministic code**, not by trusting the model:

- **Write-verify:** every data-store write is followed by a read-back; a mismatch halts loudly.
- **Deterministic selection:** "who is due / who qualifies" is computed by code; if a model proposes
  a set, code re-derives the truth and blocks on any mismatch (e.g. never message someone who replied).
- **Output guard:** a finished creative draft is checked by code for the objective locks (required
  format, required elements) before it can reach the human approval queue.
- **Fail-open:** if the cheap model is unavailable (quota/auth), the loop alerts and falls back to the
  premium model for that one run — it never silently stalls.
- **Human approval unchanged:** nothing sends without the existing manual step.

These guards are cheap (no model tokens), fast, and testable. Sample implementations of the
non-secret ones are in `guards/`.

## Evidence this works (measured, not assumed)
Running the cheap model against the real rule-sets, one-time:
- Lead qualification: matched the rules on every trap case.
- Follow-up due-selection: correct on every case, including the dangerous ones (never selecting a
  prospect who already replied) — on the *cheapest* tier.
- Templated copy (email template-fill, the audit generation): the cheap/mid model produced it
  cleanly — these move down a tier with no quality loss.

Conclusion: the judgment + mechanical loops move to the cheap tier safely; creative stays premium;
code guards the boundaries.

## Rollout order (lowest risk first)
1. Prove the data-store write path + read-back verify on the target environment.
2. Tighten each rule-set so the objective locks are unmissable, then re-test the cheap model.
3. Go live on lead-gen first — its output waits for human review, so a miss is caught before spend.
4. Then follow-up routing (behind the deterministic selector), then the rest.
5. Keep the premium model as a one-line fallback the whole time.

## What NOT to do
- Don't remove the deterministic guards or the final verification step.
- Don't replace the human approval / no-auto-send guarantees.
- Don't add heavy infrastructure (queues, schedulers, service mesh) unless a measured need appears.
