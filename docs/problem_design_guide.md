# Problem Design Guide

**Purpose.** This is a structured, evidence-based guide for designing new problems for
idea-evolve. It codifies what we learned from sidon (combinatorial), permcodes (discrete
search), gemm (algebraic), and strawberry (GPU/ML) — four problems with radically different
evaluation shapes, all running on the same orchestrator.

The guide is opinionated: every rule below comes with the failure mode it prevents. When
you deviate, do so deliberately — not because the rule "seemed optional".

---

## 1. What idea-evolve can and cannot optimize

### Good fits
- **A measurable scalar objective.** You can compute one number from a Python file and
  say "higher (or lower) is better." Fitness must be deterministic or low-variance.
- **Evaluation under ~15 minutes.** Agents iterate dozens of times per generation. If
  one evaluation takes an hour, the feedback loop breaks.
- **Nontrivial search space.** If a naïve greedy solution already beats the theoretical
  bound, there's nothing to search. Sidon's 66 baseline vs 100 target = clean headroom.
- **Solutions expressible as Python files.** Even GPU training scripts work (see
  strawberry) — as long as `entrypoint()` or a top-level import executes the work and
  returns a dict / scalar.

### Bad fits
- **Objectives that require human judgment** (style, aesthetics, "is this a good
  explanation"). No automated evaluator = no fitness signal.
- **Evaluations that depend on external state** (live API, random seed from a remote
  server, time-of-day). Caching by content-hash breaks; identical solutions get
  different scores across generations and the ranking table becomes noise.
- **Multi-hour training runs.** Even with a GPU lock, a 2-hour eval means 1 generation
  = 12+ hours wall clock. The orchestrator was designed for 3–10 minute eval cycles.
- **Problems where the helper code is the problem.** If writing a correct scorer
  requires the same insight as solving the problem, the agents end up gaming the
  scorer. Keep `validate.py` and `evaluate.py` simple and obviously correct.

---

## 2. Required files (the problem contract)

Every problem lives under `problems/<id>/` and MUST contain:

```
problems/<id>/
├── description.md       # What the agent reads first
├── evaluate.py          # CLI: python3 evaluate.py <solution.py>  → prints JSON
├── validate.py          # Invariants check; returns {is_valid, ...}
├── metrics.yaml         # Primary + auxiliary metric specs
└── helpers/             # Imported by solutions (shared utilities + constants)
    ├── core.py
    └── README.md
```

Optional:

```
├── initial_solutions/   # Seed solutions for gen0 (bootstrapped into population)
├── initial_ideas.md     # Domain knowledge to bootstrap the knowledge base
└── initial_facts.md     # Hard facts (theorems, invariants, prior results)
```

### description.md — the agent's first contact

It is read verbatim into every agent prompt. Structure it in this order:

1. **Task** — one sentence defining the fitness direction.
2. **Solution format** — a minimal, runnable example. Not a spec, not pseudocode: a
   real `entrypoint()` (or equivalent) the agent can copy and modify.
3. **Available helpers** — `from helpers.core import ...` with one-line comments per
   symbol. Update this section every time you add a helper — stale comments mislead
   agents for weeks.
4. **Key findings** — baseline scores, what's been tried before, what failed and why.
   Evidence compresses search.
5. **Agent-readable artifacts on disk** — paths agents can read via Bash (training
   logs, per-class metrics, crash tails) without polluting prompt context. See §5.

Keep it under ~200 lines. Anything longer signals the problem is underspecified or
helpers should absorb the complexity.

### evaluate.py — the CLI contract

Contract: `python3 evaluate.py <solution.py>` prints ONE line of JSON to stdout
containing at minimum `{"fitness": float, "is_valid": 0|1}`. Everything else is
optional but recommended.

Mandatory behaviors:
- **Content-hash caching.** Read `eval_cache.json` keyed by `sha256(solution_file)`.
  Identical solutions must return the cached result instantly, not re-run.
- **`.score` sidecar.** Write `<solution>.score` alongside the Python file. This is
  the authoritative score source for the orchestrator; cache is a speed optimization.
- **Sentinel on invalid.** If `validate.py` returns `is_valid=0`, fitness MUST be
  `sentinel_value` from metrics.yaml (usually 0). No partial credit, no near-miss
  scoring. A broken solution has no rank.
- **File locking on the cache.** Parallel agents read/write concurrently. Use
  `fcntl.flock` — without it, eval_cache.json gets corrupted at gen 5+.

GPU-bound problems add:
- **System-wide GPU lock.** Exclusive `fcntl.flock` on `/tmp/idea_evolve_gpu.lock`.
  Parallel agents queue automatically. See `problems/strawberry/evaluate.py` for the
  reference implementation.
- **Transparent venv re-exec.** If the solution needs a different Python env (e.g.
  ultralytics in a specific venv), use `os.execve(VENV_PYTHON, ...)` to REPLACE the
  current process — not `subprocess.run`, which creates a grandchild that survives
  timeout-kill. This is a hard-won lesson (zombie GPU processes on SIGKILL).

### validate.py — cheap and obvious

Should run in milliseconds, return `{"is_valid": 0|1, ...}`. If validation is expensive,
fold it into evaluate.py, but keep the boundary: validate checks invariants (is this a
Sidon set? is the permutation code the right length?); evaluate computes the score.

Agents will try to game the scorer. If `validate.py` is wrong, they find the hole and
the leaderboard is meaningless. Keep it O(N log N) at worst and unit-test it on known
good + known bad inputs.

### metrics.yaml — the metric catalog

See §4 for the full schema. One primary metric (`is_primary: true`) plus any number of
auxiliary metrics that get stored, displayed, and passed through evaluation pipelines
but do NOT affect ranking.

### helpers/core.py — the shared toolbox

Every import an agent might want, with:
- **Path constants** — absolute paths to datasets, checkpoints, configs. Agents should
  never hardcode paths.
- **Epoch / budget constants** — `PROXY_EPOCHS_FINETUNE = 20`. Change one constant,
  every solution picks up the new budget on next eval.
- **Standard training/eval loops** as functions (`train_and_eval`, `evaluate_on_test`).
  Absorb boilerplate so agents can focus on the interesting kwargs.
- **A README.md index** — one-line descriptions of every symbol. The Architect reads
  this when deciding which helpers to point agents at.

Keep imports lazy inside helper functions. `helpers.core` is imported by the orchestrator
during preflight; if importing it triggers ultralytics / torch / CUDA, preflight fails on
machines without a GPU.

---

## 3. Evaluation time budget

Hard rule: **median eval time ≤ 10 minutes**. If a generation has 8 agents × 3 iterations
× 10 min = 4 hours, you still get 6 generations a day. Anything slower breaks the loop.

Measured baselines:
- sidon, permcodes: <1 s per eval (pure Python, cached).
- gemm: 1–3 s per eval (Python + small numpy).
- strawberry: ~210 s per eval (20-epoch YOLO fine-tune, GPU-serialized).

If your problem inherently takes longer, you have three levers:
1. **Proxy evaluation.** strawberry uses 20 epochs (3.6 min) as a proxy for 100 epochs
   (18 min). The proxy is faithful enough that ranking correlates with full training.
2. **Smaller dataset / model.** Subsample to the smallest data where signal is still
   clear. For ML: the smallest model size that shows the same ranking.
3. **Aggressive caching.** Content-hash on solution file is mandatory; you can also
   cache intermediate artifacts (trained weights keyed by config hash, preprocessed
   datasets by dataset hash).

**Eval timing is always collected.** Every `evaluate.py` unconditionally records three fields
in every `.score` (success and error) and in the matching `eval_cache.json` entry:

- `eval_time_s` — wall-clock duration of the measured region, seconds.
- `eval_started_at` — ISO-8601 UTC timestamp captured immediately before the measured region.
- `eval_ended_at` — ISO-8601 UTC timestamp captured immediately after the measured region.

On error, all three are still written (reflecting how long the attempt ran before crashing).
If an exception occurs before measurement begins (e.g. import failure), the fields are omitted.

Control LLM visibility with `show_eval_time_in_prompts: true` (default: true, recommended).
When true, orchestrator-generated summaries include timing data so agents can spot regressions
or GPU queue waits. Set to `false` only if eval time is meaningless noise for your problem
(e.g. sub-millisecond trivial computation). The dashboard always shows all three columns
regardless of this flag — it reads `.score` files directly.

The dashboard Solutions tab renders all three (Eval time, Started, Ended) so you can see
per-eval cost alongside the actual timeline — useful for spotting GPU queue waits, wall-clock
drift, and evals that straddle midnight. Sudden slowdowns in `eval_time_s` signal a
regression in helper code or an agent that turned off caching. Started/ended timestamps
anchor `.score` files to log events (proc_logs, run_state) when debugging.

---

## 4. Multi-metric support — the evidence-based pattern

A fitness scalar is necessary (orchestrator needs one number to sort by) but not
sufficient. Real problems have multiple axes:
- sidon: set size (primary) + violation count (diagnostic)
- strawberry: mAP50 (primary) + mAP50_95, F1, precision, recall, per-class mAP, TTA flag

If only fitness reaches the knowledge base, agents fly blind on the bottleneck. Strawberry
proved this: 15× class imbalance meant aggregate mAP50 was dominated by the common class;
agents couldn't target the rare class until per-class metrics appeared.

### Primary + auxiliary metrics

```yaml
# problems/<id>/metrics.yaml
show_eval_time_in_prompts: true   # optional; true by default — controls LLM prompt inclusion
target_score: 0.92

specs:
  fitness:                          # whatever the primary metric is called
    description: "Mask mAP50 on test split"
    is_primary: true                # exactly ONE metric has this
    higher_is_better: true
    lower_bound: 0.0
    upper_bound: 1.0
    decimals: 4
    include_in_prompts: true
    significant_change: 0.002       # below this is marked ~ in progression
    sentinel_value: 0               # invalid → fitness = 0

  is_valid:
    description: "1 if solution ran and validated, 0 otherwise"
    higher_is_better: true
    sentinel_value: 0

  mAP50_95:                         # auxiliary metric — displayed, not ranked
    description: "Stricter IoU average"
    higher_is_better: true
    decimals: 4
    include_in_prompts: true
    sentinel_value: 0

  per_class_mAP50:                  # structured auxiliary — list per class
    description: "Per-class mAP50; index matches classes in helpers.core.CLASS_NAMES"
    higher_is_better: true
    decimals: 4
    sentinel_value: []
```

Rules:
- **Exactly one `is_primary: true`.** This is the fitness. The orchestrator sorts and
  targets on it.
- **Auxiliary metrics pass through evaluate.py** — if the entrypoint returns them, they
  get stored in `.score` and the eval cache. No registration step required beyond
  listing them in metrics.yaml.
- **`include_in_prompts: true`** means the agent sees this metric in population
  summaries and their own solution scores. Without it, the metric is stored but hidden
  — useful for developer-only diagnostics.
- **Structured metrics** (lists, dicts, per-class breakdowns) are fine. They don't
  appear in the progression table but are fully available in `.score` files. See §5
  for how to surface them without polluting prompt context.

### Adding a metric mid-run (standardized way)

You will want to track a new metric after generation 5 when you realize it's missing.
This must NOT invalidate prior scores or require re-evaluating the population.

The standard flow:

1. **Add the metric to `metrics.yaml`** with `include_in_prompts` and `sentinel_value`.
2. **Update `evaluate.py` / `entrypoint()` to compute and return it.** Solutions that
   already evaluated before this change will have the metric missing from their
   cached results — that is fine.
3. **The orchestrator treats missing auxiliary metrics as `sentinel_value`** (or
   renders them as `—` in summaries). Primary fitness is never retroactively touched.
4. **Optional: re-evaluate specific solutions** you care about by deleting their
   `.score` sidecar AND their eval_cache entry (by content hash). The next run of
   `evaluate.py` recomputes with the new metric.

Do NOT bulk-rerun the population; you'll waste GPU and perturb rankings. Let the metric
fill in naturally as new solutions are evaluated and spot-fill past generations only
when diagnosing a specific question.

---

## 5. Agent-readable artifacts on disk (not in context)

Two distinct channels to surface information to agents:

| Channel | When to use |
|---------|-------------|
| Prompt context (description.md, knowledge files, brief, `.score` inline) | Small, durable, consulted every turn |
| **Disk artifacts (Bash/Read on specific paths)** | Large, high-detail, consulted only when the agent has a specific question |

### When to write to disk instead of prompt
- **YOLO `results.csv` with 40 epochs × 10 metric columns** — 4KB per run, useless until
  an agent asks "did training plateau?"
- **Per-class precision/recall arrays** — 7 classes × 4 metrics = 28 floats per eval.
  Storing them in `.score` is fine; dumping them into every agent's prompt is waste.
- **Training stdout / crash tracebacks** — noisy but critical for debugging a single
  failure.

### The pattern

Pick a stable, well-known path. Overwrite on each run (so stale data doesn't accumulate)
but preserve across the `cleanup` step. Document the path prominently in
`description.md`.

```python
# helpers/core.py
TRAIN_LOG_DIR = Path("/tmp/idea_evolve_<problem>/last_train_logs")
LAST_PER_CLASS_METRICS = Path("/tmp/idea_evolve_<problem>/last_per_class.json")
```

```markdown
<!-- description.md -->
## Agent-readable artifacts on disk

| Path | What's there | When to read |
|------|--------------|--------------|
| `/tmp/.../last_train_logs/results.csv` | Per-epoch loss + val curves | Diagnose plateaus |
| `/tmp/.../last_per_class.json` | Per-class metrics from last eval | Identify class bottleneck |
```

This keeps prompts lean (SCALE-7 hygiene) while giving agents the tools to investigate
when a specific question arises. Agents use `cat`, `head`, `tail`, or `Read` as needed.

---

## 5.5. Error preservation (so agents can learn from failures)

When `entrypoint()` raises, an agent has three questions:
1. What was the error?
2. Where did it happen?
3. Did my ancestors hit this same error?

If the answer to (3) is "I can't tell", agents repeat their predecessors' failures
generation after generation. This happened on strawberry: multiple solutions died with
`"error": "[Errno 32] Broken pipe"` — 22 characters with no traceback — and the
`/tmp/.../last_train_logs/` artifacts that would have explained why were overwritten
by the next training run.

### The rule

On error, `evaluate.py` MUST preserve enough context next to the failing solution that
a future agent reading `population/genNNN/<agent>/sol01.score` can diagnose the failure
without re-running anything.

**Minimum preserved fields in `.score`:**
```json
{
  "is_valid": 0,
  "fitness": 0,
  "error": "<first 500 chars of exception message>",
  "traceback": "<first 4000 chars of traceback.format_exc()>"
}
```

**If your problem writes ephemeral diagnostic files (training logs, intermediate
artifacts, profiling output)**, snapshot them next to the solution on error:

```python
# evaluate.py — in the top-level except clause
import shutil, traceback
tb = traceback.format_exc()
error_result = _error_result(str(e), tb=tb)
# Snapshot /tmp/<problem>/last_run/ into <solution>_crash_logs/
sol = Path(solution_path)
dest = sol.parent / f"{sol.stem}_crash_logs"
if TRAIN_LOG_DIR.exists():
    dest.mkdir(parents=True, exist_ok=True)
    for src in TRAIN_LOG_DIR.iterdir():
        if src.is_file():
            shutil.copy2(src, dest / src.name)
_write_score_sidecar(solution_path, error_result)
```

This costs ~10 lines of code and nothing at runtime (the copy only happens on failure).
See `problems/strawberry/evaluate.py` for the reference implementation.

### Why "next to the solution" specifically

The solution file lives in `population/genNNN/<agent>/sol01.py` permanently — that
directory survives the orchestrator's cleanup step. Anything copied next to it persists
across generations. `/tmp/` paths get overwritten by the next evaluation and are
single-use.

### Document the path in description.md

Agents won't read `<solution>_crash_logs/` unless you tell them to. Add it to the
"Agent-readable artifacts" table in `description.md` with a one-line description and
an example `cat` command. Without documentation, the feature is invisible.

---

## 6. Helpers: the contract between problem author and agents

Helpers are a force multiplier. A good helper compresses 30 lines of boilerplate into
one call and encodes best practice. A bad helper hides a footgun.

### Principles

1. **Every constant has a comment** with units and when to use it.
   `PROXY_EPOCHS_FINETUNE = 20  # 20 — fine-tuning from checkpoint (~3.6 min)`
2. **Every function has an example** in the docstring. Agents copy examples; missing
   example = missing feature from their POV.
3. **Warn about footguns in the docstring.** Strawberry's `train_and_eval` defaults to
   `optimizer='AdamW'` because YOLO's `optimizer='auto'` silently ignores `lr0`. The
   docstring says so explicitly. Without the warning, agents pass `lr0=0.005` and
   wonder why results don't change.
4. **Save logs before cleanup.** If your helper wraps training+cleanup, preserve logs
   to the well-known path (§5) BEFORE `rmtree`. Both on success and on crash — crash
   logs are the most valuable.
5. **Raise, don't return, on failure.** `RuntimeError("Training failed: <msg>. Logs at
   <path>")` beats `return {"mAP50": 0}`. The orchestrator will mark the solution
   invalid; the error message tells the agent where to look.

### Anti-patterns

- **Helpers that hide randomness.** If the helper picks a seed internally, different
  agents "trying the same thing" get different scores and the search loop thrashes.
  Always expose `seed` and default it to `0`.
- **Helpers that require network.** Dataset download, model download, API calls.
  Cache to disk at project setup, then assume it's there.
- **Helpers that mutate their arguments.** `model.train(cfg)` that modifies `cfg` in
  place. Agents pass the same dict twice and get different results.

---

## 7. Problem lifecycle checklist

When you add a new problem, work through this list:

**Design phase:**
- [ ] One primary scalar metric; higher or lower is better, documented in metrics.yaml.
- [ ] Evaluation runs in <10 minutes on the target hardware. If not, design a proxy.
- [ ] Invariant check is obviously correct and runs in <1 s.
- [ ] Baseline solution exists and scores meaningfully below the target.
- [ ] Target score is achievable in principle (has theoretical bound, prior art, or
  human-crafted solution achieves it).

**Implementation:**
- [ ] `description.md` has: task, solution template, helpers import block, key findings,
  disk-artifact paths.
- [ ] `evaluate.py` has: content-hash caching, `.score` sidecar write, `fcntl` lock,
  sentinel on invalid.
- [ ] `validate.py` is called from evaluate.py and enforces invariants.
- [ ] `metrics.yaml` has exactly one `is_primary: true`.
- [ ] `helpers/core.py` has path constants, budget constants, at least one "do everything"
  helper, and a README.md index.
- [ ] If GPU-bound: system-wide file lock + `os.execve` re-exec (NOT `subprocess.run`).

**Validation:**
- [ ] `python3 orchestrator.py . --problem <id> --new-attempt --dry-run` shows the
  expected plan.
- [ ] `python3 evaluate.py <known_good.py>` prints valid JSON with correct fitness.
- [ ] `python3 evaluate.py <known_bad.py>` prints `is_valid: 0` and sentinel fitness.
- [ ] Run gen0 bootstrap + gen1 with 2 agents end-to-end. Scores appear on dashboard.
- [ ] Kill the orchestrator mid-run. Restart. It resumes from the last completed phase.

**Post-launch monitoring (first 3 generations):**
- [ ] Baseline solutions evaluated successfully (check `gen000_baseline/*.score`).
- [ ] Agent reports show they read `description.md` and used helpers (not hand-rolled
  boilerplate).
- [ ] `eval_time_s` in `.score` matches your budget; no surprise slowdowns.
- [ ] No zombie processes after `pkill -9 orchestrator`. `nvidia-smi --query-compute-apps`
  shows nothing if you're GPU-bound and the orchestrator isn't running.

---

## 8. Known pitfalls (learned the hard way)

- **`subprocess.run` for venv re-exec creates a grandchild that survives `killpg`.** Use
  `os.execve`. See strawberry `evaluate.py`.
- **YOLO `optimizer='auto'` ignores `lr0`.** Silently. Always set `optimizer='AdamW'`
  (or SGD, or Adam) explicitly.
- **`evaluate.py` timeout of 60s kills training that legitimately takes minutes.**
  Bootstrap baseline evaluations use `safe_run(timeout=600)`.
- **Caching by file content hash means identical solutions return identical scores** —
  but if you changed evaluate.py or the dataset, old cache is wrong. Clear
  `history/eval_cache.json` when you change scoring logic.
- **`helpers/core.py` imported at preflight.** Lazy-import torch/ultralytics INSIDE
  helper functions, not at module top level, or non-GPU machines fail preflight.
- **Initial solutions go in `initial_solutions/`, NOT in gen000 directly.** Orchestrator
  copies them into gen000/baseline on first run. Direct placement breaks restart.
- **Solutions read their path at runtime.** If your `entrypoint()` needs the solution
  file's directory (e.g. to write outputs next to itself), use `Path(__file__).parent`
  — NOT `os.getcwd()`. The evaluator runs them from the agent workspace.

---

## 9. Resource-contended problems (GPU, file-locked, shared external service)

Some problems cannot run as many `evaluate.py` instances in parallel as the architect
would like: GPU training without NVIDIA MPS ⇒ one at a time (GPU context collisions);
GPU with MPS ⇒ a handful of kernels before memory thrashes; a shared rate-limited
HTTP API ⇒ capped by the service's per-second budget; eval binds a fixed TCP port ⇒
one at a time. Idea-evolve offers **two layered mechanisms** for this. Pick
between them based on evidence from your problem, or combine them:

1. **Architect-driven budget** (primary). `metrics.yaml: concurrency: N` declares a
   numeric eval-slot budget. The architect sizes `parallel_groups` so no group
   exceeds N agents; the orchestrator auto-splits any that do and leaves a note
   in `feedback/architect_hints.md` so the next architect learns. Cheap, pure
   scheduling, works for any hardware shape including MPS-capped GPUs.

2. **Physical lock inside `evaluate.py`** (backstop). A file lock on a canonical
   path (typically `GPU_LOCK_PATH` for GPU training, see
   `problems/_shared/constants.py`) serializes evaluations even if the architect
   mis-schedules. This is the only defense when an agent launches two evals back-
   to-back — the same-agent kill contract (§9.2) assumes this lock exists for
   single-GPU problems.

**The two are complementary, not alternatives.** Evidence from the shipped
problems:

| Problem | Hardware reality | `concurrency:` | Physical lock | Why this pair |
|---|---|---|---|---|
| sidon, gemm, permcodes | CPU only, cache-friendly | 0 | none | No contention — parallel is free wall-clock. |
| megaminx | GPU (RTX 5060 Ti) with NVIDIA MPS | 3 | none | MPS shares the device at the CUDA-context level; the numeric budget prevents over-subscription beyond what the GPU's memory can hold. |
| strawberry | GPU without MPS (YOLO training) | 1 | `GPU_LOCK_PATH` | One eval at a time is the only safe number. File lock is the backstop against an agent racing itself. |

### 9.1 Declare it in metrics.yaml

```yaml
# problems/<id>/metrics.yaml
concurrency: 0          # default. Unlimited — CPU-bound or GPU+MPS-safe.
concurrency: 1          # serial — one eval at a time. GPU without MPS.
concurrency: 3          # at most 3 simultaneous evals. GPU+MPS with memory cap, etc.

archive_checkpoints: true      # default: false; only for problems that train models
checkpoint_retention: 50       # default 50; LRU pruning keyed by content hash
```

`concurrency` must be a non-negative integer. Non-integer values (including the
old string forms `"parallel"` / `"serial"`) raise `ValueError` at load time —
there is one canonical form and the system enforces it.

**Every agent role counts as one slot.** Research and experimentator agents can also
call `evaluate.py` (research testing a paper baseline, experimentator verifying a
helper it built), so there is no free-role exemption. Size groups by total agent
count, not by role.

The orchestrator passes `concurrency` to the architect prompt context. The architect
sizes `parallel_groups` accordingly. If the architect writes an oversized group, the
orchestrator silently splits it into sequential sub-groups of size ≤ budget and
writes a note to `feedback/architect_hints.md` that the next architect reads.
Malformed YAML falls back to `[[all agents]]` (then budget-splits if needed).

### 9.1.1 Picking a budget value — evidence-based

- **Start with 0** unless you have a concrete resource the eval contends for. Over-
  serializing wastes wall-clock and compresses exploration diversity (fewer parallel
  ideas per generation).
- **Set 1** when the eval holds an exclusive resource: GPU training without MPS, a
  fixed TCP port, an exclusive file lock on a mutable dataset. Evidence: you observe
  broken pipes, OOMs, or "address in use" errors when two evals overlap. Also add
  a physical file lock in `evaluate.py` as a backstop.
- **Set N > 1** when you have measured how many concurrent evals the resource
  tolerates. For GPU+MPS, the measurement is "how many simultaneous kernels before
  GPU memory saturates." For a rate-limited API, it's the service's per-second
  limit divided by per-eval request rate. Don't guess — if you don't have the
  measurement, start at 1 and raise it when monitoring shows headroom.
- **For new Kaggle problems** (see §13), default `concurrency: 0` unless the baseline
  already uses the GPU. If it does, classify: MPS-safe → pick N via measurement;
  MPS-unsafe → `concurrency: 1` + `GPU_LOCK_PATH`.

### 9.2 Same-agent kill contract

When an agent launches a new `evaluate.py` while a previous one of theirs is still
running, the new invocation **terminates the old one** before acquiring resources.
Implementation:

- Every `evaluate.py` calls `eval_queue.enqueue(agent_name, problem, attempt, solution_path)`
  on entry. The queue lives at `/tmp/idea_evolve_eval_queue.json` under `fcntl.flock`.
- Every `evaluate.py` calls `eval_queue.kill_stale_same_agent(agent_name, kill_hook=...)`
  *before* acquiring the problem-level lock (e.g. GPU lock).
- The kill check enforces 8 invariants (queue presence, agent name match, pid alive,
  pgid match, `/proc/<pid>/cmdline` contains `evaluate.py`, env shows the same
  `IDEA_EVOLVE_AGENT_NAME`, per-agent fcntl mutex held). On any mismatch it **fails
  open** — the new eval simply queues, never kills the wrong process.
- Per-problem `eval_hooks.py` defines `kill_eval(pid, pgid, solution_path)`. CPU
  problems can omit this (default hook = `killpg(pgid, SIGTERM)` → grace → SIGKILL).
  Strawberry's hook also waits for the GPU lock to be released and logs every step
  to `/tmp/idea_evolve_strawberry/kill_log.json`.

The killed solution will have **no `.score` sidecar**. Agent prompts (via
`agents/_shared_eval_contract.md`) instruct agents to treat it as permanently
abandoned, not retry.

### 9.3 Agent-readable narrative logs (proc_logs)

Every non-trivial process outcome — crash, kill, slow success — writes a markdown
narrative log under `runs/<problem>/<attempt>/proc_logs/<ts>_<agent>_<kind>_<pid>.md`
via `problems/_shared/proc_log.Writer`. Format:

```markdown
# Process Log — explore_1 / evaluate.py / pid 12345

## Summary
- **Outcome:** CRASHED
- **Error class:** BrokenPipeError
- **Duration:** 67s
- **Solution:** output/sol01.py (hash a1b2c3...)

## Timeline
- 18:03:12 — enqueue
- 18:03:14 — mark_running (lock acquired)
- 18:04:01 — exception raised

## Traceback
```python
...
```

## What to try next
(produced by problems/<id>/eval_hooks.py:diagnose_failure)
- If broken pipe: check that metrics.yaml says `concurrency: 1` ...
```

The `.score` sidecar gains a `log_path` field on failure. Agents are taught to read it
before retrying (see `_shared_eval_contract.md` § "Reading failure logs"). Logs are
append-only line-buffered with `os.fsync` so they survive SIGKILL up to the last line.
Retention: last 200 per attempt, with `sticky: true` logs (failures, kills) excluded
from pruning.

### 9.4 Reproducing a scored solution

Required `description.md` section for any problem that trains models or has run-to-run
variance. Four steps:

1. **Bust the cache** — `evaluate.py` caches by file content hash; without busting, the
   re-run returns the cached score instantly.
2. **Re-evaluate from the archive** — `python3 problems/<id>/evaluate.py --reproduce <hash>`
   loads the archived `best.pt` and runs only the test/eval phase (no retraining).
3. **Expected variance** — state the numeric range and source of nondeterminism.
4. **Required artifacts** — list files that must still exist (e.g. archived
   `<hash>.pt`).

If the problem does not train models (sidon, gemm, permcodes), the reproduction story
is "the cache hit IS the reproduction; identical content hash → identical result".

### 9.5 Per-group Light Evaluator (opt-in/out)

A **Light Evaluator** (Phase 2.5) runs between parallel groups inside a
generation. Scope: surgical — read only THAT group's outputs, write ideas /
patterns / `group_notes.md` so the next group's agents see them before they
start. The end-of-generation Heavy Evaluator still runs for full consolidation.
See `agents/evaluator_light.md` for the prompt.

**Per-problem toggle — `metrics.yaml: evaluator_light_enabled`**

```yaml
# Default for every concurrency value (knob can be omitted)
evaluator_light_enabled: true

# Explicit opt-out — only if the sonnet cost dominates an already-cheap eval
evaluator_light_enabled: false
```

Resolution order in `orchestrator.evaluator_light_enabled()`:

1. `metrics.yaml: evaluator_light_enabled` (per-problem override)
2. `user/config.yaml: analysis.evaluator_light.enabled` (global default)
3. `DEFAULT_EVALUATOR_LIGHT_ENABLED` from `problems/_shared/constants.py` (True)

**When to leave enabled (default — all concurrency values):**

- `concurrency: 0` (unlimited) or `concurrency: N` (N ≥ 2) — the architect
  commonly produces 2+ groups per generation; the compounding-knowledge
  benefit justifies the one extra sonnet run between groups.
- `concurrency: 1` — every group holds a single agent, so a light eval runs
  between every single agent. That is **the intended mid-gen learning loop**
  for serial-eval problems: agent N+1 reads the new ideas/patterns extracted
  from agent N before starting, instead of waiting for the end-of-gen heavy
  evaluator. The wall-clock cost is a sonnet run per agent boundary (~tens
  of seconds), which is usually small compared to a serial eval. Strawberry,
  megaminx, gemm, sidon, permcodes all default to true.

**When to disable:**

- The sonnet run cost dominates an already-cheap eval (e.g. sub-second
  evals with dozens of agents per gen).
- Single-agent workflows where the architect never produces any groups
  with multiple or sequential agents.

The skip rules inside the orchestrator still apply even when enabled:
single-group manifests skip (heavy is next anyway), the last group in any
manifest skips (heavy is next), and groups that produced literally no output
skip. The knob controls **whether the gate exists at all** for this problem.

Tunables (global, in `user/config.yaml`):

- `analysis.evaluator_light.model` — default `sonnet`
- `timeouts.evaluator_light` — default `900s`
- `max_turns.evaluator_light` — default `400`

---

## 10. Glossary (consistent terminology across docs and prompts)

| Term | Definition |
|---|---|
| **Evaluation** | One call to `evaluate.py <solution>` that produces a `.score` sidecar (or fails into a proc_log). |
| **Concurrency budget** | Integer in `metrics.yaml: concurrency`. `0` = unlimited, `1` = serial, `N` = at most N simultaneous evals. Every agent role counts as one slot. |
| **Eval-serial problem** | A problem with `concurrency: 1`. Architect must use single-element `parallel_groups`. |
| **Eval-parallel problem** | A problem with `concurrency: 0` (unlimited). Architect groups all agents together. |
| **Budgeted problem** | A problem with `concurrency: N` where N ≥ 2. Architect may group up to N agents; the orchestrator auto-splits oversized groups. |
| **Auto-split** | Orchestrator silently chunks an oversized group into sequential sub-groups of size ≤ budget and writes a note to `feedback/architect_hints.md`. |
| **Same-agent kill contract** | Rule that a new `evaluate.py` from agent X kills any still-running `evaluate.py` from the same agent X before acquiring resources. |
| **Kill hook** | `problems/<id>/eval_hooks.py:kill_eval(pid, pgid, solution_path)` — problem-specific termination logic. |
| **Diagnosis hook** | `problems/<id>/eval_hooks.py:diagnose_failure(error_class, message, context)` — returns markdown hint surfaced in the failure proc_log. |
| **Eval queue** | `/tmp/idea_evolve_eval_queue.json` — single source of truth for live evaluations. |
| **Proc log** | Markdown narrative at `runs/<problem>/<attempt>/proc_logs/...md` describing what one process did and why it ended. |
| **Archive checkpoint** | `runs/<problem>/<attempt>/checkpoints/<content_hash>.pt` — kept iff `metrics.yaml: archive_checkpoints: true`. LRU-pruned to `checkpoint_retention`. |
| **Stale evaluation** | A queue entry whose pid is alive but belongs to a previous `evaluate.py` of the same agent that is launching a new one. Targeted by the kill contract. |
| **Sticky proc_log** | A proc_log marked `sticky: true` (typically failures, kills) and excluded from the 200-log retention prune. |
| **Light Evaluator** | Phase 2.5 surgical sonnet eval that runs between parallel groups in a generation — writes new ideas/patterns + `group_notes.md` for the next group. Gated by `metrics.yaml: evaluator_light_enabled`. See §9.5. |
| **Heavy Evaluator** | End-of-generation opus eval that consolidates all group findings, rewrites state of affairs, updates clusters, coverage matrix, and solution-idea map. |

All other docs (`CLAUDE.md`, `description.md`, `helpers/README.md`, agent prompts) MUST
use these exact terms.

---

## 11. Cross-reference table — code ↔ doc ↔ prompt

When you change a row, update every cell in that row. The `scripts/check_docs_consistency.py`
script verifies the references resolve.

| Behavior | Code | Doc | Agent prompt |
|---|---|---|---|
| `concurrency` budget parsing | `orchestrator.py:concurrency_budget()`, `problems/_shared/constants.py:DEFAULT_CONCURRENCY` | this guide §9.1 | `architect.md` § "Parallel groups" |
| `parallel_groups` honoring | `orchestrator.py:_normalize_parallel_groups()` | this guide §9.1 | `architect.md` § "What You Produce" |
| Eval queue | `problems/_shared/eval_queue.py`, `problems/_shared/constants.py:EVAL_QUEUE_PATH` | this guide §9.2 | `_shared_eval_contract.md` § "Per-evaluation artifacts" |
| Same-agent kill | `eval_queue.kill_stale_same_agent()`, per-problem `eval_hooks.py:kill_eval` | this guide §9.2 | `_shared_eval_contract.md` § "Same-agent kill contract" |
| Proc logs | `problems/_shared/proc_log.py:Writer` | this guide §9.3 | `_shared_eval_contract.md` § "Reading failure logs" |
| Archive checkpoint | `metrics.yaml: archive_checkpoints`, helpers/core.py `archive_checkpoint`/`evaluate_from_checkpoint` | this guide §9.4 | per-problem `description.md` "Reproducing a scored solution" |
| Light Evaluator toggle | `metrics.yaml: evaluator_light_enabled`, `orchestrator.py:evaluator_light_enabled()`, `problems/_shared/constants.py:DEFAULT_EVALUATOR_LIGHT_ENABLED` | this guide §9.5 | `agents/evaluator_light.md` |
| Identity env vars | `problems/_shared/constants.py:ENV_AGENT_NAME` etc., `orchestrator_harness._build_env` | this guide §9.2 | (transparent to agents) |
| Kaggle competition import | `scripts/new_kaggle_problem.py`, `problems/_kaggle_template/`, `problems/_shared/constants.py:KAGGLE_*` | this guide §13 | (transparent to agents) |
| Kaggle classification manifest | `problems/<id>/data/.kaggle_spec.yaml`, `scripts/check_docs_consistency.py:check_kaggle_specs()` | this guide §13.3 | (operator-facing) |

---

## 12. Single source of truth for constants

All cross-cutting paths, env-var names, and timeouts live in
`problems/_shared/constants.py`. Imports look like:

```python
from problems._shared.constants import (
    EVAL_QUEUE_PATH, GPU_LOCK_PATH,
    KILL_GRACE_SECONDS, KILL_DEADLINE_SECONDS,
    DEFAULT_CHECKPOINT_RETENTION, DEFAULT_CONCURRENCY,
    ENV_AGENT_NAME, ENV_PROBLEM, ENV_ATTEMPT,
)
```

**Never duplicate these as string literals in evaluate.py, helpers, or docs.** The
consistency checker walks code + docs and fails if a constant name appears in a doc
without resolving from `constants.py`.

---

## 13. Turning a Kaggle competition into a problem

Kaggle competitions are a rich source of well-scoped optimization tasks with
clear scalar metrics. The orchestrator has no Kaggle awareness — the integration
lives entirely at the problem-author layer. This section is the canonical recipe.

The reference implementations are:

- **Skeleton:** [`idea-evolve/problems/_kaggle_template/`](../idea-evolve/problems/_kaggle_template/)
- **Worked example (Class A):** [`idea-evolve/problems/megaminx/`](../idea-evolve/problems/megaminx/)
- **Scaffolding script:** [`idea-evolve/scripts/new_kaggle_problem.py`](../idea-evolve/scripts/new_kaggle_problem.py)
- **Submit-to-Kaggle (opt-in):** [`idea-evolve/scripts/submit_to_kaggle.py`](../idea-evolve/scripts/submit_to_kaggle.py)

### 13.1 Classification first

Every Kaggle competition is one of five classes. Classify before you write any
code — the answer drives every later decision.

| Class | Definition | Local-eval fidelity | Recommended |
|---|---|---|---|
| **A** | Test set downloadable AND metric is self-checking from inputs alone (Megaminx, optimization, search) | Perfect — local = Kaggle | ✅ Ideal |
| **B** | Test set downloadable AND ground-truth labels released | Perfect — reproducible | ✅ Ideal |
| **C** | Test inputs downloadable, labels hidden; large train set available (most prediction comps) | Good with holdout | ✅ With care |
| **D** | Code/notebook-only, or server-side synthetic test (RL, ARC Prize) | None unless simulator replicated | ⚠️ Only if simulator is reproducible |
| **E** | TOS-gated, proprietary data, redistribution-blocked | N/A | ❌ Skip |

If the answer is E, stop. Don't proceed.

### 13.2 TOS and credentials

1. **Accept the rules** on `kaggle.com/competitions/<comp_id>/rules` — click
   "Understand and Accept". Without this, every download returns HTTP 403.
2. **Get a token** at `kaggle.com/settings → Create New API Token` (downloads
   `kaggle.json`).
3. **Store it** in the project `.env` (see [CLAUDE.md § Secrets](../CLAUDE.md))
   as `KAGGLE_API_TOKEN=KGAT_...`. Load with `set -a && source .env && set +a`
   before running any Kaggle-touching script.
4. The constant name `KAGGLE_API_TOKEN_ENV` is exported from
   `problems/_shared/constants.py`. Read the env var via that name in code.

### 13.3 The `.kaggle_spec.yaml` contract

Every Kaggle problem ships a committed manifest at
`problems/<id>/data/.kaggle_spec.yaml`. Even when the data payload is gitignored
(see §13.4), this file commits — it is the source of truth for what
competition the problem mirrors. Schema:

```yaml
competition_id: cayley-py-megaminx          # Kaggle URL slug
classification: A                            # A | B | C | D
local_eval_strategy: self_check              # self_check | holdout_split | simulator | submit
primary_metric_name: sum_path_length
primary_metric_direction: lower_is_better
primary_metric_kaggle_leaderboard_top: 80499
downloaded_at: 2026-04-16T19:30:00Z
file_hashes:
  puzzle_info.json: sha256:...
  test.csv: sha256:...
  sample_submission.csv: sha256:...
holdout_spec: null                           # only for class C
simulator_spec: null                         # only for class D
tos_accepted_by: sasha
tos_accepted_at: 2026-04-16T19:30:00Z
```

`scripts/check_docs_consistency.py:check_kaggle_specs()` validates the
classification + strategy on every spec.

### 13.4 Data acquisition

```bash
cd idea-evolve
python3 scripts/new_kaggle_problem.py <kaggle_id> <problem_id> --class A|B|C|D
```

What it does:

- Copies `problems/_kaggle_template/` → `problems/<problem_id>/`.
- Runs `kaggle competitions download -c <id> -p problems/<id>/data/ --unzip`.
- Catches HTTP 403 → prints TOS-acceptance instructions.
- Warns if data > 1 GB.
- Writes `data/.kaggle_spec.yaml` with `competition_id`, `classification`,
  UTC timestamp, and per-file sha256.

**The data dir is gitignored** via `idea-evolve/problems/*/data/` in the repo
root `.gitignore`, with `!.../data/.kaggle_spec.yaml` to negate the spec.
Operators on each machine must download for themselves; the spec lets them
verify the bytes match.

To pull updated competition data later:

```bash
python3 scripts/new_kaggle_problem.py --refresh <problem_id>
```

This re-downloads, diffs hashes, prints a warning if anything changed, and tells
the operator to clear `runs/<id>/*/history/eval_cache.json` so cached scores
get recomputed against the new data.

### 13.5 Solution interface

Every Kaggle problem's `entrypoint()` returns a Python dict in whatever shape
the domain expects — `{puzzle_id: path}` for Megaminx, `{image_id: class}` for
classification, `{row_id: probability}` for tabular, etc.

`evaluate.py` does the translation to a Kaggle-equivalent score using
`helpers.core.score_predictions()`. **Never write a Kaggle-format
`submission.csv` during evaluation** — that's only for `submit_to_kaggle.py`
and lives in `helpers/core.write_submission()`.

### 13.6 Metric mapping to `metrics.yaml`

| Kaggle behavior | metrics.yaml field |
|---|---|
| "Higher is better" (accuracy, AUC, F1) | `higher_is_better: true`, `sentinel_value: 0` |
| "Lower is better" (RMSE, log-loss, path length) | `higher_is_better: false`, `sentinel_value: 1000000000` |
| Display direction in dashboard | `lower_bound`/`upper_bound` set to the LB range |
| Round-off for display | `decimals` |
| Threshold for "real" improvement | `significant_change` (rendered as `~` if smaller) |

**Sentinel for lower-is-better must be very large** — see §13.10.

### 13.7 Class C (holdout) discipline

When the test labels are hidden, you cannot evaluate locally against the real
test set. Three rules to keep your local score honest:

1. **Split the train set once** with a fixed seed committed to the spec:
   ```yaml
   holdout_spec:
     train_file: train.csv
     split_ratio: 0.85
     split_seed: 17
     split_strategy: stratified_by_class   # or random, time_based, group_kfold
   ```
2. **Never let `evaluate.py` touch `test.csv`** — it has no labels; any
   "score" computed against it is meaningless. Only `helpers.core.write_submission()`
   reads it (and only when `submit_to_kaggle.py` is invoked).
3. **Periodically calibrate** by submitting top-5 solutions monthly via
   `scripts/submit_to_kaggle.py`. Record the local-vs-public score gap in
   `runs/<id>/<attempt>/kaggle_submissions.jsonl` (the script does this).

### 13.8 Class D (simulator) guidance

If the competition's evaluation requires running a simulator (RL, code-eval),
you have two options:

- **Replicate the simulator locally** if it's small and well-specified
  (Halite-style envs, simple games). Place it in `helpers/simulator.py` and
  have `evaluate.py` call it on every agent output. Spec the location:
  ```yaml
  simulator_spec:
    module_path: helpers.simulator
    entrypoint: run
    install_hint: "pip install halite-engine==2.0"
  ```
- **Skip** if the simulator is complex, slow, or requires Kaggle infrastructure
  (notebook-only competitions, ML-judging competitions). The Kaggle competition
  is not a good idea-evolve problem in that case.

### 13.9 Proxy vs full eval (universal pattern)

Most Kaggle test sets are too large for every-solution evaluation. The
universal pattern (matches strawberry's Mode 1 vs Mode 2):

- `helpers/core.py` exports `PROXY_SIZE` and `FULL_SIZE` constants.
- `entrypoint()` itself decides which mode by passing `proxy=True/False` to
  `helpers.core.load_test()`.
- `evaluate.py` exposes only an operator-facing `--full` override (used by
  `submit_to_kaggle.py` and manual re-scoring).

Why solution-driven (not env/CLI): both alternatives break content-hash cache
coherence. Same bytes must always produce the same score, or the cache lies.

### 13.10 Sentinel for `lower_is_better`

Use **`1_000_000_000` (1e9)**. The orchestrator's `update_rankings()` filters
with `not higher_better and score >= sentinel * 0.9`. Real scores must be
comfortably below the filter — leave at least 3 orders of magnitude of buffer
above the realistic worst case.

For `higher_is_better: true`, the sentinel is `0` (matches existing problems).

### 13.11 Submit-to-Kaggle (opt-in only)

```bash
python3 scripts/submit_to_kaggle.py <problem_id> <solution.py> [--message TEXT]
```

- Calls `entrypoint()` with `full=True`.
- Calls `helpers.core.write_submission(predictions, path)` to produce the CSV.
- Submits via `kaggle competitions submit`.
- Polls until scored, returns the public LB score.
- Logs `{timestamp, solution, public_score}` to
  `runs/<id>/<latest_attempt>/kaggle_submissions.jsonl`.

**Never call from `evaluate.py`.** Kaggle rate-limits submissions (typically
5/day). Operator-controlled only.

### 13.12 Edge cases

- **Big datasets (>1 GB):** the scaffold script warns; consider a partial-load
  helper that streams instead of materializing.
- **External-data rules:** some competitions forbid extra training data.
  Document any such restriction in `problems/<id>/initial_facts.md` so
  agents know.
- **Mid-competition test-set updates:** `--refresh` diffs hashes and tells you
  to clear the eval cache.
- **Library cache races:** if your problem uses a library that downloads
  models on first run (cayleypy, HuggingFace, ultralytics), pre-warm the cache
  during scaffolding so parallel agents don't race on first eval.
- **GPU access:** Kaggle problems default to `concurrency: 0` (unlimited) on CPU.
  If a problem grows GPU-dependent without NVIDIA MPS, follow §9 (declare
  `concurrency: 1`, ship `eval_hooks.py`, acquire `GPU_LOCK_PATH`). If MPS is
  available, `concurrency: N` with N matching the desired per-process memory
  slice is usually the better trade-off.

### 13.13 Resource-aware scheduling (roadmap, not yet implemented)

Some Kaggle problems will eventually have *mixed* compute needs: a baseline
that runs in 2 seconds on CPU plus an experimental beam-search variant that
needs 3 minutes on GPU. The current scalar `concurrency: N` budget is a
single pool — it can't express "run 4 CPU agents in parallel + 1 GPU agent
in the same group" without conservatively capping the whole generation at
the GPU-slot count. Tracked as **DESIGN-18** in CLAUDE.md.

Planned schema (NOT YET ACTIVE):

```yaml
resources:
  pools:
    cpu: 8                # max simultaneous CPU-only evals
    gpu: 1                # max simultaneous GPU evals
  per_agent_hints:
    explore: cpu          # the architect colocates this in a CPU slot
    full: gpu             # the architect places this in the GPU slot
```

Until DESIGN-18 lands, Kaggle problems should pick one scalar
`concurrency:` value (0 for CPU-unlimited, 1 for GPU-without-MPS, N for
GPU-with-MPS or other bounded pools) and let the backstop locks handle
any residual contention.

### 13.14 Quick checklist for a new Kaggle problem

- [ ] Classified (A/B/C/D); E means stop.
- [ ] TOS accepted on kaggle.com.
- [ ] `KAGGLE_API_TOKEN` in `.env`.
- [ ] `python3 scripts/new_kaggle_problem.py <kaggle_id> <id> --class X` ran cleanly.
- [ ] `data/.kaggle_spec.yaml` filled (no remaining `<REPLACE>`).
- [ ] `description.md` placeholders all replaced.
- [ ] `metrics.yaml` has correct direction + sentinel (1e9 for lower-is-better).
- [ ] `helpers/core.py:load_test()` and `score_predictions()` implemented.
- [ ] `helpers/README.md` reflects the actual symbol set.
- [ ] At least one `initial_programs/baseline_*.py` produces `is_valid=1`.
- [ ] `python3 scripts/check_docs_consistency.py` exits 0.
- [ ] `python3 orchestrator.py . --problem <id> --new-attempt --dry-run` succeeds.
- [ ] `python3 problems/<id>/evaluate.py problems/<id>/initial_programs/baseline_*.py` returns valid JSON.
