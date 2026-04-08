# Observations — gen006_full_1

## Summary

No improvement over the 105-mark baseline. All solutions return fitness=105. Four approaches
were tried, all generating significant new information about the problem structure.

## Solution Scores

| File   | Fitness | Approach |
|--------|---------|----------|
| sol01.py | 105 | 105-mark Rokicki-Dogon baseline (instant) |
| sol02.py | 105 | CP-SAT k=106 with 105-mark hint (UNKNOWN after 1200s + 600s) |
| sol03.py | 105 | VLNS: fix 85 elements, find 21 via CP-SAT (INFEASIBLE in <1s each) |
| sol04.py | 105 | Binary search on N for k=106 (UNKNOWN at N=10000–15000, 120s each) |

## Key Findings

### 1. CP-SAT k=106 still UNKNOWN after 1200s (sol02)
The full k=106 problem with 105-mark hint returned UNKNOWN after 1200s (16 workers).
A second 600s run with `linearization_level=2, symmetry_level=2` also returned UNKNOWN.
Also notable: k=104 with 30s timeout returned UNKNOWN — the formulation may have high
difficulty even for tractable sub-cases.

### 2. VLNS reveals the 105-mark set is extremely constrained (sol03)
**Critical new finding:** All 9 VLNS trials returned INFEASIBLE (not UNKNOWN) in < 1 second.

VLNS approach: remove 20 elements from S105 (leaving 85 fixed), then use CP-SAT to find 21
replacements. This gives a subproblem with only 21 free variables vs 106 in the full problem.

Despite the much smaller search space, CP-SAT proved INFEASIBLE immediately via presolve.
Error: "INFEASIBLE: linear: never in domain" — domain propagation reduces some difference
variable's domain to empty during presolve.

**Interpretation:** The 85-element subsets of the 105-mark set are so "difference-saturated"
that no 21 additional elements can possibly coexist with them while maintaining the Sidon
property — at least for the 9 removal patterns tried (random-20, random-15, random-25,
high-density-20, spread-20).

This is either:
(a) The 105-mark set is provably "k-critical" — any 85-element subset cannot be extended to 106
(b) The VLNS formulation has a bug causing false INFEASIBLE reports

The "linear: never in domain" error points to the `add_abs_equality` constraint for cross
differences. A possible bug: if y[i] == f for some fixed element f, then |y[i] - f| = 0,
which is outside the domain [1, N]. Since we added `y[i] != f` constraints, but CP-SAT's
domain propagation may not see this immediately. The presolve may be hitting a domain of
[0, 0] before the != constraint fires.

**Likely the VLNS formulation has a bug** — the `add_abs_equality` before `y[i] != f`
constraints may produce domain [0, 10000] which includes 0, but the diff domain starts at 1.
If y[i] = f is still in domain during presolve, the abs difference can be 0, which is
excluded by domain, causing INFEASIBLE.

This needs to be fixed by either:
- Adding lower bound constraint: `y[i] != f` as a hard constraint BEFORE diff domain
- Using domain [0, N] for diff vars (allowing 0) and handling 0 separately
- Starting free var domain explicitly excluding fixed elements

### 3. Binary search on N shows k=106 is hard even for larger N (sol04)
CP-SAT returned UNKNOWN for k=106 at N=10000, 10200, 10500, 11000, 12000, 15000 (120s each).
Even at N=15000 (50% larger search space), no feasible k=106 set found in 120s.
This suggests the difficulty is not primarily due to the tight N=10000 bound.

## What This Tells Us

1. **VLNS formulation bug**: The INFEASIBLE results from sol03 are likely false due to a
   constraint modeling issue with `add_abs_equality`. This approach is worth retrying
   with a corrected formulation.

2. **CP-SAT is fundamentally slow on this problem**: Even 1800s of compute cannot find
   k=106. The search tree structure may require hours or commercial solvers (Gurobi).

3. **k=106 may genuinely not exist at N=10000**: The combination of algebraic ceiling=105
   and CP-SAT's inability to find k=106 even at N=15000 in 120s suggests it may be infeasible.
   However, 120s is insufficient to prove infeasibility — INFEASIBLE vs UNKNOWN matters.
