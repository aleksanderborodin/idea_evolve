## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 105 (Bose-Chowla ap q=107, mul=433)
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/top/rank02_105.py` → fitness = 105

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md` — Strategic overview
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_004.md` — Exact methods cluster (CP-SAT history)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/reports/gen006/full_1.md` — Gen 6 CP-SAT attempts (AllDifferent, VLNS, binary search on N)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/feedback/system_recommendations.md` — REC-5 (do NOT use AllDifferent formulation)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/feedback/experiment_suggestions/gen006.md` — EXP-3, EXP-4, EXP-5 (binary CP-SAT, anti-algebraic, maximize-k)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/helpers/rokicki_data.py` — BEST_105 (the 105-mark set for warm-start hint)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py` — is_sidon, count_violations (for validation)
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/sidon/attempt_001/population/best.py` — The 105-element Bose-Chowla set

## Directive

**Implement CP-SAT with a BINARY VARIABLE formulation and maximize-k objective. This is a
completely different formulation from all previous attempts (which used AllDifferent over
integer difference variables and failed across 6000+ seconds of compute).**

### Formulation (binary variable, maximize-k)

```
Variables: x_i in {0, 1} for i in {0, 1, ..., 10000}
Objective: MAXIMIZE sum(x_i)

Sidon constraint: For all quadruples (a, b, c, d) where a < b, c < d, (a,b) != (c,d),
and a + b = c + d:
    x_a + x_b + x_c + x_d <= 3

This means: you cannot have all four elements in the set (which would create
two pairs with the same sum).
```

**Warm-start hint**: Set `x_i = 1` for all i in the 105-mark set, `x_i = 0` otherwise.
This gives CP-SAT an immediate incumbent of 105.

**Key insight**: The AllDifferent formulation required 5565 difference variables and was
pathologically hard for CP-SAT presolve. The binary formulation has 10001 binary variables
with O(N^2) forbidden-tuple constraints. CP-SAT may handle binary propagation + cutting
planes much better than domain-based AllDifferent.

### Constraint generation

The number of forbidden 4-tuples is large (~N^2/2 pairs of pairs with equal sums). You MUST
generate them efficiently:
- For each possible sum s in {0, ..., 20000}:
  - Enumerate all pairs (a, b) with a <= b and a + b = s
  - For each pair of pairs with the same sum, add constraint x_a + x_b + x_c + x_d <= 3
- Use symmetry: each constraint covers both orderings

**WARNING**: With N=10000, there are ~25M pair-sum collisions. Adding all as individual
constraints may overwhelm the solver. Optimization strategies:
- Only add constraints for sums s that have >= 2 pairs (skip unique sums)
- For sums with many pairs (e.g., s=10000 has ~5000 pairs), the number of pairwise constraints
  is O(k^2) where k = #pairs. Consider: for each sum s with k pairs, add a single constraint
  `sum of x_a, x_b over all pairs ≤ k + (k-1)` — but this is weaker. Better: use the
  at-most-one encoding for each sum (at most one pair from each sum can be fully present).

Alternative constraint encoding: For each sum s, define pair indicator variables p_{a,b} = x_a * x_b.
Then add AllDifferent or at-most-one over p_{a,b} for each s. This may be more compact.

**If binary variable formulation is too large** (>50M constraints), fall back to:

### Fallback: Maximize-k with integer variables

Instead of "find exactly k=106" (feasibility, UNKNOWN for 3 gens), use:
- Integer variables y_0, ..., y_{k_max-1} with domain [0, N]
- Objective: maximize k_max (or use a large k_max=120 and maximize how many are "used")
- AllDifferent constraints on pairwise differences
- Hint: the 105-mark set

This is softer than the decision version — the solver gets gradient information.

### Phase plan

1. **Phase 1** (first 30 min): Implement and run binary variable CP-SAT maximize-k. Time limit: 1800s, 16 workers.
2. **Phase 2** (if Phase 1 produces 105 or UNKNOWN): Try anti-algebraic constraint:
   Add `sum(x_i for i in S_105) <= 52` (force ≤50% overlap with known 105-mark set).
   This forces the solver to search in a completely different region. Time limit: 900s.
3. **Phase 3** (if time remains): Try maximize-k with integer variables as described above.
   Time limit: remaining session time minus 3 minutes for evaluation.

### Output files

Write solutions to `output/sol01.py`, `output/sol02.py`, etc. Run `python3 evaluate.py output/solXX.py`
after each solution. Always include the 105-mark set as a fallback (`from helpers.rokicki_data import BEST_105`).

### What NOT to do

- Do NOT use the AllDifferent-over-differences formulation from gens 4-6. It has failed across
  6000+ seconds. REC-5 explicitly forbids it.
- Do NOT run CP-SAT as a feasibility problem for fixed k=106. Use maximize-k objective.
- Do NOT spend more than 5 minutes on formulation setup. The implementation matters more than
  perfecting the formulation on paper.
