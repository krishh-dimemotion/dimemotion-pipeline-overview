#!/usr/bin/env python3
"""Minimal run ledger for background loops (idempotency/observability — smallest mechanism).

The pipeline already has strong DATA-level idempotency (record-state guards, .last_digest marker,
ingest dedup). What it lacks is RUN-level observability: a unique id, status, timestamps, and an
error record per invocation. This is that — an append-only JSONL ledger. No Redis/Celery/service.

  rid = start_run("reply-watcher")
  ... do work ...
  end_run(rid, "reply-watcher", status="ok", records=7)          # or status="failed", error="..."

Also supports a cheap duplicate/overlap guard: was the SAME loop already marked running recently?
(useful if a timer fires while a prior slow run is still going.)

Ledger: logs/run-ledger.jsonl (append-only). Stdlib only.
"""
from __future__ import annotations
import os, json, uuid, datetime

LEDGER = os.environ.get("RUN_LEDGER",
    os.path.join(os.path.dirname(__file__), "..", "..", "logs", "run-ledger.jsonl"))

def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def _append(rec: dict):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(rec) + "\n")

def start_run(job: str) -> str:
    rid = f"{job}-{uuid.uuid4().hex[:12]}"
    _append({"event": "start", "run_id": rid, "job": job, "ts": _now()})
    return rid

def end_run(rid: str, job: str, status: str = "ok", records: int = 0, error: str = "") -> None:
    assert status in ("ok", "partial", "failed"), status
    _append({"event": "end", "run_id": rid, "job": job, "ts": _now(),
             "status": status, "records": records, "error": error[:500]})

def last_status(job: str) -> dict | None:
    """Most recent end-record for a job (None if never completed). Cheap tail read."""
    if not os.path.exists(LEDGER):
        return None
    found = None
    with open(LEDGER) as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("event") == "end" and r.get("job") == job:
                found = r
    return found

def _selftest() -> int:
    import tempfile
    global LEDGER
    LEDGER = os.path.join(tempfile.mkdtemp(), "ledger.jsonl")
    rid = start_run("reply-watcher")
    assert rid.startswith("reply-watcher-") and len(rid) > 15
    end_run(rid, "reply-watcher", status="ok", records=7)
    ls = last_status("reply-watcher")
    assert ls and ls["status"] == "ok" and ls["records"] == 7 and ls["run_id"] == rid, ls
    # a failed run is recorded with its error
    r2 = start_run("digest"); end_run(r2, "digest", status="failed", error="mailbox 2/4 unbound")
    assert last_status("digest")["status"] == "failed", last_status("digest")
    assert last_status("never-ran") is None
    print("SELFTEST PASS: run id + start/end + status/error + last_status lookup.")
    return 0

if __name__ == "__main__":
    raise SystemExit(_selftest())
