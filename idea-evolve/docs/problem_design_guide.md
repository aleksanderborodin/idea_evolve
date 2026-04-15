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

Track eval time explicitly. Set `track_eval_time: true` in metrics.yaml; the orchestrator
records `eval_time_s` in every `.score`. Sudden slowdowns indicate a regression in the
helper code or an agent that turned off caching.

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
track_eval_time: true
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
