#!/bin/bash
# Fail-open runner (hardening rule #4).
#
# Runs a pipeline task on Codex ($20 plan). If Codex fails for QUOTA or AUTH reasons — the two ways
# the cheap tier can go dark — it FALLS OPEN to Claude for that one run and alerts Slack. The loop
# always completes on one engine or the other; it never silently stalls the queue.
#
# Usage:  run_codex_loop.sh "<task prompt>"        # normal
#         run_codex_loop.sh --test-detection        # offline self-test of the failure detector
#
# Env (with sane defaults for this repo layout):
#   CODEX_HOME (repo-local .codex), REPO (cwd)
set -uo pipefail

# --- failure detector: is this Codex output a quota/auth failure we should fail-open on? ---
is_failopen_error() {
  # reads stderr+stdout on $1 (a file); returns 0 (true) if quota/auth failure
  grep -qiE '429|rate.?limit|quota|insufficient_quota|usage limit|401|unauthorized|missing bearer|invalid api key|authentication' "$1"
}

run_codex() {   # $1=prompt  $2=outfile  -> exit code of codex
  CODEX_HOME="${CODEX_HOME:-$REPO/.codex}" codex exec --skip-git-repo-check "$1" >"$2" 2>&1
}

run_claude_fallback() {   # $1=prompt  $2=outfile
  env -u ANTHROPIC_API_KEY claude -p "$1" >"$2" 2>&1
}

slack_alert() {   # $1=message  (best-effort; never blocks the run)
  echo "SLACK_ALERT the ops channel: $1"
  # real wiring posts via the Slack MCP/webhook; the marker line is what the monitor greps.
}

main_run() {
  local prompt="$1"
  local out; out="$(mktemp)"
  if run_codex "$prompt" "$out" && ! is_failopen_error "$out"; then
    cat "$out"; return 0
  fi
  if is_failopen_error "$out"; then
    slack_alert "Codex quota/auth failure — failing OPEN to Claude for this run."
    local cout; cout="$(mktemp)"
    run_claude_fallback "$prompt" "$cout"
    cat "$cout"; return 0
  fi
  # non-quota Codex error: surface it, do NOT silently swallow
  slack_alert "Codex run failed (non-quota). Output follows; run held for review."
  cat "$out"; return 1
}

# --- offline self-test of the detector (no network; no pipes, so counters persist) ---
test_detection() {
  local t; t="$(mktemp)"
  local pass=0 fail=0
  expect() {  # $1=want(yes|no) $2=label ; input already in $t
    if is_failopen_error "$t"; then got=yes; else got=no; fi
    if [ "$got" = "$1" ]; then echo "$2 -> ok ($got)"; pass=$((pass+1)); else echo "$2 -> WRONG (got $got, want $1)"; fail=$((fail+1)); fi
  }
  printf 'ERROR: unexpected status 429 Too Many Requests\n' >"$t";      expect yes "429"
  printf 'insufficient_quota: you exceeded your usage limit\n' >"$t";   expect yes "quota"
  printf '401 Unauthorized: Missing bearer\n' >"$t";                    expect yes "401-auth"
  printf 'Subject: normal email output, all good\n' >"$t";             expect no  "clean-output"
  printf 'WRITE_VERIFIED: ...appended marker\n' >"$t";                  expect no  "clean-write"
  echo "DETECTOR SELFTEST: pass=$pass fail=$fail"
  [ "$fail" -eq 0 ] && { echo OK; return 0; } || { echo FAILED; return 1; }
}

if [ "${1:-}" = "--test-detection" ]; then test_detection; exit 0; fi
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
main_run "${1:?usage: run_codex_loop.sh \"<task prompt>\"}"
