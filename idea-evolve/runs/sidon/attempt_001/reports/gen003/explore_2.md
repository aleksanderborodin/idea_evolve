# Debrief Report — Explore 2, Generation 3 (Resume Session)

> NOTE: This is a SECOND session for explore_2. The first session (which ran
> completely and whose outputs are in population/gen003/explore_2/) scored:
> sol01=63, sol02=0 (bug), sol03=67, sol04=65, sol05=68.
> This session adds sol05 (score=69) and sol06 (score=68) to the workspace.

## 1. What Did I Try?

| Solution | Approach | Score | Notes |
|----------|----------|-------|-------|
| sol05 | Wide Fibonacci/geo search + LNS | **69** | New best for pure search! |
| sol06 | SA with violation relaxation on 68-set | 68 | SA doesn't escape local optimum |

**Detailed findings:**

**sol05 (69)**: Searched Fibonacci(a,b) for 2400 parameter pairs (a∈[0,39], b∈[a+1,a+59])
plus geometric sequences (bases 1.3–3.0) and Wythoff sequence. Found that some Fibonacci
parameters give 69 elements (vs 68 from previous session's fib(3,13)). LNS on the 69-element
result gave no further improvement.

**sol06 (68)**: SA on the 68-element Fibonacci set with objective = size - 8*violations
(allowing temporary violations). After 58 seconds: NO improvement. The 68-element Fibonacci
set is a hard local optimum even under SA with violation relaxation.

**ILP attempt (abandoned)**: Tried PuLP ILP for M=200. The quadruple-constraint formulation
generated 661,650 constraints — far too many for CBC in 24 seconds. CBC returned invalid
all-elements-selected solution after timing out. ILP requires a better formulation and
offline execution.

## 2. What Information Did I Lack?

- **Whether there exist Fibonacci-like sequences giving 70+ elements**: The 69 ceiling
  appears hard. A more exhaustive search (100,000+ parameter pairs) might find 70, but
  likely not 80+. Would need ~30 minutes offline.

- **Correct ILP formulation for small M**: The quadruple-constraint formulation scales
  poorly. The difference-indicator formulation (z_{a,d} variables) would be much better.
  Not sure of the exact optimal formulation without more research.

- **Blocker count comparison**: I didn't measure how many blockers the 69-element search set
  has vs Singer-102's 40+. This would confirm/refute whether SA has potential.

## 3. What Given Facts Might Be Wrong or Outdated?

- **"ILP is the only reliable path to 103+"** (from state of affairs): This might
  be too optimistic. ILP for N=10000 has far too many constraints in any formulation
  I considered. Even offline, it would require serious solver infrastructure (Gurobi,
  CPLEX) rather than PuLP/CBC.

- **"SA from algebraic seeds fails due to 40+ blockers"**: This was for Singer-102.
  Our 69-element search set also resists SA (even with violations allowed). The 40+
  blocker problem isn't specific to Singer.

## 4. Was the State of Affairs Accurate?

Yes. Key observations confirmed:
- ILP is rated "HIGHEST PRIORITY" but is infeasible without better formulation ✓
- SA from search-found sets also fails ✓ (new finding)
- Algebraic constructions are the ceiling ✓

**One correction/addition**: The coverage map says "Backtracking/exhaustive: verification only - LOW priority". I agree — backtracking can verify small-M solutions but doesn't scale to N=10000 within time limits.

**New entry for coverage map**:
- "Fibonacci/structured ordering greedy": 3 trials, best 69, status: "Ceiling ~69 for N=10000"

## 5. What Would I Do Differently?

1. Implement ILP with difference-indicator variables for M≤100, verify Singer is optimal there
2. Measure blocker counts for search-found 69-element set vs Singer-102
3. Try parallel greedy runs with shared-memory to explore more orderings faster

## 6. Specific Experiments to Run

**Experiment A — Correct ILP formulation (offline, 10+ minutes)**:
```python
# For M=100: difference indicators
import pulp
M = 100; N = M + 1
prob = pulp.LpProblem("sidon", pulp.LpMaximize)
x = [pulp.LpVariable(f"x_{i}", cat='Binary') for i in range(N)]
prob += pulp.lpSum(x)
# For each diff d, at most one pair (a, a+d) can have both 1
for d in range(1, N):
    for a in range(N-d):
        z = pulp.LpVariable(f"z_{d}_{a}", cat='Binary')
        prob += z <= x[a]; prob += z <= x[a+d]
        prob += x[a] + x[a+d] - 1 <= z
    prob += pulp.lpSum(pulp.LpVariable(f"z_{d}_{a}") for a in range(N-d)) <= 1
# N=101 x vars, ~5050 z vars, ~15250 constraints: manageable
```

**Experiment B — Blocker analysis on 69-element set**:
```python
def blocker_count_dist(S, N=10000):
    used_diffs = set(abs(S[j]-S[i]) for i in range(len(S)) for j in range(i+1,len(S)))
    return [sum(1 for s in S if abs(c-s) in used_diffs)
            for c in range(N+1) if c not in set(S)]
# Compare: 69-element search set vs Singer-102
```

**Experiment C — Longer ordering search (offline)**:
For 100,000+ Fibonacci parameter pairs with 5 minutes runtime, might find 70+.

## 7. What Surprised Me?

1. **SA completely fails even with violation relaxation**: After 58 seconds, the SA
   never improved on 68. The swap neighborhood (remove 1, add 1) is essentially
   disconnected at 68+ elements. The "landscape" has no improving paths.

2. **ILP constraint count explosion**: Expected ~30,000 constraints for M=200.
   Actual: 661,650. The quadruple-constraint count scales as O(M^3) not O(M^2).
   Big mistake in my estimation.

3. **69 is achievable but 70 is hard**: After 2400 Fibonacci parameter trials, found
   69 but not 70. The Fibonacci-ordering ceiling seems to be 69 for N=10000.

4. **Wythoff sequence (floor(k*φ)) gives only 66**: Despite being the "most Fibonacci-like"
   integer sequence, Wythoff gives exactly the same as ascending order. This means
   the golden ratio spacing doesn't help - it's the EXPONENTIAL GROWTH property
   that matters, not the ratio itself.

## 8. Helper Tools Feedback

**helpers.search.greedy_sidon**: Used extensively. Correct and fast. Very useful.

**Helper I wished existed**: 
`helpers.analysis.count_blockers_per_element(S, N)`: For each non-member c,
return list of (c, count) sorted by count. This would enable targeted LNS removal
(remove the element that, when removed, unblocks the most new candidates).

## 9. Time Budget

This resume session used ~2 hours of total wall-clock time (mostly blocked
by slow evaluations). Key findings:
1. sol05 (wide ordering search): 56 seconds → score 69
2. sol06 (SA with violations): 58 seconds → score 68
3. ILP test: 87 seconds → failed (score 0)

**With more time**:
1. Run the correct ILP formulation offline for M=100-500 to verify Singer optimality
2. Try 10,000+ greedy orderings with different mathematical structures (e.g., look at
   sequences from OEIS related to Sidon sets)
3. Profile the 69-element set structure vs Singer to understand why both are hard local optima

**Bottom line**: Pure search approaches ceiling at ~69 for N=10000. The gap from 69 to
102 (Singer) to 109 (target) is bridgeable only by algebraic methods or ILP with
sophisticated solver infrastructure. The Fibonacci ordering finding (66→69) is a useful
marginal improvement but not a breakthrough.
