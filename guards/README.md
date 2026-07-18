# Guards (sample deterministic checks)

The non-secret, method-free guards that let a cheap model run the mechanical loops safely. Pure logic —
no vendor endpoints, no credentials, no copy. Each is self-testing: run it directly to see it pass.

- `fup_selector.py`  — deterministic "who is due for which follow-up" + a validator that blocks a wrong
  selection (e.g. never selecting a prospect who already replied). `python3 fup_selector.py --selftest`
- `leadgen_sla.py`   — pauses lead generation when the human review backlog is too large/old.
- `run_ledger.py`    — minimal per-run id / status / timestamps / error record for background loops.
- `run_codex_loop.sh`— fail-open runner: if the cheap model is unavailable, fall back to the premium
  model for that run instead of stalling. `bash run_codex_loop.sh --test-detection`
