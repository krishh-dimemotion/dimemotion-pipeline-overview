#!/usr/bin/env python3
"""Deterministic follow-up selection + validation (hardening rule #2).

FUP routing is fully deterministic, so CODE is the source of truth — not an LLM. This module
computes who is due for which FUP from the locked selection rule, and can VALIDATE a proposed
selection (e.g. from a cheap agent) against that truth: any mismatch BLOCKS before a draft/send.

Selection rule (locked, mirrors FUP.md):
  A record is DUE on run_date for FUP n IFF:
    FUP{n}_DATE is set AND FUP{n}_DATE <= run_date         (past-due still counts)
    AND FUP{n}_SEND is falsy (untick = not yet handled)
    AND the record is NOT replied/terminal (Status in the halted set).
  Scan ALL FIVE FUP columns. Never chain-anchor to decide due-ness (that is a BUILD gate only).

Record shape (dict):
  {"id": "...", "status": "active"|"replied — handle manually"|...,
   "fups": {1: {"date": "2026-07-18", "sent": False}, 3: {"date":"2026-07-14","sent":False}, ...}}

Stdlib only. Dates are ISO "YYYY-MM-DD" strings (lexical compare == chronological).
"""
from __future__ import annotations

TERMINAL_STATES = {  # any of these halts the sequence — never select
    "replied — handle manually", "replied", "bounced", "unsubscribed",
    "halted", "do not contact", "closed",
}

def due_for(record: dict, run_date: str) -> list[int]:
    """Return the FUP numbers this record is due for on run_date (usually 0 or 1)."""
    status = (record.get("status") or "").strip().lower()
    if status in {s.lower() for s in TERMINAL_STATES}:
        return []
    out = []
    for n in (1, 2, 3, 4, 5):
        slot = (record.get("fups") or {}).get(n) or (record.get("fups") or {}).get(str(n))
        if not slot:
            continue
        date = slot.get("date")
        if not date:
            continue
        if slot.get("sent"):
            continue
        if date <= run_date:           # ISO lexical compare
            out.append(n)
    return out

def select(records: list[dict], run_date: str) -> list[tuple[str, int]]:
    """The authoritative due list: [(record_id, fup_n), ...]."""
    picks = []
    for r in records:
        for n in due_for(r, run_date):
            picks.append((r["id"], n))
    return sorted(picks)

def validate(proposed: list[tuple[str, int]], records: list[dict], run_date: str) -> dict:
    """Compare a proposed selection to the deterministic truth.
    Returns {"ok": bool, "missing": [...], "extra": [...]}. ok=False must BLOCK the run."""
    truth = set(select(records, run_date))
    prop = set(tuple(p) for p in proposed)
    missing = sorted(truth - prop)   # due but not selected (would skip a lead)
    extra = sorted(prop - truth)     # selected but not due (would send wrongly — e.g. to a replier)
    return {"ok": not missing and not extra, "missing": missing, "extra": extra}

# ---- embedded self-test (no LLM, no network): the exact scenario Codex passed 6/6 ----
def _selftest() -> int:
    run = "2026-07-18"
    recs = [
        {"id": "P1", "status": "active", "fups": {1: {"date": "2026-07-18", "sent": False}}},
        {"id": "P2", "status": "active", "fups": {3: {"date": "2026-07-14", "sent": False}}},  # past-due
        {"id": "P3", "status": "active", "fups": {2: {"date": "2026-07-18", "sent": True}}},   # already sent
        {"id": "P4", "status": "replied — handle manually", "fups": {5: {"date": "2026-07-18", "sent": False}}},  # replied
        {"id": "P5", "status": "active", "fups": {4: {"date": "2026-07-18", "sent": False}}},  # scan-the-column
        {"id": "P6", "status": "active", "fups": {1: {"date": "2026-07-25", "sent": False}}},  # future
    ]
    expected = [("P1", 1), ("P2", 3), ("P5", 4)]
    got = select(recs, run)
    assert got == expected, f"select wrong: {got} != {expected}"
    # validator catches a bad proposal that includes the replied prospect + drops a due one
    bad = [("P1", 1), ("P4", 5)]  # missing P2/P5, extra P4 (the reply-after-halt bug)
    v = validate(bad, recs, run)
    assert v["ok"] is False and ("P4", 5) in v["extra"] and ("P2", 3) in v["missing"], v
    # a correct proposal passes
    assert validate(expected, recs, run)["ok"] is True
    print("SELFTEST PASS: select 3/3 correct; validator blocks replied-inclusion + missed-due.")
    return 0

if __name__ == "__main__":
    import sys
    raise SystemExit(_selftest() if "--selftest" in sys.argv else _selftest())
