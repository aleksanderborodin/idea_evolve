# System Recommendations — Generation 2

Ranked by expected impact on pipeline's ability to reach the target (15000 proxy moves).

---

## REC-1: Fix the trained-predictor end-to-end experiment (CRITICAL)

**What to change:** The pipeline needs one agent that RUNS the trained MLP predictor experiment, end-to-end, in gen 3. This is not a helper fix or a documentation fix — it is an execution mandate.

**Why:** idea_008 has 0 central uses after 2 generations. The trained predictor is the primary path to the target. Every generation without it is a wasted generation.

**How:**
1. The Architect MUST assign at least one agent (exploit or full) to: (a) generate training data via `graph.random_walks(width=50000, length=20, mode='bfs')`, (b) train a tiny MLP, (c) run `beam_search(predictor=predictor)` on hard/very_hard buckets, (d) compare to 44114 compression floor.
2. Give this agent a longer timeout (3600s) and a MANDATORY produce-something rule: if the first attempt fails with the state encoding error, iterate until it works.

**Expected impact:** If successful, this experiment determines whether trained-predictor beam search can beat 44114. If it cannot, we need a different architecture. If it can, we have a path to the target.

---

## REC-2: Add a trained_predictor_beam_search helper (CRITICAL)

**What to change:** `problems/megaminx/helpers/core.py` — add a new function:

```python
def trained_predictor_beam_search(state, depth=20, nWalks=50000, beam_width=4096, max_steps=80):
    """Train a tiny MLP on random walks and run predictor-guided beam search.
    
    Returns: (compressed_path, beam_path, fitness)
    - state: starting state (list of ints)
    - depth: random walk depth for training data
    - nWalks: number of random walks
    - beam_width: beam search width
    - max_steps: max beam search depth
    
    Raises if state encoding fails.
    """
```

**Why:** exploit_1 hit the state encoding error (`rshift_cuda` on float) because no documented wrapper exists. Every agent must rediscover the cayleypy integration details. A single working helper with device-placement handling unlocks the primary path.

**Expected impact:** Eliminates the #1 friction point blocking the primary direction.

---

## REC-3: Fix experimentator role — give it concrete experiments (CRITICAL)

**What to change:** The architect prompt for experimentators should mandate specific experiments from `experiment_suggestions.md`, not vague "run experiments." The gen_002 experimentator was given no specific task and produced nothing.

**Why:** The experimentator role has a full agent slot and GPU access. When it produces nothing, that slot is wasted.

**How:** gen_003 architect should assign the experimentator ONE specific experiment:
- EXP-A: Trained MLP Predictor Baseline (from research_1's suggestions) — train on depth-20 walks, test on proxy, compare to 44114.
- The experimentator should NOT be given a stop request until it produces output.

**Expected impact:** The experimentator runs the critical trained-predictor experiment while solution agents work on other approaches.

---

## REC-4: Document beam_mode='advanced' bug in helper docs (HIGH)

**What to change:** `problems/megaminx/helpers/README.md` and `helpers/core.py` docstring — add:

> **NOTE:** `beam_mode='advanced'` is ~2x faster but has a bug where `return_path=True` returns `path=None` even when `path_found=True`. Always use `beam_mode='simple'` when you need the actual path.

**Why:** research_1 confirmed this bug but it wasn't written to a knowledge file. Agents using 'advanced' mode get silently empty paths.

**Expected impact:** Prevents agents from using the fast-but-broken mode and spending time debugging why their beam search produces no output.

---

## REC-5: Fix documentation inconsistencies (HIGH)

**What to change:**
1. `problems/megaminx/description.md` — remove "CPU-only" claim; confirm GPU + CUDA auto-detection.
2. `problems/megaminx/helpers/README.md` — change `PROXY_SIZE = 100` to `PROXY_SIZE = 101`.
3. Orchestrator — stop referencing non-existent `runs/.../problem/` files in briefs.

**Why:** Three agents noted these inconsistencies. The architect explicitly flagged them. These are easy fixes that prevent agent confusion.

**Expected impact:** Minor reduction in agent confusion; agents spend less time verifying basic facts.

---

## REC-6: Add string-replacement warning to helper docs (MODERATE)

**What to change:** `problems/megaminx/helpers/README.md` — add a warning section:

> **DANGER: Never use string replacement for move sequences.**
> Python string `.replace()` on dot-joined paths creates empty move names at pattern boundaries. Example: `U.-U.-U` replacing `U.-U` gives `.-U` which splits to `['', '-U']` → `unknown move '-'`.
> Always use move-list manipulation: split the path string into a list, apply rules element-by-element, join the result.

**Why:** explore_2/sol04 failed this way. All agents independently discovered the danger. It's preventable with documentation.

**Expected impact:** Prevents one class of solution failures.

---

## REC-7: Combine compression + beam search in next agent (MODERATE)

**What to change:** The next exploit or full agent should use empirical identity compression (336 rules from explore_2/sol01) to get baseline paths, then run trained-predictor beam search on the compressed paths.

**Why:** Compression gets paths to 0.8723 ratio. Starting beam search from already-short paths is much easier than from raw sample_submission. This is the most promising order of operations and no agent has tried it.

**Expected impact:** If the trained predictor works, this combination should beat pure compression.

---

## REC-8: Add eval_hooks.py for Megaminx (LOW)

**What to change:** Create `problems/megaminx/eval_hooks.py` similar to strawberry's, with:
- Diagnostic path `/tmp/idea_evolve_megaminx/`
- `diagnose_failure()` function
- Basic kill hook (killpg SIGTERM → SIGKILL)

**Why:** If a solution crashes, there's no log_path in the `.score` file. agents can't read crash diagnostics.

**Expected impact:** Agents can diagnose failures without re-running.

---

## Previously Filed Recommendations (Status Update)

| REC | Status | Notes |
|-----|--------|-------|
| REC-1 (beam solver helper fix) | PARTIAL | helpers/core.py still doesn't expose `predictor` kwarg |
| REC-2 (hamming predictor baseline) | DONE | research_1 debunked hamming — zero advantage |
| REC-3 (fix hardware contradiction) | NOT DONE | description.md still says CPU-only |
| REC-4 (fix PROXY_SIZE typo) | NOT DONE | helpers/README.md still says 100 |
| REC-5 (surface growth function implications) | PARTIAL | agents still trying unguided beam search |
| REC-6 (widen research timeout) | PARTIAL | still 1800s |
| REC-7 (beam search diagnostic logging) | NOT DONE | no diagnostic output |

**Only REC-2 (hamming predictor) has been resolved.** All others remain open.

---

## Priority for gen_3

1. **REC-1 + REC-3:** trained-predictor experiment MUST run in gen 3. Assign to experimentator or a dedicated exploit/full agent.
2. **REC-2:** Add the helper wrapper that eliminates state encoding friction.
3. **REC-4:** Fix the 'advanced' mode bug documentation.
4. **REC-5:** Fix the three documentation inconsistencies.
5. **REC-6:** Document the string replacement danger.

The pipeline cannot reach the target without the trained-predictor experiment running. Every generation that skips it is a generation lost toward the 15000 target.