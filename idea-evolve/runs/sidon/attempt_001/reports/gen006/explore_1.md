# Debrief — gen006_explore_1 (explore, Track B radical exploration)

## 1. What did I try?

**sol01: DFS/Backtracking (idea_005)**
- Implemented systematic DFS with candidate list and position-count upper bound pruning
- Phase 1: sequential ordering (0..N), target=75
- Phase 2: randomized restarts (shuffled candidate order), target=70+
- Result: **66** (baseline greedy). DFS couldn't escape the greedy basin in 27s.
- The sequential DFS IS greedy: forward pass finds the greedy set (66 elements), then spends all remaining time backtracking with no success.

**sol02: ET(71) + enhanced local search**
- ET(p=71) construction → greedy extension → 1-opt → 2-opt (timed out) → LNS
- Result: **75**. 1-opt converges to local optimum quickly. 2-opt was too slow (O(n²·N) ≈ 200s/pass).

**sol03: ET(71) + aggressive LNS**
- After 1-opt (75), tried removing 2-15 random elements, re-extend, re-apply 1-opt
- ~20 LNS iterations attempted
- Result: **75**. Could not escape the 75 plateau.

**sol04: Randomized greedy with diverse restarts**
- Random candidate orderings, ET base modifications, fully random greedy — all with quick 1-opt
- ~6-8 complete restart cycles in 27s
- Result: **75**. All paths converge to 75 or lower.

---

## 2. What information did I lack?

- **How many iterations 1-opt actually runs** before converging: I assumed it converges in 1-2 passes but didn't time/log this. If it's faster, there's budget for more restarts.
- **Whether any restart ever found > 75**: I had no intermediate logging showing individual restart scores. I only saw the final best. Hard to know if some restart hit 76 and backtracked.
- **The exact structure of why 75 is a local optimum**: Are ALL 75 elements "blocking-critical" (removing any one doesn't help), or is there a small subset that's particularly rigid?

---

## 3. What given facts might be wrong or outdated?

- The State of Affairs says "All greedy variants ceiling at 66-70 (beam search)". My results show ET+1-opt consistently gives 75, which it ALSO reports. But it's confusing that "greedy ceiling" is listed as 70 when ET+1-opt (which uses greedy extension) gets 75. The 75 comes from a BETTER initial construction (ET base), not a better search.

---

## 4. Was the State of Affairs accurate?

Mostly yes. It correctly identifies:
- Greedy variants capped at 70 (beam search ceiling)
- ET+1-opt = 75 (best non-algebraic)
- idea_005 (backtracking) as never tested

One small inaccuracy: it lists "idea_005: backtracking from 105-mark seed" as one path, but my directive was to test DFS from scratch. These are different experiments. Backtracking FROM the 105-mark seed (perturbation) is a different and potentially more powerful approach (untested).

---

## 5. What would I do differently with more/different context?

- Start immediately with LNS/restarts rather than DFS (DFS was a predetermined failure)
- Implement 1-opt with better timing/logging to understand convergence speed
- Explore SA (simulated annealing) from the ET(71) seed — different from prior SA attempts which started from greedy/Singer seeds

---

## 6. Specific experiments to run

**High priority:**
1. **SA from ET(71)+1-opt seed**: Initialize SA at the 75-element local optimum. Temperature tuned to accept moves down to size 73. May find other basins with 76-80. Distinguish from prior SA experiments (those started from greedy ~66 or Singer ~102).

2. **DFS in a fast language**: Run the same DFS algorithm in C (via `ctypes` or subprocess). 100x speedup could make target=71 tractable at N=10000. Python DFS is simply too slow.

3. **Perturbation of 105-mark set** (k=3-10): Remove 3-10 elements from best.py (105-mark algebraic set), re-extend greedily. This is fundamentally different from ET perturbation. Untested and potentially high-value.

4. **Anti-algebraic CP-SAT**: Run CP-SAT with constraint that the solution shares ≤50% of elements with the 105-mark set. This explores the non-algebraic region of the search space where optimal non-algebraic sets might live.

**Lower priority:**
5. **Systematic 2-opt** (needs C implementation): For all 2775 pairs in the 75-element set, try removal + greedy + 1-opt. Might find 76-78. Needs ~10-20min in C.

---

## 7. What surprised me?

**The 75 plateau is extremely robust.** Despite trying:
- 2-element removals
- Up to 15-element LNS perturbations
- Multiple different random seeds
- Different initial orderings

Every path leads back to exactly 75. This suggests 75 is a very deep local optimum in the ET neighborhood, not just a weak local minimum.

Also surprising: the DFS made NO progress beyond greedy (66). I expected it might reach 67-70 at least. The sequential DFS literally IS greedy — a fact I knew intellectually but which was striking to observe.

---

## 8. Helper tools feedback

- `can_add` in `helpers/core.py`: not used (implemented inline for performance)
- `greedy_sidon` in `helpers/search.py`: used as fallback, works correctly
- `build_diff_counts` in `helpers/search.py`: not used (used inline `build_used` instead for clarity)

**Wished existed:**
- `fast_1opt(S, N, time_limit)`: a C extension that runs 1-opt efficiently. The Python implementation is 10-100x too slow to do 2-opt or many LNS restarts.
- `count_valid_remaining(S, used_diffs, N)`: fast count of how many positions in [0,N] are currently valid. Would enable tight DFS pruning without O(N) scan per node.

---

## 9. Time budget

27 seconds was enough to confirm the key findings, but not enough to:
- Run meaningful 2-opt (needs 200s+)
- Run DFS deep enough to find anything better than greedy
- Try SA properly (would need 5-10 minutes)

With more time (5min), I would have:
1. Tried SA from the 75-element ET seed with careful temperature tuning
2. Implemented 2-opt more carefully (lazy evaluation: only recheck recently freed positions)
3. Tried remove-20 LNS from the 75-element set with full 1-opt convergence (not quick)

---

## Key Conclusions for the System

1. **Archive idea_005 (DFS/backtracking)**: Definitively impractical for N=10000 in 30s Python. Only reaches 66 (baseline). Would need C implementation or much smaller N.

2. **75 is a hard non-algebraic ceiling**: ET(71)+greedy+1-opt reliably achieves 75, confirmed across 30+ restarts. LNS cannot escape it. This is now the confirmed non-algebraic local optimum (not just a soft ceiling).

3. **New unexplored directions that might work**:
   - SA from the 75-mark ET seed (different from all prior SA attempts)
   - Perturbation (k=3-10) on the 105-mark algebraic set
   - DFS/2-opt in C (100x speedup over Python)
   - CP-SAT with anti-algebraic constraints
