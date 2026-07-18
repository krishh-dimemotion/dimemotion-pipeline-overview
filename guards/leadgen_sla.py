#!/usr/bin/env python3
"""Lead-gen human-review SLA gate (hardening rule #5).

The operator is the real throughput ceiling: new leads land with Lead Status BLANK and wait for
manual review. If the unreviewed backlog grows faster than it is cleared, keep generating and the
queue rots. This gate makes lead-gen SELF-THROTTLE:

  PAUSE lead-gen when either:
    - the count of BLANK (unreviewed) leads  > BACKLOG_MAX (30), OR
    - the oldest BLANK lead's age            > MAX_AGE_HOURS (48h).
  On PAUSE: the caller alerts Slack and STOPS adding leads. Resume is MANUAL (never auto).

Deterministic, stdlib only. Times are epoch seconds (pass now + each lead's created_at) so the
logic is testable without wall-clock.
"""
from __future__ import annotations

BACKLOG_MAX = 30
MAX_AGE_HOURS = 48

def evaluate(blank_created_ats: list[float], now: float,
             backlog_max: int = BACKLOG_MAX, max_age_hours: float = MAX_AGE_HOURS) -> dict:
    """blank_created_ats: epoch seconds for each BLANK (unreviewed) lead. now: epoch seconds.
    Returns {"pause": bool, "reason": str, "count": int, "oldest_hours": float}."""
    count = len(blank_created_ats)
    oldest_hours = (now - min(blank_created_ats)) / 3600 if blank_created_ats else 0.0
    reasons = []
    if count > backlog_max:
        reasons.append(f"backlog {count} > {backlog_max}")
    if oldest_hours > max_age_hours:
        reasons.append(f"oldest blank {oldest_hours:.1f}h > {max_age_hours}h")
    pause = bool(reasons)
    return {
        "pause": pause,
        "reason": ("; ".join(reasons) if pause else "within SLA"),
        "count": count,
        "oldest_hours": round(oldest_hours, 1),
        "action": ("PAUSE lead-gen + Slack the ops channel; manual resume required" if pause else "continue"),
    }

def _selftest() -> int:
    H = 3600
    now = 1_000_000 * H  # arbitrary fixed 'now' (no wall-clock)
    # A: 31 fresh leads -> pause on count
    a = evaluate([now - H] * 31, now)
    assert a["pause"] and "backlog 31" in a["reason"], a
    # B: 10 leads, oldest 50h -> pause on age
    b = evaluate([now - 50 * H] + [now - H] * 9, now)
    assert b["pause"] and "50.0h" in b["reason"], b
    # C: 10 leads, oldest 20h -> within SLA
    c = evaluate([now - 20 * H] + [now - H] * 9, now)
    assert not c["pause"] and c["reason"] == "within SLA", c
    # D: empty backlog -> continue
    d = evaluate([], now)
    assert not d["pause"], d
    print("SELFTEST PASS: pauses on backlog>30 and on oldest>48h; continues within SLA.")
    return 0

if __name__ == "__main__":
    raise SystemExit(_selftest())
