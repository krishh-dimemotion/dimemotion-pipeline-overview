# Outreach Pipeline — Architecture & Cost Overview

A high-level, implementation-agnostic map of an automated B2B cold-outreach + content-audit
pipeline, written for a **cost review**. It describes *what runs, how often, and where money is
spent* — the surface a consultant needs to find savings.

This repo contains **no credentials and no customer data.** It includes the architecture, the method
overviews, and a few small sample guard scripts — enough to review structure and cost. Full
implementation details are internal.

## Contents
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — the domains, the automated loops, and how a task flows.
- [`COST-MODEL.md`](COST-MODEL.md) — where cost accrues (LLM tiers + paid APIs) and the candidate cuts.
- [`SHIFT-CLAUDE-TO-CODEX.md`](SHIFT-CLAUDE-TO-CODEX.md) — the playbook for moving mechanical work from a premium agent to a cheap one, safely.
- [`AUDIT-PIPELINE-COST.md`](AUDIT-PIPELINE-COST.md) — the audit output's cost surface + how to cut it (method withheld).
- [`FOLLOWUP-SEQUENCE.md`](FOLLOWUP-SEQUENCE.md) — the follow-up sequence structure (no copy).
- [`LEAD-QUALIFICATION.md`](LEAD-QUALIFICATION.md) — how candidates are scored + qualified.
- [`EMAIL-METHOD.md`](EMAIL-METHOD.md) — how cold emails are generated.
- [`AUDIT-METHOD.md`](AUDIT-METHOD.md) — how audit pages are generated.
- [`guards/`](guards/) — sample method-free deterministic guards, each self-testing.

## The system in one paragraph
An agent-driven pipeline finds prospects, drafts personalized outreach, runs a multi-step follow-up
sequence, and builds per-prospect "audit" web pages as a sales asset. Today it is driven by a
**premium LLM agent on every step**, which is the dominant cost. The active project is to move the
**templated, mechanical, and rule-driven steps onto a cheap model** and keep the premium model only
for final verification — same output, a fraction of the cost.

## The one-line cost thesis
> Most of the daily spend is a premium model doing work a cheap model could do. The lever is
> **tiering**: cheap/mid model for templated + deterministic loops, premium only for final verification.
