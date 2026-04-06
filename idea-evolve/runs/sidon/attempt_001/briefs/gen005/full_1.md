## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` -> fitness = 102 (Singer q=101 truncation)
Second best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank02_102.py` -> fitness = 102
**Target: 109. CP-SAT returned UNKNOWN for k=103 after 600s — not disproved.**

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_019.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_004.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/reports/gen004/full_1.md` (previous CP-SAT work — READ THIS CAREFULLY)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/gen004/full_1/sol01.py` (previous CP-SAT implementation)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/singer.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/experiment_suggestions/gen004.md` (see EXP-C and EXP-D)

## Directive

**Two-part mission: (A) Singer+1 structure analysis at small N, then (B) extended CP-SAT
run for k=103 at N=10000.**

### Part A: Singer+1 Structure Analysis (first ~30 minutes)

full_1 in gen 4 proved Singer is suboptimal for small N:
- N=56 (q=7): Singer=8, ILP optimal=10
- N=132 (q=11): Singer=12, ILP finds=13

Your job: **analyze the structure of these "extra" elements.**

1. Use the CP-SAT integer element formulation from gen 4's sol01.py. Reproduce the optimal
   sets for N=56 (k=10) and N=132 (k=13).

2. For each case, compute:
   - Which elements are in the ILP-optimal set but NOT in the Singer set?
   - Where do these extra elements fall relative to the Singer difference structure?
   - Do they fill specific gaps in the Singer difference set?
   - Is there a construction rule for the extras?

3. Extend to N=306 (q=17, Singer=18) — find the ILP optimal k. If k>18, analyze the extras.
   Also try N=552 (q=23, Singer=24) if time permits.

4. Write findings to `output/singer_plus_one_analysis.md`.

### Part B: Extended CP-SAT Run for k=103 (remaining session time)

After Part A, devote ALL remaining session time to finding a 103-element Sidon set in
{0, ..., 10000}.

1. Use the integer element formulation: k=103 ordered integer variables, C(103,2)=5253
   difference variables, AllDifferent constraint.

2. **Warm-start with the Singer q=101 set** (102 elements). Add one unconstrained variable
   for the 103rd element. This gives CP-SAT a feasible 102-element starting point.

3. **Try symmetry-breaking**: Fix e_0=0 (WLOG). Add constraint e_{102} <= 10000.

4. **Try search strategies**: If CP-SAT supports different search strategies
   (`cp_model.AUTOMATIC_SEARCH` vs `FIXED_SEARCH` vs `PORTFOLIO_SEARCH`), try multiple.
   Use `num_workers=8` or higher.

5. Run for as long as the session allows (you have 2700s timeout). If you get FEASIBLE,
   immediately write the solution and evaluate it. If you get INFEASIBLE, that's equally
   valuable — document it.

6. If CP-SAT is stuck at UNKNOWN after significant time, try:
   - k=104 (might have more solutions in the search space)
   - Different variable ordering (sorted by Singer position vs natural order)
   - Reducing N to find the smallest N where k=103 is feasible

7. Write all solutions to `output/sol*.py` and evaluate immediately.

### Important
- Read the gen 4 full_1 solution FIRST to avoid re-deriving the formulation from scratch.
- The CP-SAT formulation is: `model.NewIntVar(0, N, f'e_{i}')` for each element,
  ordering constraints `e[i] < e[i+1]`, difference vars `d[i][j] = e[j] - e[i]`,
  `model.AddAllDifferent(all_diffs)`.
- Every solution MUST be evaluated with evaluate.py before moving on.

### Available helpers
- `from helpers.core import is_sidon, count_violations, differences, can_add, is_prime`
- `from helpers.singer import singer_set` (if available — check the file)
