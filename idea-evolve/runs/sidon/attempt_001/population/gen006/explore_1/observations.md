# Observations — gen006_explore_1

## Summary of attempts

| Solution | Approach | Score |
|----------|----------|-------|
| sol01.py | DFS/backtracking with randomized restarts | 66 |
| sol02.py | ET(71)+greedy+1-opt+2-opt+LNS | 75 |
| sol03.py | ET(71)+greedy+1-opt+aggressive LNS (k=2-15 removals) | 75 |
| sol04.py | Randomized greedy restarts with quick 1-opt | 75 |

---

## Finding 1: DFS/Backtracking is impractical for N=10000 (idea_005 DEBUNKED)

**sol01** tested systematic DFS with constraint propagation. It achieved **66** — the greedy baseline — in the full 27s budget.

Why DFS fails:
- Sequential ordering (0..N) IS the greedy algorithm. The forward pass finds exactly the greedy set (66), then backtracks to try alternatives.
- Backtracking into the search tree at depth ~66 requires exploring an exponential space.
- In 27s, Python can explore only the top few levels of backtracking — not enough to escape the greedy basin.
- Randomized restarts (shuffled candidate order) also hit the greedy ceiling (~60-66 per run).

**Verdict: Archive idea_005.** DFS/backtracking is definitively impractical for N=10000 within the 30s time limit. The search tree is too large for Python. Even with perfect pruning, the combinatorial space is astronomical.

If this approach were to work, it would require:
- A compiled language (C++/Rust) for 100x speedup
- Or a much smaller N (N≤200 is tractable, N≤1000 might work with tight pruning)

---

## Finding 2: 75 is a ROBUST local optimum for ET(71)-based approaches

All 3 non-DFS solutions converged to **exactly 75**.

Experiments tried to escape this:
1. **2-opt** (remove all pairs): too slow (O(n²*N) per pass, ~200s in Python)
2. **LNS with k=2..15 removals**: all random restarts return to 75 after greedy re-extension
3. **ET base modification** (remove 1-5 ET elements, shuffle fill): always returns to 75
4. **Fully random greedy + 1-opt**: returns to ~75 or slightly below

The 75 plateau is robust. It appears to be a genuine local optimum for any 1-opt-like move in the ET neighborhood. To escape it would require either:
- A fundamentally different initial construction (not ET-based)
- Or a deeper search (larger neighborhoods, which are too expensive in Python/30s)

---

## Finding 3: ET(71) construction is nearly optimal for non-algebraic methods

ET(71) gives exactly 70 elements (k=0..70, filtered to [0,10000]).
Greedy extension adds 5 more = 75.
1-opt converges immediately (already at local optimum after the first pass).

The 75-element local optimum is confirmed across 25+ restarts in gen2, and now across all 4 sol02-04 attempts here.

---

## What I didn't have time to try

1. **DFS in C** (via ctypes/subprocess): could be 100x faster than Python DFS, might reach 75+ via backtracking
2. **Exact 2-opt on 75-element set**: requires 2775 pairs × ~1s each ≈ 46min. Infeasible in 30s.
3. **Simulated annealing accepting worse solutions**: might escape the 75 plateau stochastically
4. **Modular constructions from non-prime-power fields**: didn't implement (time ran out)
5. **Random independent restarts from a diverse set of seeds** (>100 restarts): each runs in ~0.3s for greedy alone, might explore more local optima with more time

---

## What might actually work

1. **Remove 25+ elements from the 75-element set**: essentially a restart from a 50-element seed. But this loses the ET structure and likely returns to 65-70.

2. **SA with large step moves**: Simulated annealing that accepts size-decrease moves occasionally could explore the energy landscape beyond 75. Previous SA attempts failed (gen 2-4, debunked as cluster 003), but all were initialized from Singer/greedy, not from the 75-element ET set.

3. **CP-SAT with ET(71) as seed**: The 75-element ET set might be a better warm-start than the 105-mark algebraic set for anti-algebraic search. Untested.

4. **Iterated hillclimbing with different 1-opt acceptance criteria**: Instead of "only accept improvements", accept any move of size ≥ 74 (relaxed acceptance). This could escape the 75 basin by temporarily accepting 74-element solutions.

---

## Note on the State of Affairs

The SoA says "Remove-k (k=3-10) perturbation on 105-mark set: 0 trials" — this is different from what I did. I removed elements from the 75-mark ET set, not the 105-mark algebraic set. These are very different experiments. The 105-mark set perturbation might behave differently (and is the more strategically interesting case given the algebraic ceiling).
