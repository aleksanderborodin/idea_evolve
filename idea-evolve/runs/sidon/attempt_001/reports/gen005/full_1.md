# Debrief Report — gen005_full_1 (full_1)

## Solution Table

| File | Fitness | is_valid | Approach |
|------|---------|----------|----------|
| sol01.py | **102** | 1 | Singer q=101 baseline (CP-SAT fallback after UNKNOWN) |

Best score this session: **102** (no improvement over previous best).

---

## 1. What Did I Try?

### Part A: Singer+1 Structure Analysis

Used CP-SAT integer element formulation to find optimal Sidon sets for small N:

- **q=7, N=56**: Singer=8, optimal=**10** (OPTIMAL proved). Overlap: 3 elements only.
  - Singer set and optimal set are structurally unrelated (5/8 Singer elements dropped).
- **q=11, N=132**: Singer=12, optimal=**13** (OPTIMAL proved). Overlap: 1 element only.
  - Only 1 of 12 Singer elements appears in the optimal set.
- **q=17, N=306**: Singer=18, optimal=18 (k=19 UNKNOWN at 120s — Singer may or may not be optimal).
- **q=23, N=552**: Singer=24, optimal=24 (k=25 UNKNOWN at 120s — same caveat).

Key finding: For small q, optimal Sidon sets are completely different from Singer sets. The "Singer+1" framing is misleading — it's more like "replace Singer entirely with a better set."

Extra elements do NOT use only "free" differences (`extra_uses_free_diffs: False`). They require dropping Singer elements and reorganizing the difference structure from scratch.

### Part B: Extended CP-SAT for k=103, N=10000

Three phases, each 600 seconds, all returned UNKNOWN:

1. **No hint, portfolio search, 16 workers (600s)** → UNKNOWN
2. **Partial Singer hint (51 lower elements), portfolio search, 16 workers (600s)** → UNKNOWN
3. **Full Singer hint (102 elements), auto search, 16 workers (600s)** → UNKNOWN (session terminated before completion)

CP-SAT presolve reduced to 5253 variables (102 affine relations, 101 redundant constraints). Search tree progressed but found no feasible k=103 solution.

---

## 2. What Information Did I Lack?

- **Why CP-SAT's search is stuck**: Is it repeatedly finding k=102 solutions and failing to add a 103rd? Or failing at much lower k? The verbose log showed tree progress but no near-misses.
- **Published F(10000)**: Still unknown. If the true optimal is 102, the CP-SAT effort is wasted. If it's 105+, we need entirely different methods.
- **Whether q=17 and q=23 Singer is actually optimal**: With 120s budget those cases returned UNKNOWN. A longer run (10 min each) could establish whether Singer becomes optimal for larger q.

---

## 3. What Given Facts Might Be Wrong or Outdated?

- "Singer is the ceiling" — **False for small N**, possibly false for N=10000 too. The small-N analysis is definitive: Singer is provably suboptimal for q=7 (-25%) and q=11 (-8%).
- The gen4 report said "optimal is 10" for N=56 — confirmed correct.
- The gen4 report said "optimal is 13" for N=132 — confirmed correct.

---

## 4. Was the State of Affairs Accurate?

Mostly yes. The SoA correctly identified CP-SAT and Singer+1 analysis as priorities. The formulation description was correct (matching gen4 sol01.py). The main gap: SoA didn't anticipate that the Singer hint might be counterproductive (analysis suggests the optimal set for N=10000 may share very few elements with Singer).

---

## 5. What Would I Do Differently?

1. **Shorter CP-SAT phases, more variety**: Instead of 3×600s, try 10×60s with different random seeds and strategies. CP-SAT's randomized components may occasionally get lucky.
2. **Anti-Singer hint**: Explicitly forbid the top 50 Singer elements to force exploration far from Singer. The analysis shows the optimal is far from Singer for small N.
3. **Find minimum N for k=103**: Binary search on N to find the smallest N where k=103 is feasible. If it's N=9500, we can scale back. This would give CP-SAT a tractable sub-problem.
4. **Gurobi trial**: The most likely path to finding k=103. Open-source CP-SAT may simply not have adequate branching for this problem class.

---

## 6. Specific Experiments to Run

1. **Binary search on N**: Find smallest N where k=103 is feasible. Try N=5000, N=7500, N=9000, N=10000. Each run 300s. If N=9000 is feasible but N=10000 is not, that's a near-miss to report.
2. **Gurobi for k=103**: If available, a 60s Gurobi run likely outperforms 600s CP-SAT.
3. **Extend q=17 and q=23 analysis**: Run 10 minutes each to check if Singer is actually optimal for larger q. Determines whether the "Singer is suboptimal" finding generalizes.
4. **ILP maximize at N=1000-5000**: Find largest Sidon set at intermediate scales. Compare to Singer. Establishes the trend of Singer gap vs N.

---

## 7. What Surprised Me?

- **No feasible k=103 found even without any Singer hint**: The no-hint run (Phase 1) explored different regions of the search space but still found nothing. This suggests k=103 is either genuinely hard (many constraints, sparse feasible region) or actually infeasible for N=10000.
- **q=11 optimal set shares only 1 element with Singer**: I expected at least 50% overlap. The complete structural divergence suggests Singer constructions are not just "nearly optimal" — they may be in a completely different part of the solution space for small N.
- **CP-SAT presolve eliminated 102 affine relations**: CP-SAT found and exploited the ordering constraints efficiently. The model is well-suited to the solver — the problem difficulty is genuine, not a modeling artifact.

---

## 8. Helper Tools Feedback

- `helpers/singer.py` (`find_singer_set`): worked correctly. Fast and reliable.
- `helpers/core.py`: not needed directly.

**Desired helper**: A `solve_sidon_cpsat(k, N, hint, time_limit, workers, strategy)` encapsulating the integer element formulation would save significant boilerplate. The gen4 report suggested this and it's still needed — the formulation is non-obvious and every agent re-derives it.

---

## 9. Time Budget

Session time was tight. Accomplished:
- Full Singer+1 analysis for q=7, q=11, q=17, q=23 (~5 min)
- 3 × 600s CP-SAT phases for k=103 (~30 min, terminated partway through phase 3)

With more time:
- Complete phase 3 and phase 4 (k=104 attempt)
- Binary search on N for k=103 feasibility
- Extend q=17/q=23 analysis to 10 minutes each
