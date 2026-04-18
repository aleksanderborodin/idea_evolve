# System Recommendations — Generation 1

Ranked by expected impact on pipeline's ability to reach the target (15000).

---

## REC-1: Fix beam solver helper to expose predictor kwarg (CRITICAL)

**What to change:** `helpers/core.py` — add `predictor` parameter to `cayleypy_beam_solver()`, passing it through to `graph.beam_search(predictor=predictor)`.

**Why:** The primary path to the target (predictor-guided beam search) is confirmed viable but blocked by helper friction. Agents using the documented entry point cannot access the predictor. The direct API call exists but isn't discoverable without reading cayleypy source.

**Expected impact:** Enables all solution agents to try predictor-guided search with one line of code. Expected to unlock the 30%+ improvement needed to approach the target.

---

## REC-2: Assign an experimentator to run the hamming predictor baseline (CRITICAL)

**What to change:** Architect should allocate an `experimentator` in gen 2 with a narrow mandate: run `Predictor(graph, 'hamming')` on all 101 proxy puzzles, record fitness and timing. This is the zero-cost, zero-training-data experiment that establishes whether guided search adds any value over compression.

**Why:** We don't know if even the simplest predictor helps. This single experiment answers the yes/no question that unblocks all subsequent predictor work. Without it, we can't calibrate expected gains.

**Expected impact:** If hamming predictor doesn't beat compression → we know learned predictors are necessary. If it does beat compression → we have a cheap baseline and the path to target is clearer.

---

## REC-3: Fix initial_facts.md hardware contradiction (MODERATE)

**What to change:** `problems/megaminx/initial_facts.md` — remove the CPU-only block, confirm GPU + MPS parallelism is the correct hardware description. Remove any ambiguity about whether CUDA is available.

**Why:** Agents reading conflicting information may form incorrect assumptions about hardware capabilities. `research_1` correctly identified GPU as available but unused, but an agent following the wrong block might not know to use CUDA.

**Expected impact:** Prevents agent confusion, ensures hardware utilization strategy is consistent.

---

## REC-4: Fix helpers/README.md PROXY_SIZE typo (MINOR)

**What to change:** `problems/megaminx/helpers/README.md` — change `PROXY_SIZE = 100` to `PROXY_SIZE = 101`.

**Why:** Three agents noted the inconsistency. Actual code is correct; the README misleads agents who read it.

**Expected impact:** Minor reduction in agent confusion.

---

## REC-5: Surfaced growth function implications in agent briefs (MODERATE)

**What to change:** Brief templates or `initial_facts.md` should explicitly state the strategic implication: "unguided beam search is mathematically impossible for hard/very_hard buckets (depth 8 = 3.5B states). Do not attempt unguided beam search for depth > 6."

**Why:** Multiple agents spent time on unguided beam search despite the growth function proving it futile. The information existed but wasn't incorporated into strategy. Surfacing the implication prevents wasted iterations.

**Expected impact:** Agents in gen 2 will not revisit unguided beam search; they can spend that time on predictor implementation instead.

---

## REC-6: Widen research agent timeout or narrow scope (MODERATE)

**What to change:** Either (a) increase `timeouts.research` from 1800s to 3600s, or (b) have research agents focus on ONE specific notebook or API verification rather than broad research + multiple experiments.

**Why:** `research_1` ran out of time before running the ML pipeline. The research was valuable (confirmed API, documented growth function) but the critical predictor experiment was left untested. Narrower scope or more time would let research agents finish at least one experiment.

**Expected impact:** More complete research outputs; fewer critical experiments left unfinished.

---

## REC-7: Add beam search diagnostic logging to helper (MINOR)

**What to change:** `helpers/core.py` — when `cayleypy_beam_solver` returns, log whether beam_search returned None, returned a longer path than compression, or returned a shorter path. Record the outcome in a structured way agents can read.

**Why:** No agent diagnosed WHY beam search failed. Diagnostic output would let future agents understand the failure mode without re-running the same experiments.

**Expected impact:** Faster iteration; less repeated diagnostic work.