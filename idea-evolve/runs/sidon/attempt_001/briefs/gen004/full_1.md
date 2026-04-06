## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 102 (Singer q=101 truncation)
Second best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank02_69.py` → fitness = 69 (Fibonacci ordering greedy)
Non-algebraic ceiling: 69. All top-tier solutions are identical Singer q=101 constructions.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_013.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/experiment_suggestions/gen003.md` (read EXP-2 carefully — the ILP formulation)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/system_recommendations.md` (read REC-5 carefully — ILP formulation details)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` (the 102-element Singer set — you will need the actual elements)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/description.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/singer.py`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py`

## Dead Ends — DO NOT pursue these
- Singer q=101 perturbation (any k, any removal strategy): 4000+ trials, all ≤ 102. Proven futile — 45+ minimum blockers per non-member.
- SA from any seed (Singer, ET, Fibonacci, random): Zero improvement in any trial. SA does not work for Sidon sets.
- Randomized greedy restarts: Ceiling 63, worse than deterministic greedy (66).
- Probabilistic alteration: Ceiling 63. Debunked.
- Singer perturbation + greedy extend: Zero net gain after removal + extension. Debunked.

## CRITICAL: Stale fact files warning
`/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/fact_002.md` says upper bound is "~100-102" — THIS IS WRONG. The correct upper bound is ~109 (Carter/Hunter/O'Bryant 2023).
`/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/fact_004.md` says validator extracts valid subsets — THIS IS WRONG. Invalid solutions get sentinel score 0 with no partial credit.
Ignore these fact files. Trust the state of affairs and this brief.

## Directive

**ILP / Constraint Programming for Sidon sets.** This is the highest-priority untested approach. One previous attempt (gen 3, explore_2) used the wrong formulation (quadruple constraints — 661K constraints for M=200, crashed CBC in 24s). You must use the CORRECT formulation.

### Step 1: Implement the difference-indicator ILP formulation

Use OR-Tools CP-SAT (preferred) or PuLP. The correct formulation:

```
Variables: x_i ∈ {0,1} for i in {0,...,N}
Objective: maximize sum(x_i)
For each difference d in {1,...,N}:
    sum over a in {0,...,N-d} of (x_a AND x_{a+d}) <= 1
    i.e., at most one pair of elements can have difference d
```

In CP-SAT, the AND constraint can be encoded as: for each d, create auxiliary bool vars z_{d,a} = x_a AND x_{a+d}, then add sum(z_{d,a}) <= 1.

Alternatively, a simpler encoding that CP-SAT handles well:
```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()
x = [model.NewBoolVar(f'x_{i}') for i in range(N+1)]
model.Maximize(sum(x))

for d in range(1, N+1):
    pairs_with_diff_d = []
    for a in range(N + 1 - d):
        z = model.NewBoolVar(f'z_{d}_{a}')
        model.AddBoolAnd([x[a], x[a+d]]).OnlyEnforceIf(z)
        model.AddBoolOr([x[a].Not(), x[a+d].Not()]).OnlyEnforceIf(z.Not())
        pairs_with_diff_d.append(z)
    model.Add(sum(pairs_with_diff_d) <= 1)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = time_limit
status = solver.Solve(model)
```

### Step 2: Validate at small N first

Test at N=50, N=100, N=200 to:
1. Verify your formulation produces valid Sidon sets
2. Compare ILP optimal size vs Singer construction size for each N
3. Measure solve time scaling

For N=50: Singer q=7 gives 8 elements. ILP should find 8 (confirming Singer optimality at this scale).
For N=100: Singer q=9-ish. Check if ILP matches or beats Singer.

### Step 3: Scale up

Try N=500, N=1000, N=2000 with increasing time limits (30s, 60s, 120s, 300s).
Record: optimal size found, solve time, solver status (optimal vs feasible vs timeout).

### Step 4: Attempt N=10000

Run CP-SAT on N=10000 with a 600-second time limit. If it finds a feasible solution better than 102, that's a breakthrough. Even a feasible solution of 103 is a major result. If it only finds ≤102, record the best bound the solver achieved.

**Warm start**: If CP-SAT supports solution hints, provide the 102-element Singer set as a hint. The elements are in `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` (the SINGER_SET list).

### Step 5: Package the best result

Your `entrypoint()` must return the best Sidon set found. If ILP beats 102, return the ILP solution. If not, return the Singer 102 set as baseline.

Run `python3 evaluate.py output/sol01.py` after each solution to verify and get the `.score` file. Write the score as a comment at the top of each solution file.

### Additional notes
- If OR-Tools is not installed, install it: `pip install ortools`
- If CP-SAT is too slow, try a simpler encoding: for each d, add pairwise exclusion constraints directly (x_a + x_{a+d} + x_{a'} + x_{a'+d} <= 3 for each pair of pairs with same d). This has O(N²) constraints per d but CP-SAT propagation may handle it.
- Test at N=100 BEFORE N=10000. A broken formulation at N=100 saves hours vs discovering it at N=10000.
