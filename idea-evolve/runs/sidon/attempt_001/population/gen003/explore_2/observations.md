# Observations — Explore 2, Generation 3 (Resume Session)

## Context
This is a RESUME session. The original explore_2 session ran 5 solutions
(scores: 63, 0, 67, 65, 68) and wrote a full report. This session extends that work.

## New Findings in This Session

### SA with Violation Relaxation (sol06, score=68)
Applied simulated annealing starting from the 68-element Fibonacci set, allowing
temporary violations (objective = size - 8*violations). After 58 seconds:
- **No improvement over 68**
- SA accepted few moves (most swaps made things worse)
- Conclusion: the 68-element Fibonacci set IS a deep local optimum under swap moves

### Extended Ordering Search (sol05, score=69)
Searched wider parameter spaces for greedy orderings:
- Fibonacci(a,b) for a∈[0,39], b∈[a+1, a+59]: **found 69-element sets**
  (parameter space much wider than previous session's 450 pairs)
- Geometric sequences (bases 1.3–3.0): best was ~67
- Wythoff sequence (floor(k×φ)): ~66
- LNS on 69-element result: no improvement

Key finding: **broader Fibonacci sweep gives 69, not 70+**. The 69 ceiling
appears robust across Fibonacci-type sequences.

## Blocker Analysis (ILP Attempt)

PuLP (ILP solver) IS available. However:
- For M=200, the quadruple-constraint formulation generates **661,650 constraints**
  (far more than estimated earlier). CBC solver takes 87+ seconds.
- ILP is feasible for OFFLINE analysis but NOT within a 24-60 second entrypoint().
- The CBC solver returned an invalid all-1s solution when time-limited to 10 seconds.

**Recommendation for future agents**: Use scipy.optimize.milp with a better
formulation (difference indicator variables z_{a,d}) for M≤100. Expected:
~10,200 binary variables and ~30,600 constraints for M=100. Should solve in
~10 seconds.

## Key Insight: Why Search Can't Beat 66-70

Mathematical analysis confirms the structural barrier:
- A 66-element greedy Sidon set uses 66×65/2 = 2145 differences
- Probability that a random candidate is valid: ≈ (1-2145/10000)^66 ≈ 2×10^{-7}
- Expected valid candidates: ~0. So the set is saturated.

After removing k=20 elements (46 remaining, 1035 diffs used):
- Valid candidates: ~66. Greedy adds ~3-5 more (since each blocks ~47 others).
- Total: 46 + 5 = 51 < 66. LNS almost always makes things WORSE.
- Occasionally (by luck) adds back 21 elements → 67. Very rare.

## What Ordering Properties Help

The best orderings (Fibonacci, 68-69) share:
- **Exponential growth**: elements grow by factor ~φ≈1.618, so differences
  between consecutive elements double over time
- **Non-repetitive differences**: Fibonacci sequences have the property that
  no Fibonacci number equals the sum of two others, so early differences
  are automatically distinct
- **Small initial elements**: starting with small a,b means small elements
  are used first, consuming "small difference slots" efficiently

Standard ascending greedy (66) uses differences 1,2,3,... efficiently.
Fibonacci (68-69) is slightly better because it avoids certain repeated-diff traps.

## What's Still Untested

1. **ILP for M=100 with correct formulation**: might verify Singer optimality
2. **Blocker counts for 68/69-element sets vs Singer-102**: are they fewer?
3. **Parallel multi-start with much longer runtime**: maybe 500+ restarts over 10 minutes?
4. **Complete SA space**: SA currently restarts every 58 seconds; with 10,000 restarts
   it might find 70+ but probably not 80+
5. **Correct Bose-Chowla/Ruzsa constructions** (non-Singer algebraic)
