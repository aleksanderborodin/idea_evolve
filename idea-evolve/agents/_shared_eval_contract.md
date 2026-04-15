# Shared Evaluation Contract — solution agents

> KEEP IN SYNC: this block is referenced verbatim by `explore.md`, `exploit.md`, `full.md`,
> and `genetic.md`. Edit here, then re-run `scripts/check_docs_consistency.py`.

## The write-then-evaluate loop

You write **one** solution file, then run `python3 evaluate.py output/sol01.py` and wait
for it to finish. Read the resulting `output/sol01.score` file. Decide what to try next.
Write `sol02.py`. Repeat.

**Never launch a second `evaluate.py` while the first is still running.** Your shell
already enforces this if you call it foreground — keep it that way. Backgrounding eval
is forbidden: it wastes turns and triggers the kill contract below.

## Same-agent kill contract

Evaluations are **automatically serialized per agent**. If you somehow launch a second
`evaluate.py` (different solution file, same agent identity) while a previous one is
still alive, the new invocation will:

1. Read the system-wide eval queue (`/tmp/idea_evolve_eval_queue.json`).
2. Verify the previous entry is owned by you (matches `agent_name`, `pid` is alive,
   `/proc/<pid>/cmdline` contains `evaluate.py`, env shows the same `IDEA_EVOLVE_AGENT_NAME`).
3. Send `SIGTERM` → 2 s grace → `SIGKILL` to the entire process group.
4. Wait until the relevant problem-level lock (e.g. GPU lock for strawberry) is released,
   then proceed.

The killed solution will have **no `.score` sidecar**. Treat it as permanently abandoned.
**Do not retry it.** Write a different `solNN.py` instead. The kill is logged to
`runs/<problem>/<attempt>/proc_logs/<ts>_<agent>_kill_<pid>.md` so future agents can see
what happened.

If you did not intend to abandon the previous solution, you have a bug in your loop —
slow down and run evaluations one at a time.

## Reading failure logs

When a `.score` shows `is_valid: 0`, an `error` field, or a non-finite fitness:

1. Read the `log_path` field inside the `.score` JSON. It points at a markdown narrative
   log under `runs/<problem>/<attempt>/proc_logs/`.
2. The log contains a timeline (when training started, when it crashed), the full
   traceback, and a problem-specific **"What to try next"** section produced by
   `problems/<id>/eval_hooks.py:diagnose_failure()`.
3. **Do not just re-run the solution.** Understand the cause first; then write a different
   `solNN.py` that addresses it.

If the failure looks like resource contention (broken pipe, CUDA OOM with low requested
memory, suspicious timeouts), check whether the architect placed your agent in a
single-element `parallel_group` for a `concurrency: serial` problem. If not, that is a
plan-level bug — note it in your debrief.

## Per-evaluation artifacts

Every `evaluate.py` invocation produces:

- `output/solNN.score` — JSON with all metrics declared in `metrics.yaml`, plus
  `log_path` on failure.
- A row in `/tmp/idea_evolve_eval_queue.json` while running (visible on the dashboard's
  Pipeline tab). Removed automatically on exit.
- A narrative log under `runs/<problem>/<attempt>/proc_logs/` for any non-trivial
  outcome (crash, kill, long-running success). Important logs are marked `sticky` and
  survive the 200-log retention prune.

## Reproducing a previously scored solution

If `metrics.yaml` has `archive_checkpoints: true` (currently: strawberry only), every
successful evaluation also archives any trained model under
`runs/<problem>/<attempt>/checkpoints/<content_hash>.pt`. To verify a score:

```bash
python3 problems/<id>/evaluate.py --reproduce <content_hash>
```

This re-runs only the test/eval phase — no retraining. See the per-problem
`description.md` "Reproducing a scored solution" section for the cache-busting and
expected-variance details.
