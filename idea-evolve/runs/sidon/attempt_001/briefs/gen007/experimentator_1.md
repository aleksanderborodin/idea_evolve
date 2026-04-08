## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 105 (Bose-Chowla ap q=107, mul=433)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/top/rank02_105.py` → fitness = 105

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md` — Current strategic overview
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_004.md` — Exact methods cluster (CP-SAT, VLNS)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/reports/gen006/full_1.md` — VLNS formulation bug diagnosis (Phase 2 section)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/reports/gen006/exploit_1.md` — Self-healing property and perturbation evidence
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/feedback/system_recommendations.md` — REC-2 (VLNS fix), REC-3 (this task)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/feedback/experiment_suggestions/gen006.md` — EXP-1 (VLNS corrected formulation)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py` — Existing helper functions (is_sidon, can_add, etc.)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/helpers/rokicki_data.py` — Known best sets (BEST_105, BEST_104, BEST_102)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/helpers/extend.py` — Greedy extend, blocking power, perturbation utilities
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/best.py` — The 105-element Bose-Chowla set (use for testing)

## Directive

**MANDATORY TASK: Create `output/helpers/cpsat.py` — a shared CP-SAT helper module.**

This helper has been requested for **3 consecutive generations** (gen 4, 5, 6) and agents
keep re-deriving the CP-SAT formulation from scratch, introducing bugs each time. You must
build this helper this generation.

### Required functions

**Function 1: `solve_sidon_cpsat(k, N, hint=None, time_limit=300, num_workers=8)`**
- Standard CP-SAT formulation for finding a k-element Sidon set in {0, ..., N}
- Use **binary variable formulation**: `x_i in {0,1}` for each i in {0,...,N}, with constraint
  `sum(x_i) >= k` and Sidon constraints via forbidden 4-tuples (if i-j = k-l and {i,j} != {k,l},
  then x_i + x_j + x_k + x_l <= 3)
- Objective: maximize `sum(x_i)` (maximize-k, not decision for fixed k)
- `hint` is an optional list of integers (e.g., the 105-mark set) used as SolutionHint
- Returns: dict with `{"status": str, "solution": list[int] or None, "size": int, "time_s": float}`

**Function 2: `vlns_sidon(fixed_elements, n_free, N, time_limit=120, num_workers=8)`**
- Very Large Neighborhood Search: fix some elements of a known Sidon set, use CP-SAT to
  find replacements for the freed positions
- **CRITICAL BUG FIX**: The gen 6 VLNS had a formulation bug where `add_abs_equality(d, y[i] - fv)`
  used domain `[1, N]` for the difference variable. This caused INFEASIBLE in <1s for all 9 trials.
  The fix:
  1. Use domain `[0, N]` for difference variables (not `[1, N]`)
  2. Add explicit `model.Add(y[i] != fv)` constraints for each fixed element `fv` BEFORE
     the abs_equality constraint — this prevents the y[i]=fv case that makes abs_diff=0
  3. The rest of the formulation stays the same
- `fixed_elements`: list of integers to keep fixed
- `n_free`: number of free positions to fill (target total = len(fixed) + n_free)
- Returns: dict with `{"status": str, "solution": list[int] or None, "size": int, "time_s": float,
  "fixed_count": int, "free_count": int}`

**Function 3: `vlns_batch(base_set, removal_sizes, n_trials_per_size, N, time_limit_per_trial=30)`**
- Convenience wrapper: for each removal size k in `removal_sizes`, run `n_trials_per_size`
  trials with random removal of k elements from `base_set`, then VLNS to fill back + 1 extra
- Returns: list of trial results with removal pattern and outcome

### Self-test requirement

Include a `self_test()` function that runs:
1. `solve_sidon_cpsat(k=10, N=100, time_limit=30)` — should find a 10+ element set quickly
2. `vlns_sidon(fixed_elements=[0,1,3,7,12,20], n_free=2, N=50, time_limit=10)` — should find
   a feasible 8-element set (or at least not INFEASIBLE in <1s from a formulation bug)
3. Verify all returned solutions with `is_sidon()` from `helpers.core`

Run `self_test()` after writing the helper. If any test fails, debug and fix before finalizing.

### Output files

1. `output/helpers/cpsat.py` — The helper module (primary deliverable)
2. `output/report.md` — Debrief report

### What NOT to do

- Do NOT allocate compute to finding new Sidon sets. Your job is to build the tool, not use it.
- Do NOT modify any existing helper files. Write only to `output/helpers/`.
- Do NOT use the AllDifferent formulation — it has been proven pathologically hard for CP-SAT
  on this problem across 6+ runs and 5400+ seconds of compute.
